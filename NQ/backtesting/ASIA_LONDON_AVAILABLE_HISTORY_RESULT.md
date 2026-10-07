# NQ Asia Range -> London Immediate Breakout: available-history validation

Strategy A baseline
- Timeframe: 5-minute
- Asia range: 00:00-07:00 Europe/London
- London entry window: 07:00-12:00 Europe/London
- Entry: first 5m close above Asia High + 2 points or below Asia Low - 2 points
- One trade per day
- Stop: 35% of Asia range, bounded 25-120 NQ points
- Target: 2R
- Conservative OHLC handling: stop first if both stop and target are touched on the same bar
- Time exit: end of London window

## Data coverage warning

The repository does NOT currently contain a full year of NQ data suitable for this strategy.

Available files:
- NQ/data/NQ_5min_20260120_20260415.csv
- NQ/data/NQ_1min_20260401_20260902.csv

The 1-minute file has full-day coverage in August and early September, but May-July rows are only approximately 13:30-20:14 UTC (U.S. RTH). Those months therefore lack the required Asia session and were excluded.

Valid tested period:
- 2026-01-21 through 2026-04-15
- 2026-08
- 2026-09-01

## Combined valid-sample result

- Trades: 61
- Wins: 25
- Losses: 36
- Win rate: 41.0%
- Total: -1.27R
- Average: -0.021R/trade
- Profit factor: 0.96
- Targets: 12
- Stops: 31
- Time exits: 18

## Monthly results

| Month | Trades | Win rate | Total R | Profit factor |
|---|---:|---:|---:|---:|
| 2026-01 | 7 | 28.6% | -2.99R | 0.40 |
| 2026-02 | 16 | 31.3% | -7.38R | 0.33 |
| 2026-03 | 18 | 50.0% | +4.51R | 1.55 |
| 2026-04 | 9 | 33.3% | -1.29R | 0.70 |
| 2026-08 | 10 | 50.0% | +3.87R | 2.08 |
| 2026-09 | 1 | 100.0% | +2.00R | n/a |

## Interpretation

August showed a strong edge, but that edge does not persist across the currently valid multi-month sample. The combined result is approximately flat/slightly negative. Do not call this strategy validated yet.

Next research should:
1. obtain continuous full-day NQ history for missing months;
2. repeat this exact baseline unchanged;
3. inspect regime/time/range filters only after establishing the full baseline.
