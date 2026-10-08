# Rudra-Reversal-2.0 — Saved research state (2026-10-08)

**STATUS: PAUSED / EXPERIMENTAL / NEEDS REFINEMENT. NOT APPROVED FOR LIVE TRADING.**
**Read this checkpoint and [HANDOFF.md](HANDOFF.md) before work in another session.**

## 1. Versions: Do not mix

**Rudra-Reversal-1.0 — LOCKED**: [rules](Rudra-Reversal-1.0.md), [frozen Python](rudra_reversal_1_0.py). The canonical original engine is `NQ/backtesting/rudra_reversal_nq_1h.py`. Benchmark 2025-10-07–2026-10-07 NQ 1H: **136 closed trades, 101 wins, 35 losses, 74.2647% win rate, +33.5512% compounded** (one open trade excluded). September: **16 trades, 13 wins, 3 losses, +6.3127%**. Never edit, replace or rebaseline v1.0 while developing v2.0.

**Rudra-Reversal-2.0 — experimental**: [rules](Rudra-Reversal-2.0.md), [combined Filter 5/6 Python](rudra_reversal_2_0.py), [trend entry/exit research script](experiment_regime_entry_exit_sep.py), [September trend research](SEPTEMBER_TREND_ENTRY_EXIT_RESEARCH.md). Scripts are saved to GitHub. Their independent execution/reproducibility has NOT been verified in this checkpoint. The integrated regime-switching strategy is not implemented yet.

Historical input `NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`; all displayed times Europe/London.

## 2. Critical user intent

We are not seeking only a higher September percent. Need to **detect market regime before selecting entry and exit**, and **capture big winning moves** instead of rejecting every upper-half or narrow-band setup.

Proposed switching concept:
- RANGE: mean reversal at lower BB/support, exit near upper BB/resistance; test Filters 5/6 carefully.
- TREND STARTING: breakout and follow-through confirmation; tighter invalidation / initial protection.
- UPTREND CONFIRMED: breakout retest / higher low / MA20 pullback; trail by confirmed swing lows to capture long winners.
- DOWN/UNCLEAR: WAIT for long-only system.
- Never look ahead; completed 1H candles only. Avoid one shared trading account holding overlapping range and trend trades.

## 3. Filter 5 — narrow BBW AND flat MA20

- MA20 slope over 10 bars % = `100*(MA20_now/MA20_10bars_ago-1)`.
- Flat **-0.05% through +0.05% inclusive**. Strong negative slope is NOT automatically bad for reversal.
- BB width % = `100*(BB_upper-BB_lower)/MA20`; narrow = lowest 20% of trailing 150 readings.
- Block BUY only if both narrow AND flat.
- Sep Filter 5-only: **15 trades, 12 wins, 3 losses, +5.8728% compounded**, below v1.0; keep experimental.

## 4. Filter 6 — last 60 candles, swing levels

- Confirm local swing pivots with 3 left + 3 right candles, only once right-side candles are completed.
- Prototype swing box: highest confirmed pivot high and lowest confirmed pivot low among 60 bars.
- Position % = `100*(entry - swingLow)/(swingHigh-swingLow)`. Upper half (>50% and <=100%) rejected; lower half candidate.
- Values outside 0–100%, missing pivots: **UNCLASSIFIED**, not automatically safe.
- On 8 Sep at 10:00/15:00/21:00 original entries were 76.1%/70.8%/65.3%, correctly flagged as range entries to avoid visually. But 15 Sep 16:00 and 16 Sep 20:00 profitable reversals were also rejected. Swing-box boundaries can be unstable as pivots expire.
- Preliminary combined Filter 5+6 **without regime switching**: **8 trades / 5 wins / 3 losses / +2.5762%** compounded in September. In-session exploratory calculation only; run saved script independently before making benchmark claims.

## 5. Separate 2.5 standard deviation test

BB 2.5 STD for entries AND exits with other v1 rules: September **9 trades, 6 wins, 3 losses, +2.9524%** compounded in-session preliminary. Do not change v1 or promote based on this.

## 6. Two trend-start benchmark candles

- **04 Sep 05:00 UK**, NQ close 29,598.25; MA20 29,428.26; 10-bar slope +0.607%; prior 12-bar high 29,584.25. Breakout signaled but later faded: **failed trend**.
- **17 Sep 12:00 UK**, close 29,620.00; MA20 29,444.03; slope +0.170%; prior 12-bar high 29,592.75. Early breakout before sustained rally.
- V1 on 16 Sep 20:00 bought 29,254.25, exited 17 Sep 08:00 at 29,567.50, +1.0708%. Sep 21 20:00 high 30,862.75, another +4.38% after that exit **as hindsight opportunity**.
- Trend state machine may group 04 Sep with earlier **03 Sep 14:00** episode, and 17 Sep with a preceding **16 Sep 14:00** episode. Needs meaningful fresh-breakout / reset logic rather than hindsight labeling.

## 7. September trend-only entry × exit matrix

[Full documentation](SEPTEMBER_TREND_ENTRY_EXIT_RESEARCH.md), [Python](experiment_regime_entry_exit_sep.py).

Entry variants: initial 12-bar BREAKOUT, CONFIRM within 3 bars, RETEST of breakout zone, MA20 PULLBACK after confirmation.

Exit A: first close below MA20. B: two closes below MA20. C: close below latest confirmed 3/3 swing low. D: below MA20 AND below swing low. E: protect with MA20 until +1% achieved on close, then use swing low trail.

| Entry | Exit A | Exit B | Exit C | Exit D | Exit E |
|---|---:|---:|---:|---:|---:|
| BREAKOUT | +1.102% | +0.790% | +3.562% | +3.562% | +2.419% |
| CONFIRM | +1.685% | +2.327% | **+4.113%** | **+4.113%** | +1.722% |
| RETEST | +0.714% | +1.457% | +3.858% | +3.858% | +1.370% |
| MA_PULLBACK | -0.357% | -0.129% | +2.667% | +2.667% | -0.672% |

Results = **experimental trend-only September-entry compounded returns** (some exits in October), before fees/slippage. Not a combined v2.0 result. Saved script should be rerun for reproducibility. CONFIRM+C: 4 trades, 2 wins, 2 losses, +4.113%; dominated by **16 Sep 15:00→23 Sep 12:00 +4.95%**. Highest return in development sample is NOT proof of optimum.

## 8. State of work / instructions for next session

**Save and stop here; do not lock v2.0.**

1. Improve RANGE ↔ TREND STARTING ↔ UPTREND CONFIRMED ↔ WAIT detector, using only available candles; distinguish 04 Sep false breakout from the 17 Sep sustained rally.
2. Refine coherent and stable 60-bar swing high/low zone; identify actual nearby resistance and reject upper-half buys mainly in ranges, not confirmed uptrends.
3. Compare trend entry variants & trailing exits. Study capture of maximum favorable excursion vs worst drawdown, early false breakouts, protection, and higher-low break.
4. Build ONE combined regime switching v2 portfolio (range + trend, no duplicate positions); keep outputs isolated from canonical v1.
5. Develop on September until acceptable for chart review, THEN validate on out-of-sample months and costs before considering live use. User permission required before promotion.
6. Tables: entry UK date/time, entry/exit prices, MA slope%, BBW%, confirmed swing high/low, 50% level and box position%, GOOD/BAD reason, actual P/L & WIN/LOSS. Show entry yellow triangles, exit purple X outside candle area with guide lines.

**No live bot/alert changes. No v1.0 changes. No new locked v2.0 rules yet.**
