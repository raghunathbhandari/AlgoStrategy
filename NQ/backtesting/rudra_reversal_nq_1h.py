#!/usr/bin/env python3
"""
Rudra-Reversal NQ 1H backtest.

CANONICAL LOCKED STRATEGY
-------------------------
Instrument: NQ
Timeframe: 1H
Direction: LONG only
Bollinger Bands: 20-period SMA, 2.0 StdDev
Entry proximity:
  - At least 2 of the last 3 candles touch the Lower BB
    OR come within 0.15% above the Lower BB.
150-bar range:
  - Highest HIGH and lowest LOW of the last 150 candles.
Depth:
  - Use SIGNAL CANDLE CLOSE.
  - Signal close must be at least 20% down from the 150-bar top.
Removed filters:
  - No MA20 touch filter.
  - No RSI filter.
Positioning:
  - One trade at a time.
Exit:
  - Upper BB touch OR within 0.15% below the Upper BB.
Session:
  - Use all available overnight/premarket + regular-session bars.
Time display:
  - Europe/London / UK time.

IMPORTANT VALIDATION CHECKSUM
-----------------------------
Historical latest-1Y benchmark previously produced:
  Period: 2025-10-07 -> 2026-10-07
  Trades: 136
  Wins: 101
  Losses: 35
  Win rate: 74.3%
  Compounded return: +33.55%

Do NOT retune rules to force this checksum.
If a fresh implementation does not reproduce it, investigate execution semantics
(entry fill, exit fill, rolling std convention, tolerance interpretation, etc.)
before using the new result as canonical.

This file intentionally preserves the locked strategy and reporting framework so
future AI sessions do not lose the strategy definition again.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class Config:
    timezone: str = "Europe/London"
    bb_period: int = 20
    bb_std: float = 2.0
    bb_tolerance_pct: float = 0.0015
    touch_count: int = 2
    touch_lookback: int = 3
    range_lookback: int = 150
    min_depth_from_top: float = 0.20
    starting_capital: float = 10_000.0


BENCHMARK = {
    "start": "2025-10-07",
    "end": "2026-10-07",
    "trades": 136,
    "wins": 101,
    "losses": 35,
    "win_rate_pct": 74.3,
    "compounded_return_pct": 33.55,
}


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    timestamp_col = None
    for c in ("timestamp_uk", "timestamp_utc", "datetime", "timestamp"):
        if c in df.columns:
            timestamp_col = c
            break
    if timestamp_col is None:
        raise ValueError("No supported timestamp column found.")

    idx = pd.to_datetime(df[timestamp_col], utc=True, errors="coerce")
    df = df.loc[idx.notna()].copy()
    df.index = idx[idx.notna()].dt.tz_convert("Europe/London")

    required = ["open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df.dropna(subset=required).sort_index()


def add_indicators(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    out = df.copy()

    out["bb_mid"] = out["close"].rolling(cfg.bb_period).mean()

    # NOTE:
    # The exact historical benchmark implementation's rolling StdDev convention
    # must be verified before calling a rerun canonical. Pandas default ddof=1.
    out["bb_std"] = out["close"].rolling(cfg.bb_period).std(ddof=1)
    out["bb_lower"] = out["bb_mid"] - cfg.bb_std * out["bb_std"]
    out["bb_upper"] = out["bb_mid"] + cfg.bb_std * out["bb_std"]

    out["range_high_150"] = out["high"].rolling(cfg.range_lookback).max()
    out["range_low_150"] = out["low"].rolling(cfg.range_lookback).min()
    width = out["range_high_150"] - out["range_low_150"]
    out["depth_from_top"] = (out["range_high_150"] - out["close"]) / width

    out["lower_touch"] = out["low"] <= out["bb_lower"] * (1.0 + cfg.bb_tolerance_pct)
    out["touches_last_3"] = (
        out["lower_touch"].astype(int).rolling(cfg.touch_lookback).sum()
    )

    out["entry_signal"] = (
        (out["touches_last_3"] >= cfg.touch_count)
        & (out["depth_from_top"] >= cfg.min_depth_from_top)
    )

    out["upper_exit_touch"] = (
        out["high"] >= out["bb_upper"] * (1.0 - cfg.bb_tolerance_pct)
    )

    return out


def run_reference_backtest(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """
    Reference implementation of the locked rule structure.

    IMPORTANT:
    This is NOT yet declared benchmark-identical until the execution semantics
    reproduce BENCHMARK exactly. It is saved so future sessions have one place
    to inspect and adjust execution semantics without changing the strategy.
    """
    trades = []
    in_position = False
    entry_time: Optional[pd.Timestamp] = None
    entry_price: Optional[float] = None

    for ts, row in df.iterrows():
        if not in_position:
            if bool(row.get("entry_signal", False)):
                in_position = True
                entry_time = ts
                entry_price = float(row["close"])
            continue

        if bool(row.get("upper_exit_touch", False)):
            exit_price = float(row["close"])
            ret = exit_price / float(entry_price) - 1.0
            trades.append(
                {
                    "entry_time_uk": entry_time,
                    "exit_time_uk": ts,
                    "entry_price": float(entry_price),
                    "exit_price": exit_price,
                    "return_pct": ret * 100.0,
                    "holding_hours": (ts - entry_time).total_seconds() / 3600.0,
                    "win": ret > 0,
                }
            )
            in_position = False
            entry_time = None
            entry_price = None

    return pd.DataFrame(trades)


def summary(trades: pd.DataFrame, cfg: Config) -> dict:
    if trades.empty:
        return {}

    rets = trades["return_pct"] / 100.0
    wins = rets[rets > 0]
    losses = rets[rets < 0]

    capital = cfg.starting_capital
    equity = [capital]
    peak = capital
    max_dd = 0.0

    for r in rets:
        capital *= 1.0 + r
        equity.append(capital)
        peak = max(peak, capital)
        max_dd = max(max_dd, (peak - capital) / peak)

    gross_profit = wins.sum()
    gross_loss = -losses.sum()
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

    losing_streak = 0
    max_losing_streak = 0
    for r in rets:
        if r < 0:
            losing_streak += 1
            max_losing_streak = max(max_losing_streak, losing_streak)
        else:
            losing_streak = 0

    return {
        "trades": int(len(trades)),
        "wins": int((rets > 0).sum()),
        "losses": int((rets < 0).sum()),
        "win_rate_pct": float((rets > 0).mean() * 100.0),
        "simple_return_pct": float(rets.sum() * 100.0),
        "compounded_return_pct": float((capital / cfg.starting_capital - 1.0) * 100.0),
        "starting_capital": cfg.starting_capital,
        "ending_capital": capital,
        "net_profit": capital - cfg.starting_capital,
        "profit_factor": None if profit_factor is None else float(profit_factor),
        "max_drawdown_pct": float(max_dd * 100.0),
        "max_losing_streak": int(max_losing_streak),
        "avg_win_pct": float(wins.mean() * 100.0) if len(wins) else None,
        "avg_loss_pct": float(losses.mean() * 100.0) if len(losses) else None,
        "expectancy_pct": float(rets.mean() * 100.0),
        "avg_holding_hours": float(trades["holding_hours"].mean()),
        "median_holding_hours": float(trades["holding_hours"].median()),
        "min_holding_hours": float(trades["holding_hours"].min()),
        "max_holding_hours": float(trades["holding_hours"].max()),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--input",
        default="NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv",
    )
    p.add_argument(
        "--trades-output",
        default="NQ/backtesting/results/rudra_reversal_nq_1h_trades.csv",
    )
    args = p.parse_args()

    cfg = Config()
    df = add_indicators(load_data(Path(args.input)), cfg)
    trades = run_reference_backtest(df, cfg)
    stats = summary(trades, cfg)

    print("RUDRA-REVERSAL NQ 1H")
    print("Locked strategy preserved in code.")
    print()
    for k, v in stats.items():
        print(f"{k}: {v}")

    print()
    print("Historical benchmark target:")
    for k, v in BENCHMARK.items():
        print(f"{k}: {v}")

    out = Path(args.trades_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(out, index=False)
    print(f"trades_csv: {out}")


if __name__ == "__main__":
    main()
