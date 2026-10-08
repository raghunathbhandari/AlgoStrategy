# Rudra-Reversal NQ 1H — Canonical Locked Strategy

This is the permanent strategy and reproducibility guide for future AI sessions.

## Final locked rules

| Rule | Final setting |
|---|---|
| Instrument | **NQ** |
| Timeframe | **1H** |
| Direction | **LONG only** |
| Bollinger Band | **20-period SMA, 2.0 StdDev** |
| StdDev convention | **Population StdDev, ddof=0** |
| Lower BB entry | Current candle must touch/near-touch Lower BB and at least **2 of last 3 candles** must touch/near-touch |
| Lower-BB tolerance | **0.15% above Lower BB** |
| 150-bar range | Highest **HIGH** and lowest **LOW** of last 150 candles, including signal candle |
| Depth measure | Use **signal candle CLOSE** |
| Minimum depth | **20% down from 150-bar top** |
| MA20 touch | **Removed** |
| RSI | **Removed** |
| Entry fill | **Signal candle CLOSE** |
| Position count | **One trade at a time** |
| Exit trigger | First later candle touching Upper BB or within **0.15% below Upper BB** |
| Exit fill | If HIGH reaches Upper BB: fill at **Upper BB**. If only near-touch: fill at **candle HIGH** |
| Session | Full available **overnight/premarket + regular session** |
| Time shown | **UK time / Europe-London** |
| End-of-data open trade | Preserve separately; **exclude from closed-trade benchmark** |

## Recovered historical implementation

The exact execution semantics were recovered from Git history on 2026-10-08 from the earlier Rudra-Reversal chart/backtest engine in commit:

`25e81b7e99560bf6cac66d15eb59c94266cf7b7a`

The historical file was:

`NQ/tools/make_nq_2025_monthly_bb_charts.py`

That code established the missing mechanics:
- `rolling(20).std(ddof=0)`
- near-lower and near-upper tolerance measured relative to the BB value
- entry at signal candle close
- exact Upper-BB exit filled at the Upper-BB value
- near-touch exit filled at candle high
- next signal allowed only after the prior trade exits

The final rule changes applied on top of that historical engine are:
- depth = **20%**
- depth uses **signal CLOSE**
- **MA20 filter removed**
- **RSI removed**

## Exact benchmark — CHECKSUM PASS

Source:
`NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`

Period:
**2025-10-07 to 2026-10-07**

| Metric | Exact result |
|---|---:|
| Closed trades | **136** |
| Wins | **101** |
| Losses | **35** |
| Win rate | **74.2647%** |
| Simple return | **+29.4701%** |
| Compounded return | **+33.5512%** |
| Best trade | **+1.6786%** |
| Worst trade | **-3.2936%** |
| Open trade at data end | **1 — excluded from benchmark** |

The month-by-month counts also match the historical benchmark exactly:
Oct-2025 3, Nov 9, Dec 18, Jan-2026 11, Feb 13, Mar 12, Apr 8, May 6, Jun 11, Jul 12, Aug 15, Sep 16, Oct-2026 2.

## Standard workflow for every future AI session

1. Read this guide first.
2. Use the canonical source data or a clearly named newer dataset.
3. Run `NQ/backtesting/rudra_reversal_nq_1h.py`.
4. For the historical one-year source, require the hard checksum PASS:
   - 136 closed trades
   - 101 wins
   - 35 losses
   - 74.2647% win rate
   - +33.5512% compounded return
5. Do not alter locked strategy rules to make results fit.
6. Save the exact closed-trade ledger.
7. Preserve any end-of-data open trade separately.
8. Generate capital, Profit Factor, drawdown, expectancy, losing-streak, holding-period and monthly reports from the saved ledger.
9. Only create a new strategy version if the user explicitly changes a rule.

## Canonical files

Backtest:
`NQ/backtesting/rudra_reversal_nq_1h.py`

Exact 136-trade ledger:
`NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv`

One-year report:
`NQ/backtesting/RUDRA_REVERSAL_NQ_1H_1Y_REPORT.md`

Source data:
`NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`

This strategy is **locked** unless the user explicitly asks to create a revised version.
