# NQ London Session Breakout Backtest

Initial research backtester for the NQ London morning session.

## Baseline

- Input: `NQ/data/NQ_1min_20260401_20260902.csv`
- Convert timestamps to `Europe/London`
- Resample 1-minute data to 5-minute candles
- Test month: August 2026
- Opening range: 08:00-08:30 UK
- Entry window: 08:30-12:00 UK
- Long after first 5-minute close above range high + 2 points
- Short after first 5-minute close below range low - 2 points
- One trade per day
- Stop distance: 50% of opening-range width, minimum 20 points, maximum 100 points
- Target: 2R
- Time exit at 12:00 UK if neither target nor stop is hit

The OHLC backtest is conservative: if one 5-minute candle can touch both stop and target, the stop is counted first.

## Run

```bash
python NQ/backtesting/london_session_breakout.py
```

Change the month or parameters:

```bash
python NQ/backtesting/london_session_breakout.py --month 2026-08 --rr 2 --buffer 2
```

## First August 2026 research comparison

Four simple opening-range definitions were compared. The 08:00-08:30 UK range with an 08:30-12:00 breakout window was the best initial candidate of the four.

Rough baseline result for that configuration at 2R:

- Trades: 10
- Win rate: 50%
- Total: +3.30R
- Average: +0.33R/trade
- Profit factor: ~1.66

This is only one month and is not validation. The next stage should test additional months and filters without overfitting.
