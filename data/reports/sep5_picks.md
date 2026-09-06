# Sep 5 Weather Picks — Saturday, September 5, 2026

**Generated:** 2026-09-05 08:15 CDT (13:15 UTC)  
**Run type:** Scheduled proposal (unattended)  
**Book:** $79.30 settled bankroll

---

## NO QUALIFIED PICKS for Sep 5

### Why

All 24 Sep 5 Kalshi weather band markets (DEN / NYC / MIA / CHI, 6 bands each) are listed and open but have **completely empty orderbooks** — zero bids, zero asks, zero volume, no last trade. With no live prices, there is no market center to compute, no edge to measure, and no way to satisfy the hard gates. The instruction is explicit: **real API prices only — never simulate. If the API fails, report and hold cash.**

### What I checked

- **NWS forecasts:** Successfully fetched for all four cities (fresh as of this morning's update cycle):

| City | NWS High (°F) | NWS Low (°F) | Notes |
|------|---------------|--------------|-------|
| Denver | 94 | 65 | Mostly sunny, 20% afternoon storms, NNE wind 3-7 mph |
| New York | 80 | 68 | Sunny, 0% precip, N wind 9 mph |
| Miami | 89 | 81 | 50% storms, SE wind 8 mph, heat index 106 |
| Chicago | 76 | 68 | Patchy fog AM then mostly cloudy, 10% precip, N wind 5-15 mph |

- **Kalshi API:** Fetched all open markets for `KXHIGHDEN`, `KXHIGHNY`, `KXHIGHMIA`, `KXHIGHCHI` series. Confirmed 6 Sep 5 markets per city (band + threshold format). Checked both the series endpoint and individual market endpoints. Also pulled orderbook for every market — all empty.

- **Market center:** Cannot compute. No YES-mid prices exist to weight.

- **Model center (would-be, for reference):**

| City | NWS High | +1.5°F TWC bias | Model Center |
|------|----------|-----------------|-------------|
| Denver | 94 | +1.5 | 95.5 |
| New York | 80 | +1.5 | 81.5 |
| Miami | 89 | +1.5 | 90.5 |
| Chicago | 76 | +1.5 | 77.5 |

These are informational only — without live market prices, the model-vs-market gap can't be measured and no gate can fire.

### What this means

The Sep 5 weather markets haven't attracted any market makers yet. This is a Saturday — Kalshi weather markets sometimes go live later in the day or may have limited weekend participation. The markets exist in the API (status open) but nobody is quoting.

### Recommendation

**Hold cash.** No action on Sep 5 weather. Check again later today if liquidity arrives, or pivot to Sunday Sep 6 / Labor Day Sep 7 markets which may have more activity. Do not place orders without a live orderbook — there's no one to take the other side.

---

*Proposal only. Thad approves all buys. No orders placed.*