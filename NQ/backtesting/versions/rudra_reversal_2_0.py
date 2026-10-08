#!/usr/bin/env python3
"""Rudra-Reversal-2.0 EXPERIMENTAL (NQ 1H; Filters 5 + 6).
Never edits v1.0 files. Recomputes trades after suppressing entry signals.
Run from AlgoStrategy root: python3 NQ/backtesting/versions/rudra_reversal_2_0.py
"""
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rudra_reversal_nq_1h import load_data, add_indicators, build_trades

SOURCE = Path("NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv")
DIR = Path("NQ/backtesting/results/rudra_reversal_2_0")
WING, LOOKBACK = 3, 60

def pivot_box(df, i):
    """Only pivots fully confirmed by the signal candle; 60-bar window."""
    start = max(0, i - LOOKBACK + 1)
    hi, lo = [], []
    for j in range(start + WING, i - WING + 1):
        item = df.iloc[j]
        neighbors = df.iloc[j-WING:j+WING+1]
        if item["high"] > neighbors.drop(df.index[j])["high"].max():
            hi.append(float(item["high"]))
        if item["low"] < neighbors.drop(df.index[j])["low"].min():
            lo.append(float(item["low"]))
    if not hi or not lo: return None
    top, bottom = max(hi), min(lo)
    if top <= bottom: return None
    return top, bottom, 100 * (float(df.iloc[i]["close"])-bottom)/(top-bottom)

def main():
    df = add_indicators(load_data(SOURCE))
    df["bbw_pct"] = 100*(df["bb_upper"]-df["bb_lower"])/df["bb_mid"]
    df["bbw_p20"] = df["bbw_pct"].rolling(150).quantile(.20)
    df["slope10_pct"] = 100*(df["bb_mid"]/df["bb_mid"].shift(10)-1)
    df["f5_block"] = (df["bbw_pct"] <= df["bbw_p20"]) & df["slope10_pct"].between(-.05,.05, inclusive="both")
    audit=[]
    filtered=df["entry_signal"].fillna(False).copy()
    for i in range(149,len(df)):
        if not bool(df["entry_signal"].iloc[i]): continue
        box=pivot_box(df,i)
        location=(box[2] if box else float("nan"))
        # Upper half inside box only; outside-box is unclassified, not automatically GOOD.
        f6_block=bool(box is not None and 50 < location <= 100)
        f5_block=bool(df["f5_block"].iloc[i])
        rejected=f5_block or f6_block
        filtered.iloc[i]=not rejected
        audit.append({
            "entry_time_uk":df.index[i],"entry_price":df["close"].iloc[i],
            "bbw_pct":df["bbw_pct"].iloc[i],"slope10_pct":df["slope10_pct"].iloc[i],
            "swing_high":box[0] if box else None,"swing_low":box[1] if box else None,
            "swing_midpoint":(box[0]+box[1])/2 if box else None,
            "swing_position_pct":location,
            "f5_block":f5_block,"f6_block":f6_block,
            "decision":"BAD" if rejected else ("UNCLASSIFIED_BOX" if box is None or not 0<=location<=100 else "GOOD")
        })
    df["entry_signal"]=filtered
    trades,open_trade=build_trades(df)
    september=trades[trades["entry_time_uk"].dt.strftime("%Y-%m")=="2026-09"].copy()
    DIR.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(audit).to_csv(DIR/"candidate_entry_audit.csv",index=False)
    trades.to_csv(DIR/"all_closed_trades_experimental.csv",index=False)
    september.to_csv(DIR/"september_2026_trades.csv",index=False)
    open_trade.to_csv(DIR/"open_end_of_data.csv",index=False)
    ret=september["return_pct"].div(100)
    print("Rudra-Reversal-2.0 EXPERIMENTAL; Filters 5+6; 60-bar pivot-extremes PROTOTYPE")
    print("September trades:",len(september),"wins:",int((ret>0).sum()),"losses:",int((ret<0).sum()))
    print("September compounded %:",round(100*((1+ret).prod()-1),4))
    print("Output:",DIR)
    print("WARNING: unstable box boundaries; do NOT promote or deploy without chart review.")

if __name__=="__main__":
    main()
