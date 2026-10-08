#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv"
OUT=ROOT/"NQ/reports/rudra_reversal_1y_monthly"
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

signals=[]
for i in range(149,len(df)):
    r=df.iloc[i]
    if bool(r["signal"]):
        signals.append({"i":i,"entry_time":r["timestamp_uk"],"entry_price":float(r["close"])})

trades=[]; missed=[]; next_allowed=0; trade_no=0; open_trade=None
for s in signals:
    if s["i"]<next_allowed:
        missed.append(s); continue
    trade_no+=1
    ex=None
    for j in range(s["i"]+1,len(df)):
        r=df.iloc[j]
        if bool(r["near_upper"]):
            exact=bool(r["high"]>=r["bb_upper"])
            px=float(r["bb_upper"] if exact else r["high"])
            ex={"j":j,"exit_time":r["timestamp_uk"],"exit_price":px,"return_pct":(px/s["entry_price"]-1)*100}
            break
    if ex:
        trades.append({"trade_no":trade_no,**s,**ex})
        next_allowed=ex["j"]+1
    else:
        open_trade={"trade_no":trade_no,**s}
        next_allowed=len(df)

tdf=pd.DataFrame(trades)
mdf=pd.DataFrame(missed)
if len(tdf)!=136 or int((tdf["return_pct"]>0).sum())!=101:
    raise RuntimeError("Benchmark checksum failed")

# Exact benchmark touches 13 calendar months; generate all 13 so no trade is omitted.
periods=pd.period_range("2025-10","2026-10",freq="M")
manifest=[]
for p in periods:
    start=pd.Timestamp(p.start_time,tz="Europe/London")
    end=pd.Timestamp(p.end_time,tz="Europe/London")
    m=df[(df["timestamp_uk"]>=start)&(df["timestamp_uk"]<=end)].copy().reset_index(drop=True)
    if m.empty: continue
    pos={ts:i for i,ts in enumerate(m["timestamp_uk"])}
    fig,ax=plt.subplots(figsize=(12,4.8),dpi=90)
    for i,r in m.iterrows():
        ax.vlines(i,r["low"],r["high"],linewidth=.55)
        lo=min(r["open"],r["close"]); h=max(abs(r["close"]-r["open"]),.2)
        ax.add_patch(Rectangle((i-.28,lo),.56,h,fill=False,linewidth=.65))
    x=np.arange(len(m))
    ax.plot(x,m["bb_upper"],linewidth=.9,label="BB Upper")
    ax.plot(x,m["bb_mid"],linewidth=.8,label="BB Mid")
    ax.plot(x,m["bb_lower"],linewidth=.9,label="BB Lower")

    ent=tdf[(tdf["entry_time"]>=start)&(tdf["entry_time"]<=end)]
    ext=tdf[(tdf["exit_time"]>=start)&(tdf["exit_time"]<=end)]
    for _,t in ent.iterrows():
        if t["entry_time"] in pos:
            xx=pos[t["entry_time"]]; yy=t["entry_price"]
            ax.scatter(xx,yy,marker="^",s=38,zorder=5)
            ax.annotate(f"T{int(t['trade_no'])}",(xx,yy),xytext=(0,-12),textcoords="offset points",ha="center",fontsize=6)
    for _,t in ext.iterrows():
        if t["exit_time"] in pos:
            xx=pos[t["exit_time"]]; yy=t["exit_price"]
            ax.scatter(xx,yy,marker="v",s=38,zorder=5)
            ax.annotate(f"T{int(t['trade_no'])}",(xx,yy),xytext=(0,8),textcoords="offset points",ha="center",fontsize=6)
    if not mdf.empty:
        mm=mdf[(mdf["entry_time"]>=start)&(mdf["entry_time"]<=end)]
        for _,s in mm.iterrows():
            if s["entry_time"] in pos:
                ax.scatter(pos[s["entry_time"]],s["entry_price"],marker="x",s=16,zorder=4)

    if open_trade and start<=open_trade["entry_time"]<=end and open_trade["entry_time"] in pos:
        xx=pos[open_trade["entry_time"]]; yy=open_trade["entry_price"]
        ax.scatter(xx,yy,marker="^",s=46,zorder=6)
        ax.annotate(f"T{open_trade['trade_no']}-OPEN",(xx,yy),xytext=(0,-12),textcoords="offset points",ha="center",fontsize=6)

    ti=np.linspace(0,len(m)-1,min(10,len(m)),dtype=int)
    ax.set_xticks(ti); ax.set_xticklabels(m.iloc[ti]["timestamp_uk"].dt.strftime("%d-%b"),rotation=45,ha="right",fontsize=7)
    wins=int((ent["return_pct"]>0).sum()); losses=int((ent["return_pct"]<0).sum())
    ax.set_title(f"NQ 1H Rudra-Reversal | {p} | Entries {len(ent)} | W {wins} L {losses}",fontsize=9)
    ax.grid(alpha=.18); ax.legend(fontsize=7,loc="best"); ax.set_ylabel("Price")
    fig.tight_layout()
    f=OUT/f"{p}.png"; fig.savefig(f,dpi=90,bbox_inches="tight"); plt.close(fig)
    manifest.append({"month":str(p),"entries":len(ent),"wins":wins,"losses":losses,"file":f.name})

tdf.to_csv(OUT/"trade_ledger_chart_ids.csv",index=False)
mdf.to_csv(OUT/"missed_raw_signals.csv",index=False)
pd.DataFrame(manifest).to_csv(OUT/"monthly_manifest.csv",index=False)
print("generated",len(manifest),"charts")
