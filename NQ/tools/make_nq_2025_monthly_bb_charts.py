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
       .resample("1H")
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

hourly["bb_mid"] = hourly["close"].rolling(20).mean()
hourly["bb_std"] = hourly["close"].rolling(20).std(ddof=0)
hourly["bb_upper"] = hourly["bb_mid"] + 2 * hourly["bb_std"]
hourly["bb_lower"] = hourly["bb_mid"] - 2 * hourly["bb_std"]

saved = []
manifest_rows = []

for month in range(1, 13):
    month_start = pd.Timestamp(year=2025, month=month, day=1)
    month_end = pd.Timestamp(year=2026, month=1, day=1) if month == 12 else pd.Timestamp(year=2025, month=month+1, day=1)

    mdf = hourly[(hourly["timestamp"] >= month_start) & (hourly["timestamp"] < month_end)].copy()
    if mdf.empty:
        continue

    x = np.arange(len(mdf))
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.vlines(x, mdf["low"], mdf["high"], linewidth=0.6)

    body = mdf["close"] - mdf["open"]
    bottom = np.minimum(mdf["open"], mdf["close"])
    height = np.abs(body)
    height = np.where(height > 0, height, 0.5)
    ax.bar(x, height, bottom=bottom, width=0.65)

    ax.plot(x, mdf["bb_upper"], linewidth=1.2, label="BB Upper")
    ax.plot(x, mdf["bb_mid"], linewidth=1.2, label="BB Mid")
    ax.plot(x, mdf["bb_lower"], linewidth=1.2, label="BB Lower")

    tick_count = min(10, len(mdf))
    tick_idx = np.linspace(0, len(mdf)-1, tick_count, dtype=int)
    tick_labels = mdf.iloc[tick_idx]["timestamp"].dt.strftime("%d-%b")
    ax.set_xticks(tick_idx)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right")

    ax.set_title(f"NQ 1H Candles + Bollinger Bands (20, 2) — 2025-{month:02d}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True, alpha=0.25)
    plt.tight_layout()

    out_file = OUT_DIR / f"NQ_2025_{month:02d}_1H_BB20_STD2.png"
    fig.savefig(out_file, dpi=180, bbox_inches="tight")
    plt.close(fig)

    saved.append(out_file)
    manifest_rows.append({"month": f"2025-{month:02d}", "bars": len(mdf), "file": str(out_file)})

manifest = OUT_DIR / "NQ_2025_monthly_chart_manifest.csv"
pd.DataFrame(manifest_rows).to_csv(manifest, index=False)

zip_path = OUT_DIR / "NQ_2025_12_month_BB_candle_charts.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for f in saved:
        zf.write(f, arcname=f.name)
    zf.write(manifest, arcname=manifest.name)

print("DONE")
print(f"Charts created: {len(saved)}")
print(f"Output dir   : {OUT_DIR}")
print(f"ZIP file     : {zip_path}")
print(f"Manifest     : {manifest}")
