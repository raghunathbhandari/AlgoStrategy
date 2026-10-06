#!/usr/bin/env python3
"""NQ London-session breakout backtest.

Baseline researched on August 2026:
- Source: 1-minute NQ OHLCV, converted to Europe/London
- Resample: 5-minute bars
- Opening range: 08:00-08:30 UK
- Entry window: 08:30-12:00 UK
- Long: first 5m close > range high + buffer
- Short: first 5m close < range low - buffer
- One trade per UK trading day
- Stop distance: 0.5 x opening-range width, bounded by min/max points
- Target: configurable R multiple (default 2R)
- If both stop and target are touched in one bar, stop is assumed first (conservative)
- Remaining trades are closed at the end of the entry window.

Research only. Futures involve substantial risk.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Config:
    month: str = "2026-08"
    timezone: str = "Europe/London"
    range_start: str = "08:00"
    range_end: str = "08:30"
    trade_start: str = "08:30"
    trade_end: str = "12:00"
    breakout_buffer: float = 2.0
    stop_range_fraction: float = 0.50
    min_stop_points: float = 20.0
    max_stop_points: float = 100.0
    reward_risk: float = 2.0


def load_1m(path: Path, timezone: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"datetime", "open", "high", "low", "close", "volume"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    dt = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df = df.loc[dt.notna()].copy()
    df.index = dt[dt.notna()].dt.tz_convert(timezone)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df.sort_index()


def resample_5m(df: pd.DataFrame) -> pd.DataFrame:
    bars = df.resample("5min", label="left", closed="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    )
    return bars.dropna(subset=["open", "high", "low", "close"])


def hhmm_mask(index: pd.DatetimeIndex, start: str, end: str) -> pd.Series:
    hhmm = pd.Series(index.strftime("%H:%M"), index=index)
    return (hhmm >= start) & (hhmm < end)


def backtest(bars: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    bars = bars.loc[bars.index.strftime("%Y-%m") == cfg.month].copy()
    trades: list[dict] = []

    for session_date, day in bars.groupby(bars.index.date):
        rmask = hhmm_mask(day.index, cfg.range_start, cfg.range_end)
        opening = day.loc[rmask.values]
        if opening.empty:
            continue

        range_high = float(opening["high"].max())
        range_low = float(opening["low"].min())
        range_width = range_high - range_low
        if range_width <= 0:
            continue

        risk = min(
            cfg.max_stop_points,
            max(cfg.min_stop_points, range_width * cfg.stop_range_fraction),
        )

        smask = hhmm_mask(day.index, cfg.trade_start, cfg.trade_end)
        scan = day.loc[smask.values]
        if scan.empty:
            continue

        for entry_time, bar in scan.iterrows():
            direction = 0
            if bar["close"] > range_high + cfg.breakout_buffer:
                direction = 1
            elif bar["close"] < range_low - cfg.breakout_buffer:
                direction = -1
            else:
                continue

            side = "LONG" if direction == 1 else "SHORT"
            entry = float(bar["close"])
            stop = entry - direction * risk
            target = entry + direction * risk * cfg.reward_risk

            exit_price = float(scan.iloc[-1]["close"])
            exit_time = scan.index[-1]
            reason = "TIME"

            future = scan.loc[scan.index > entry_time]
            for t, b in future.iterrows():
                hit_stop = b["low"] <= stop if direction == 1 else b["high"] >= stop
                hit_target = b["high"] >= target if direction == 1 else b["low"] <= target

                # Conservative ordering when OHLC cannot tell which came first.
                if hit_stop:
                    exit_price = stop
                    exit_time = t
                    reason = "STOP"
                    break
                if hit_target:
                    exit_price = target
                    exit_time = t
                    reason = "TARGET"
                    break

            pnl_points = direction * (exit_price - entry)
            r_multiple = pnl_points / risk

            trades.append(
                {
                    "date": str(session_date),
                    "side": side,
                    "range_high": range_high,
                    "range_low": range_low,
                    "range_points": range_width,
                    "entry_time_uk": entry_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "exit_time_uk": exit_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "exit": exit_price,
                    "exit_reason": reason,
                    "pnl_points": pnl_points,
                    "r_multiple": r_multiple,
                }
            )
            break  # one trade per day

    return pd.DataFrame(trades)


def summarize(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate_pct": 0.0,
            "total_r": 0.0,
            "avg_r": 0.0,
            "profit_factor": None,
        }

    wins = trades["r_multiple"] > 0
    gross_profit = trades.loc[wins, "r_multiple"].sum()
    gross_loss = -trades.loc[trades["r_multiple"] < 0, "r_multiple"].sum()
    pf = gross_profit / gross_loss if gross_loss > 0 else None

    return {
        "trades": int(len(trades)),
        "wins": int(wins.sum()),
        "losses": int((trades["r_multiple"] < 0).sum()),
        "win_rate_pct": round(float(wins.mean() * 100), 2),
        "total_r": round(float(trades["r_multiple"].sum()), 3),
        "avg_r": round(float(trades["r_multiple"].mean()), 3),
        "profit_factor": round(float(pf), 3) if pf is not None else None,
        "targets": int((trades["exit_reason"] == "TARGET").sum()),
        "stops": int((trades["exit_reason"] == "STOP").sum()),
        "time_exits": int((trades["exit_reason"] == "TIME").sum()),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="NQ/data/NQ_1min_20260401_20260902.csv")
    p.add_argument("--month", default="2026-08")
    p.add_argument("--range-start", default="08:00")
    p.add_argument("--range-end", default="08:30")
    p.add_argument("--trade-start", default="08:30")
    p.add_argument("--trade-end", default="12:00")
    p.add_argument("--buffer", type=float, default=2.0)
    p.add_argument("--rr", type=float, default=2.0)
    p.add_argument("--output", default="NQ/backtesting/results/london_breakout_trades.csv")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = Config(
        month=args.month,
        range_start=args.range_start,
        range_end=args.range_end,
        trade_start=args.trade_start,
        trade_end=args.trade_end,
        breakout_buffer=args.buffer,
        reward_risk=args.rr,
    )

    df = load_1m(Path(args.input), cfg.timezone)
    bars = resample_5m(df)
    trades = backtest(bars, cfg)
    summary = summarize(trades)

    print("NQ LONDON SESSION BREAKOUT")
    print(cfg)
    for k, v in summary.items():
        print(f"{k}: {v}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(out, index=False)
    print(f"trades_csv: {out}")


if __name__ == "__main__":
    main()
