# NQ Asia -> London breakout: swing-retest revision

Test month: August 2026
Chart logic: 5-minute NQ
Asia range: 00:00-07:00 Europe/London
London trade window: 07:00-12:00 Europe/London
Target: 2R
One trade per day

## Immediate breakout baseline
- Trades: 10
- Wins: 5
- Losses: 5
- Win rate: 50%
- Total: +3.87R
- Average: +0.39R
- Profit factor: 2.08

## Strict swing-retest revision
Rules:
- First 5m close outside Asia High/Low by 2 points
- Retest cannot be immediate
- Minimum 3 bars after breakout
- Price must first move at least 10 points away from broken level
- Retest must occur within 12 bars
- Retest tolerance: 5 points
- Long confirmation candle closes bullish and back above Asia High + 2
- Short confirmation candle closes bearish and back below Asia Low - 2

Result:
- Trades: 2
- Wins: 2
- Losses: 0
- Win rate: 100%
- Total: +2.92R
- Average: +1.46R
- Targets: 1
- Stops: 0
- Time exits: 1

Trades:
- 2026-08-17 LONG 07:20 UK, +0.92R time exit
- 2026-08-25 LONG 07:15 UK, +2.00R target

Interpretation:
The strict swing-retest definition improves selectivity but cuts trade frequency too much. Keep it as a reference version and test a looser structural-swing retest next.
