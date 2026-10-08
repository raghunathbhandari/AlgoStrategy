# Rudra-Reversal-1.0 — LOCKED / CANONICAL

Status: **LOCKED**, verified historical benchmark. Do not change code or results when researching v2.0.

Canonical rules: [RUDRA_REVERSAL_NQ_1H_LOCKED.md](../RUDRA_REVERSAL_NQ_1H_LOCKED.md)

Implementation: [rudra_reversal_nq_1h.py](../rudra_reversal_nq_1h.py)

Dataset: `NQ/data/recent/NQ_1h_12m_2025-10-07_2026-10-07.csv`.

Period: 2025-10-07 to 2026-10-07. NQ, 1H, long only. BB(20,2; ddof=0), 2 of last 3 near lower BB (0.15% tolerance), 150-bar range >=20% depth measured from signal close, entry at signal close, one trade at a time, upper BB near-touch or touch exit, no fixed stop loss.

**Benchmark checksum:** 136 closed trades; 101 wins; 35 losses; 74.2647% win rate; +33.5512% compounded. One open end-of-data trade excluded.

**September 2026**: 16 entries; 13 wins; 3 losses; +6.3127% compounded.

No Filter 5 or 6 is applied in this version. Any v2 investigation must use a separate script/outputs and avoid overwriting this version's ledger.
