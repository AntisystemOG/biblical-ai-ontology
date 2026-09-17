# 🌡️ DAILY WEATHER PICKS — Wednesday, September 9, 2026

**Generated:** 8:15 AM CDT (13:15 UTC)  
**Bankroll:** $37.43 cash | $35.27 portfolio value  
**Data sources:** NWS API (live) + Kalshi API (live, real prices)

---

## NO QUALIFIED PICKS for 2026-09-09

---

## Full Analysis

### NWS Forecasts (fresh from API)

| City | NWS High | Condition | Precip% | Wind | Cloud |
|------|----------|-----------|---------|------|-------|
| DEN | 83°F | Sunny | 0% | NE 3-7 | 0% |
| NYC | 84°F | Mostly Sunny | 2% | S 5-15 | 25% |
| MIA | 89°F | Chance TSTM | 47% | E 8-12 | 60% |
| CHI | 76°F | Rain Showers | 86% | WSW 10 | 90% |

### Market Centers (YES-mid-weighted, live Kalshi prices)

| City | Market Center | Model Center | Gap | Status |
|------|--------------|--------------|-----|--------|
| DEN | 82.0°F | 82°F | 0.0F | ✅ Clean |
| NYC | 83.8°F | 84°F | 0.2F | ✅ Clean |
| MIA | 90.7°F | 88°F | 2.7F | 🚩 RED FLAG — SKIP |
| CHI | 81.4°F | 76°F | 5.4F | 🚩 RED FLAG — SKIP |

### Model Center Computation

- **DEN**: NWS 83 + 1.5 TWC = 84.5 → NE wind -3 → 81.5 → capped at -2F from base → **82.5F → round 82F**
- **NYC**: NWS 84 + 1.5 TWC = 85.5 → S wind -1 → **84.5F → round 84F**  
- **MIA**: NWS 89 + 1.5 TWC = 90.5 → storm cap -5 (47% + TSTM) → 85.5 → E wind -2 → 83.5 → capped → **88.5F → round 88F**
- **CHI**: NWS 76 + 1.5 TWC = 77.5 → precip -2 (86% non-tstm) → 75.5 → cloud -2 (90%) → 73.5 → capped → **75.5F → round 76F**

### Gate Results by City

**DEN** (gap 0.0F — clean):
- T78 NO @ 100¢ → SKIP (zero profit at $1.00 ask)
- T85 NO @ 99¢ → SKIP (94¢ gate FAIL: 99¢ ≥ 94¢ but cushion 4.0F < 5.0F)
- B78.5 YES @ 4¢ → SKIP (model 82F is 3F from band 78-79, too far for lottery)
- B84.5 YES @ 6¢ → **marginal qualify** (model 82F, band 84-85, 2.0F from band edge). Already hold 4 shares @ 12¢ ($0.48). Only $0.34 remaining lottery capacity. ROI 1567% but pure lottery.
- All other DEN bands: < 4F from market center, not eligible for NO; YES prices too high for lottery.

**NYC** (gap 0.2F — clean):
- T91 NO @ 100¢ → SKIP (zero profit)
- B88.5 NO @ 100¢ → SKIP (94¢ gate FAIL: 100¢ ≥ 94¢, cushion 4.7F < 5.0F)
- B90.5 NO @ 100¢ → SKIP (zero profit)
- B86.5 YES @ 8¢ → marginal (model 84F, band 86-87, 2.0F from edge) but aggregate lottery cap hit by DEN pick. Without DEN, would get $0.82.
- T84, B84.5: YES prices 47-52¢ — not lottery territory, no NO edge (dist < 4F)

**MIA** (gap 2.7F — RED FLAG):  
Model says 88°F, market says 90.7°F. The market is pricing MIA much warmer than our model (likely pricing TWC settlement bias + heat index). TWC double-count rule → **SKIP entire city**. The MIA blacklist on low-side lots would also block the 87-88 band.

**CHI** (gap 5.4F — RED FLAG):  
NWS says 76°F (rain, 86% precip, 90% cloud cover). Market center is 81.4°F — market is pricing 5F warmer than our model. This is a massive disagreement. The TWC double-count rule says skip because our storm/cloud adjustments may be over-counting (NWS already bakes storm cooling into their 76°F forecast). Could be a data advantage, but the 5.4F gap is too wide to trust — **SKIP per hard gate**.

### Existing Position

| Ticker | Side | Shares | Cost | Current YES Ask |
|--------|------|--------|------|-----------------|
| KXHIGHDEN-26SEP09-B84.5 | YES | 4 | $0.48 | 6¢ |

Already holding 4 shares of DEN 84-85 YES @ 12¢ average. Model center 82F is 2F from this band — this is a warm-tail lottery that needs Denver to bust 2F above forecast. With sunny skies and 0% precip, there's no storm risk to push cooler, but also no heat mechanism to push warmer. Hold existing position; do not add.

### Why No Picks Today

1. **MIA and CHI both red-flagged** (model-vs-market gap ≥ 2F) — the TWC double-count rule protects us from over-counting storm/cloud adjustments that NWS already embeds in their forecast.
2. **DEN** market is perfectly aligned with our model (82F), but the band ladder is tight — the 82-83 band (where the high should land) trades at 55-58¢ YES, not cheap enough for a lottery and not far enough from center for a NO. The tail bands (T78, T85) have NO asks at 99-100¢ (zero or near-zero profit).
3. **NYC** is similarly well-aligned but tight — the 84-85 band trades at 46-47¢ (coin flip territory, no edge), and tail bands have NO asks at 100¢.
4. The only marginal qualifier (DEN B84.5 YES @ 6¢) already has exposure from this morning's earlier entry, and the remaining capacity ($0.34) is too small to meaningfully add.

### Peak-Exit Watcher

No new positions → no exit watcher needed today. Existing DEN B84.5 YES position: monitor 1:00-4:30 PM CDT half-hourly. Exit plan: if Denver hits 84°F by 2 PM local (MDT), hold to settlement. If Denver stays ≤ 82°F by 3 PM MDT, consider exit at bid (currently 5¢) to salvage ~$0.20.

---

**Bottom line:** Today's market is efficiently priced for DEN and NYC. The storm cities (MIA, CHI) have large model-vs-market gaps that trigger the TWC double-count safety rule. Cash is the correct position. Hold the existing DEN B84.5 YES lottery ticket — it's already placed and the cost is sunk.

*Proposal only. Thad approves all buys. No orders placed.*