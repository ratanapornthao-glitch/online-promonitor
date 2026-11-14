"""Validation step (Pydantic): extractor JSON -> checked rows in extracted.csv.

Flow position: Screenshots -> Extraction Agent (JSON) -> **Validation** -> Human Review.

The extractor agent writes one JSON file per screenshot to
data/output/raw/<campaign_name>/<screenshot stem>.json with only what it read
from the image. This script:

1. derives snapshot_date / campaign / brand / platform from folder + file name
   (deterministic, never from the LLM),
2. validates types and allowed values with Pydantic,
3. applies business rules (display <= list, voucher <= display, ...) as flags,
4. recomputes effective_price, price_per_unit, discount_depth_pct,
5. appends new rows to extracted.csv and routes low-confidence / flagged rows
   to review_queue.csv. Rows already in extracted.csv are skipped (rule 3).

Usage:
  python src/validate.py <campaign_name>          # validate raw JSON for one campaign
  python src/validate.py <campaign_name> --force  # replace rows already in extracted.csv
  python src/validate.py --audit                  # re-check extracted.csv, report only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Literal, Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

DATA_DIR = Path("data/output")
CONFIDENCE_REVIEW = 0.7

COLUMNS = [
    "screenshot_file", "snapshot_date", "campaign_type", "campaign_name", "brand", "platform",
    "product_name_raw", "size_ml_g", "pack_qty", "list_price", "display_price", "shop_voucher_thb",
    "platform_voucher_note", "upsell_mechanic", "upsell_detail", "min_spend_or_qty",
    "gift_with_purchase", "effective_price", "price_per_unit", "discount_depth_pct",
    "confidence", "flags",
]
FILE_RE = re.compile(r"^(?P<brand>[A-Za-z0-9]+)_(?P<sku>[A-Za-z0-9-]+)_(?P<platform>shopee|lazada|tiktok)"
                     r"_(?P<date>\d{8})\.(png|jpe?g|webp)$", re.IGNORECASE)
CAMPAIGN_PREFIX = [  # folder-name prefix -> campaign_type
    (re.compile(r"^normal_"), "normal"),
    (re.compile(r"^\d{1,2}\.\d{1,2}_"), "double_date"),
    (re.compile(r"^payday_"), "payday"),
    (re.compile(r"^brand_?day_"), "brand_day"),
    (re.compile(r"^flash(_sale)?_"), "flash_sale"),
    (re.compile(r"^seasonal_"), "seasonal"),
    (re.compile(r"^launch_"), "launch"),
]

Platform = Literal["shopee", "lazada", "tiktok"]
CampaignType = Literal["normal", "double_date", "payday", "brand_day", "flash_sale", "seasonal", "launch"]
Mechanic = Literal["bundle", "spend_x_save_y", "multi_buy", "gift_threshold", "none"]
Money = Optional[float]


class Extraction(BaseModel):
    """What the extractor agent read from one screenshot (raw JSON)."""
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    screenshot_file: str
    brand_seen: Optional[str] = None        # brand as printed on the page
    platform_seen: Optional[Platform] = None
    product_name_raw: Optional[str] = None
    size_ml_g: Optional[float] = Field(None, gt=0)
    pack_qty: int = Field(1, ge=1)
    list_price: Money = Field(None, gt=0)
    display_price: Money = Field(None, gt=0)
    shop_voucher_thb: float = Field(0, ge=0)
    platform_voucher_note: Optional[str] = None
    upsell_mechanic: Mechanic = "none"
    upsell_detail: Optional[str] = None
    min_spend_or_qty: Optional[float] = Field(None, gt=0)
    gift_with_purchase: Optional[str] = None
    confidence: float = Field(ge=0, le=1)
    flags: list[str] = []

    @field_validator("flags", mode="before")
    @classmethod
    def split_flags(cls, v):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return []
        if isinstance(v, str):
            return [f.strip() for f in v.split(";") if f.strip()]
        return v

    @field_validator("upsell_mechanic", mode="before")
    @classmethod
    def none_mechanic(cls, v):
        return "none" if v in (None, "", "null") else v


class PromoRow(Extraction):
    """One validated row of extracted.csv."""
    snapshot_date: date
    campaign_type: CampaignType
    campaign_name: str
    brand: str
    platform: Platform
    effective_price: Money = None
    price_per_unit: Money = None
    discount_depth_pct: Money = None


def _norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def campaign_type_of(campaign_name: str) -> str | None:
    for rx, ctype in CAMPAIGN_PREFIX:
        if rx.match(campaign_name.lower()):
            return ctype
    return None


def parse_filename(name: str) -> dict | None:
    m = FILE_RE.match(name)
    if not m:
        return None
    d = m.groupdict()
    try:
        d["date"] = date(int(d["date"][:4]), int(d["date"][4:6]), int(d["date"][6:]))
    except ValueError:
        return None
    d["platform"] = d["platform"].lower()
    return d


def business_flags(r: PromoRow) -> list[str]:
    f = []
    if r.list_price is None:
        f.append("list_price_missing")
    if r.display_price is None:
        f.append("display_price_missing")
    if r.size_ml_g is None:
        f.append("size_not_visible")
    if r.list_price and r.display_price and r.display_price > r.list_price:
        f.append("display_gt_list")
    if r.display_price and r.shop_voucher_thb > r.display_price:
        f.append("voucher_gt_display")
    if r.upsell_mechanic != "none" and r.min_spend_or_qty is None:
        f.append("upsell_threshold_missing")
    if r.upsell_mechanic == "none" and r.upsell_detail:
        f.append("upsell_detail_without_mechanic")
    if r.brand_seen and _norm(r.brand_seen) != _norm(r.brand):
        f.append("filename_mismatch")
    if r.platform_seen and r.platform_seen != r.platform:
        f.append("filename_mismatch")
    if r.discount_depth_pct is not None and r.discount_depth_pct > 80:
        f.append("discount_over_80pct")
    return f


def derive(r: PromoRow) -> PromoRow:
    if r.display_price is not None:
        r.effective_price = round(r.display_price - r.shop_voucher_thb, 2)
    if r.effective_price is not None and r.size_ml_g:
        r.price_per_unit = round(r.effective_price / (r.size_ml_g * r.pack_qty), 2)
    if r.effective_price is not None and r.list_price:
        r.discount_depth_pct = round((1 - r.effective_price / r.list_price) * 100, 1)
    return r


def validate_record(raw: dict, campaign_name: str, brand_names: dict[str, str]) -> tuple[dict | None, list[str]]:
    """Return (csv row, errors). Invalid fields become null + flag, never guessed."""
    fn = parse_filename(raw.get("screenshot_file", ""))
    if fn is None:
        return None, [f"bad file name: {raw.get('screenshot_file')!r}"]
    ctype = campaign_type_of(campaign_name)
    if ctype is None:
        return None, [f"unknown campaign prefix: {campaign_name!r}"]

    # Brand comes from the file name; brand_seen (from the image) is only used to check it.
    seen = raw.get("brand_seen")
    brand = brand_names.get(_norm(fn["brand"])) or (
        seen if _norm(seen) == _norm(fn["brand"]) else fn["brand"].capitalize())
    base = dict(raw, snapshot_date=fn["date"], campaign_type=ctype, campaign_name=campaign_name,
                brand=brand, platform=fn["platform"])
    extra_flags, errors = [], []
    for _ in range(len(base)):  # drop offending fields one by one
        try:
            row = PromoRow.model_validate(base)
            break
        except ValidationError as e:
            fields = {str(err["loc"][0]) for err in e.errors() if err["loc"]}
            fatal = fields & {"screenshot_file", "confidence", "snapshot_date", "campaign_type",
                              "brand", "platform", "campaign_name"}
            if fatal:
                if fatal == {"confidence"}:
                    base["confidence"] = 0.0
                    extra_flags.append("invalid_confidence")
                    continue
                return None, [str(e)]
            for f in fields:
                base.pop(f, None)
                extra_flags.append(f"invalid_{f}")
                errors.append(f"{raw['screenshot_file']}: {f} invalid, set to null")
    else:
        return None, ["could not validate"]

    row = derive(row)
    flags = list(dict.fromkeys(row.flags + extra_flags + business_flags(row)))
    if flags and row.confidence >= CONFIDENCE_REVIEW:
        row.confidence = round(min(row.confidence, 0.69), 2)  # anything flagged goes to review
    out = row.model_dump()
    out["snapshot_date"] = row.snapshot_date.isoformat()
    out["flags"] = ";".join(flags) or None
    return {c: out.get(c) for c in COLUMNS}, errors


def known_brand_names(data_dir: Path) -> dict[str, str]:
    path = data_dir / "extracted.csv"
    if not path.exists():
        return {}
    b = pd.read_csv(path, usecols=["brand"])["brand"].dropna().unique()
    return {_norm(x): x for x in b}


def run_campaign(campaign: str, data_dir: Path, force: bool) -> int:
    raw_dir = data_dir / "raw" / campaign
    files = sorted(raw_dir.glob("*.json"))
    if not files:
        print(f"No JSON in {raw_dir}. Run the extractor agent first.")
        return 1

    ext_path, rq_path = data_dir / "extracted.csv", data_dir / "review_queue.csv"
    existing = pd.read_csv(ext_path) if ext_path.exists() else pd.DataFrame(columns=COLUMNS)
    done = set(existing["screenshot_file"])
    names = known_brand_names(data_dir)

    rows, skipped, problems = [], 0, []
    for fp in files:
        try:
            raw = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{fp.name}: not valid JSON ({e})")
            continue
        if raw.get("screenshot_file") in done and not force:
            skipped += 1
            continue
        row, errs = validate_record(raw, campaign, names)
        problems += errs
        if row:
            rows.append(row)

    new = pd.DataFrame(rows, columns=COLUMNS)
    if force and len(new):
        existing = existing[~existing.screenshot_file.isin(new.screenshot_file)]
    if len(new):
        combined = pd.concat([existing, new], ignore_index=True) if len(existing) else new
        assert combined["screenshot_file"].is_unique, "duplicate screenshot_file"
        combined.to_csv(ext_path, index=False)

    review = new[(new["confidence"] < CONFIDENCE_REVIEW) | new["flags"].notna()]
    if len(review):
        rq = pd.read_csv(rq_path) if rq_path.exists() else pd.DataFrame(columns=COLUMNS)
        rq = rq[~rq.screenshot_file.isin(review.screenshot_file)]
        (pd.concat([rq, review], ignore_index=True) if len(rq) else review).to_csv(rq_path, index=False)

    print(f"validated {len(new)} | skipped (already extracted) {skipped} | "
          f"to review {len(review)} | rejected {len(files) - len(new) - skipped}")
    for p in problems:
        print("  !", p)
    return 0


def audit(data_dir: Path) -> int:
    """Re-run the schema and business rules over extracted.csv without writing."""
    df = pd.read_csv(data_dir / "extracted.csv")
    names = known_brand_names(data_dir)
    issues = 0
    for rec in df.to_dict("records"):
        raw = {k: (None if isinstance(v, float) and pd.isna(v) else v) for k, v in rec.items()}
        raw["brand_seen"] = raw.pop("brand", None)
        row, errs = validate_record(raw, rec["campaign_name"], names)
        if row is None:
            print("  REJECT", rec["screenshot_file"], errs)
            issues += 1
            continue
        old = set(str(rec.get("flags") or "").split(";")) - {"", "nan"}
        new = set((row["flags"] or "").split(";")) - {""}
        if new - old:
            print(f"  {rec['screenshot_file']}: new flags {sorted(new - old)}")
            issues += 1
    print(f"audited {len(df)} rows, {issues} with issues not yet flagged")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("campaign", nargs="?")
    ap.add_argument("--data-dir", default=str(DATA_DIR))
    ap.add_argument("--force", action="store_true", help="replace rows already in extracted.csv")
    ap.add_argument("--audit", action="store_true", help="re-check extracted.csv, report only")
    a = ap.parse_args()
    if a.audit:
        return audit(Path(a.data_dir))
    if not a.campaign:
        ap.error("campaign name required (or --audit)")
    return run_campaign(a.campaign, Path(a.data_dir), a.force)


if __name__ == "__main__":
    sys.exit(main())
