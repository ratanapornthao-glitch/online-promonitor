"""Online Promonitor metrics.

Reads data/output/extracted.csv (+ sku_map.csv) and writes metric tables to
data/output/metrics/. Every number in the insight briefs and the dashboard
comes from these tables.

Usage: python src/analyze.py [--data-dir data/output]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

NUMERIC = [
    "size_ml_g", "pack_qty", "list_price", "display_price", "shop_voucher_thb",
    "min_spend_or_qty", "effective_price", "price_per_unit", "discount_depth_pct",
    "confidence",
]
FAKE_DISCOUNT_TOLERANCE = 0.02  # list price >2% above normal counts as raised


def load(data_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(data_dir / "extracted.csv")
    for col in NUMERIC:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["pack_qty"] = df["pack_qty"].fillna(1)
    df["shop_voucher_thb"] = df["shop_voucher_thb"].fillna(0)
    df["upsell_mechanic"] = df["upsell_mechanic"].fillna("none")
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")

    # Recompute derived fields so the formulas in CLAUDE.md always hold.
    df["effective_price"] = df["display_price"] - df["shop_voucher_thb"]
    df["price_per_unit"] = df["effective_price"] / (df["size_ml_g"] * df["pack_qty"])
    df["discount_depth_pct"] = (1 - df["effective_price"] / df["list_price"]) * 100

    sku_path = data_dir / "sku_map.csv"
    if sku_path.exists():
        sku = pd.read_csv(sku_path)[["brand", "product_name_raw", "platform", "sku_id"]]
        df = df.merge(sku.drop_duplicates(["brand", "product_name_raw", "platform"]),
                      on=["brand", "product_name_raw", "platform"], how="left")
    else:
        df["sku_id"] = pd.NA
    # Fall back to the raw title so unmatched rows are still analysable per platform.
    df["sku_id"] = df["sku_id"].fillna(df["brand"] + "|" + df["product_name_raw"])
    return df


def listing_level(df: pd.DataFrame) -> pd.DataFrame:
    """One row per brand × sku × platform × campaign (averaging repeat snapshots)."""
    return (df.groupby(["brand", "sku_id", "platform", "campaign_type", "campaign_name"], dropna=False)
              .agg(list_price=("list_price", "mean"),
                   effective_price=("effective_price", "mean"),
                   price_per_unit=("price_per_unit", "mean"),
                   discount_depth_pct=("discount_depth_pct", "mean"),
                   has_upsell=("upsell_mechanic", lambda s: (s != "none").any()))
              .reset_index())


def campaign_uplift(lst: pd.DataFrame) -> pd.DataFrame:
    """Discount in each campaign minus discount on normal days, same SKU and platform."""
    normal = (lst[lst.campaign_type == "normal"]
              .groupby(["brand", "sku_id", "platform"])["discount_depth_pct"].mean()
              .rename("normal_discount_pct"))
    camp = lst[lst.campaign_type != "normal"].join(normal, on=["brand", "sku_id", "platform"])
    camp = camp.dropna(subset=["normal_discount_pct", "discount_depth_pct"])
    camp["uplift_pp"] = camp["discount_depth_pct"] - camp["normal_discount_pct"]
    return (camp.groupby(["campaign_type", "campaign_name", "brand"])
                .agg(normal_discount_pct=("normal_discount_pct", "mean"),
                     campaign_discount_pct=("discount_depth_pct", "mean"),
                     uplift_pp=("uplift_pp", "mean"),
                     listings_compared=("sku_id", "size"))
                .round(1).reset_index())


def uplift_by_type(uplift: pd.DataFrame) -> pd.DataFrame:
    return (uplift.groupby(["brand", "campaign_type"])["uplift_pp"].mean().round(1)
                  .unstack("campaign_type").reset_index())


def promo_breadth(lst: pd.DataFrame) -> pd.DataFrame:
    lst = lst.assign(on_promo=(lst["discount_depth_pct"].fillna(0) > 0.5) | lst["has_upsell"])
    return (lst.groupby(["campaign_type", "campaign_name", "brand"])
               .agg(listings=("sku_id", "size"), on_promo=("on_promo", "sum"))
               .assign(promo_breadth_pct=lambda t: (t.on_promo / t.listings * 100).round(1))
               .reset_index())


def channel_depth(lst: pd.DataFrame) -> pd.DataFrame:
    return (lst.groupby(["campaign_type", "brand", "platform"])["discount_depth_pct"]
               .mean().round(1).rename("avg_discount_pct").reset_index())


def best_channel_share(lst: pd.DataFrame) -> pd.DataFrame:
    """% of SKUs (seen on 2+ platforms) where each platform is cheapest per unit."""
    lst = lst.assign(compare_price=lst["price_per_unit"].fillna(lst["effective_price"]))
    lst = lst.dropna(subset=["compare_price"])
    keys = ["campaign_type", "campaign_name", "brand", "sku_id"]
    multi = lst.groupby(keys)["platform"].transform("nunique") >= 2
    lst = lst[multi]
    if lst.empty:
        return pd.DataFrame(columns=["campaign_type", "campaign_name", "brand", "platform",
                                     "cheapest_count", "skus_compared", "best_channel_share_pct"])
    cheapest = lst.loc[lst.groupby(keys)["compare_price"].idxmin()]
    counts = cheapest.groupby(["campaign_type", "campaign_name", "brand", "platform"]).size()
    totals = cheapest.groupby(["campaign_type", "campaign_name", "brand"]).size()
    out = counts.rename("cheapest_count").reset_index()
    out = out.join(totals.rename("skus_compared"), on=["campaign_type", "campaign_name", "brand"])
    out["best_channel_share_pct"] = (out.cheapest_count / out.skus_compared * 100).round(1)
    return out


def upsell_mix(df: pd.DataFrame) -> pd.DataFrame:
    mix = (df.groupby(["campaign_type", "brand", "platform", "upsell_mechanic"])
             .size().rename("listings").reset_index())
    mix["share_pct"] = (mix.listings / mix.groupby(["campaign_type", "brand", "platform"])
                        ["listings"].transform("sum") * 100).round(1)
    return mix


def upsell_threshold(df: pd.DataFrame) -> pd.DataFrame:
    up = df[(df.upsell_mechanic != "none") & df.min_spend_or_qty.notna()]
    return (up.groupby(["campaign_type", "brand", "platform", "upsell_mechanic"])["min_spend_or_qty"]
              .agg(median_threshold="median", min_threshold="min", max_threshold="max", offers="size")
              .reset_index())


def fake_discount(lst: pd.DataFrame) -> pd.DataFrame:
    normal = (lst[lst.campaign_type == "normal"]
              .groupby(["brand", "sku_id", "platform"])["list_price"].min()
              .rename("normal_list_price"))
    camp = lst[lst.campaign_type != "normal"].join(normal, on=["brand", "sku_id", "platform"])
    flagged = camp[camp.list_price > camp.normal_list_price * (1 + FAKE_DISCOUNT_TOLERANCE)].copy()
    flagged["list_price_raise_pct"] = ((flagged.list_price / flagged.normal_list_price - 1) * 100).round(1)
    flagged["discount_depth_pct"] = flagged["discount_depth_pct"].round(1)
    return flagged[["campaign_name", "brand", "sku_id", "platform", "normal_list_price",
                    "list_price", "list_price_raise_pct", "discount_depth_pct"]]


def promo_frequency(df: pd.DataFrame) -> pd.DataFrame:
    promo = df[(df.discount_depth_pct.fillna(0) > 0.5) | (df.upsell_mechanic != "none")]
    promo = promo[promo.campaign_type != "normal"].assign(month=promo.snapshot_date.dt.strftime("%Y-%m"))
    return (promo.groupby(["month", "brand", "platform"])["campaign_name"].nunique()
                 .rename("campaigns_joined").reset_index())


def promo_calendar(df: pd.DataFrame, lst: pd.DataFrame) -> pd.DataFrame:
    """Competitor Promo Calendar: one row per campaign × brand × platform, in date order,
    so the team can see each competitor's rhythm and anticipate the next campaign."""
    dates = (df.groupby("campaign_name")["snapshot_date"].min().dt.strftime("%Y-%m-%d")
               .rename("start_date"))
    lst = lst.assign(on_promo=(lst["discount_depth_pct"].fillna(0) > 0.5) | lst["has_upsell"])
    cal = (lst.groupby(["campaign_name", "campaign_type", "brand", "platform"])
              .agg(avg_discount_pct=("discount_depth_pct", "mean"),
                   max_discount_pct=("discount_depth_pct", "max"),
                   listings=("sku_id", "size"), on_promo=("on_promo", "sum"))
              .reset_index())
    cal["promo_breadth_pct"] = (cal.on_promo / cal.listings * 100).round(1)
    top = (df[df.upsell_mechanic != "none"]
           .groupby(["campaign_name", "brand", "platform"])["upsell_mechanic"]
           .agg(lambda s: s.mode().iloc[0]).rename("top_upsell_mechanic"))
    cal = cal.join(dates, on="campaign_name").join(top, on=["campaign_name", "brand", "platform"])
    cal["top_upsell_mechanic"] = cal["top_upsell_mechanic"].fillna("none")
    cal[["avg_discount_pct", "max_discount_pct"]] = cal[["avg_discount_pct", "max_discount_pct"]].round(1)
    cols = ["start_date", "campaign_name", "campaign_type", "brand", "platform", "avg_discount_pct",
            "max_discount_pct", "promo_breadth_pct", "top_upsell_mechanic", "listings"]
    return cal[cols].sort_values(["start_date", "brand", "platform"]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/output")
    args = ap.parse_args()
    data_dir = Path(args.data_dir)
    out = data_dir / "metrics"
    out.mkdir(parents=True, exist_ok=True)

    df = load(data_dir)
    lst = listing_level(df)
    uplift = campaign_uplift(lst)
    tables = {
        "campaign_uplift": uplift,
        "uplift_by_type": uplift_by_type(uplift),
        "promo_breadth": promo_breadth(lst),
        "channel_depth": channel_depth(lst),
        "best_channel_share": best_channel_share(lst),
        "upsell_mix": upsell_mix(df),
        "upsell_threshold": upsell_threshold(df),
        "fake_discount": fake_discount(lst),
        "promo_frequency": promo_frequency(df),
        "promo_calendar": promo_calendar(df, lst),
    }
    for name, table in tables.items():
        table.to_csv(out / f"{name}.csv", index=False)
        print(f"{name:20s} {len(table):4d} rows")
    print(f"Wrote {len(tables)} tables to {out}")


if __name__ == "__main__":
    main()
