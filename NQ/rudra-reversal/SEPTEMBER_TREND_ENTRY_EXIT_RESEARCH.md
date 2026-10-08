# Rudra-Reversal-2.0 — Trend Entry × Exit September 2026 Research (2026-10-08)

**Status: experimental, in-sample, NOT a new locked strategy.**
The live/canonical v1.0 engine and its 136-trade ledger are unchanged.
Python reproducer: [experiment_regime_entry_exit_sep.py](experiment_regime_entry_exit_sep.py).

## Trend regime definition (causal)

1. RANGE → TREND STARTING: 1H close above the **previous 12-bar high**, above MA20, and 10-bar MA20 slope >= +0.05%.
2. Starting → UPTREND: within 3 candles, close exceeds starting signal close, stays above MA20, slope >= +0.05%.
3. UPTREND → RANGE: two consecutive closes below MA20.
4. Candidate may fail before confirmation; there is no guarantee of a profitable trend.

This is a **trend-only** test. It does NOT yet merge the v2.0 range reversal strategy and Filters 5/6. A range regime detector independent of breakout signals is still required.

## Entry variants

- BREAKOUT: initial signal-bar close.
- CONFIRM: confirmation-bar close.
- RETEST: first bar within 12 bars of confirmation, within 0.15% above breakout level by its low, closing back at/above the breakout level and above MA20.
- MA_PULLBACK: first bar within 24 bars after confirmation touching/coming within 0.15% above MA20, closing at/above MA20, with slope >= +0.05%.

## Exit variants

- A_MA1: first close below MA20.
- B_MA2: second consecutive close below MA20.
- C_SWING: first close below last confirmed 3-left/3-right pivot low.
- D_MA_AND_SWING: close below MA20 AND confirmed pivot low on the same bar.
- E_PROTECT_THEN_SWING: MA20 close exit until a candle **closes** +1% or more above entry, then swing-low trailing. A high reaching +1% alone does not activate.

One open position at a time per entry/exit variant. Entry on September **episode start**, exits can happen in October. All fills at signal-bar close, no costs. There is **no guarantee** a completed-bar close can be filled at the exact historical close. Performance calculations are approximate research.

## Preliminary September entry-vintage compounded returns (%)

| Entry | Exit A | Exit B | Exit C | Exit D | Exit E |
|---|---:|---:|---:|---:|---:|
| BREAKOUT | +1.102 | +0.790 | +3.562 | +3.562 | +2.419 |
| CONFIRM | +1.685 | +2.327 | **+4.113** | **+4.113** | +1.722 |
| RETEST | +0.714 | +1.457 | +3.858 | +3.858 | +1.370 |
| MA_PULLBACK | -0.357 | -0.129 | +2.667 | +2.667 | -0.672 |

- CONFIRM+C: 4 trades, 2 wins, 2 losses. High return concentrated in a prolonged September trend.
- BREAKOUT+A: 10 trades, 4 wins, 6 losses, +1.102%.
- D matched C in this sample because all observed pivot-break exits also satisfied the MA20 condition; this does **not** prove it will always do so.
- Strategy outcomes depend on holding-period overlap, so columns are not directly comparable per trade.
- September v1.0's 16 reversal trades / +6.3127% is **not** an equivalent benchmark for this trend-only module.

## Critical limitations and next tests

- The state machine started a trend episode **03 Sep 14:00**, which encompassed the important **04 Sep 05:00** breakout. It may not identify independent trend launches as expected. Fix/validate this before drawing conclusions.
- A second early signal **16 Sep 14:00** preceded the key **17 Sep 12:00** breakout. Detect transition earlier without prematurely labeling a stable uptrend.
- C and D swing stops can be loose and retain losing trades. Measure worst intratrade drawdown, stop distance and risk exposure; consider initial protective invalidation.
- Test dynamic regime transitions and full RANGE+UPTREND portfolio accounting with original Filters 5 and 6, no double counted positions.
- Continue September chart review; then validate any selected parameters out-of-sample (other months). Do not pick the highest in-sample return alone.

Reproduce:
`python3 NQ/rudra-reversal/experiment_regime_entry_exit_sep.py`

Files written by script to `NQ/backtesting/results/rudra_reversal_2_0/regime_sep/`: `september_regime_episodes.csv`, `entry_exit_matrix.csv`, `entry_exit_all_trades.csv`.

**Note:** the table above is an initial in-session computation from the connected CSV. The committed Python script is provided for independent reproducibility and must be run/checked before interpreting the figures as production quality.
