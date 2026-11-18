# Online Promonitor

**Online Promonitor: A Document Intelligence Agent for Cross-Platform Searching for Sales Promotion on Shopee, Lazada, and TikTok Shop**
**รู้โปรรู้เขา: ส่องโปรโมชันคู่แข่งข้าม Shopee, Lazada และ TikTok Shop เพื่อวางกลยุทธ์แคมเปญอัพเซลล์**

-  Video presentation: _YouTube link_
-  Live demo: _https://online-promonitor.streamlit.app_

## Problem

Before every monthly campaign (double date, Payday, Brand Day, Flash Sale, seasonal), a skincare brand's marketing team spends 2–3 days opening 5 competitors' shops on Shopee, Lazada and TikTok Shop and copying prices into Excel. By the time the strategy is agreed, competitors have already launched, the campaign misses the shopper's buying window, and ROI falls short.

**Why all three platforms matter.** Thailand's platform e-commerce reached about US$35.5B in 2025, up 51.8%, the fastest growth in Southeast Asia ([Momentum Works](https://thelowdown.momentum.asia/new-report-southeast-asias-platform-ecommerce-reaches-us157-6b-in-2025-with-top-platforms-expanding-share-to-98-8/)). The split between platforms moves quickly:

| Thailand GMV share | Shopee | TikTok Shop | Lazada |
| --- | --- | --- | --- |
| Q2 2025 | 56% | 30% | 14% |
| Q2 2026 | 45% | 48% | 7% |

TikTok Shop passed Shopee for the first time in Q2 2026 ([Cube Asia, Tradewinds](https://cube.asia/ecommerce-in-thailand/)). A brand that watches competitors on only one platform misses where they are moving their promotion budget. Sources and caveats: [docs/literature_review.md](docs/literature_review.md).

## Solution

Claude Code works as the document intelligence agent. Every screenshot passes through the agent and a human check before it reaches the dashboard:

```
1 Screenshots → 2 Extraction Agent → 3 Validation → 4 Human Review
                 (Vision LLM → JSON)   (Pydantic)     (low confidence)
5 SKU Matching → 6 Analysis → 7 Insight Agent → 8 Dashboard
  (price/ml·g)    (metrics +     (Thai brief)     (Streamlit)
                   GP simulator)
```

Three subagents plus a Pydantic validator do the work:

| Agent | Job |
| --- | --- |
| `extractor` | Reads each screenshot → one JSON (prices, brand vs platform discounts, upsell offers, gifts) |
| `src/validate.py` | Pydantic schema + business rules (display ≤ list, voucher ≤ display, file-name match); recomputes derived fields; routes flagged rows to human review |
| `sku-matcher` | Matches the same product across platforms; price per ml/g |
| `analyst` (Insight Agent) | Computes metrics and writes the Thai insight brief with upsell recommendations |

A human checks low-confidence rows before analysis. The Streamlit dashboard shows Campaign Pattern by campaign type, Competitor Promo Calendar, Channel Strategy, upsell mechanics, fake-discount alerts, and a GP margin simulator.

## Report documents

| Rubric | Document |
| --- | --- |
| Literature Review (existing solutions, pros/cons, why this approach) | [docs/literature_review.md](docs/literature_review.md) |
| Methodology & Results (blind test: accuracy, time to insight, insights found) | [docs/results.md](docs/results.md) |
| Real-data pilot (how to collect and label real screenshots) | [docs/real_data_pilot.md](docs/real_data_pilot.md) |

## How to run

1. Install [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and open this folder in it.
2. Put screenshots in `data/screenshots/<campaign_name>/` named `<brand>_<sku-hint>_<platform>_<YYYYMMDD>.png` (see `CLAUDE.md`).
3. In Claude Code: `รัน promonitor กับ <campaign_name>`
4. Dashboard: `pip install -r requirements.txt` then `streamlit run app.py`
5. Accuracy: `python src/evaluate.py` — field accuracy, brand/platform discount separation, SKU-match accuracy (`data/ground_truth_sku.csv`) and minutes per screenshot vs manual
6. Re-check existing data: `python src/validate.py --audit`

## Repository

```
CLAUDE.md                     project context, schema and rules for every agent
.claude/agents/               extractor, sku-matcher, analyst
.claude/skills/run-promonitor pipeline in one command
data/screenshots/             input
data/output/                  agent output (extracted.csv, metrics/, insights/)
src/validate.py               Pydantic validation (JSON → extracted.csv)
src/analyze.py                metrics
src/evaluate.py               accuracy vs ground truth
app.py                        dashboard (reads data/output only; no API key needed)
```

## Synthetic demo data

This repo ships with **synthetic data** for a classroom mockup. All brands (Lumira, Hadaso, Vela Skin, Nurish Lab, Kiriya), products, prices and promotions are fictional, and every screenshot is watermarked "SYNTHETIC DATA · MOCKUP". Regenerate it with `python src/generate_synthetic.py`.

- 360 mock product-page screenshots: 5 brands × 4 products × 3 platforms × 6 campaign snapshots (Oct–Nov 2026: 2 normal days, 10.10, Payday, 11.11, Flash Sale)
- **Live-demo campaign:** `data/screenshots/payday_2026-11/` (60 screenshots, 25 Nov) is left unprocessed on purpose. In the video, type `รัน promonitor กับ payday_2026-11` to show all 8 steps running. Recreate it with `python src/generate_synthetic.py --demo-only`
- `data/synthetic_truth.csv` holds the true values; `data/output/extracted.csv` simulates the extractor with a few realistic mistakes, so `src/evaluate.py` shows a believable accuracy
- Built-in stories the analysis should find: Lumira pushes Shopee, Hadaso is TikTok-first and Flash-Sale-heavy, Nurish Lab saves its deepest cuts for Payday, Kiriya barely discounts, and Vela Skin raises list prices on Lazada before campaigns (fake discount)

When you switch to real data, delete `data/synthetic_truth.csv` (the dashboard banner disappears), `data/screenshots/*` and `data/output/*`.

## Limitations

- Product-page prices only; live-stream and affiliate prices are out of scope.
- Competitors' real GP is unknown; GP-based explanations are hypotheses.
- Screenshots are collected manually in small volume for academic use; no automated scraping.

