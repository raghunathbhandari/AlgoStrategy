# NQ Asia Range -> London Breakout

Research comparison using August 2026 NQ 1-minute data resampled to 5-minute candles.

## Session definition
- Asia range: 00:00-07:00 UK
- London entry window: 07:00-12:00 UK
- One trade per day
- Breakout buffer: 2 NQ points
- Stop: 35% of Asia range, bounded 25-120 points
- Target: 2R

## Case 1: Immediate breakout
Enter on the first 5-minute close above Asia High or below Asia Low.

August result:
- Trades: 10
- Wins: 5
- Losses: 5
- Win rate: 50%
- Total: +3.87R
- Average: +0.39R/trade
- Profit factor: 2.08

## Case 2: Breakout + retest
Wait for the breakout, then require price to retest the broken Asia level within 6 x 5-minute bars and close back in the breakout direction.

August result:
- Trades: 10
- Wins: 5
- Losses: 5
- Win rate: 50%
- Total: +5.49R
- Average: +0.55R/trade
- Profit factor: 2.63

Retest is the stronger first candidate, but one month is not enough for validation.
