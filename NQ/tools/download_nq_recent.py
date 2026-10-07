#!/usr/bin/env python3
"""
Download recent NQ futures intraday data for research/backtesting.

Repository: AlgoStrategy only
Source: Yahoo Finance (NQ=F)
Default range: 2026-09-07 through 2026-10-07 inclusive
Downloads 5-minute bars and builds 1-hour bars.

This script does NOT touch the ASJR production repository or pipeline.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import time

import pandas as pd
import yfinance as yf


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "NQ" / "data" / "recent"


def download_5m(symbol: str, start: str, end_inclusive: str) -> pd.DataFrame:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end_inclusive) + pd.Timedelta(days=1)  # yfinance end is exclusive

    pieces = []
    cursor = start_ts

    # Short chunks make Yahoo intraday downloads more reliable.
    while cursor < end_ts:
        chunk_end = min(cursor + pd.Timedelta(days=7), end_ts)
        print(f"DOWNLOAD | {symbol} | 5m | {cursor.date()} -> {(chunk_end - pd.Timedelta(days=1)).date()}")

        df = yf.download(
            symbol,
            start=cursor.strftime("%Y-%m-%d"),
            end=chunk_end.strftime("%Y-%m-%d"),
            interval="5m",
            auto_adjust=False,
            prepost=True,
            progress=False,
            threads=False,
        )

        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                # yfinance can return (Price, Ticker) columns.
                df.columns = [c[0] for c in df.columns]

            df = df.reset_index()
            dt_col = "Datetime" if "Datetime" in df.columns else df.columns[0]
            df = df.rename(columns={dt_col: "timestamp"})

            keep = [c for c in ["timestamp", "Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
            df = df[keep]
            pieces.append(df)
            print(f"  rows={len(df):,}")
        else:
            print("  rows=0")

        cursor = chunk_end
        time.sleep(1.0)

    if not pieces:
        raise RuntimeError("No NQ data returned by Yahoo Finance.")

    out = pd.concat(pieces, ignore_index=True)
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    out = out.dropna(subset=["timestamp"])
    out = out.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    rename = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
    }
    out = out.rename(columns=rename)

    # Keep only requested inclusive date range in New York time.
    ny = out["timestamp"].dt.tz_convert("America/New_York")
    mask = (ny.dt.date >= start_ts.date()) & (ny.dt.date <= pd.Timestamp(end_inclusive).date())
    out = out.loc[mask].copy()

    return out


def build_1h(df5: pd.DataFrame) -> pd.DataFrame:
    x = df5.copy()
    x = x.set_index("timestamp")

    # Resample in New York time so bars align to ET clock hours.
    x.index = x.index.tz_convert("America/New_York")

    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

    h = x.resample("1h", label="left", closed="left").agg(agg)
    h = h.dropna(subset=["open", "high", "low", "close"])
    h = h.reset_index()

    # Save explicit ET and UTC timestamps for unambiguous backtesting.
    h["timestamp_et"] = h["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S%z")
    h["timestamp_utc"] = h["timestamp"].dt.tz_convert("UTC").dt.strftime("%Y-%m-%d %H:%M:%S%z")
    h = h.drop(columns=["timestamp"])

    cols = ["timestamp_et", "timestamp_utc", "open", "high", "low", "close", "volume"]
    return h[cols]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="NQ=F")
    p.add_argument("--start", default="2026-09-07")
    p.add_argument("--end", default="2026-10-07")
    args = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tag = f"{args.start}_{args.end}"
    file_5m = OUT_DIR / f"NQ_5m_{tag}.csv"
    file_1h = OUT_DIR / f"NQ_1h_{tag}.csv"

    df5 = download_5m(args.symbol, args.start, args.end)
    df1h = build_1h(df5)

    df5.to_csv(file_5m, index=False)
    df1h.to_csv(file_1h, index=False)

    print()
    print("=" * 90)
    print("DONE")
    print(f"5m rows : {len(df5):,}")
    print(f"1h rows : {len(df1h):,}")
    print(f"5m CSV  : {file_5m}")
    print(f"1h CSV  : {file_1h}")
    if not df5.empty:
        print(f"5m range: {df5['timestamp'].min()} -> {df5['timestamp'].max()}")
    if not df1h.empty:
        print(f"1h range: {df1h['timestamp_et'].iloc[0]} -> {df1h['timestamp_et'].iloc[-1]}")
    print("=" * 90)


if __name__ == "__main__":
    main()
