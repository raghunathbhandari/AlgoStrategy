#!/usr/bin/env python3
"""Rudra-Reversal-2.0: causal trend-regime entry/exit matrix (September 2026).

Separate RESEARCH script. Does NOT change canonical v1.0, the 136-trade ledger,
or existing Filters 5/6. Trend-only module, not a combined range+trend backtest.

Usage from AlgoStrategy repository root:
  python3 NQ/rudra-reversal/experiment_regime_entry_exit_sep.py

Outputs in NQ/backtesting/results/rudra_reversal_2_0/regime_sep/
Entry/exit are filled at signal candle CLOSE; no fees, slippage, financing.
Trend state and pivots only use completed candles, no future lookahead.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backtesting"))
from rudra_reversal_nq_1h import load_data, add_indicators  # canonical helpers, read-only

ENTRIES = ("BREAKOUT", "CONFIRM", "RETEST", "MA_PULLBACK")
EXITS = ("A_MA1", "B_MA2", "C_SWING", "D_MA_AND_SWING", "E_PROTECT_THEN_SWING")


def build_inputs(data):
    df = add_indicators(load_data(data))
    df["slope10_pct"] = (df["bb_mid"] / df["bb_mid"].shift(10) - 1) * 100
    df["prior12_high"] = df["high"].shift(1).rolling(12).max()
    # Confirm 3-left/3-right pivots at j+3, never on pivot candle j.
    lows = df["low"].to_numpy()
    latest = [None] * len(df)
    known = None
    for i in range(len(df)):
        k = i - 3
        if k >= 3 and k + 3 < len(df):
            if all(lows[k] < lows[p] for p in range(k - 3, k + 4) if p != k):
                known = float(lows[k])
        latest[i] = known
    df["confirmed_swing_low"] = latest
    return df


def episodes(df):
    """Regimes: RANGE -> STARTING -> UPTREND -> RANGE.
    Breakout: close > prior 12-bar high, above MA20, slope10 >= 0.05%.
    Confirm: within 3 candles, close > starting close, above MA, positive slope.
    Reset: 2 consecutive closes below MA20. A breakout need not succeed.
    """
    found = []
    state = "RANGE"
    episode = None
    below = 0
    for i in range(30, len(df)):
        r = df.iloc[i]
        if state == "RANGE":
            if (r["close"] > r["prior12_high"]
                    and r["close"] > r["bb_mid"]
                    and r["slope10_pct"] >= 0.05):
                episode = dict(start=i, confirmed=None, end=None,
                               breakout_level=float(r["prior12_high"]))
                found.append(episode)
                state = "STARTING"
            continue
        if state == "STARTING":
            if (i - episode["start"] <= 3
                    and r["close"] > df.iloc[episode["start"]]["close"]
                    and r["close"] > r["bb_mid"]
                    and r["slope10_pct"] >= 0.05):
                episode["confirmed"] = i
                below = 0
                state = "UPTREND"
            elif i - episode["start"] >= 3 or r["close"] < r["bb_mid"]:
                episode["end"] = i
                state, episode = "RANGE", None
            continue
        if state == "UPTREND":
            below = below + 1 if r["close"] < r["bb_mid"] else 0
            if below >= 2:
                episode["end"] = i
                state, episode, below = "RANGE", None, 0
    return found


def entry_index(df, ep, method):
    if method == "BREAKOUT":
        return ep["start"]
    if ep["confirmed"] is None:
        return None
    if method == "CONFIRM":
        return ep["confirmed"]
    window = 12 if method == "RETEST" else 24
    last = min(len(df) - 1,
               ep["confirmed"] + window,
               (ep["end"] - 1) if ep["end"] is not None else len(df) - 1)
    for i in range(ep["confirmed"] + 1, last + 1):
        r = df.iloc[i]
        if (method == "RETEST"
                and r["low"] <= ep["breakout_level"] * 1.0015
                and r["close"] >= ep["breakout_level"]
                and r["close"] > r["bb_mid"]):
            return i
        if (method == "MA_PULLBACK"
                and r["low"] <= r["bb_mid"] * 1.0015
                and r["close"] >= r["bb_mid"]
                and r["slope10_pct"] >= 0.05):
            return i
    return None


def exit_index(df, i, method):
    entry = float(df.iloc[i]["close"])
    activated = False
    for j in range(i + 1, len(df)):
        r, prev = df.iloc[j], df.iloc[j - 1]
        below = r["close"] < r["bb_mid"]
        two_below = below and prev["close"] < prev["bb_mid"]
        swing = r["confirmed_swing_low"]
        broken = pd.notna(swing) and r["close"] < swing
        # Dynamic exit E: protect with first MA20 close until a +1% CLOSE;
        # once activated, use confirmed 3/3 swing low. No lookahead.
        if r["close"] >= entry * 1.01:
            activated = True
        trigger = {
            "A_MA1": below,
            "B_MA2": two_below,
            "C_SWING": broken,
            "D_MA_AND_SWING": below and broken,
            "E_PROTECT_THEN_SWING": broken if activated else below
        }[method]
        if trigger:
            return j
    return None


def evaluate(df, eps, entry_method, exit_method):
    rows = []
    last_exit = -1
    for ep in eps:
        if df.index[ep["start"]].strftime("%Y-%m") != "2026-09":
            continue
        i = entry_index(df, ep, entry_method)
        if i is None or i <= last_exit:
            continue
        j = exit_index(df, i, exit_method)
        if j is None:
            continue
        px_in, px_out = float(df.iloc[i]["close"]), float(df.iloc[j]["close"])
        window = df.iloc[i + 1:j + 1]
        rows.append(dict(
            entry_variant=entry_method, exit_variant=exit_method,
            episode_started_uk=str(df.index[ep["start"]]),
            entry_time_uk=str(df.index[i]), exit_time_uk=str(df.index[j]),
            entry_price=px_in, exit_price=px_out,
            return_pct=100 * (px_out / px_in - 1),
            max_favorable_pct=100 * (window["high"].max() / px_in - 1),
            max_adverse_pct=100 * (window["low"].min() / px_in - 1),
            holding_bars=j - i,
        ))
        last_exit = j
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path(
        "NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path(
        "NQ/backtesting/results/rudra_reversal_2_0/regime_sep"))
    args = parser.parse_args()
    df = build_inputs(args.input)
    eps = episodes(df)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([{
        "trend_start_uk": str(df.index[e["start"]]),
        "confirm_uk": str(df.index[e["confirmed"]]) if e["confirmed"] is not None else "",
        "end_uk": str(df.index[e["end"]]) if e["end"] is not None else "",
        "breakout_level": e["breakout_level"],
        "start_slope_pct": df.iloc[e["start"]]["slope10_pct"],
    } for e in eps if df.index[e["start"]].strftime("%Y-%m") == "2026-09"
    ]).to_csv(args.output_dir / "september_regime_episodes.csv", index=False)

    summary, ledgers = [], []
    for entry in ENTRIES:
        for exit_type in EXITS:
            ledger = evaluate(df, eps, entry, exit_type)
            if not ledger.empty:
                ledgers.append(ledger)
                returns = ledger["return_pct"] / 100
                compounded = 100 * ((1 + returns).prod() - 1)
                wins = int((returns > 0).sum())
                losses = int((returns < 0).sum())
            else:
                compounded = 0.
                wins = losses = 0
            summary.append(dict(entry=entry, exit=exit_type, trades=len(ledger),
                                wins=wins, losses=losses,
                                win_rate_pct=100*wins/len(ledger) if len(ledger) else 0,
                                compounded_pct=compounded))
    pd.DataFrame(summary).to_csv(args.output_dir / "entry_exit_matrix.csv", index=False)
    if ledgers:
        pd.concat(ledgers, ignore_index=True).to_csv(
            args.output_dir / "entry_exit_all_trades.csv", index=False)
    print(pd.DataFrame(summary).round(4).to_string(index=False))
    print("Saved", args.output_dir)
    print("RESEARCH ONLY — September trend entries, NOT combined v2.0 portfolio.")
    print("No fees/slippage. Bar CLOSE fills; reviewed month is in-sample.")
    print("No changes to Rudra-Reversal-1.0 or the canonical trade ledger.")


if __name__ == "__main__":
    main()
