#!/usr/bin/env python3
"""Research only: causal 60-bar confirmed-pivot swing box for Rudra Reversal NQ 1H.
Does not modify canonical signals or files. Run from repository root.
"""
from pathlib import Path
import pandas as pd
from rudra_reversal_nq_1h import load_data, add_indicators, build_trades

SOURCE = Path("NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv")
OUT = Path("NQ/backtesting/results/sep_2026_swing60_audit.csv")
LOOKBACK = 60
WING = 3


def box_at(df, i):
    # Pivot j is known at candle i only when j+WING<=i.
    # The entire left/right pivot neighborhood must lie within the 60-bar window.
    begin = max(0, i - LOOKBACK + 1)
    highs, lows = [], []
    for j in range(begin + WING, i - WING + 1):
        window = df.iloc[j-WING:j+WING+1]
        if df["high"].iloc[j] > window["high"].drop(df.index[j]).max():
            highs.append((j, float(df["high"].iloc[j])))
        if df["low"].iloc[j] < window["low"].drop(df.index[j]).min():
            lows.append((j, float(df["low"].iloc[j])))
    if not highs or not lows:
        return None
    high = max(v for _, v in highs)
    low = min(v for _, v in lows)
    if high <= low:
        return None
    pct = 100 * (float(df["close"].iloc[i]) - low)/(high-low)
    return high, low, pct, len(highs), len(lows)


def run():
    df = add_indicators(load_data(SOURCE))
    baseline, _ = build_trades(df)
    sep = baseline[baseline["entry_time_uk"].dt.strftime("%Y-%m") == "2026-09"]
    rows = []
    for _, trade in sep.iterrows():
        i = df.index.get_loc(trade["entry_time_uk"])
        result = box_at(df, i)
        if result is None:
            rows.append({"entry_uk":str(trade["entry_time_uk"]), "decision":"UNDEFINED"})
            continue
        high, low, pct, nh, nl = result
        # Out-of-range is NOT automatically GOOD; it requires independent treatment.
        status = "BAD_CANDIDATE" if 50 < pct <= 100 else ("GOOD_CANDIDATE" if 0 <= pct <= 50 else "OUTSIDE_BOX")
        rows.append({"entry_uk":str(trade["entry_time_uk"]),
                     "swing_high":high, "swing_low":low,
                     "midpoint":(high+low)/2,"position_pct":pct,
                     "confirmed_highs":nh, "confirmed_lows":nl,
                     "original_return_pct":trade["return_pct"],
                     "decision":status})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT,index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print("Audit only; no trades blocked, and no new P/L claimed.")


if __name__ == "__main__":
    run()
