# Online Promonitor

**Online Promonitor: A Document Intelligence Agent for Cross-Platform Searching for Sales Promotion on Shopee, Lazada, and TikTok Shop**
**รู้โปรรู้เขา: ส่องโปรโมชันคู่แข่งข้าม Shopee, Lazada และ TikTok Shop เพื่อวางกลยุทธ์แคมเปญอัพเซลล์**

## Project context

- **Domain:** Thai beauty & skincare e-commerce
- **User:** Brand / E-commerce Manager of a mid-size Thai skincare brand
- **Problem:** Before every monthly campaign (double date, Payday, Brand Day, Flash Sale, seasonal, launch), the team spends 2–3 days manually checking 5 competitors on 3 platforms. Campaigns launch late, competitors get there first, and ROI misses target.
- **What this repo does:** Claude Code acts as the document intelligence agent. It reads screenshots of competitor product pages, extracts structured promotion data, matches SKUs across platforms, computes metrics, and writes a Thai-language insight brief for planning upsell campaigns. A Streamlit dashboard displays the results.

## Agent flow (8 steps)

```
1 Screenshots → 2 Extraction Agent → 3 Validation → 4 Human Review
                 (Vision LLM → JSON)   (Pydantic)     (low confidence)
5 SKU Matching → 6 Analysis → 7 Insight Agent → 8 Dashboard
  (price/ml·g)    (metrics +     (Thai brief)     (Streamlit)
                   GP simulator)
```

| step | who | writes |
| --- | --- | --- |
| 1 Screenshots | human | `data/screenshots/<campaign>/` |
| 2 Extraction | `extractor` agent | `data/output/raw/<campaign>/*.json` |
| 3 Validation | `src/validate.py` (Pydantic) | `extracted.csv`, `review_queue.csv` |
| 4 Human Review | human, via run-promonitor skill | fixes in `extracted.csv` |
| 5 SKU Matching | `sku-matcher` agent | `sku_map.csv` |
| 6 Analysis | `src/analyze.py` | `metrics/*.csv` (GP simulator lives in the dashboard) |
| 7 Insight | `analyst` agent (Insight Agent) | `insights/<campaign>.md` |
| 8 Dashboard | `app.py` | nothing (reads `data/output` only) |

## Folder layout

```
data/screenshots/<campaign_name>/   input screenshots, one folder per campaign snapshot
data/ground_truth.csv               hand-labelled rows for evaluation
data/ground_truth_sku.csv           hand-labelled sku_id per listing (SKU-match evaluation)
data/output/raw/<campaign>/*.json   extractor output, one JSON per screenshot
data/output/extracted.csv           one row per screenshot (written only by src/validate.py)
data/output/review_queue.csv        rows needing human check (confidence < 0.7 or flags)
data/output/sku_map.csv             raw product name → canonical sku_id (written by sku-matcher)
data/output/metrics/                metric tables (written by analyst)
data/output/insights/<campaign>.md  Thai insight brief (written by analyst)
src/validate.py                     Pydantic schema + business rules, JSON → extracted.csv
src/analyze.py                      metric calculations (pandas)
src/evaluate.py                     accuracy vs ground truth
app.py                              Streamlit dashboard (reads data/output only)
.claude/agents/                     extractor, sku-matcher, analyst
.claude/skills/run-promonitor/      one command to run the whole pipeline
```

## Screenshot naming

Folder name = campaign name, e.g. `normal_2026-11-15`, `11.11_2026`, `payday_2026-11`.
File name = `<brand>_<sku-hint>_<platform>_<YYYYMMDD>.png`, platform ∈ `shopee | lazada | tiktok`.
Example: `brandA_sunscreen50ml_shopee_20261111.png`

## Campaign types

`normal | double_date | payday | brand_day | flash_sale | seasonal | launch`

## Data schema (extracted.csv)

| column | meaning |
| --- | --- |
| screenshot_file | file name (primary key, never duplicate) |
| snapshot_date | from file name, YYYY-MM-DD |
| campaign_type, campaign_name | from folder name |
| brand, platform | from file name, confirm against the image |
| product_name_raw | product title exactly as shown |
| size_ml_g | numeric size in ml or g; null if not shown |
| pack_qty | units in the listing (1 unless a set/multipack) |
| list_price | crossed-out / original price in THB |
| display_price | price shown for 1 listing before vouchers |
| shop_voucher_thb | discount funded by the shop/brand that applies to 1 listing |
| platform_voucher_note | platform-funded vouchers/coins, text only (NOT counted) |
| upsell_mechanic | `bundle | spend_x_save_y | multi_buy | gift_threshold | none` |
| upsell_detail | e.g. "ครบ 999 ลด 150", "ซื้อ 2 ชิ้นลด 10%" |
| min_spend_or_qty | threshold number for the upsell offer |
| gift_with_purchase | gift text, or null |
| effective_price | display_price − shop_voucher_thb (brand-funded net price for 1 listing) |
| price_per_unit | effective_price / (size_ml_g × pack_qty) |
| discount_depth_pct | (1 − effective_price / list_price) × 100 |
| confidence | 0–1, extractor's own confidence |
| flags | semicolon list, e.g. `price_unclear;voucher_owner_unclear` |

## Rules for every agent

1. **Never guess.** If a value is not visible, write null and add a flag. A wrong number is worse than a missing one.
2. **Brand vs platform money.** Only brand/shop-funded discounts count toward effective_price. Platform vouchers, coins, and cashback are recorded as text only.
3. **Do not re-extract** a screenshot already in extracted.csv unless the user asks. New rows reach extracted.csv only through `src/validate.py`.
4. **Numbers in insights must come from data/output files.** Interpretations about platform GP are assumptions; say "อาจ" / "สันนิษฐานว่า".
5. **Language:** data in English column names; insight briefs in Thai.
6. **Secrets:** never write API keys or credentials into any file. This repo is public.
7. Scope is product pages only. Live-stream-only and affiliate-link prices are out of scope.

## How to run

Put screenshots in `data/screenshots/<campaign_name>/`, then ask: "รัน promonitor กับ <campaign_name>" (uses the run-promonitor skill).
Dashboard: `streamlit run app.py`
