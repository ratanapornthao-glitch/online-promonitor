"""Generate SYNTHETIC demo data for Online Promonitor.

Everything here is invented for a classroom mockup: brand names, products,
prices and promotions are fictional, and every screenshot carries a
"SYNTHETIC DATA" watermark. Do not present it as real market data.

Creates:
  data/screenshots/<campaign>/*.png      mock product-page screenshots
  data/synthetic_truth.csv               the values used to draw each screenshot
  data/ground_truth.csv                  25% sample of the truth (for evaluate.py)
  data/output/extracted.csv              simulated extractor output (with a few realistic errors)
  data/output/review_queue.csv           low-confidence / flagged rows
  data/output/sku_map.csv                cross-platform SKU matching
  data/output/run_log.csv                pipeline run times (Time to Insight)

Usage: python src/generate_synthetic.py [--no-images]
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "output"
SEED = 2026
FONT_CANDIDATES = [  # (regular, bold) — Loma on Linux, Noto Sans Thai on macOS
    (Path("/usr/share/fonts/opentype/tlwg/Loma.otf"), Path("/usr/share/fonts/opentype/tlwg/Loma-Bold.otf")),
    (Path.home() / "Library/Fonts/NotoSansThai-Regular.ttf", Path.home() / "Library/Fonts/NotoSansThai-Bold.ttf"),
    (Path("/Library/Fonts/NotoSansThai-Regular.ttf"), Path("/Library/Fonts/NotoSansThai-Bold.ttf")),
]

PLATFORMS = ["shopee", "lazada", "tiktok"]
PLATFORM_LABEL = {"shopee": "Shopee Mall", "lazada": "LazMall", "tiktok": "TikTok Shop Mall"}
PLATFORM_COLOR = {"shopee": (238, 110, 70), "lazada": (60, 80, 200), "tiktok": (30, 30, 30)}

# campaign folder, type, date
CAMPAIGNS = [
    ("normal_2026-10-05", "normal", "2026-10-05"),
    ("10.10_2026", "double_date", "2026-10-10"),
    ("payday_2026-10", "payday", "2026-10-28"),
    ("normal_2026-11-04", "normal", "2026-11-04"),
    ("11.11_2026", "double_date", "2026-11-11"),
    ("flash_2026-11-13", "flash_sale", "2026-11-13"),
]
# Screenshots only (no extracted rows) so the pipeline can be run live in the demo video.
DEMO_CAMPAIGNS = [
    ("payday_2026-11", "payday", "2026-11-25"),
]

# Fictional brands. Each has a story the analysis should be able to find.
BRANDS = {
    "lumira": dict(display="Lumira", base_disc=0.10, tier=1.0,
                   boost={"shopee": 1.6, "lazada": 0.9, "tiktok": 1.0},          # pushes Shopee hard
                   camp={"double_date": 0.25, "payday": 0.08, "flash_sale": 0.12},
                   upsell=("bundle", "เซ็ตคู่สุดคุ้ม 2 ชิ้น ลดเพิ่ม 15%", 2)),
    "hadaso": dict(display="Hadaso", base_disc=0.12, tier=0.8,
                   boost={"shopee": 0.9, "lazada": 0.8, "tiktok": 1.7},          # TikTok-first
                   camp={"double_date": 0.15, "payday": 0.06, "flash_sale": 0.28},
                   upsell=("spend_x_save_y", "ครบ 599 ลด 60", 599)),
    "velaskin": dict(display="Vela Skin", base_disc=0.08, tier=1.1,
                     boost={"shopee": 1.0, "lazada": 1.2, "tiktok": 1.0},
                     camp={"double_date": 0.20, "payday": 0.05, "flash_sale": 0.08},
                     upsell=("spend_x_save_y", "ครบ 999 ลด 150", 999),
                     fake_raise={"lazada": 0.18}),                               # raises list price on Lazada in campaigns
    "nurishlab": dict(display="Nurish Lab", base_disc=0.10, tier=0.9,
                      boost={"shopee": 1.0, "lazada": 1.1, "tiktok": 1.0},
                      camp={"double_date": 0.07, "payday": 0.18, "flash_sale": 0.05},  # payday-focused
                      upsell=("multi_buy", "ซื้อ 2 ชิ้น ลดเพิ่ม 10%", 2)),
    "kiriya": dict(display="Kiriya", base_disc=0.05, tier=1.6,
                   boost={"shopee": 1.0, "lazada": 1.0, "tiktok": 1.0},          # premium, barely discounts
                   camp={"double_date": 0.05, "payday": 0.02, "flash_sale": 0.0},
                   upsell=("gift_threshold", "ครบ 1,500 รับมินิไซซ์ฟรี", 1500)),
}

# product key, Thai type, English type, size, unit, base price
PRODUCTS = [
    ("sunscreen", "กันแดด", "UV Shield SPF50+ PA++++", 50, "ml", 590),
    ("serum", "เซรั่ม", "Bright Serum Niacinamide 10%", 30, "ml", 890),
    ("cleanser", "โฟมล้างหน้า", "Gentle Amino Cleanser", 150, "ml", 390),
    ("moisturizer", "มอยส์เจอไรเซอร์", "Barrier Repair Cream", 50, "g", 750),
]

PLATFORM_VOUCHERS = {
    "shopee": "โค้ดแพลตฟอร์มลด 10% สูงสุด ฿300 + Coins คืน 5%",
    "lazada": "LazBonus ทุก ฿300 ลด ฿30",
    "tiktok": "โค้ดลดค่าส่ง ฿40 จากแพลตฟอร์ม",
}


def title(platform: str, brand: str, p: tuple, campaign: str) -> str:
    _, th, en, size, unit, _ = p
    if platform == "shopee":
        tag = "[11.11 ลดแรง] " if campaign.startswith("11.11") else "[ของแท้ 100%] "
        return f"{tag}{brand} {en} {size}{unit} {th}"
    if platform == "lazada":
        return f"{brand} {en} {size} {unit} ({th})"
    unit_th = "มล." if unit == "ml" else "กรัม"
    return f"[HOT] {brand} {th} {en.split()[0]} {size}{unit_th} ส่งไว"


def build_truth(rng: random.Random, campaigns: list = CAMPAIGNS) -> pd.DataFrame:
    rows = []
    for camp, ctype, date in campaigns:
        for bkey, b in BRANDS.items():
            for p in PRODUCTS:
                for plat in PLATFORMS:
                    base = round(p[5] * b["tier"] / 10) * 10 - 1
                    list_price = base
                    raise_pct = b.get("fake_raise", {}).get(plat, 0) if ctype != "normal" else 0
                    if raise_pct:
                        list_price = round(base * (1 + raise_pct) / 10) * 10 - 1
                    disc = b["base_disc"] + b["camp"].get(ctype, 0)
                    disc = disc * b["boost"][plat] if ctype != "normal" else b["base_disc"] * (1 + (b["boost"][plat] - 1) * 0.3)
                    disc = min(max(disc + rng.uniform(-0.03, 0.03), 0), 0.6)
                    # Discount is applied to the *normal* list price, so a raised list price inflates the shown %
                    display = round(base * (1 - disc))
                    shop_v = 0
                    if ctype != "normal" and rng.random() < 0.45:
                        shop_v = rng.choice([20, 30, 50, 80]) if b["tier"] < 1.5 else 0
                    up_mech, up_detail, up_thr = "none", None, None
                    in_campaign = ctype != "normal"
                    if (in_campaign and rng.random() < 0.75) or (not in_campaign and rng.random() < 0.25):
                        up_mech, up_detail, up_thr = b["upsell"]
                    gift = None
                    if up_mech == "gift_threshold":
                        gift = "มินิไซซ์ 15ml"
                    elif in_campaign and rng.random() < 0.15:
                        gift = "สำลีแผ่น 1 ห่อ"
                    eff = display - shop_v
                    rows.append(dict(
                        screenshot_file=f"{bkey}_{p[0]}_{plat}_{date.replace('-', '')}.png",
                        snapshot_date=date, campaign_type=ctype, campaign_name=camp,
                        brand=b["display"], platform=plat,
                        product_name_raw=title(plat, b["display"], p, camp),
                        size_ml_g=p[3], pack_qty=1, list_price=list_price, display_price=display,
                        shop_voucher_thb=shop_v,
                        platform_voucher_note=PLATFORM_VOUCHERS[plat] if in_campaign else None,
                        upsell_mechanic=up_mech, upsell_detail=up_detail, min_spend_or_qty=up_thr,
                        gift_with_purchase=gift, effective_price=eff,
                        price_per_unit=round(eff / p[3], 2),
                        discount_depth_pct=round((1 - eff / list_price) * 100, 1),
                        confidence=1.0, flags=None,
                        _sku_id=f"{bkey}-{p[0]}-{p[3]}{p[4]}",
                    ))
    return pd.DataFrame(rows)


def simulate_extraction(truth: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    """The agent is good but not perfect: ~6% of rows get a realistic problem."""
    ext = truth.drop(columns="_sku_id").copy()
    ext["confidence"] = [round(rng.uniform(0.82, 0.98), 2) for _ in range(len(ext))]
    for i in ext.sample(frac=0.06, random_state=SEED).index:
        kind = rng.choice(["voucher_unclear", "small_text", "misread_price", "size_missing"])
        if kind == "voucher_unclear":
            ext.loc[i, "flags"] = "voucher_owner_unclear"
            ext.loc[i, "confidence"] = 0.62
        elif kind == "small_text":
            ext.loc[i, "flags"] = "price_unclear"
            ext.loc[i, "confidence"] = 0.55
        elif kind == "misread_price":   # e.g. 1 read as 7 — not flagged: shows why evaluation matters
            ext.loc[i, "display_price"] = ext.loc[i, "display_price"] + 60
            ext.loc[i, "confidence"] = 0.74
        else:
            ext.loc[i, "size_ml_g"] = None
            ext.loc[i, "flags"] = "size_not_visible"
            ext.loc[i, "confidence"] = 0.66
    over = ext["display_price"] > ext["list_price"]  # caught by src/validate.py business rules
    ext.loc[over, "flags"] = ext.loc[over, "flags"].fillna("").str.cat(["display_gt_list"] * over.sum(), sep=";").str.strip(";")
    ext.loc[over, "confidence"] = ext.loc[over, "confidence"].clip(upper=0.69)
    ext["effective_price"] = ext["display_price"] - ext["shop_voucher_thb"]
    ext["price_per_unit"] = (ext["effective_price"] / ext["size_ml_g"]).round(2)
    ext["discount_depth_pct"] = ((1 - ext["effective_price"] / ext["list_price"]) * 100).round(1)
    return ext


# ---------- mock screenshot ----------

def draw_screenshot(row: pd.Series, path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    reg, bld = next((r, b) for r, b in FONT_CANDIDATES if r.exists() and b.exists())
    f = lambda size, bold=False: ImageFont.truetype(str(bld if bold else reg), size)
    W, H = 540, 900
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    color = PLATFORM_COLOR[row.platform]

    # header (generic, no real logos)
    d.rectangle([0, 0, W, 64], fill=color)
    d.text((20, 18), f"{PLATFORM_LABEL[row.platform]}  ·  {row.brand} Official Store", font=f(22, True), fill="white")
    d.text((W - 150, 70), f"mockup · {row.snapshot_date}", font=f(14), fill=(150, 150, 150))

    # product image placeholder
    d.rounded_rectangle([20, 96, W - 20, 376], radius=16, fill=(244, 240, 236))
    d.text((W / 2, 210), row.brand, font=f(40, True), fill=(120, 110, 100), anchor="mm")
    d.text((W / 2, 260), f"{row.size_ml_g:g}{'ml' if 'Cream' not in row.product_name_raw and 'มอยส์' not in row.product_name_raw else 'g'}",
           font=f(26), fill=(150, 140, 130), anchor="mm")

    y = 396
    # title (wrap)
    words, line, lines = row.product_name_raw.split(" "), "", []
    for w in words:
        test = f"{line} {w}".strip()
        if d.textlength(test, font=f(22, True)) > W - 40:
            lines.append(line); line = w
        else:
            line = test
    lines.append(line)
    for ln in lines[:3]:
        d.text((20, y), ln, font=f(22, True), fill=(30, 30, 30)); y += 32

    # price block
    y += 10
    d.rectangle([0, y, W, y + 92], fill=(255, 246, 240) if row.platform == "shopee" else (245, 246, 252))
    d.text((20, y + 14), f"฿{row.display_price:,.0f}", font=f(44, True), fill=color)
    px = 20 + d.textlength(f"฿{row.display_price:,.0f}", font=f(44, True)) + 16
    if row.list_price > row.display_price:
        lp = f"฿{row.list_price:,.0f}"
        d.text((px, y + 34), lp, font=f(22), fill=(150, 150, 150))
        tw = d.textlength(lp, font=f(22))
        d.line([px, y + 47, px + tw, y + 47], fill=(150, 150, 150), width=2)
        pct = round((1 - row.display_price / row.list_price) * 100)
        d.rounded_rectangle([px + tw + 14, y + 30, px + tw + 84, y + 62], radius=6, fill=color)
        d.text((px + tw + 49, y + 46), f"-{pct}%", font=f(20, True), fill="white", anchor="mm")
    y += 108

    def chip(label: str, text: str, fill: tuple) -> None:
        nonlocal y
        d.rounded_rectangle([20, y, 20 + d.textlength(label, font=f(16, True)) + 20, y + 28], radius=6, fill=fill)
        d.text((30, y + 4), label, font=f(16, True), fill="white")
        d.text((30 + d.textlength(label, font=f(16, True)) + 20, y + 3), text, font=f(18), fill=(50, 50, 50))
        y += 42

    if row.shop_voucher_thb:
        chip("โค้ดร้าน", f"ลด ฿{row.shop_voucher_thb:,.0f} เมื่อกดรับในหน้าร้าน", (200, 60, 60))
    if isinstance(row.upsell_detail, str):
        chip("โปรร้าน", row.upsell_detail, (220, 130, 30))
    if isinstance(row.gift_with_purchase, str):
        chip("ของแถม", row.gift_with_purchase, (60, 150, 90))
    if isinstance(row.platform_voucher_note, str):
        chip("แพลตฟอร์ม", row.platform_voucher_note, (120, 120, 120))

    # footer
    d.rectangle([0, H - 70, W, H], fill=(250, 250, 250))
    d.rounded_rectangle([W / 2 + 10, H - 58, W - 20, H - 12], radius=8, fill=color)
    d.text((3 * W / 4 + 5, H - 35), "ซื้อเลย", font=f(22, True), fill="white", anchor="mm")
    d.text((20, H - 48), "ขายแล้ว 1.2k ชิ้น", font=f(18), fill=(120, 120, 120))

    # watermark
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.text((W / 2, H / 2), "SYNTHETIC DATA · MOCKUP", font=f(32, True), fill=(200, 0, 0, 45), anchor="mm")
    wm = wm.rotate(30, center=(W / 2, H / 2))
    img = Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)


def make_demo(draw: bool = True) -> None:
    """Live-demo campaigns: screenshots + truth only. Own RNG, so the other data never changes."""
    demo = build_truth(random.Random(SEED + 100), DEMO_CAMPAIGNS).drop(columns="_sku_id")
    path = DATA / "synthetic_truth.csv"
    truth = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=demo.columns)
    truth = truth[~truth.screenshot_file.isin(demo.screenshot_file)]
    pd.concat([truth, demo], ignore_index=True).to_csv(path, index=False)
    if draw:
        for _, r in demo.iterrows():
            draw_screenshot(r, DATA / "screenshots" / r.campaign_name / r.screenshot_file)
    print(f"demo: {len(demo)} screenshots in {', '.join(c for c, _, _ in DEMO_CAMPAIGNS)} (not extracted)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--demo-only", action="store_true",
                    help="only (re)create the live-demo campaign screenshots; leave all other data as is")
    args = ap.parse_args()
    if args.demo_only:
        make_demo(draw=not args.no_images)
        return
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    truth = build_truth(rng)
    truth.drop(columns="_sku_id").to_csv(DATA / "synthetic_truth.csv", index=False)
    truth.drop(columns="_sku_id").sample(frac=0.25, random_state=SEED + 1).sort_index().to_csv(
        DATA / "ground_truth.csv", index=False)

    ext = simulate_extraction(truth, rng)
    ext.to_csv(OUT / "extracted.csv", index=False)
    ext[(ext.confidence < 0.7) | ext["flags"].notna()].to_csv(OUT / "review_queue.csv", index=False)

    sku = truth[["brand", "product_name_raw", "platform", "_sku_id"]].drop_duplicates()
    sku = sku.rename(columns={"_sku_id": "sku_id"}).assign(match_note=None)
    sku.to_csv(OUT / "sku_map.csv", index=False)
    # hand-labelled SKU truth for evaluate.py (all listings of a 25% sample of products)
    keep = sku.sku_id.drop_duplicates().sample(frac=0.25, random_state=SEED + 2)
    sku[sku.sku_id.isin(keep)].drop(columns="match_note").to_csv(DATA / "ground_truth_sku.csv", index=False)

    log = [dict(run_date=date, campaign_name=camp, images=int((truth.campaign_name == camp).sum()),
                minutes_to_insight=rng.randint(14, 26), manual_baseline_minutes=60 * 20)
           for camp, _, date in CAMPAIGNS if not camp.startswith("normal")]
    pd.DataFrame(log).to_csv(OUT / "run_log.csv", index=False)

    if not args.no_images:
        for _, r in truth.iterrows():
            draw_screenshot(r, DATA / "screenshots" / r.campaign_name / r.screenshot_file)

    make_demo(draw=not args.no_images)
    print(f"{len(truth)} listings · {truth.campaign_name.nunique()} campaigns · "
          f"{len(ext[(ext.confidence < 0.7) | ext["flags"].notna()])} rows in review queue")


if __name__ == "__main__":
    main()
