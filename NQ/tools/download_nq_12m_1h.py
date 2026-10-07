#!/usr/bin/env python3
from pathlib import Path
import argparse, time
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "NQ" / "data" / "recent"

def download(symbol, start, end):
    s = pd.Timestamp(start)
    e = pd.Timestamp(end) + pd.Timedelta(days=1)
    cur = s
    parts = []
    while cur < e:
        nxt = min(cur + pd.Timedelta(days=30), e)
        print(f"DOWNLOAD | {symbol} | 1h | {cur.date()} -> {(nxt-pd.Timedelta(days=1)).date()}")
        df = yf.download(
            symbol,
            start=cur.strftime("%Y-%m-%d"),
            end=nxt.strftime("%Y-%m-%d"),
            interval="1h",
            prepost=True,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            df = df.reset_index()
            dt = "Datetime" if "Datetime" in df.columns else df.columns[0]
            df = df.rename(columns={dt:"timestamp","Open":"open","High":"high","Low":"low","Close":"close","Adj Close":"adj_close","Volume":"volume"})
            parts.append(df)
            print(f"  rows={len(df):,}")
        else:
            print("  rows=0")
        cur = nxt
        time.sleep(0.8)

    if not parts:
        raise RuntimeError("No NQ data returned")

    x = pd.concat(parts, ignore_index=True)
    x["timestamp"] = pd.to_datetime(x["timestamp"], utc=True, errors="coerce")
    x = x.dropna(subset=["timestamp"]).drop_duplicates("timestamp").sort_values("timestamp")

    et = x["timestamp"].dt.tz_convert("America/New_York")
    mask = (et.dt.date >= s.date()) & (et.dt.date <= pd.Timestamp(end).date())
    x = x.loc[mask].copy()

    x["timestamp_et"] = x["timestamp"].dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d %H:%M:%S%z")
    x["timestamp_utc"] = x["timestamp"].dt.tz_convert("UTC").dt.strftime("%Y-%m-%d %H:%M:%S%z")
    x["timestamp_uk"] = x["timestamp"].dt.tz_convert("Europe/London").dt.strftime("%Y-%m-%d %H:%M:%S%z")

    cols = ["timestamp_et","timestamp_utc","timestamp_uk","open","high","low","close"]
    for c in ["adj_close","volume"]:
        if c in x.columns:
            cols.append(c)
    return x[cols]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="NQ=F")
    p.add_argument("--start", default="2025-10-07")
    p.add_argument("--end", default="2026-10-07")
    a = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"NQ_1h_12m_{a.start}_{a.end}.csv"
    df = download(a.symbol, a.start, a.end)
    df.to_csv(out, index=False)

    print("\nDONE")
    print(f"Rows     : {len(df):,}")
    print(f"CSV      : {out}")
    print(f"UK range : {df['timestamp_uk'].iloc[0]} -> {df['timestamp_uk'].iloc[-1]}")
    print("Session  : prepost=True (overnight/premarket included where Yahoo provides it)")

if __name__ == "__main__":
    main()
