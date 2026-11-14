"""Compare the extractor's output with hand-labelled ground truth.

ground_truth.csv uses the same columns as extracted.csv, filled in by a
team member for a random 20-30% of screenshots.

Usage: python src/evaluate.py [--extracted data/output/extracted.csv]
                              [--truth data/ground_truth.csv]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

PRICE_FIELDS = ["list_price", "display_price", "shop_voucher_thb", "size_ml_g", "min_spend_or_qty"]
CATEGORY_FIELDS = ["platform", "upsell_mechanic"]
PRICE_TOLERANCE_THB = 1.0


def _num_match(a: pd.Series, b: pd.Series) -> pd.Series:
    a, b = pd.to_numeric(a, errors="coerce"), pd.to_numeric(b, errors="coerce")
    both_null = a.isna() & b.isna()
    return both_null | ((a - b).abs() <= PRICE_TOLERANCE_THB)


def _cat_match(a: pd.Series, b: pd.Series) -> pd.Series:
    norm = lambda s: s.fillna("none").astype(str).str.strip().str.lower()
    return norm(a) == norm(b)


def sku_match_rows(truth_path: Path, map_path: Path) -> list[dict]:
    """Pairwise SKU matching accuracy: for every pair of listings of the same brand,
    did the matcher get 'same product' vs 'different product' right?"""
    if not (truth_path.exists() and map_path.exists()):
        return []
    key = ["brand", "product_name_raw", "platform"]
    truth = pd.read_csv(truth_path)[key + ["sku_id"]].drop_duplicates(key)
    pred = pd.read_csv(map_path)[key + ["sku_id"]].drop_duplicates(key)
    m = truth.merge(pred, on=key, suffixes=("_true", "_pred"), how="left")
    pairs = m.merge(m, on="brand")
    pairs = pairs[(pairs.product_name_raw_x + pairs.platform_x) < (pairs.product_name_raw_y + pairs.platform_y)]
    same_true = pairs.sku_id_true_x == pairs.sku_id_true_y
    same_pred = pairs.sku_id_pred_x.notna() & (pairs.sku_id_pred_x == pairs.sku_id_pred_y)
    ok = same_true == same_pred
    out = [{"field": "sku_match (all pairs)", "rows": len(pairs), "correct": int(ok.sum()),
            "accuracy_pct": round(ok.mean() * 100, 1) if len(pairs) else None}]
    if same_true.any():  # recall on true matches is the harder, more telling number
        ok_pos = ok[same_true]
        out.append({"field": "sku_match (true pairs found)", "rows": len(ok_pos),
                    "correct": int(ok_pos.sum()), "accuracy_pct": round(ok_pos.mean() * 100, 1)})
    return out


def time_rows(log_path: Path) -> list[dict]:
    """Minutes per screenshot: agent pipeline vs manual baseline (from run_log.csv)."""
    if not log_path.exists():
        return []
    log = pd.read_csv(log_path)
    if log.empty or log["images"].sum() == 0:
        return []
    agent = log["minutes_to_insight"].sum() / log["images"].sum()
    manual = log["manual_baseline_minutes"].sum() / log["images"].sum()
    return [{"field": "minutes_per_screenshot (agent)", "rows": int(log["images"].sum()),
             "correct": None, "accuracy_pct": round(agent, 2), "unit": "min"},
            {"field": "minutes_per_screenshot (manual baseline)", "rows": int(log["images"].sum()),
             "correct": None, "accuracy_pct": round(manual, 2), "unit": "min"}]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extracted", default="data/output/extracted.csv")
    ap.add_argument("--truth", default="data/ground_truth.csv")
    ap.add_argument("--sku-truth", default="data/ground_truth_sku.csv")
    ap.add_argument("--sku-map", default="data/output/sku_map.csv")
    ap.add_argument("--run-log", default="data/output/run_log.csv")
    ap.add_argument("--out", default=None, help="default: metrics/evaluation.csv, or evaluation_<campaign>.csv")
    ap.add_argument("--campaign", default=None,
                    help="score one campaign only (e.g. a blind test run) and list every mismatch")
    args = ap.parse_args()

    pred = pd.read_csv(args.extracted)
    truth = pd.read_csv(args.truth)
    if args.campaign:
        truth = truth[truth["campaign_name"] == args.campaign]
        if truth.empty:
            raise SystemExit(f"no ground-truth rows for campaign {args.campaign!r} in {args.truth}")
    metrics_dir = Path(args.extracted).parent / "metrics"  # results stay next to the data they score
    args.out = args.out or str(metrics_dir / (f"evaluation_{args.campaign}.csv" if args.campaign
                                              else "evaluation.csv"))
    m = truth.merge(pred, on="screenshot_file", suffixes=("_true", "_pred"), how="left")
    missing = m[[c for c in m.columns if c.endswith("_pred")][0]].isna().sum() if len(m) else 0

    rows, errors = [], []
    for f in PRICE_FIELDS + CATEGORY_FIELDS:
        if f"{f}_true" not in m or f"{f}_pred" not in m:
            continue
        ok = (_num_match if f in PRICE_FIELDS else _cat_match)(m[f"{f}_true"], m[f"{f}_pred"])
        for _, r in m[~ok].iterrows():
            errors.append({"screenshot_file": r.screenshot_file, "field": f,
                           "truth": r[f"{f}_true"], "extracted": r[f"{f}_pred"]})
        rows.append({"field": f, "rows": len(m), "correct": int(ok.sum()),
                     "accuracy_pct": round(ok.mean() * 100, 1)})

    # Brand-vs-platform discount separation: the brand-funded net price must match.
    if {"display_price_true", "shop_voucher_thb_true"} <= set(m.columns):
        net_true = pd.to_numeric(m.display_price_true, errors="coerce") - pd.to_numeric(m.shop_voucher_thb_true, errors="coerce").fillna(0)
        net_pred = pd.to_numeric(m.display_price_pred, errors="coerce") - pd.to_numeric(m.shop_voucher_thb_pred, errors="coerce").fillna(0)
        ok = _num_match(net_true, net_pred)
        rows.append({"field": "brand_net_price (discount separation)", "rows": len(m),
                     "correct": int(ok.sum()), "accuracy_pct": round(ok.mean() * 100, 1)})

    if not args.campaign:  # SKU truth and run log cover all campaigns
        rows += sku_match_rows(Path(args.sku_truth), Path(args.sku_map))
        rows += time_rows(Path(args.run_log))

    report = pd.DataFrame(rows)
    report["unit"] = report.get("unit", pd.Series(index=report.index, dtype=object)).fillna("%")
    report = report.rename(columns={"accuracy_pct": "value"})
    report["correct"] = report["correct"].astype("Int64")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.out, index=False)
    print(report.to_string(index=False))
    print(f"\nGround-truth rows: {len(truth)}  |  not found in extracted.csv: {missing}")
    print(f"Saved to {args.out}")
    if args.campaign:
        err_path = Path(args.out).with_name(f"evaluation_errors_{args.campaign}.csv")
        pd.DataFrame(errors, columns=["screenshot_file", "field", "truth", "extracted"]).to_csv(err_path, index=False)
        print(f"{len(errors)} field mismatches -> {err_path}")


if __name__ == "__main__":
    main()
