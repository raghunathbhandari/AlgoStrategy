from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data" / "NQ" / "Dataset_NQ_1min_2022_2025.csv"


@dataclass
class Config:
    # Source data timestamps are expected in US/Eastern unless tz-aware.
    # London session range is converted through Europe/London.
    london_range_start: str = "07:00"
    london_range_end: str = "08:00"
    trade_start: str = "08:00"
    trade_end: str = "11:00"
    rr: float = 2.0
    stop_buffer_points: float = 0.0
    one_trade_per_day: bool = True


def load_nq_1m(path: Path = DEFAULT_DATA) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "datetime" in df.columns:
        dt = pd.to_datetime(df["datetime"])
    elif "date" in df.columns and "time" in df.columns:
        dt = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))
    elif "timestamp_et" in df.columns:
        dt = pd.to_datetime(df["timestamp_et"])
    elif "timestamp" in df.columns:
        dt = pd.to_datetime(df["timestamp"])
    else:
        dt = pd.to_datetime(df.iloc[:, 0])

    if dt.dt.tz is None:
        dt = dt.dt.tz_localize("US/Eastern", ambiguous="infer", nonexistent="shift_forward")
    else:
        dt = dt.dt.tz_convert("US/Eastern")

    df["datetime"] = dt

    need = ["open", "high", "low", "close", "volume"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df[["datetime", *need]].sort_values("datetime").reset_index(drop=True)


def resample_5m(df: pd.DataFrame) -> pd.DataFrame:
    x = df.set_index("datetime")
    out = x.resample("5min", label="left", closed="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).dropna().reset_index()
    out["london_time"] = out["datetime"].dt.tz_convert("Europe/London")
    out["london_date"] = out["london_time"].dt.date
    return out


def backtest(df5: pd.DataFrame, cfg: Config = Config()) -> pd.DataFrame:
    trades = []

    for day, d in df5.groupby("london_date", sort=True):
        t = d["london_time"].dt.strftime("%H:%M")
        rng = d[(t >= cfg.london_range_start) & (t < cfg.london_range_end)]
        trade = d[(t >= cfg.trade_start) & (t < cfg.trade_end)]
        if rng.empty or trade.empty:
            continue

        rh = float(rng["high"].max())
        rl = float(rng["low"].min())
        width = rh - rl
        if width <= 0:
            continue

        active = None

        for row in trade.itertuples(index=False):
            if active is None:
                # Baseline v1: first 5m close outside the London opening range.
                if row.close > rh:
                    entry = row.close
                    stop = rl - cfg.stop_buffer_points
                    risk = entry - stop
                    if risk <= 0:
                        continue
                    active = {
                        "date": day,
                        "side": "LONG",
                        "entry_time": row.london_time,
                        "entry": entry,
                        "stop": stop,
                        "target": entry + cfg.rr * risk,
                        "range_high": rh,
                        "range_low": rl,
                    }
                elif row.close < rl:
                    entry = row.close
                    stop = rh + cfg.stop_buffer_points
                    risk = stop - entry
                    if risk <= 0:
                        continue
                    active = {
                        "date": day,
                        "side": "SHORT",
                        "entry_time": row.london_time,
                        "entry": entry,
                        "stop": stop,
                        "target": entry - cfg.rr * risk,
                        "range_high": rh,
                        "range_low": rl,
                    }
                continue

            if active["side"] == "LONG":
                stop_hit = row.low <= active["stop"]
                target_hit = row.high >= active["target"]
            else:
                stop_hit = row.high >= active["stop"]
                target_hit = row.low <= active["target"]

            # Conservative same-bar assumption: stop wins ties.
            if stop_hit or target_hit:
                if stop_hit:
                    exit_price, result_r, reason = active["stop"], -1.0, "SL"
                else:
                    exit_price, result_r, reason = active["target"], cfg.rr, "TP"

                trades.append({
                    **active,
                    "exit_time": row.london_time,
                    "exit": exit_price,
                    "result_r": result_r,
                    "exit_reason": reason,
                    "range_points": width,
                })
                active = None
                if cfg.one_trade_per_day:
                    break

        if active is not None:
            row = trade.iloc[-1]
            pnl = (row["close"] - active["entry"]) if active["side"] == "LONG" else (active["entry"] - row["close"])
            risk = abs(active["entry"] - active["stop"])
            trades.append({
                **active,
                "exit_time": row["london_time"],
                "exit": row["close"],
                "result_r": pnl / risk if risk else 0.0,
                "exit_reason": "TIME",
                "range_points": width,
            })

    return pd.DataFrame(trades)


def summary(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {"trades": 0}

    wins = (trades["result_r"] > 0).sum()
    return {
        "trades": int(len(trades)),
        "win_rate_pct": round(100 * wins / len(trades), 2),
        "net_r": round(float(trades["result_r"].sum()), 2),
        "avg_r": round(float(trades["result_r"].mean()), 3),
        "profit_factor_r": round(
            float(trades.loc[trades.result_r > 0, "result_r"].sum() /
                  abs(trades.loc[trades.result_r < 0, "result_r"].sum()))
            if (trades["result_r"] < 0).any() else float("inf"),
            3,
        ),
    }


if __name__ == "__main__":
    cfg = Config()
    one = load_nq_1m()
    five = resample_5m(one)
    trades = backtest(five, cfg)
    print(summary(trades))
    out = Path(__file__).resolve().parents[1] / "results"
    out.mkdir(exist_ok=True)
    trades.to_csv(out / "nq_london_session_breakout_v1_trades.csv", index=False)
