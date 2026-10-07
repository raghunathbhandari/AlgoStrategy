#!/usr/bin/env python3
from pathlib import Path
import zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
CHUNK_DIR = ROOT / "AI_Chunks" / "NQ" / "data" / "external" / "Dataset_NQ_1min_2022_2025"
OUT_DIR = ROOT / "NQ" / "reports" / "monthly_bb_2025"
OUT_DIR.mkdir(parents=True, exist_ok=True)

frames = []
for n in range(71, 106):
    p = CHUNK_DIR / f"Dataset_NQ_1min_2022_2025_part_{n:04d}.csv"
    if p.exists():
        df = pd.read_csv(p)
        frames.append(df)
        print(f"loaded {p.name} rows={len(df):,}")

if not frames:
    raise FileNotFoundError(f"No chunk files found in {CHUNK_DIR}")

raw = pd.concat(frames, ignore_index=True)
raw.columns = [c.strip().lower() for c in raw.columns]
raw = raw.rename(columns={
    raw.columns[0]: "timestamp",
    raw.columns[1]: "open",
    raw.columns[2]: "high",
    raw.columns[3]: "low",
    raw.columns[4]: "close",
    raw.columns[5]: "volume",
})

raw["timestamp"] = pd.to_datetime(raw["timestamp"], format="%m/%d/%Y %H:%M", errors="coerce")
raw = raw.dropna(subset=["timestamp"]).copy()
raw = raw[(raw["timestamp"] >= "2025-01-01") & (raw["timestamp"] < "2026-01-01")].copy()

hourly = (
    raw.set_index("timestamp")
       .sort_index()
       .resample("1h")
       .agg({
           "open": "first",
           "high": "max",
           "low": "min",
           "close": "last",
           "volume": "sum",
       })
       .dropna(subset=["open", "high", "low", "close"])
       .reset_index()
)

# Bollinger Bands: 20, 2.0, SMA, close
hourly["bb_mid"] = hourly["close"].rolling(20).mean()
hourly["bb_std"] = hourly["close"].rolling(20).std(ddof=0)
hourly["bb_upper"] = hourly["bb_mid"] + 2 * hourly["bb_std"]
hourly["bb_lower"] = hourly["bb_mid"] - 2 * hourly["bb_std"]

# 150-bar swing range
hourly["high150"] = hourly["high"].rolling(150).max()
hourly["low150"] = hourly["low"].rolling(150).min()

NEAR = 0.0015  # Allow 2: 0.15% counts as BB near-touch

def near_lower(row):
    if pd.isna(row["bb_lower"]):
        return False
    return (row["low"] <= row["bb_lower"]) or ((row["low"] - row["bb_lower"]) / row["bb_lower"] <= NEAR)

def near_upper(row):
    if pd.isna(row["bb_upper"]):
        return False
    return (row["high"] >= row["bb_upper"]) or ((row["bb_upper"] - row["high"]) / row["bb_upper"] <= NEAR)

# Build Rudra-Reversal signals/trades
hourly["near_lower"] = hourly.apply(near_lower, axis=1)
hourly["near_upper"] = hourly.apply(near_upper, axis=1)

signals = []
for i in range(149, len(hourly)):
    r = hourly.iloc[i]
    if not r["near_lower"]:
        continue

    # F1: candle must not touch MA20
    f1 = not (r["high"] >= r["bb_mid"] and r["low"] <= r["bb_mid"])

    # F2: at least 10% down through 150-bar swing range from the top
    swing_range = r["high150"] - r["low150"]
    if not (swing_range > 0):
        continue
    swing_down = (r["high150"] - r["low"]) / swing_range
    f2 = swing_down >= 0.10

    # F3: latest 3 candles, at least 2 touch/near-touch lower BB
    start = max(0, i - 2)
    near_count = int(hourly.iloc[start:i+1]["near_lower"].sum())
    f3 = near_count >= 2

    if f1 and f2 and f3:
        signals.append({
            "i": i,
            "entry_time": r["timestamp"],
            "entry_price": r["close"],
            "clean": bool(r["open"] < r["bb_lower"] and r["close"] < r["bb_lower"]),
            "near_count": near_count,
            "swing_down_pct": swing_down * 100.0,
        })

# One position at a time; exit on upper BB touch/near-touch
trades = []
next_allowed = 0

for s in signals:
    if s["i"] < next_allowed:
        continue

    exit_info = None
    for j in range(s["i"] + 1, len(hourly)):
        r = hourly.iloc[j]
        if r["near_upper"]:
            exact_touch = r["high"] >= r["bb_upper"]
            exit_price = r["bb_upper"] if exact_touch else r["high"]
            exit_info = {
                "j": j,
                "exit_time": r["timestamp"],
                "exit_price": exit_price,
                "return_pct": (exit_price / s["entry_price"] - 1.0) * 100.0,
                "exact_touch": exact_touch,
            }
            break

    trades.append({**s, **(exit_info or {})})
    next_allowed = (exit_info["j"] + 1) if exit_info else len(hourly)

trade_df = pd.DataFrame(trades)
trade_csv = OUT_DIR / "NQ_2025_rudra_reversal_trades.csv"
trade_df.to_csv(trade_csv, index=False)

saved = []
manifest_rows = []

for month in range(1, 13):
    month_start = pd.Timestamp(year=2025, month=month, day=1)
    month_end = pd.Timestamp(year=2026, month=1, day=1) if month == 12 else pd.Timestamp(year=2025, month=month+1, day=1)

    mdf = hourly[(hourly["timestamp"] >= month_start) & (hourly["timestamp"] < month_end)].copy()
    if mdf.empty:
        continue

    x = np.arange(len(mdf))
    idx_map = {ts: idx for idx, ts in enumerate(mdf["timestamp"])}

    fig, ax = plt.subplots(figsize=(16, 8))

    # Candles
    ax.vlines(x, mdf["low"], mdf["high"], linewidth=0.6)
    body = mdf["close"] - mdf["open"]
    bottom = np.minimum(mdf["open"], mdf["close"])
    height = np.abs(body)
    height = np.where(height > 0, height, 0.5)
    ax.bar(x, height, bottom=bottom, width=0.65)

    # Bollinger Bands
    ax.plot(x, mdf["bb_upper"], linewidth=1.2, label="BB Upper")
    ax.plot(x, mdf["bb_mid"], linewidth=1.2, label="BB Mid")
    ax.plot(x, mdf["bb_lower"], linewidth=1.2, label="BB Lower")

    # Trade markers
    month_trades = [t for t in trades if month_start <= t["entry_time"] < month_end]

    for n, t in enumerate(month_trades, start=1):
        ex = idx_map.get(t["entry_time"])
        if ex is not None:
            ax.scatter(ex, t["entry_price"], marker="^", s=90, zorder=6)
            ax.annotate(
                f"T{n} BUY",
                (ex, t["entry_price"]),
                xytext=(0, -22),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                fontweight="bold",
            )

        if "exit_time" in t and pd.notna(t.get("exit_time")) and month_start <= t["exit_time"] < month_end:
            xx = idx_map.get(t["exit_time"])
            if xx is not None:
                ax.scatter(xx, t["exit_price"], marker="v", s=90, zorder=6)
                ax.annotate(
                    f"T{n} EXIT\n{t['return_pct']:+.2f}%",
                    (xx, t["exit_price"]),
                    xytext=(0, 12),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    fontweight="bold",
                )

    tick_count = min(12, len(mdf))
    tick_idx = np.linspace(0, len(mdf)-1, tick_count, dtype=int)
    tick_labels = mdf.iloc[tick_idx]["timestamp"].dt.strftime("%d-%b")
    ax.set_xticks(tick_idx)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right")

    ax.set_title(f"NQ 1H Rudra-Reversal + Bollinger Bands (20, 2) — 2025-{month:02d}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True, alpha=0.25)
    plt.tight_layout()

    out_file = OUT_DIR / f"NQ_2025_{month:02d}_1H_RUDRA_REVERSAL_BB20_STD2.png"
    fig.savefig(out_file, dpi=180, bbox_inches="tight")
    plt.close(fig)

    saved.append(out_file)
    manifest_rows.append({
        "month": f"2025-{month:02d}",
        "bars": len(mdf),
        "trades": len(month_trades),
        "file": str(out_file),
    })

manifest = OUT_DIR / "NQ_2025_monthly_chart_manifest.csv"
pd.DataFrame(manifest_rows).to_csv(manifest, index=False)

zip_path = OUT_DIR / "NQ_2025_12_month_RUDRA_REVERSAL_charts.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for f in saved:
        zf.write(f, arcname=f.name)
    zf.write(manifest, arcname=manifest.name)
    zf.write(trade_csv, arcname=trade_csv.name)

print("DONE")
print(f"Charts created: {len(saved)}")
print(f"Trades found  : {len(trades)}")
print(f"Output dir    : {OUT_DIR}")
print(f"ZIP file      : {zip_path}")
print(f"Trade CSV     : {trade_csv}")
print(f"Manifest      : {manifest}")
