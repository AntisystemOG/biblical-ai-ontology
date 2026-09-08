# DAILY WEATHER PICKS — Monday, September 7, 2026 (Labor Day)

**Generated:** 2026-09-07 08:15 AM CT (13:15 UTC)
**NWS forecast source:** api.weather.gov (fresh fetch, update times below)
**Kalshi market data:** Live API (all markets active, real bid/ask)
**Bankroll:** $52.77 cash | $21.60 portfolio | Settled bankroll ~$52.77

---

## NO QUALIFIED PICKS for 2026-09-07

All four cities trigger the **Model-vs-Market Center Gap ≥ 2°F RED FLAG** (TWC double-count rule). No entries — holding cash.

---

## Full Analysis

### NWS Forecasts (fetched 13:15 UTC)

| City | NWS High | Condition | Precip% | Wind | Cloud% | NWS Update |
|------|----------|-----------|---------|------|--------|------------|
| DEN | 91°F | Partly Sunny, Chance T-storms PM | 30% | ENE 2-7 | ~50% | 08:56 UTC |
| NYC | 81°F | Sunny | 0% | NW 8 | ~15% | 06:23 UTC |
| MIA | 89°F | Showers/T-storms Likely | 70% | S 3-8 | ~30%* | 08:01 UTC |
| CHI | 75°F | Sunny | 0% | E 5-10 | ~15% | 09:40 UTC |

*MIA forecast says "Mostly sunny" despite 70% precip — cloud cover mapped at 30% but storm activity is the dominant factor.

### Model Center Computation
(NWS + 1.5°F TWC bias; storm cap -5°F if storm prob >40%; cloud -2°F if cloud >75%)

| City | NWS | +TWC 1.5°F | Storm Cap | Cloud Cap | **Model Center** |
|------|-----|-----------|-----------|-----------|-----------------|
| DEN | 91 | 92.5 | ❌ (30% < 40%) | ❌ (50% < 75%) | **92.5°F** |
| NYC | 81 | 82.5 | ❌ (0%) | ❌ (15%) | **82.5°F** |
| MIA | 89 | 90.5 | ✅ -5°F (70% > 40%) | ❌ (30% < 75%) | **85.5°F** |
| CHI | 75 | 76.5 | ❌ (0%) | ❌ (15%) | **76.5°F** |

### Market Center (YES-mid-weighted across band ladder)

| City | Bands (YES-mid) | Weighted Center | **Market Center** |
|------|-----------------|-----------------|-------------------|
| DEN | B90.5: .535, B88.5: .315, B92.5: .045, B86.5: .045 | 89.7 | **89.7°F** |
| NYC | B79.5: .645, B77.5: .215, B81.5: .140, B83.5: .035 | 79.5 | **79.5°F** |
| MIA | B92.5: .435, B90.5: .365, B88.5: .115, B86.5: .045 | 90.9 | **90.9°F** |
| CHI | B80.5: .615, B78.5: .320, B82.5: .055, B76.5: .015 | 79.8 | **79.8°F** |

### RED FLAG Gate — Model vs Market Gap

| City | Model Center | Market Center | Gap | Status |
|------|-------------|---------------|-----|--------|
| DEN | 92.5°F | 89.7°F | **2.8°F** | 🚩 RED FLAG → SKIP |
| NYC | 82.5°F | 79.5°F | **3.0°F** | 🚩 RED FLAG → SKIP |
| MIA | 85.5°F | 90.9°F | **5.4°F** | 🚩 RED FLAG → SKIP |
| CHI | 76.5°F | 79.8°F | **3.3°F** | 🚩 RED FLAG → SKIP |

**All four cities exceed the 2°F gap threshold. No entries permitted.**

### Per-City Notes

**DEN** — Model says 92.5°F (NWS 91 + 1.5 TWC), market prices 90-91 as peak band (53.5¢). The 2.8°F gap suggests the market is pricing below NWS — possibly discounting the TWC bias or factoring in the 30% storm chance more aggressively. With only 30% precip, our storm cap doesn't trigger but the market may be applying one. The gap is too wide to force.

**NYC** — Cleanest forecast of the day: sunny, 0% precip, NW wind. NWS says 81°F, we model 82.5°F with TWC bias. But the market is firmly pricing 79-80°F (64.5¢ YES on B79.5). The market is 3°F below our model center. Either the market is underpricing TWC's warm bias or TWC itself is forecasting cooler than NWS. Either way, 3°F gap = skip. Note: we already hold 4 YES shares of B81.5 (81-82°F) at $0.13 from a prior entry — that position benefits if the high reaches 81-82°F as NWS forecasts.

**MIA** — Biggest gap of the day at 5.4°F. Our storm cap (-5°F for 70% precip) pulls our model to 85.5°F, but the market is pricing 90-91°F as the peak (43.5¢ YES on B92.5). The market is essentially ignoring storm cooling despite "Showers and Thunderstorms Likely" in the NWS forecast. Miami storms often develop late afternoon after peak heating — the market may be right that the daily high is set before storms hit. Combined with the MIA low-side blacklist, no play.

**CHI** — NWS says 75°F (confirmed by hourly data: max 75°F at 15:00-18:00 CT). Market prices 80-81°F as peak (61.5¢ YES on B80.5). This is the widest disagreement relative to a clean forecast. The market appears to be using a warmer model. However, the gap direction (market warmer than model) means NO plays would target high-side bands, and the 3.3°F gap exceeds our threshold. We already hold 8 YES shares of B76.5 (76-77°F) at $0.01 — that position is a lottery that hits if NWS is right and the market is wrong.

### Existing Positions (already held, NOT new picks)

| Ticker | Side | Shares | Cost | Current |
|--------|------|--------|------|---------|
| KXHIGHNY-26SEP07-B81.5 | YES | 4 | ~$0.13 | $0.14 mid |
| KXHIGHCHI-26SEP07-B76.5 | YES | 8 | ~$0.07 | $0.015 mid |

Both are tiny lottery positions from prior entries. No action needed — let them resolve.

---

## Gate Summary

| Gate | Result |
|------|--------|
| NWS fetch | ✅ All 4 cities fetched successfully |
| Kalshi API | ✅ All 24 markets fetched with live bid/ask |
| Model-vs-market gap < 2°F | ❌ ALL 4 CITIES FAIL (DEN 2.8, NYC 3.0, MIA 5.4, CHI 3.3) |
| NO-heavy core (≥4F from center) | N/A — blocked by gap gate |
| YES lottery (model within 1F) | N/A — blocked by gap gate |
| MIA blacklist | N/A — blocked by gap gate |

**Decision: NO QUALIFIED PICKS for 2026-09-07. Hold cash.**

---

*Discipline note: The RED FLAG gate exists exactly for days like this. The TWC double-count rule prevents us from stacking our NWS+TWC model against a market that may already incorporate TWC data. Every city today has a ≥2°F gap — the market and our model disagree on all four. This is not an edge; it's a disagreement. When we can't tell who's right, we hold cash. No exceptions, no "just this once."*