# NQ Rudra Reversal 1H — 12-Month PDF Chart Review (V3)

## Purpose
Create a **new 12-page landscape PDF**, one monthly NQ 1H candlestick chart per page, from **October 2025 through September 2026**, for manual review of missed trades, wrong entries, improved entries/exits, and sideways-market filters.

**Output (do not overwrite existing PDFs):**
`NQ/reports/rudra_reversal_1y_monthly/NQ_Rudra_Reversal_12_Month_Chart_Review_Outside_Labels.pdf`

## Source of truth — LOCKED strategy
Before generating any revised PDF, read:
1. `NQ/backtesting/RUDRA_REVERSAL_NQ_1H_LOCKED.md`
2. `NQ/backtesting/rudra_reversal_nq_1h.py`
3. `NQ/tools/make_rudra_reversal_monthly_review_charts.py`

Use only the **original canonical 136 closed-trade benchmark** (101 wins, 35 losses), **not** the separate 238-trade/two-entry experiment. Do **not** change signal rules, trading results, entry/exit times, prices, or trade numbering while making charts.

Locked calculation reference: NQ, 1H, LONG only, full overnight and regular session; BB(20, 2), population standard deviation (`ddof=0`); current candle near/touch lower BB and at least 2 of last 3 near/touch lower BB, 0.15% tolerance; 150-bar highest high/lowest low including signal bar; signal-close depth at least 20%; no MA20-touch or RSI filters; buy signal candle CLOSE; one position at a time; exit on first subsequent near/touch upper BB, filled at upper BB on an exact touch or candle HIGH on a near-touch. Times shown in **Europe/London**, observing daylight saving. Preserve any final open trade separately, never add it to closed-trade benchmark.

## Data to read directly from GitHub
- 1H OHLC: `NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`
- Original chart-ID ledger: `NQ/reports/rudra_reversal_1y_monthly/trade_ledger_chart_ids.csv`
- Manifest: `NQ/reports/rudra_reversal_1y_monthly/monthly_manifest.csv`
- Canonical backtest ledger (cross-reference): `NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv`

Draw markers **from the saved ledger**, not from a fresh backtest; fresh calculations must never silently alter original coordinates. Note the complete benchmark also includes two October 2026 trades, which are **outside** the requested 12 pages. Each entry/exit is shown on the page of **its own timestamp**, including cross-month trades. Thus individual page BUY and SELL counts may differ.

## Required page format
- Exactly **12 landscape pages**, one each from Oct 2025 to Sep 2026.
- Genuine 1H candles: bullish **green**, bearish **red**; true candle OHLC.
- Bollinger upper **blue**, middle/MA20 **grey**, lower **purple**.
- Month and year, legible UK dates and prices, entry count, number of wins/losses, legend, and blank area for review notes.
- Normal readable size/resolution; keep PDF compact.

### BUY entries
- **Yellow upward triangle** with **black outline** placed at exact entry candle and saved entry fill price.
- Label **B1, B2, ...** preserving the canonical trade number (never restart numbering by month).
- Put **all BUY text labels in a dedicated top strip OUTSIDE the price chart**, and draw a **thin black leader line** from each label to its triangle.

### SELL exits
- **Large purple X** at the exact saved exit price for **winning** trades.
- **Large red X** at the exact saved exit price for **losing** trades.
- Label **S1, S2, ...** using the same canonical trade number.
- Put **all SELL text labels in a dedicated bottom strip OUTSIDE the price chart**, connected to their X by a **thin matching purple/red leader line**.

### Absolutely no label overlap
- No label text on candles or Bollinger Bands.
- Labels must not cover one another: assign close-together events to **staggered rows / lanes**.
- Check particularly dense trade IDs **B122–B127**.
- Increase the dedicated top/bottom label strip height or width before shrinking the font excessively.
- **Never move the actual marker** from its correct candle and fill price to fix a label.
- Leader lines may cross the chart, but label text must stay outside.

## Reproduce V3
The existing GitHub Actions workflow `.github/workflows/rudra_monthly_charts.yml` runs on updates to the generator and supports manual dispatch. Its script is:
`python3 NQ/tools/make_rudra_reversal_monthly_review_charts.py`
Dependencies: `pandas numpy matplotlib`. The script should **only** create the named V3 PDF: do not regenerate/overwrite earlier images, PDFs, trade ledgers or manifest. Do not modify the locked trading implementation. GitHub Actions automatically commits newly generated output under `NQ/reports/rudra_reversal_1y_monthly/`.

## Checks before delivery
1. Confirm canonical ledger is **136 trades, 101 wins, 35 losses**; trade numbers unique 1..136.
2. Verify entry/exit times equal the referenced OHLC candle's **UK timestamp** and saved entry/exit prices remain unchanged.
3. For each month, validate entry count and winning/losing entry count against the manifest.
4. Verify generated PDF has **exactly 12 pages** and includes all events in the period, including cross-month exits. The V3 run showed **134 BUY events and 134 SELL events** inside the 12-month display window (two 2026-10 entries are excluded; some exits cross months).
5. Open/render representative pages, especially a dense month and B122–B127, and check no labels overlap each other or the candle chart.
6. Confirm new PDF is present in GitHub and its commit/push succeeded. **Do not delete or replace prior PDFs.**
7. Give the user both the GitHub file page and direct raw download URL.

## Last verified generation (2026-10-08)
- Generator commit: `93fa1610d36792e4a2c43ff565c7afbf12014f8a`
- PDF generation/upload commit: `3ba625b`
- GitHub: https://github.com/raghunathbhandari/AlgoStrategy/blob/main/NQ/reports/rudra_reversal_1y_monthly/NQ_Rudra_Reversal_12_Month_Chart_Review_Outside_Labels.pdf
- Direct PDF: https://raw.githubusercontent.com/raghunathbhandari/AlgoStrategy/main/NQ/reports/rudra_reversal_1y_monthly/NQ_Rudra_Reversal_12_Month_Chart_Review_Outside_Labels.pdf

**Future changes:** modify PDF presentation only unless the user explicitly authorizes a new strategy version. Keep a fresh filename for revised PDF versions if the user requests one.
