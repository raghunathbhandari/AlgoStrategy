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


## Proper $10,000 portfolio test — 2 slots × 50%

Capital model:
- Starting account: **$10,000**
- Slot 1 starts with **$5,000**
- Slot 2 starts with **$5,000**
- Each slot compounds only the trades assigned to that slot
- No overlapping trade is allowed to use more than its slot capital
- This avoids the invalid 100%-capital-per-overlapping-trade assumption

| Metric | Result |
|---|---:|
| Slot 1 trades | **136** |
| Slot 1 ending capital | **$6,677.56** |
| Slot 1 return | **+33.55%** |
| Slot 2 trades | **102** |
| Slot 2 ending capital | **$6,637.65** |
| Slot 2 return | **+32.75%** |
| Portfolio ending capital | **$13,315.21** |
| Portfolio net profit | **+$3,315.21** |
| Portfolio compounded return | **+33.15%** |
| Closed-equity max drawdown | **4.17%** |
| Closed-equity max drawdown $ | **$454.60** |

### Interpretation

The second slot clearly has edge on its own: **+32.75%** on its $5,000 allocation.

However, splitting the account 50/50 means the total portfolio return is **+33.15%**, which is very close to the canonical one-position full-capital result of **+33.55%**.

So the benefit of two slots is currently:
- more trade participation
- similar portfolio return
- slightly lower closed-equity drawdown
- less dependence on one entry timing

It does **not** materially increase compounded return under a strict 50/50 split.

To seek higher portfolio return, the next research step would be dynamic allocation rather than fixed 50/50, while keeping leverage/risk explicit.
