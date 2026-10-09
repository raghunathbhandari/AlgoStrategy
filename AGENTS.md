# AI instructions — AlgoStrategy / Rudra Reversal

## Canonical data location (read before research)
- Rudra Reversal historical data is in this **GitHub repository**, not dependent on the user uploading a file into chat.
- Repo: https://github.com/raghunathbhandari/AlgoStrategy (main)
- Verified NQ 1H September 2026 + historical warm-up: `NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`
- Additional verified files: `NQ/data/recent/NQ_1h_2026-09-07_2026-10-07.csv`, `NQ/data/recent/NQ_5m_2026-09-07_2026-10-07.csv`.
- Other NQ history is stored under `NQ/data/` and related backtesting/data folders. User reports approx. three years of data across Git. **Inspect directories/chunks/manifests to verify exact coverage before asserting years available or missing.**
- For a request concerning historic NQ or Rudra Reversal data, **search/fetch the repository FIRST**. Use the connected GitHub tool to read file contents, even if Python/container network access is unavailable. Do NOT request CSV upload before checking verified Git paths. Do not pretend a failed container URL request implies that GitHub data is unavailable.
- If a large file cannot be fetched as one response, read bounded line ranges/chunks using the GitHub connector; inspect file headings/row coverage and retrieve all needed rows including indicator warm-up, or use the repository's AI-chunk files. Never fabricate unaccessed candles.

## Strategy separation
- Rudra-Reversal V1 locked, original code/ledger unchanged.
- V2 experimental, market regime detection RANGE reversal vs TREND follower; only one portfolio position at a time. No live changes until explicit approval.
- Start with `NQ/rudra-reversal/MEMORY_POINTS.md`, `HANDOFF.md`, and latest checkpoint.

## RudraChart1 standard
- NQ 1H chart, price (Close), EMA(5), SMA/MA(20); time axis UK Europe/London.
- At **every EMA5 and MA20 point** show the corresponding **10-completed-candle slope %**, formatted signed to 3 decimals, with anti-overlap offset labels.
- EMA5 = span 5 exponential average; MA20 = 20-bar simple average. Slope = `100*(MA_now / MA_10_bars_ago - 1)`; calculate on contiguous historical data **before** filtering date range so 00:00 values are valid.
- Show directly in chat if requested; preserve all observed hourly candles (no fabricated 22:00 market break bar); chart-only request should not include repeated prose.
- Standard analytical table if requested: `Time (UK) | Close | EMA5 slope % | MA20 slope %`.
- Research example: 17 Sep 2026 08:00 EMA5 slope ~+0.491%, MA20 slope ~+0.170%, trial exit first 1H close below EMA5; provisional, not validated.

## Communication
- Plain concise English, avoid asking users to repeat prior decisions or provide files present in Git.
- Name the exact repository path when referring to data; report genuine limitations accurately.
