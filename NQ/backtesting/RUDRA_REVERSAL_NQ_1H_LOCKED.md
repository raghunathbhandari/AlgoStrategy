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
- Average trade: **about +0.22%**
- Best trade: **+1.68%**
- Worst trade: **-3.29%**
- Starting-capital example: **$10,000**
- Ending-capital benchmark: **$13,355**
- Net-profit benchmark: **+$3,355**

Weak months previously identified:
- **November 2025**
- **March 2026**
- **July 2026**

## Mandatory validation gate

Before any future AI session changes, optimizes, or interprets this strategy:

1. Load the saved 1H NQ dataset.
2. Run the canonical backtest implementation.
3. Confirm the historical checksum:
   - 136 trades
   - 101 wins
   - 35 losses
   - 74.3% win rate
   - +33.55% compounded return
4. If the checksum does not match, **do not tune the strategy rules**.
5. Investigate only execution semantics until the benchmark is reproduced.

Execution details to verify first:
- Bollinger StdDev convention
- exact 0.15% Lower-BB tolerance interpretation
- exact 0.15% Upper-BB tolerance interpretation
- signal-bar inclusion in rolling windows
- entry fill price and timing
- exit fill price and timing
- treatment of incomplete / zero-volume overnight bars
- end-of-file handling for an open trade

Only after the checksum is reproduced may a rerun be called canonical.

## Standard detailed report flow

Every 1-year Rudra-Reversal report should include the following sections.

### 1. Strategy validation
- Dataset period and row count
- Locked-rule version
- Benchmark checksum match: PASS / FAIL
- Any unresolved execution-semantic differences

### 2. Trade statistics
- Total trades
- Wins
- Losses
- Win rate
- Average trade return
- Best trade
- Worst trade

### 3. Capital report
Default capital example: **$10,000** unless the user specifies otherwise.

Report:
- Starting capital
- Ending capital
- Net profit in dollars
- Compounded return %
- Simple return %
- Monthly compounded returns
- Best month
- Worst month

### 4. Risk report
Report:
- Profit factor
- Maximum drawdown %
- Maximum drawdown $
- Maximum losing streak
- Average winning trade %
- Average losing trade %
- Win/loss payoff ratio
- Expectancy per trade %
- Return / max-drawdown ratio

Important: the locked Rudra-Reversal strategy has **no separate fixed stop-loss rule**. Therefore maximum drawdown, worst trade, losing streak, and time in trade are mandatory risk fields.

### 5. Holding-period report
Report:
- Average holding hours
- Median holding hours
- Minimum holding hours
- Maximum holding hours
- Average winning-trade holding time
- Average losing-trade holding time
- Same-session exits
- Overnight/multi-session exits
- Longest-held trade details

### 6. Monthly/regime review
Always identify weak months and inspect them for market-condition clues.

Current historical weak months:
- November 2025
- March 2026
- July 2026

Do not add filters merely because a weak month exists. Study regime first.

### 7. Trade ledger
Preserve a CSV containing at least:
- entry UK timestamp
- exit UK timestamp
- entry price
- exit price
- trade return %
- holding hours
- win/loss
- signal depth
- Lower-BB touch count
- 150-bar high/low
- relevant BB values

The ledger is required for reproducible Profit Factor, Max Drawdown, and holding-period statistics.

## Important reproducibility rule

Do **not** change the strategy rules simply to force the benchmark.

If a fresh implementation does not reproduce the checksum, first investigate execution details. Only after those execution semantics are matched should a new run replace the historical benchmark.

## Files

Backtest implementation:

`NQ/backtesting/rudra_reversal_nq_1h.py`

Canonical strategy + workflow guide:

`NQ/backtesting/RUDRA_REVERSAL_NQ_1H_LOCKED.md`

Latest 1-year benchmark report:

`NQ/backtesting/RUDRA_REVERSAL_NQ_1H_1Y_REPORT.md`

Default source data:

`NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`

Expected trade ledger output:

`NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv`

This strategy definition is **locked** unless the user explicitly asks to create a new version.
