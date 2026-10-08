# RUDRA REVERSAL — NEXT SESSION HANDOFF (2026-10-08)

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
