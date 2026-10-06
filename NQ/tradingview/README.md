# TradingView indicator

File: `NQ/tradingview/NQ_Asia_London_Breakout.pine`

Use on **NQ 5-minute chart**.

What it shows:
- Asia High and Asia Low from **00:00-07:00 Europe/London**
- Asia-session background shading
- First London-session breakout candle between **07:00-12:00 UK**
- BUY BREAK / SELL BREAK label on the immediate breakout candle
- RETEST triangle when price retests the broken Asia level and closes back in the breakout direction within the configured number of bars
- Alert conditions for both breakout and retest signals

Default research settings match the current August 2026 backtest:
- breakout buffer = 2 NQ points
- retest tolerance = 5 points
- max retest wait = 6 bars (30 minutes on a 5m chart)

The script uses `Europe/London` explicitly, so the session calculation follows UK daylight-saving changes automatically.
