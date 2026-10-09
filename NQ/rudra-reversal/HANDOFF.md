# RUDRA REVERSAL — NEXT SESSION HANDOFF (2026-10-08)

> **PAUSED STATE — 2026-10-08:** Start with [MEMORY_POINTS.md](MEMORY_POINTS.md) for quick recall, then [V2_RESEARCH_CHECKPOINT_2026-10-08.md](V2_RESEARCH_CHECKPOINT_2026-10-08.md) for exact results, assumptions and remaining work. **v1.0 is LOCKED; v2.0 is EXPERIMENTAL.** Do not run further experiments or edit live bot until requested. No complete validated range+trend v2.0 backtest yet.

**Start here.** The canonical project folder for versioned Rudra Reversal work is `NQ/rudra-reversal/`.

## Version separation

**Rudra-Reversal-1.0 — LOCKED**: [Rules](Rudra-Reversal-1.0.md) | [Frozen Python](rudra_reversal_1_0.py)
- Canonical engine: `NQ/backtesting/rudra_reversal_nq_1h.py`, unchanged.
- Source data: `NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`
- Benchmark: 136 closed, 101 wins, 35 losses, 74.2647% win rate, +33.5512% compounded. One end-of-data open trade excluded.
- September 2026: 16 trades, 13 wins, 3 losses, +6.3127% compounded.
- Locked rules include BB20 2std ddof0, lower-band near touch (2 of last 3), 150-bar 20% depth, one long at a time, upper-band exit. No fixed SL, RSI or MA20-touch requirements.
- Never edit its code or overwrite the canonical ledger to try v2.0.

**Rudra-Reversal-2.0 — EXPERIMENTAL**: [Rules](Rudra-Reversal-2.0.md) | [Combined Python](rudra_reversal_2_0.py)
- Filter 5: Narrow BBW (trailing 150-bar lowest 20%) **AND** MA20 10-bar slope between -0.05% and +0.05% => reject new BUY. Negative meaningful slope does not automatically fail.
- Filter 6: Last 60 bars, confirmed swing pivots using 3-left/3-right. Swing high / low define 0%-100% range; entry in upper 50% => reject candidate. Current prototype uses highest confirmed pivot high and lowest confirmed pivot low within window.
- Known issue: swing box can shift when prior pivots leave window, or entry falls outside 0–100%. Need better stable S/R box and breakout invalidation. No lookahead.
- Separate v2 runner recomputes trades after filtering and writes outputs to `NQ/backtesting/results/rudra_reversal_2_0/`. Does not overwrite v1.
- Filter 5 alone September: 15 trades, 12 wins, 3 losses, +5.8728%, **below v1**. Combined Filters 5+6 has not been verified yet.
- September chart review: 8 Sep 10:00/15:00/21:00 were at 76.1%/70.8%/65.3% of prototype 60-bar box (BAD candidates). Better entries on 15–17 Sep should be protected.

## Next session work
1. Run v2 combined Python and inspect September 2026 ONLY until user approves.
2. Audit every entry: UK time, BBW, slope, swing high/low, midpoint, entry swing%, Filter 5/6 classification, actual P/L, and replacement entries.
3. Review 8–10 Sep range and 15–17 Sep trend, adjust causal swing selection without overfitting.
4. Never promote v2 to live or call it locked without explicit user decision.

Charts: entry yellow triangle, exit purple X; labels must be legible. User prefers concise English and per-entry tables.


## 2026-10-08 trend-entry and trailing-exit experiments (latest)

- [September 2026 trend-entry × exit research](SEPTEMBER_TREND_ENTRY_EXIT_RESEARCH.md)
- [Reproducible separate experimental script](experiment_regime_entry_exit_sep.py)
- Trend-entry candidates: 12-bar breakout, follow-through confirmation, breakout retest, MA20 pullback.
- Exit research: A first MA20 close below, B two consecutive below, C confirmed 3/3 swing-low break, D MA20+ swing low, E MA20 protection until +1% close then swing-low trailing.
- September exploratory trend-only table: confirmed-breakout + swing low: **4 trades, 2 wins, +4.113% compounded** (not combined v2 strategy; research only). MA20-exit combinations capture less of sustained rallies but often protect false breakouts sooner.
- Important issue: trend state starts 03 Sep 14:00 and spans 04 Sep 05:00; also 16 Sep 14:00 precedes the key 17 Sep 12:00 signal. Review dynamic regime classification before changing signals.
- v2.0 must eventually dynamically choose RANGE reversal vs UPTREND trend follower and maintain **one shared portfolio position at a time**. No combined test has been validated.
- Retain original v1.0 benchmark and no production changes. Do not optimize solely for September: study other months after manual review.


## Data source and user communication rules — 2026-10-09 (IMPORTANT)

- **Primary repository:** https://github.com/raghunathbhandari/AlgoStrategy (branch main).
- **NQ 1H full continuous dataset for Sep 2026 and adjacent dates:** `NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv` (verified present; includes 17–22 September 2026).
- Additional NQ recent files: `NQ/data/recent/NQ_1h_2026-09-07_2026-10-07.csv` and `NQ/data/recent/NQ_5m_2026-09-07_2026-10-07.csv`.
- Other historical data live under `NQ/data/` and backtesting/data folders elsewhere in AlgoStrategy; the user reports **three years of historical data in Git**. Discover exact coverage/paths by examining the repository folders, README and chunk manifests before claiming a historical file is missing. The verified 12-month source above is sufficient for the current Sep 17–22 request; do not confuse the 12-month source with the total available repository history.
- **ALWAYS consult the connected GitHub repository first**, fetch the relevant file or lines and run calculations. Do not ask the user to re-upload CSV already in Git or claim it is unavailable just because the local container has no network access. GitHub connected fetch is not the same as internet access from Python; use connector retrieval.
- For charts, calculate EMA(5), MA(20) and their **10-candle percentage slopes** on the **continuous history including prior days** BEFORE selecting the requested date range. EMA5 = exponential moving average span=5, MA20 = rolling 20-candle simple moving average; slope% = 100 * (indicator_current / indicator_10_completed_bars_ago - 1). Never restart EMA at midnight; no 00:00 N/A if history is available. Treat missing market hours as no candle, not zero.
- **RudraChart1 standard:** NQ 1H PRICE line, EMA(5) line, MA(20) line with EMA5 slope% near every EMA point and MA20 slope% near every MA point; show date/time UK (Europe/London) and a readable legend. Separate/offset annotations so they do not overlap the lines, price points, or each other. Include all bars across requested multi-day period, not just signal bars. For a long span, enlarge the chart or split into readable daily panels while preserving full underlying data; never omit labels silently.
- Response format: concise English; when a table is requested, use `Time (UK) | Close | EMA5 slope % | MA20 slope %`, then a chart. When the user requests **chart only**, show just the chart with minimal commentary. Prefer presenting directly in chat, offer optional download link. Charts/research drafts stay local; only save code/handoffs/reports in Git when needed.
- Trading research: Rudra Reversal V2 experimental; V1 locked. User's experimental 17 Sep entry baseline at 08:00: EMA5 10-bar slope ~+0.491%, MA20 10-bar slope ~+0.170%; exit at first hourly close below EMA5 (21:00 in that isolated test). Do not claim these thresholds are validated on other days.
- If connector read genuinely fails, explain the precise access issue and try another verified repository path before asking for data. **Communication must reflect what has already been retrieved earlier in the conversation.**


---

## Permanent data + result recovery index (2026-10-09) — READ THIS IN EVERY NEW SESSION

**Problem this solves:** new ChatGPT/Codex sessions have sometimes lost the data location or repeated a result inconsistently. **Do not rely on chat memory or an earlier assistant response as the authoritative source.** Use the repository's source CSV, locked code, locked ledger, and checksum documentation.

### Verified data files (GitHub main, checked 2026-10-09)

| Full repository path | File name date range | Resolution | Purpose |
|---|---|---|---|
| `NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv` | 2025-10-07 to 2026-10-07 | 1H | **Canonical V1 reference and common V2 comparison input** |
| `NQ/data/recent/NQ_1h_2026-09-07_2026-10-07.csv` | 2026-09-07 to 2026-10-07 | 1H | Recent chart cross-check |
| `NQ/data/recent/NQ_5m_2026-09-07_2026-10-07.csv` | 2026-09-07 to 2026-10-07 | 5m | Intraday experiments |
| `NQ/data/NQ_1min_20260401_20260902.csv` | 2026-04-01 to 2026-09-02 | 1m | Historical intraday |
| `NQ/data/NQ_5min_20260120_20260415.csv` | 2026-01-20 to 2026-04-15 | 5m | Historical intraday |

URLs follow `https://github.com/raghunathbhandari/AlgoStrategy/blob/main/<path>`. Paths were verified present, not every row audited in this update; **read CSV timestamps and coverage before calculations**. Other history/chunks may be in `NQ/data/` and `AI_Chunks/`; inspect folders and manifests before declaring years unavailable. Use connected GitHub file access, including bounded line reads, even if the container cannot access internet. Do not demand a repeated upload of existing Git data.

### Canonical V1 source-of-truth chain

1. Detailed immutable contract: `NQ/backtesting/RUDRA_REVERSAL_NQ_1H_LOCKED.md`.
2. Backtest implementation: `NQ/backtesting/rudra_reversal_nq_1h.py`.
3. **Original 136-closed-trade ledger:** `NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv`.
4. Report: `NQ/backtesting/RUDRA_REVERSAL_NQ_1H_1Y_REPORT.md`.
5. Frozen version: `NQ/rudra-reversal/Rudra-Reversal-1.0.md` and `NQ/rudra-reversal/rudra_reversal_1_0.py`.
6. September/monthly chart review: `NQ/reports/rudra_reversal_1y_monthly/`, including `README_CHART_REVIEW_V3.md`, `trade_ledger_chart_ids.csv`, `monthly_manifest.csv`, and `NQ_Rudra_Reversal_12_Month_Chart_Review_Outside_Labels.pdf`.

**Do not use a separate 238-trade/two-entry experimental ledger as V1. Never overwrite canonical code/ledger during V2 research.**

### V1 exact LOCKED rules

- Instrument **NQ**, timeframe **1H**, **LONG only**, full session including overnight, time zone **Europe/London**.
- Bollinger Bands: 20-period SMA, **2.0 population standard deviations (ddof=0)**.
- Entry: current candle touches or comes within **0.15% above lower BB**, and at least **2 of last 3 candles** also touch/near-touch lower BB.
- Range: 150-candle highest **HIGH** and lowest **LOW**, including signal candle. `depth_pct = 100 * (highest_high_150 - signal_close) / (highest_high_150 - lowest_low_150)`. Require **depth >= 20%**.
- Buy at signal candle **CLOSE**; **one open trade**; do not open additional positions before exit.
- Exit on a **later** candle if high touches upper BB or comes within **0.15% below upper BB**. Exact touch -> fill **upper BB**; near-touch -> fill **candle HIGH**.
- **No fixed stop**, **no RSI**, **no MA20-touch requirement**, **no V2 filters**. Keep end-of-data open positions separate from closed-trade statistics.

### Benchmark checksum: do not silently change it

| Period | Closed trades | Wins | Losses | Win rate | Compounded return |
|---|---:|---:|---:|---:|---:|
| 2025-10-07 through 2026-10-07 | **136** | **101** | **35** | **74.2647%** | **+33.5512%** |
| September 2026 | **16** | **13** | **3** | **81.25%** | **+6.3127%** |

Other 12-month results: **+29.4701% sum of trade returns**, best **+1.6786%**, worst **-3.2936%**, **one end-of-data open trade excluded**. These are saved historical backtest benchmarks, NOT claims of a fresh recalculation or net live return.

**Verification gate for every new session:** confirm you have opened source CSV + locked rules + code + ledger; run/reconcile counts and returns before claiming a *new* backtest. If a result disagrees, report both with exact data interval, filter, engine version, execution assumptions, and cause; **do not modify V1 to make the numbers fit**. Do not substitute September-to-October rolling windows for the **calendar month September 1–30, 2026**.

### V2 research — NOT LOCKED

- Separate V2 project files: `NQ/rudra-reversal/Rudra-Reversal-2.0.md`, `rudra_reversal_2_0.py`, `V2_RESEARCH_CHECKPOINT_2026-10-08.md`, `SEPTEMBER_TREND_ENTRY_EXIT_RESEARCH.md`, `experiment_regime_entry_exit_sep.py`.
- **Regime first:** RANGE -> BB reversal; TREND STARTING -> confirmed breakout/retest; UPTREND CONFIRMED -> follow trend; DOWN/UNCLEAR -> WAIT. **One combined portfolio position**, no lookahead, no live bot changes without user approval.
- Filter 5 exploratory: bottom 20% BB width over 150 bars **and** MA20 10-bar slope within +/-0.05%. September F5-only **15 trades, 12 wins, 3 losses, +5.8728%** (below V1).
- Filter 6 exploratory: 60-bar box with confirmed 3-left/3-right pivots; reject candidate reversal in upper half; unstable box needs correction. Combined Filter 5+6 preliminary September **8 trades, 5 wins, 3 losses, +2.5762%**; not independently verified.
- Trend-only September experiment: confirmed breakout plus confirmed swing-low trailing **4 trades, 2 wins, 2 losses, +4.113%**, not combined V2 and not approved as best outside sample.
- **New 2026-10-09 user research instruction:** investigate **EMA9 replacing EMA5 for the trend component** and its slope/flat-market detection. This does **not** edit locked V1 and does **not** automatically replace the older EMA5/MA20 `RudraChart1` convention in `AGENTS.md`. Label old-vs-new chart versions clearly; EMA9 thresholds/results still require documented independent verification.
- Separate trend and BB charts, candles for the requested date window, yellow triangle entry, purple X exit, marker labels outside candle area with guide lines, **actual entry/exit price, exit P/L percent and slope at each signal**. For 'September' show September 1–30, not a mid-month rolling period.

### Explicit instructions to future Codex/AI

- **First read `AGENTS.md`, this handoff, locked V1 rules, and the latest V2 checkpoint.** Never say data/results are missing without searching verified Git paths.
- Record exact input filename, first/last candle UTC/UK times, trading hours, indicator warm-up, code commit/version, full rule parameters, completed trade count, win rate, compounded-return definition, open trades and fee/slippage assumptions with each report.
- Keep one immutable baseline and separate experimental result names; do not present experimental metrics as locked V1; report whether figures are **verified by a fresh run** or **quoted from the saved benchmark**.
- Preserve version history and avoid silent overwrites. Check `NQ/reports/rudra_reversal_1y_monthly/README_CHART_REVIEW_V3.md` before regenerating PDF.
- No change to canonical V1 code, trade ledger, production alerts or trading bot unless user explicitly authorizes it.

**This 2026-10-09 handoff edit updates documentation only; no trading code or data has been changed.**
