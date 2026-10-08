# Rudra-Reversal NQ 1H — Exact 1-Year Report

## Validation
**CHECKSUM PASS**

Period: **2025-10-07 to 2026-10-07**

Source:
`NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`

Ledger:
`NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv`

## Trade results

| Metric | Exact result |
|---|---:|
| Closed trades | **136** |
| Wins | **101** |
| Losses | **35** |
| Win rate | **74.2647%** |
| Simple return | **+29.4701%** |
| Compounded return | **+33.5512%** |
| Average trade / expectancy | **+0.2167%** |
| Best trade | **+1.6786%** |
| Worst trade | **-3.2936%** |
| Open trade at dataset end | **1, excluded** |

## $10,000 capital report

| Metric | Result |
|---|---:|
| Starting capital | **$10,000.00** |
| Ending capital | **$13,355.12** |
| Net profit | **+$3,355.12** |
| Compounded return | **+33.5512%** |
| Maximum drawdown | **4.3699%** |
| Maximum drawdown dollars | **$477.34** |
| Return / Max DD | **7.68x** |

## Risk statistics

| Metric | Result |
|---|---:|
| Profit Factor | **1.94** |
| Max losing streak | **4 trades** |
| Average winner | **+0.6016%** |
| Average loser | **-0.8941%** |
| Payoff ratio | **0.67** |
| Expectancy per trade | **+0.2167%** |

The payoff ratio is below 1 because the average loser is larger than the average winner, but the **74.3% win rate** makes the total expectancy positive.

The locked strategy has **no separate fixed stop-loss**. Drawdown, losing streak, worst trade, and holding time therefore remain key controls when evaluating live implementation.

## Holding-period statistics

| Metric | Result |
|---|---:|
| Average holding time | **25.62 hours** |
| Median holding time | **16.5 hours** |
| Shortest trade | **1 hour** |
| Longest trade | **119 hours** |
| Average winning trade hold | **16.51 hours** |
| Average losing trade hold | **51.89 hours** |
| Same-UK-date exits | **60** |
| Overnight / multi-date exits | **76** |

Longest trade:
- Entry: **2026-01-16 15:00 UK**
- Exit: **2026-01-21 14:00 UK**
- Holding time: **119 hours**
- Return: **-1.5302%**

A useful observation is that losing trades remained open much longer on average than winning trades: **51.89h vs 16.51h**. This is a research observation only; it does not change the locked strategy.

## Monthly results

| Month | Trades | Wins | Compounded return |
|---|---:|---:|---:|
| 2025-10 | 3 | 2 | **+0.76%** |
| 2025-11 | 9 | 4 | **-1.19%** |
| 2025-12 | 18 | 17 | **+3.84%** |
| 2026-01 | 11 | 7 | **+1.49%** |
| 2026-02 | 13 | 11 | **+1.59%** |
| 2026-03 | 12 | 7 | **-0.72%** |
| 2026-04 | 8 | 7 | **+6.38%** |
| 2026-05 | 6 | 5 | **+3.47%** |
| 2026-06 | 11 | 9 | **+3.42%** |
| 2026-07 | 12 | 6 | **+0.03%** |
| 2026-08 | 15 | 11 | **+2.38%** |
| 2026-09 | 16 | 13 | **+6.31%** |
| 2026-10 | 2 | 2 | **+1.82%** |

Primary weak periods for later regime study:
**November 2025, March 2026, July 2026.**

Do not add filters solely to remove those periods. Analyze the market regime separately first.

## Reproducibility status

The benchmark has now been reproduced from the source data with exact historical execution semantics.

Canonical checksum:
**136 / 101 / 35 / 74.2647% / +33.5512% — PASS**
