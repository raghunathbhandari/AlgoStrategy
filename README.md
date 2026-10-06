# AlgoStrategy

Research and backtesting repository. Separate from ASJR/VPS.

## Current project
NQ London Session Breakout research on 5-minute candles.

### Data
Run:

```bash
python scripts/fetch_nq_data.py
```

### Baseline test
Run:

```bash
python strategies/nq_london_session_breakout_5m.py
```

Baseline v1:
- Build London opening range 07:00-08:00 Europe/London
- Trade 08:00-11:00 Europe/London
- First 5-minute close outside range
- Stop on opposite side of range
- Target 2R
- Maximum one trade per London day

This is only a baseline. It will be refined using the full 2022-2025 dataset.
