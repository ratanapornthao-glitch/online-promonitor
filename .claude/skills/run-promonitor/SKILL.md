---
name: run-promonitor
description: Run the full Online Promonitor pipeline (screenshots → extract → validate → human review → SKU match → analyze → insight → dashboard) on one campaign folder of competitor screenshots. Use when the user says "รัน promonitor", "run promonitor", or asks to analyze a new batch of promo screenshots.
---

# Run Online Promonitor

Every screenshot passes through the agent and a human check before it reaches the dashboard:

```
1 Screenshots → 2 Extraction Agent → 3 Validation → 4 Human Review
                 (Vision LLM → JSON)   (Pydantic)     (low confidence)
5 SKU Matching → 6 Analysis → 7 Insight Agent → 8 Dashboard
  (price/ml·g)    (metrics +     (Thai brief)     (Streamlit)
                   GP simulator)
```

Input: a campaign folder name under `data/screenshots/` (e.g. `payday_2026-11`). If the user did not name one, list the folders and ask which. Note the start time.

1. **Screenshots — check input.** Confirm the folder exists and file names follow CLAUDE.md naming (`<brand>_<sku-hint>_<platform>_<YYYYMMDD>.png`) and the folder prefix maps to a campaign type. Report badly named files and skip them.
2. **Extract.** Delegate to the `extractor` subagent with the folder path. It writes one JSON per screenshot to `data/output/raw/<campaign>/`.
3. **Validate.** The extractor finishes by running `python src/validate.py <campaign>`. Confirm its summary line; if it was not run, run it yourself. Nothing reaches `extracted.csv` without this step.
4. **Human review.** If `data/output/review_queue.csv` has rows for this campaign, show them as a short table (file, field, value, flag) and ask for corrections. Apply corrections to `extracted.csv`, recompute the derived columns with the CLAUDE.md formulas, clear the fixed flags, and remove fixed rows from the queue. If the user says to continue without review, keep the flags.
5. **Match SKUs.** Delegate to the `sku-matcher` subagent. Show uncertain matches and ask the user to confirm or reject.
6. **Analyze.** Run `python src/analyze.py` (metrics incl. Promo Calendar data); the GP margin simulator lives in the dashboard.
7. **Insight.** Delegate to the `analyst` subagent (Insight Agent) with the campaign name. It writes `data/output/insights/<campaign>.md` in Thai.
8. **Dashboard + report.** Reply with: images processed, rows validated / rejected / reviewed, the 3-line summary, the brief path, and `streamlit run app.py`.

Log the run as one line in `data/output/run_log.csv` (`run_date, campaign_name, images, minutes_to_insight, manual_baseline_minutes`; baseline 1200 unless the user gives another) so Time to Insight can be measured. If ground truth exists for this campaign, also run `python src/evaluate.py`.
