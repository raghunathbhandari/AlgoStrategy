#!/usr/bin/env python3
"""Rudra-Reversal NQ 1H — TWO-ENTRY EXPERIMENT.

SEPARATE RESEARCH FLOW. Does not modify canonical one-position strategy.

Rules:
- Same canonical Rudra-Reversal signals/exits
- BB20, 2.0 StdDev, ddof=0
- 2 of last 3 lower-BB touch/near-touch
- 20% depth from 150-bar top using signal close
- Entry at signal candle close
- Up to 2 simultaneous positions
- Each position exits independently on canonical Upper-BB exit
- No new entry on a candle where an exit occurs
- End-of-data open positions are excluded from closed-trade stats
"""
from pathlib import Path
import pandas as pd

SRC=Path("NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv")
OUT=Path("NQ/backtesting/experiments/two_entries")
OUT.mkdir(parents=True,exist_ok=True)

df=pd.read_csv(SRC)
df["timestamp_uk"]=pd.to_datetime(df["timestamp_uk"],utc=True,errors="coerce").dt.tz_convert("Europe/London")
for c in ["open","high","low","close"]: df[c]=pd.to_numeric(df[c],errors="coerce")
df=df.dropna(subset=["timestamp_uk","open","high","low","close"]).sort_values("timestamp_uk").reset_index(drop=True)
df["bb_mid"]=df["close"].rolling(20).mean()
df["bb_std"]=df["close"].rolling(20).std(ddof=0)
df["bb_upper"]=df["bb_mid"]+2*df["bb_std"]
df["bb_lower"]=df["bb_mid"]-2*df["bb_std"]
df["high150"]=df["high"].rolling(150).max()
df["low150"]=df["low"].rolling(150).min()
df["depth"]=(df["high150"]-df["close"])/(df["high150"]-df["low150"])
df["near_lower"]=(df["low"]<=df["bb_lower"])|(((df["low"]-df["bb_lower"])/df["bb_lower"])<=0.0015)
df["near_upper"]=(df["high"]>=df["bb_upper"])|(((df["bb_upper"]-df["high"])/df["bb_upper"])<=0.0015)
df["touch3"]=df["near_lower"].astype(int).rolling(3).sum()
df["signal"]=df["near_lower"]&(df["touch3"]>=2)&(df["depth"]>=0.20)

active=[]; trades=[]; seq=0
for i in range(149,len(df)):
    r=df.iloc[i]
    exited=False
    remain=[]
    for p in active:
        if i>p["entry_i"] and bool(r["near_upper"]):
            exact=bool(r["high"]>=r["bb_upper"])
            exit_price=float(r["bb_upper"] if exact else r["high"])
            trades.append({
                **p,
                "exit_i":i,
                "exit_time_uk":r["timestamp_uk"],
                "exit_price":exit_price,
                "return_pct":(exit_price/p["entry_price"]-1)*100,
                "holding_hours":(r["timestamp_uk"]-p["entry_time_uk"]).total_seconds()/3600,
                "result":"WIN" if exit_price>p["entry_price"] else "LOSS",
            })
            exited=True
        else:
            remain.append(p)
    active=remain

    if (not exited) and bool(r["signal"]) and len(active)<2:
        seq+=1
        active.append({
            "trade_no":seq,
            "entry_i":i,
            "entry_time_uk":r["timestamp_uk"],
            "entry_price":float(r["close"]),
            "signal_depth_pct":float(r["depth"]*100),
        })

trade_df=pd.DataFrame(trades)
open_df=pd.DataFrame(active)
trade_df.to_csv(OUT/"rudra_reversal_nq_1h_two_entries_trades.csv",index=False)
open_df.to_csv(OUT/"rudra_reversal_nq_1h_two_entries_open.csv",index=False)

wins=trade_df[trade_df["return_pct"]>0]
losses=trade_df[trade_df["return_pct"]<0]
gross_profit=wins["return_pct"].sum()
gross_loss=-losses["return_pct"].sum()

print("TWO-ENTRY EXPERIMENT")
print("closed trades:",len(trade_df))
print("wins:",len(wins))
print("losses:",len(losses))
print("win rate:",len(wins)/len(trade_df)*100)
print("profit factor:",gross_profit/gross_loss)
print("expectancy %:",trade_df["return_pct"].mean())
print("open positions at dataset end:",len(open_df))
