from pathlib import Path
import json
import pandas as pd

from strategies.nq_london_session_breakout_5m import load_nq_1m, resample_5m, backtest, summary, Config

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

one = load_nq_1m()
five = resample_5m(one)

rows = []
for start, end in [("07:00","08:00"), ("07:00","08:30"), ("07:30","08:30")]:
    for rr in [1.0, 1.5, 2.0, 2.5, 3.0]:
        cfg = Config(london_range_start=start, london_range_end=end, trade_start=end, trade_end="11:00", rr=rr)
        trades = backtest(five, cfg)
        s = summary(trades)
        rows.append({
            "range_start": start,
            "range_end": end,
            "rr": rr,
            **s,
        })

out = pd.DataFrame(rows).sort_values(["net_r","avg_r"], ascending=False)
out.to_csv(RESULTS / "nq_london_breakout_parameter_sweep.csv", index=False)

best = out.iloc[0].to_dict() if not out.empty else {}
(RESULTS / "nq_london_breakout_summary.json").write_text(json.dumps({
    "data_rows_1m": int(len(one)),
    "bars_5m": int(len(five)),
    "data_start_et": str(one["datetime"].min()),
    "data_end_et": str(one["datetime"].max()),
    "best_baseline": best,
}, indent=2, default=str))

print(out.to_string(index=False))
print("\nBEST:", best)
