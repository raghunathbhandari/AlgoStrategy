# Rudra-Reversal NQ 1H — Two-Entry Experiment

Separate experiment. Canonical one-position strategy remains unchanged.

## Control vs two-entry test

| Metric | Canonical 1 position | Two-entry experiment |
|---|---:|---:|
| Closed trades | **136** | **238** |
| Wins | **101** | **175** |
| Losses | **35** | **63** |
| Win rate | **74.26%** | **73.53%** |
| Profit Factor | **1.94** | **1.99** |
| Expectancy / trade | **+0.2167%** | **+0.2452%** |
| Average winner | **+0.6016%** | **+0.6698%** |
| Average loser | **-0.8941%** | **-0.9342%** |
| Best trade | **+1.6786%** | **+2.3991%** |
| Worst trade | **-3.2936%** | **-3.3630%** |
| Avg holding | **25.62h** | **28.35h** |
| Avg winner hold | **16.51h** | **19.87h** |
| Avg loser hold | **51.89h** | **51.89h** |
| Open positions at dataset end | **1** | **2** |

## Main result

Allowing a second simultaneous entry produced **102 additional closed trades**.

Trade quality stayed broadly similar:
- Win rate: **74.26% -> 73.53%**
- Profit Factor: **1.94 -> 1.99**
- Expectancy: **+0.2167% -> +0.2452%**

This is encouraging: the extra entries did **not** destroy the edge.

## Important capital note

The raw compounded figure obtained by multiplying every trade sequentially is **not a valid portfolio return** for overlapping positions, because two trades can be active at the same time.

Therefore this experiment intentionally reports trade-level edge first.

For a valid $10,000 portfolio comparison, the next test must define position sizing, for example:
- **50% account allocation per slot**, max two slots, or
- fixed NQ/MNQ contracts per entry.

Do not compare the naive overlapping compounded return with the canonical +33.55% until position sizing is defined.
