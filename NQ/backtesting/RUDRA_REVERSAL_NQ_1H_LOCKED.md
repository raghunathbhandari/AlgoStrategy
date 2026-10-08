# Rudra-Reversal NQ 1H — Canonical Locked Strategy

This document is the permanent reference for future AI sessions.

## Final locked rules

| Rule | Final setting |
|---|---|
| Instrument | **NQ** |
| Timeframe | **1H** |
| Direction | **LONG only** |
| Bollinger Band | **20-period SMA, 2.0 StdDev** |
| Lower BB entry | At least **2 of last 3 candles** touch Lower BB or come within **0.15%** |
| 150-bar range | Highest **HIGH** and lowest **LOW** of last 150 candles |
| Depth measure | Use **signal candle CLOSE** |
| Minimum depth | **20% down from 150-bar top** |
| MA20 touch | **Removed** |
| RSI | **Removed** |
| Position count | **One trade at a time** |
| Exit | Upper BB touch or within **0.15% below Upper BB** |
| Session | Full available **overnight/premarket + regular session** |
| Time shown | **UK time / Europe-London** |

## Historical benchmark checksum

The previous latest-1-year benchmark run produced:

- Period: **2025-10-07 to 2026-10-07**
- Trades: **136**
- Wins: **101**
- Losses: **35**
- Win rate: **74.3%**
- Compounded return: **+33.55%**
- Starting-capital example: **$10,000**
- Ending-capital benchmark: **$13,355**
- Net-profit benchmark: **+$3,355**

Weak months previously identified:
- **November 2025**
- **March 2026**
- **July 2026**

## Important reproducibility rule

Do **not** change the strategy rules simply to force the benchmark.

If a fresh implementation does not reproduce the checksum, first investigate execution details such as:

- Bollinger StdDev convention
- exact interpretation of the 0.15% entry tolerance
- exact interpretation of the 0.15% exit tolerance
- entry fill price/timing
- exit fill price/timing
- whether the signal bar is included in rolling windows
- handling of incomplete/zero-volume overnight bars

Only after those execution semantics are matched should a new run replace the historical benchmark.

## Files

Backtest implementation:

`NQ/backtesting/rudra_reversal_nq_1h.py`

Default source data:

`NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`

Expected trade ledger output:

`NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv`

This strategy definition is **locked** unless the user explicitly asks to create a new version.
