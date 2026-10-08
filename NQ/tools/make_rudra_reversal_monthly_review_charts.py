#!/usr/bin/env python3
"""Version 3: twelve-page Rudra Reversal review PDF. Plot only; never recalculate trades."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, ConnectionPatch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "NQ/reports/rudra_reversal_1y_monthly"
SRC = ROOT / "NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv"
LEDGER = OUT / "trade_ledger_chart_ids.csv"
MANIFEST = OUT / "monthly_manifest.csv"
PDF = OUT / "NQ_Rudra_Reversal_12_Month_Chart_Review_Outside_Labels.pdf"

def uk(series):
    return pd.to_datetime(series, utc=True, errors="raise").dt.tz_convert("Europe/London")

def label_positions(events, rows=6, spacing=12):
    """Allocate each label a separate lane when horizontally close; no label overlap."""
    lanes=[-1e9]*rows
    placed={}
    for event in sorted(events, key=lambda x:(x["x"],x["id"])):
        x=event["x"]
        possible=[k for k in range(rows) if x-lanes[k]>=spacing]
        if not possible:
            raise RuntimeError(f"Too many clustered labels around bar {x}; add label rows")
        k=min(possible, key=lambda j:(lanes[j],j))
        lanes[k]=x
        placed[event["id"]]=k
    return placed

df=pd.read_csv(SRC)
df["t"]=uk(df["timestamp_uk"])
for c in ("open","high","low","close"):
    df[c]=pd.to_numeric(df[c],errors="raise")
df=df.sort_values("t").reset_index(drop=True)
df["bb_middle"]=df["close"].rolling(20).mean()
sd=df["close"].rolling(20).std(ddof=0)
df["bb_upper"]=df["bb_middle"]+2*sd
df["bb_lower"]=df["bb_middle"]-2*sd

tr=pd.read_csv(LEDGER)
required={"trade_no","i","entry_time","entry_price","j","exit_time","exit_price","return_pct"}
assert required.issubset(tr.columns), "Canonical ledger columns missing"
assert len(tr)==136 and (tr.return_pct>0).sum()==101 and (tr.return_pct<0).sum()==35, "136/101/35 checksum failure"
assert sorted(tr.trade_no.astype(int).tolist())==list(range(1,137)), "Trade numbers changed"
tr["ent"]=uk(tr["entry_time"])
tr["ext"]=uk(tr["exit_time"])
# Exact canonical candle position and fill checks, with no strategy recalculation.
for t in tr.itertuples():
    i,j=int(t.i),int(t.j)
    assert 0<=i<j<len(df), f"bad candle index {t.trade_no}"
    assert df.at[i,"t"]==t.ent and df.at[j,"t"]==t.ext, f"timestamp mismatch {t.trade_no}"
    assert np.isclose(df.at[i,"close"],t.entry_price,atol=1e-6), f"entry price mismatch {t.trade_no}"
    assert df.at[j,"low"]-0.01 <=t.exit_price<=df.at[j,"high"]+0.01, f"exit outside candle {t.trade_no}"
    assert np.isclose((t.exit_price/t.entry_price-1)*100,t.return_pct,atol=1e-6), f"return mismatch {t.trade_no}"

manifest=pd.read_csv(MANIFEST)
months=pd.period_range("2025-10","2026-09",freq="M")
assert all(str(p) in set(manifest.month) for p in months)
plt.rcParams.update({"font.size":9,"font.family":"DejaVu Sans","pdf.fonttype":42})
count_entries=0; count_exits=0

with PdfPages(PDF,metadata={"Title":"NQ Rudra Reversal 1H - 12 Month Chart Review - Outside Labels V3"}) as pdf:
    for page,p in enumerate(months,1):
        start=pd.Timestamp(p.start_time,tz="Europe/London")
        end=start+pd.DateOffset(months=1)
        month=df[(df.t>=start)&(df.t<end)].copy()
        assert len(month)>50, f"Insufficient candles {p}"
        gindex=month.index.to_numpy()
        start_i=int(gindex[0]); end_i=int(gindex[-1])
        entry=tr[(tr.ent>=start)&(tr.ent<end)].copy()
        exits=tr[(tr.ext>=start)&(tr.ext<end)].copy()
        mrow=manifest[manifest.month==str(p)].iloc[0]
        assert len(entry)==int(mrow.entries), f"manifest entry count mismatch {p}"
        assert int((entry.return_pct>0).sum())==int(mrow.wins)
        assert int((entry.return_pct<0).sum())==int(mrow.losses)
        count_entries+=len(entry);count_exits+=len(exits)
        n=len(month)
        fig=plt.figure(figsize=(20,12),facecolor="white")
        gs=fig.add_gridspec(nrows=4,ncols=1,height_ratios=[2.5,7.1,2.5,.8],
                           left=.06,right=.985,top=.92,bottom=.07,hspace=.09)
        top=fig.add_subplot(gs[0]); ax=fig.add_subplot(gs[1],sharex=top)
        bot=fig.add_subplot(gs[2],sharex=top)
        notes=fig.add_subplot(gs[3])
        fig.suptitle(f"NQ 1H | Rudra Reversal | {p.strftime('%B %Y')} | Page {page}/12",
                     x=.06,y=.975,ha="left",fontsize=17,fontweight="bold")
        w=int((entry.return_pct>0).sum()); l=int((entry.return_pct<0).sum())
        fig.text(.985,.967,f"Entries: {len(entry)}   Wins: {w}   Losses: {l}   Exits this month: {len(exits)}",
                 ha="right",fontsize=10)
        x=np.arange(n)
        for k,r in enumerate(month.itertuples()):
            color="#17985c" if r.close>=r.open else "#d63e43"
            ax.vlines(k,r.low,r.high,color=color,lw=.64,zorder=2)
            bottom=min(r.open,r.close); height=max(abs(r.close-r.open),.2)
            ax.add_patch(Rectangle((k-.33,bottom),.66,height,facecolor=color,
                                  edgecolor=color,linewidth=.3,zorder=3))
        ax.plot(x,month.bb_upper.to_numpy(),color="#2564bc",lw=1.0,zorder=4)
        ax.plot(x,month.bb_middle.to_numpy(),color="#7b838e",lw=.9,zorder=4)
        ax.plot(x,month.bb_lower.to_numpy(),color="#8951ac",lw=1.0,zorder=4)
        ax.set_xlim(-4,n+3)
        lo=float(np.nanmin(month[["low","bb_lower"]].to_numpy()))
        hi=float(np.nanmax(month[["high","bb_upper"]].to_numpy()))
        d=max(hi-lo,1); ax.set_ylim(lo-.06*d,hi+.06*d)
        ax.set_ylabel("NQ price",fontsize=10)
        ax.grid(alpha=.12,lw=.45)
        ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
        ax.tick_params(labelsize=8)
        ticks=np.linspace(0,n-1,9,dtype=int)
        ax.set_xticks(ticks)
        ax.set_xticklabels([month.iloc[k].t.strftime("%d %b\n%H:%M") for k in ticks],fontsize=8)
        ax.tick_params(axis="x",pad=5)

        top.set_ylim(0,1);bot.set_ylim(0,1)
        for a in (top,bot):
            a.set_yticks([])
            a.tick_params(axis="x",which="both",bottom=False,labelbottom=False)
            a.set_facecolor("#f8f9fc")
            for sp in a.spines.values():sp.set_visible(False)
        top.text(.006,.95,"BUY labels (UK time)  |  yellow triangle = entry close",
                 transform=top.transAxes,va="top",fontsize=9,color="#4b5563")
        bot.text(.006,.05,"SELL labels (UK time)  |  purple X = win; red X = loss",
                 transform=bot.transAxes,va="bottom",fontsize=9,color="#4b5563")
        buys=[{"id":int(t.trade_no),"x":int(t.i)-start_i,"y":float(t.entry_price),
               "color":"#111827","time":t.ent} for t in entry.itertuples()]
        sells=[{"id":int(t.trade_no),"x":int(t.j)-start_i,"y":float(t.exit_price),
                "color":"#8b42ae" if t.return_pct>0 else "#db353f",
                "time":t.ext} for t in exits.itertuples()]
        # Each event keeps its original candle X and fill price. Labels use 6 lanes.
        for events,area,kind in ((buys,top,"B"),(sells,bot,"S")):
            lanes=label_positions(events,rows=6,spacing=13)
            for e in events:
                xx,yy=e["x"],e["y"]
                if kind=="B":
                    ax.scatter([xx],[yy],marker="^",s=82,facecolors="#f9da29",
                               edgecolors="#111111",linewidths=1.0,zorder=8)
                    color="#111111";label_y=.78-lanes[e["id"]]*.12
                else:
                    ax.scatter([xx],[yy],marker="x",s=92,color=e["color"],
                               linewidths=2.4,zorder=8)
                    color=e["color"];label_y=.81-lanes[e["id"]]*.12
                line=ConnectionPatch(xyA=(xx,yy),coordsA=ax.transData,
                                     xyB=(xx,label_y),coordsB=area.transData,
                                     color=color,lw=.58,alpha=.8,zorder=1)
                fig.add_artist(line)
                area.text(xx,label_y,f"{kind}{e['id']}",ha="center",va="center",
                          fontsize=8.2,fontweight="bold",color=color,
                          bbox=dict(facecolor="#f8f9fc",edgecolor="none",pad=.6),zorder=12)
        handles=[
            Line2D([0],[0],color="#2564bc",lw=1.4,label="BB upper"),
            Line2D([0],[0],color="#7b838e",lw=1.4,label="MA20 / BB middle"),
            Line2D([0],[0],color="#8951ac",lw=1.4,label="BB lower"),
            Line2D([0],[0],marker="^",color="none",markerfacecolor="#f9da29",
                   markeredgecolor="black",markersize=9,label="BUY"),
            Line2D([0],[0],marker="x",color="#8b42ae",lw=0,markersize=9,label="Winning SELL"),
            Line2D([0],[0],marker="x",color="#db353f",lw=0,markersize=9,label="Losing SELL"),
        ]
        ax.legend(handles=handles,loc="upper center",bbox_to_anchor=(.5,1.015),
                  ncol=6,fontsize=8,framealpha=.90)
        notes.axis("off")
        notes.axhline(.94,color="#d1d5db",lw=.6)
        notes.text(.006,.76,"REVIEW NOTES:",transform=notes.transAxes,color="#475569",weight="bold")
        notes.text(.13,.76,"Missed trades / incorrect entry / better entry / exit / sideways:",
                   transform=notes.transAxes,color="#64748b")
        notes.axhline(.18,color="#d1d5db",lw=.5)
        fig.text(.06,.038,"Canonical 136-trade ledger; labels retain original IDs and fill prices. All candle times UK.",
                 color="#6b7280",fontsize=8)
        pdf.savefig(fig,dpi=115)
        plt.close(fig)
        print(f"PAGE {page:02d}: {p} candles={n} BUY={len(buys)} SELL={len(sells)} wins={w} losses={l}")
print(f"COMPLETE: 12 pages, {count_entries} included entries, {count_exits} included exits, PDF={PDF}, size={PDF.stat().st_size} bytes")
