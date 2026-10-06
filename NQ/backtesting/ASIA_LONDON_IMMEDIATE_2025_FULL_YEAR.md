# NQ Asia Range -> London Immediate Breakout — Full-Year Test

## Test period
- Calendar year: **2025**
- Data: 5-minute NQ continuous futures bars
- Source used for the validation run: public Databento-derived NQ 5-minute dataset
- Source coverage used: 2025-01-01 through 2025-12-31
- Session timezone: Europe/London with DST handling

## Strategy rules
- Asia range: 00:00-07:00 UK
- London trade window: 07:00-12:00 UK
- Long: first 5-minute close > Asia High + 2 NQ points
- Short: first 5-minute close < Asia Low - 2 NQ points
- One trade per day
- Stop distance: 35% of Asia range, minimum 25 points, maximum 120 points
- Target: 2R
- If a 5-minute bar touches both stop and target, stop is assumed first
- If neither stop nor target hits, exit at the end of the London window

## 2025 result
- Trades: **212**
- Wins: **83**
- Losses: **129**
- Win rate: **39.2%**
- Total result: **-4.97R**
- Average per trade: **-0.023R**
- Profit factor: **0.96**
- Targets: 41
- Stops: 105
- Time exits: 66
- Max drawdown: **19.74R**

## Direction split
- LONG: 122 trades, 44.3% win rate, **+1.70R**
- SHORT: 90 trades, 32.2% win rate, **-6.67R**

## Monthly result
| Month | Trades | Win rate | R |
|---|---:|---:|---:|
| Jan | 19 | 52.6% | +5.41 |
| Feb | 15 | 46.7% | -1.83 |
| Mar | 18 | 33.3% | -2.82 |
| Apr | 20 | 40.0% | -0.49 |
| May | 19 | 52.6% | +1.89 |
| Jun | 18 | 38.9% | -0.41 |
| Jul | 18 | 16.7% | -7.59 |
| Aug | 14 | 64.3% | +10.53 |
| Sep | 20 | 30.0% | -3.35 |
| Oct | 20 | 35.0% | +0.79 |
| Nov | 14 | 21.4% | -8.95 |
| Dec | 17 | 41.2% | +1.84 |

## Interpretation
The unfiltered immediate-breakout rule does **not** show a robust full-year edge in 2025. The one-month result was encouraging, but the full-year test is approximately breakeven/slightly negative.

The most obvious structural clue is direction: longs were slightly profitable (+1.70R), while shorts lost -6.67R. Month-to-month behavior is also highly regime-dependent, with August exceptionally strong and July/November very weak.
