#!/usr/bin/env python3
"""Canonical Rudra-Reversal NQ 1H backtest.

LOCKED RULES
- NQ, 1H, LONG only
- Bollinger Bands: SMA(20), 2.0 standard deviations
- Historical engine uses population StdDev: pandas rolling std(ddof=0)
- Lower-BB setup: current candle must touch/near-touch Lower BB, and at least
  2 of the last 3 candles must touch/near-touch Lower BB
- Near-touch tolerance: 0.15% above Lower BB
- 150-bar range: highest HIGH and lowest LOW, including signal candle
- Depth: (150-bar high - SIGNAL CLOSE) / (150-bar high - 150-bar low)
- Minimum depth: 20%
- No MA20-touch filter
- No RSI filter
- Entry fill: signal candle CLOSE
- One position at a time
- Exit: first later candle that touches Upper BB or comes within 0.15% below it
- Exit fill: exact Upper-BB value when candle HIGH reaches/exceeds Upper BB;
  otherwise candle HIGH for a near-touch exit
- Full available overnight/premarket + regular session
- UK timestamps in outputs
- Final open trade at end of dataset is preserved separately and excluded from
  closed-trade benchmark statistics.

Historical checksum for 2025-10-07 -> 2026-10-07:
136 closed trades / 101 wins / 35 losses / 74.2647% / +33.5512% compounded.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

BB_PERIOD = 20
BB_STD = 2.0
NEAR = 0.0015
RANGE_LOOKBACK = 150
MIN_DEPTH = 0.20
STARTING_CAPITAL = 10_000.0

EXPECTED = {
    "trades": 136,
    "wins": 101,
    "losses": 35,
    "win_rate_pct": 74.26470588235294,
    "compounded_return_pct": 33.55123290244009,
}


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"timestamp_uk", "open", "high", "low", "close"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    ts = pd.to_datetime(df["timestamp_uk"], utc=True, errors="coerce")
    df = df.loc[ts.notna()].copy()
    df.index = ts[ts.notna()].dt.tz_convert("Europe/London")

    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df.dropna(subset=["open", "high", "low", "close"]).sort_index()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bb_mid"] = out["close"].rolling(BB_PERIOD).mean()
    out["bb_std"] = out["close"].rolling(BB_PERIOD).std(ddof=0)
    out["bb_upper"] = out["bb_mid"] + BB_STD * out["bb_std"]
    out["bb_lower"] = out["bb_mid"] - BB_STD * out["bb_std"]

    out["high150"] = out["high"].rolling(RANGE_LOOKBACK).max()
    out["low150"] = out["low"].rolling(RANGE_LOOKBACK).min()
    width = out["high150"] - out["low150"]
    out["depth_from_top"] = (out["high150"] - out["close"]) / width

    out["near_lower"] = (
        (out["low"] <= out["bb_lower"])
        | (((out["low"] - out["bb_lower"]) / out["bb_lower"]) <= NEAR)
    )
    out["near_upper"] = (
        (out["high"] >= out["bb_upper"])
        | (((out["bb_upper"] - out["high"]) / out["bb_upper"]) <= NEAR)
    )
    out["lower_touch_count_3"] = out["near_lower"].astype(int).rolling(3).sum()

    out["entry_signal"] = (
        out["near_lower"]
        & (out["lower_touch_count_3"] >= 2)
        & (out["depth_from_top"] >= MIN_DEPTH)
    )
    return out


def build_trades(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    signals = []
    for i in range(RANGE_LOOKBACK - 1, len(df)):
        r = df.iloc[i]
        if not bool(r["entry_signal"]):
            continue
        signals.append({
            "i": i,
            "entry_time_uk": df.index[i],
            "entry_price": float(r["close"]),
            "lower_bb_touch_count": int(r["lower_touch_count_3"]),
            "signal_depth_pct": float(r["depth_from_top"] * 100.0),
            "range_high_150": float(r["high150"]),
            "range_low_150": float(r["low150"]),
            "entry_bb_lower": float(r["bb_lower"]),
            "entry_bb_mid": float(r["bb_mid"]),
            "entry_bb_upper": float(r["bb_upper"]),
        })

    closed = []
    open_rows = []
    next_allowed = 0

    for s in signals:
        if s["i"] < next_allowed:
            continue

        exit_info = None
        for j in range(s["i"] + 1, len(df)):
            r = df.iloc[j]
            if bool(r["near_upper"]):
                exact_touch = bool(r["high"] >= r["bb_upper"])
                exit_price = float(r["bb_upper"] if exact_touch else r["high"])
                exit_info = {
                    "j": j,
                    "exit_time_uk": df.index[j],
                    "exit_price": exit_price,
                    "exit_bb_upper": float(r["bb_upper"]),
                    "exit_high": float(r["high"]),
                    "exit_exact_touch": exact_touch,
                    "return_pct": (exit_price / s["entry_price"] - 1.0) * 100.0,
                    "holding_bars": j - s["i"],
                    "holding_hours": (
                        (df.index[j] - s["entry_time_uk"]).total_seconds() / 3600.0
                    ),
                }
                break

        if exit_info is None:
            open_rows.append({k: v for k, v in s.items() if k != "i"})
            next_allowed = len(df)
        else:
            row = {k: v for k, v in s.items() if k != "i"}
            row.update({k: v for k, v in exit_info.items() if k != "j"})
            row["result"] = "WIN" if row["return_pct"] > 0 else "LOSS"
            closed.append(row)
            next_allowed = exit_info["j"] + 1

    trades = pd.DataFrame(closed)
    if not trades.empty:
        trades.insert(0, "trade_no", range(1, len(trades) + 1))
    return trades, pd.DataFrame(open_rows)


def summarize(trades: pd.DataFrame) -> dict:
    r = trades["return_pct"] / 100.0
    wins = r[r > 0]
    losses = r[r < 0]

    capital = STARTING_CAPITAL
    peak = capital
    max_dd = 0.0
    max_dd_dollars = 0.0

    for x in r:
        capital *= 1.0 + x
        peak = max(peak, capital)
        dd = (peak - capital) / peak
        if dd > max_dd:
            max_dd = dd
            max_dd_dollars = peak - capital

    losing_streak = 0
    max_losing_streak = 0
    for x in r:
        if x < 0:
            losing_streak += 1
            max_losing_streak = max(max_losing_streak, losing_streak)
        else:
            losing_streak = 0

    gross_profit = float(wins.sum())
    gross_loss = float(-losses.sum())

    return {
        "trades": int(len(trades)),
        "wins": int((r > 0).sum()),
        "losses": int((r < 0).sum()),
        "win_rate_pct": float((r > 0).mean() * 100.0),
        "simple_return_pct": float(r.sum() * 100.0),
        "compounded_return_pct": float((capital / STARTING_CAPITAL - 1.0) * 100.0),
        "starting_capital": STARTING_CAPITAL,
        "ending_capital": float(capital),
        "net_profit": float(capital - STARTING_CAPITAL),
        "profit_factor": float(gross_profit / gross_loss),
        "max_drawdown_pct": float(max_dd * 100.0),
        "max_drawdown_dollars": float(max_dd_dollars),
        "max_losing_streak": int(max_losing_streak),
        "avg_win_pct": float(wins.mean() * 100.0),
        "avg_loss_pct": float(losses.mean() * 100.0),
        "payoff_ratio": float(wins.mean() / abs(losses.mean())),
        "expectancy_pct": float(r.mean() * 100.0),
        "avg_holding_hours": float(trades["holding_hours"].mean()),
        "median_holding_hours": float(trades["holding_hours"].median()),
        "min_holding_hours": float(trades["holding_hours"].min()),
        "max_holding_hours": float(trades["holding_hours"].max()),
    }


def validate(stats: dict) -> None:
    assert stats["trades"] == EXPECTED["trades"], stats
    assert stats["wins"] == EXPECTED["wins"], stats
    assert stats["losses"] == EXPECTED["losses"], stats
    assert abs(stats["win_rate_pct"] - EXPECTED["win_rate_pct"]) < 1e-9, stats
    assert abs(stats["compounded_return_pct"] - EXPECTED["compounded_return_pct"]) < 1e-9, stats


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
    p.add_argument(
        "--open-output",
        default="NQ/backtesting/results/rudra_reversal_nq_1h_open_trade.csv",
    )
    args = p.parse_args()

    df = add_indicators(load_data(Path(args.input)))
    trades, open_trade = build_trades(df)
    stats = summarize(trades)
    validate(stats)

    out = Path(args.trades_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(out, index=False)

    open_out = Path(args.open_output)
    open_out.parent.mkdir(parents=True, exist_ok=True)
    open_trade.to_csv(open_out, index=False)

    print("RUDRA-REVERSAL NQ 1H | CHECKSUM PASS")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"closed_trades_csv: {out}")
    print(f"open_trade_csv: {open_out}")


if __name__ == "__main__":
    main()
