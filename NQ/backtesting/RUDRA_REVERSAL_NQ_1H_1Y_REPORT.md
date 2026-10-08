# Rudra-Reversal NQ 1H — Latest 1-Year Detailed Report

## Benchmark period
**2025-10-07 to 2026-10-07**

## Strategy
Canonical locked **Rudra-Reversal NQ 1H** rules.

## Confirmed benchmark results

| Metric | Result |
|---|---:|
| Trades | **136** |
| Wins | **101** |
| Losses | **35** |
| Win rate | **74.3%** |
| Average trade | **about +0.22%** |
| Best trade | **+1.68%** |
| Worst trade | **-3.29%** |
| Compounded return | **+33.55%** |

## $10,000 capital example

| Metric | Result |
|---|---:|
| Starting capital | **$10,000** |
| Compounded return | **+33.55%** |
| Net profit | **+$3,355** |
| Ending capital | **$13,355** |

This capital example assumes the historical benchmark return stream is applied proportionally to account equity.

## Risk interpretation

The strategy has a high historical win rate, but it does **not** use a separate fixed stop-loss in the locked rule set. Because of that, win rate alone is not sufficient to judge risk.

The following fields are mandatory before the benchmark is considered fully documented:
- Profit Factor
- Maximum Drawdown %
- Maximum Drawdown $
- Maximum losing streak
- Average winner %
- Average loser %
- Payoff ratio
- Expectancy per trade
- Return / Max Drawdown ratio

These metrics must be calculated from the exact **136-trade ledger** that reproduces the benchmark checksum. They must not be estimated from the summary statistics.

## Holding-period statistics required

The exact benchmark trade ledger must also provide:
- Average holding hours
- Median holding hours
- Shortest holding period
- Longest holding period
- Average holding time for winners
- Average holding time for losers
- Same-session exits
- Overnight / multi-session exits
- Longest-held trade details

These values are intentionally left unfilled until the exact 136-trade benchmark implementation is reproduced. Do not substitute values from a different implementation.

## Monthly/regime review

Weak periods already identified from the benchmark:
- **November 2025**
- **March 2026**
- **July 2026**

These months should be studied for regime characteristics after the benchmark implementation is reproduced. Do not add filters solely to eliminate weak months.

## Validation status

Historical benchmark checksum:

- **136 trades**
- **101 wins**
- **35 losses**
- **74.3% win rate**
- **+33.55% compounded return**

Current requirement:
**reproduce this checksum with the saved code before filling Profit Factor, drawdown, and holding-period fields.**

## Reproducibility files

Strategy + workflow guide:
`NQ/backtesting/RUDRA_REVERSAL_NQ_1H_LOCKED.md`

Backtest code:
`NQ/backtesting/rudra_reversal_nq_1h.py`

Source data:
`NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`

Trade ledger target:
`NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv`

## Future AI-session rule

A future AI session must:

1. Read the locked strategy guide.
2. Run the saved backtest code on the stated source dataset.
3. Confirm the benchmark checksum.
4. If it fails, debug execution semantics only; do not change strategy rules.
5. Once it passes, save the exact trade ledger.
6. Generate the full capital, Profit Factor, Max Drawdown, expectancy, losing-streak, and holding-period report.
7. Update this report with those exact values.

Do not replace the benchmark with results from a slightly different implementation.
