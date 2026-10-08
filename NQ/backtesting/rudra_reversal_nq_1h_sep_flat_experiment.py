#!/usr/bin/env python3
"""EXPERIMENT ONLY: Rudra Reversal NQ 1H, September 2026 sideways-market filter.
Never change the canonical locked strategy or its 136-trade ledger.

Narrow: current BB width (% of SMA20) <= trailing 150-bar 20th percentile,
including current bar. Flat: abs((SMA20 / SMA20_10_bars_ago - 1)*100)
is below configured threshold. Reject a BUY only when BOTH conditions hold.
Existing canonical upper-BB exits are unchanged.
Run from AlgoStrategy root:
 python3 NQ/backtesting/rudra_reversal_nq_1h_sep_flat_experiment.py
"""
from pathlib import Path
import pandas as pd
from rudra_reversal_nq_1h import load_data, add_indicators, build_trades

DATA = Path("NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv")
OUT = Path("NQ/backtesting/results/sep_2026_flat_filter_experiment.csv")


def run():
    base = add_indicators(load_data(DATA))
    base["bbw_pct"] = (base["bb_upper"] - base["bb_lower"]) / base["bb_mid"] * 100.0
    base["bbw_p20_150"] = base["bbw_pct"].rolling(150).quantile(0.20)
    base["narrow"] = base["bbw_pct"] <= base["bbw_p20_150"]
    base["slope10_pct"] = (base["bb_mid"] / base["bb_mid"].shift(10) - 1.0) * 100.0

    rows = []
    for threshold in [None, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20]:
        df = base.copy()
        if threshold is not None:
            reject = df["narrow"] & (df["slope10_pct"].abs() < threshold)
            df["entry_signal"] = df["entry_signal"] & ~reject.fillna(False)
        trades, _ = build_trades(df)
        sep = trades[trades["entry_time_uk"].dt.strftime("%Y-%m") == "2026-09"]
        returns = sep["return_pct"].div(100.0)
        rows.append({
            "flat_threshold_pct": "BASELINE" if threshold is None else threshold,
            "trades": len(sep),
            "wins": int((returns > 0).sum()),
            "losses": int((returns < 0).sum()),
            "win_rate_pct": (returns > 0).mean() * 100 if len(sep) else 0,
            "compounded_return_pct": ((1 + returns).prod() - 1) * 100,
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"Saved: {OUT}")
    print("EXPERIMENT ONLY: do not replace locked strategy or its benchmark.")


if __name__ == "__main__":
    run()
