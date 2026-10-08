# Rudra-Reversal-2.0 — EXPERIMENTAL / NOT LOCKED FOR TRADING

Status: **RESEARCH ONLY**. Based on `Rudra-Reversal-1.0`, with proposed Filters 5 and 6. No live deployment or validated 2.0 performance claim.

## Unchanged baseline
Retain v1.0's BB entry, 150-bar depth, fill, one-position, upper-BB exit, full-session and UK-time handling unchanged.

## Filter 5 — narrow bands AND flat moving average
- BBW percent = `100 * (BB_upper - BB_lower)/BB_middle`.
- MA20 slope percent = `100 * (MA20_now/MA20_10_bars_ago - 1)`.
- Flat means slope in **[-0.05%, +0.05%]** (inclusive).
- Narrow means current BBW is in the lowest 20% of its trailing 150 candle readings (causal).
- Proposed rejection: narrow AND flat => skip new BUY. A materially positive OR negative slope does not itself reject the trade.
- Separate experimental runner: `NQ/backtesting/rudra_reversal_nq_1h_sep_flat_experiment.py`.
- September-only result for this filter ALONE: 15 trades, 12 wins, 3 losses, +5.8728% compounded vs v1.0 16 / 13 / 3 / +6.3127%. **Not an improvement**.

## Filter 6 — 60-bar confirmed swing box
- Look back 60 hourly candles.
- Confirm a swing high/low using 3 candles on each side; a pivot only becomes available once its 3 right-side candles have completed.
- Prototype takes highest confirmed swing high and lowest confirmed swing low inside that 60-bar window.
- Swing position = `100*(entry_close - swing_low)/(swing_high - swing_low)`.
- Proposed: if swing position is **above 50% and at or below 100%**, mark BUY as BAD candidate; lower 50% is potentially valid, subject to v1 entry rules and Filter 5.
- If swing position is negative, above 100%, or pivots are unavailable, classify `OUTSIDE_BOX` or `UNDEFINED`, **not automatically GOOD**.
- Need to refine selection of meaningful, stable swing high/low pairs, and test breakout/old-box invalidation; current extreme-pivot prototype can jump as pivots expire.
- Audit runner: `NQ/backtesting/rudra_reversal_nq_1h_swing60_experiment.py`.
- Filter 6 has only an initial September pivot audit; **no verified combined Filter 5+6 trade ledger or return** exists yet.

## Version separation / next validation
1. Never edit/overwrite `NQ/backtesting/rudra_reversal_nq_1h.py`, its canonical trade ledger, or 1.0 checksum.
2. Implement and test a separate v2 combined runner, writing to uniquely named files.
3. Compare September 2026 first, including exact entries, exclusions, replacement entries, win/loss, compounded returns and visual swing-box alignment.
4. Confirm no forward-looking candles are used for the signal and the 60-bar box.
5. Do not promote v2 to locked/live without explicit user approval.
