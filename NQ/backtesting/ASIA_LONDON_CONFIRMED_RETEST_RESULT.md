# NQ Asia -> London breakout: confirmed swing-retest revision

Test month: August 2026
Timeframe: 5-minute NQ
Asia range: 00:00-07:00 Europe/London
London trade window: 07:00-12:00 Europe/London

## Retest structure used in Pine and backtest

1. First 5m close outside Asia High/Low by 2 points = BREAKOUT CANDLE.
2. Price must move at least 10 NQ points away from the broken level.
3. Wait at least 3 bars after breakout.
4. A pullback/swing candle must touch the broken Asia level within 5 points.
5. The RETEST CANDLE is the NEXT candle, not the pullback candle.
6. Long confirmation: next candle is bullish, closes above the pullback candle high, and above Asia High + 2.
7. Short confirmation: next candle is bearish, closes below the pullback candle low, and below Asia Low - 2.
8. Pullback must occur within 12 bars after breakout.
9. Exit model remains 2R target with the same risk model used in the current research.

## August 2026 result

- Trades: 2
- Wins: 1
- Losses: 1
- Win rate: 50%
- Total: +0.07R
- Average: +0.04R/trade
- Profit factor: 1.07
- Targets: 0
- Stops: 1
- Time exits: 1

Trades:
- 2026-08-17 LONG 07:25 UK -> -1.00R
- 2026-08-25 LONG 07:20 UK -> +1.07R time exit

Interpretation:
This confirmed two-candle swing retest better matches the visual definition requested, but the exact current parameter set is too restrictive and did not improve the August result. Keep the structural definition, then tune the swing-away distance, minimum bars, retest tolerance, and confirmation threshold rather than reverting to the old next-candle touch logic.
