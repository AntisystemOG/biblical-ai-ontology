# Daily Weather Picks — September 11, 2026 (Friday)

**Generated:** 2026-09-11 08:15 AM CT (13:15 UTC)
**NWS fetch:** Live from api.weather.gov at 13:15 UTC
**Kalshi prices:** Live API via Edge Scanner at 13:15 UTC
**Bankroll:** $0.44 cash | ~$77.21 portfolio (jobless claims + Fed positions)

---

## NO QUALIFIED PICKS for 2026-09-11

All four cities triggered the **RED FLAG** (model-vs-market center gap ≥ 2F). Per the TWC double-count rule, every city is skipped.

---

## Full Analysis

### NWS Forecasts (fetched 13:15 UTC)

| City | NWS High | PoP | Forecast | Wind |
|------|----------|-----|----------|------|
| DEN  | 92°F     | 4%  | Mostly Sunny | NNE 3-8 mph |
| NYC  | 81°F     | 12% | Mostly Sunny | NW 12 mph |
| MIA  | 89°F     | 56% | Chance Showers/Thunderstorms | SE 10 mph |
| CHI  | 76°F     | 0%  | Sunny | ESE 5-10 mph |

### Model vs. Market Centers

| City | Market Center | Model Center | Gap | Status |
|------|--------------|-------------|-----|--------|
| DEN  | 91.0°F       | 93.5°F (NWS 92 + 1.5 TWC) | 2.5°F | 🔴 RED FLAG |
| NYC  | 80.1°F       | 82.5°F (NWS 81 + 1.5 TWC) | 2.4°F | 🔴 RED FLAG |
| MIA  | 90.2°F       | 85.5°F (NWS 89 + 1.5 TWC - 5 storm) | 4.7°F | 🔴 RED FLAG |
| CHI  | 81.0°F       | 77.5°F (NWS 76 + 1.5 TWC) | 3.5°F | 🔴 RED FLAG |

**Why every city flagged:**
- **DEN**: Market is pricing 91°F center (heavy weight on 91-92 band at 62¢ YES). NWS says 92°F + 1.5 TWC = 93.5°F model. Gap = 2.5°F. The market is *below* NWS, meaning TWC bias pushes our model even further from market — the double-count rule fires.
- **NYC**: Market center 80.1°F (79-80 and 81-82 bands split the weight). NWS 81°F + 1.5 = 82.5°F model. Gap = 2.4°F. Market is cooler than NWS forecast.
- **MIA**: Market center 90.2°F (90-91 band dominates at 67¢ YES). NWS 89°F + 1.5 TWC - 5 storm cap = 85.5°F model. Gap = 4.7°F. Storm cap creates a massive divergence — market isn't pricing the storm cooling effect.
- **CHI**: Market center 81.0°F (80-81 band at 53¢ YES). NWS 76°F + 1.5 = 77.5°F model. Gap = 3.5°F. Market is pricing 4-5°F warmer than NWS — the lake breeze ESE wind isn't being discounted by the market.

### Gate Results

**NO-heavy core:** 0 qualified picks. All four cities skipped due to RED FLAG (model-vs-market gap ≥ 2F).

**YES lotteries:** 0 qualified picks. The RED FLAG gate blocks YES entries too (requires model center within 1F of market center, which can't be met when gap ≥ 2F).

**MIA blacklist:** N/A (no YES lottery candidates reached this gate).

### Existing Weather Positions (held from prior entries)

| Ticker | Position | Cost | Notes |
|--------|----------|------|-------|
| KXHIGHDEN-26SEP11-B93.5 | 3 YES | $0.27 | 93-94°F band — NWS 92 + 1.5 = 93.5 model, market mid 5¢. Long shot. |
| KXHIGHCHI-26SEP11-B76.5 | 4 YES | $0.28 | 76-77°F band — NWS 76, model center 77.5. Close to model. Cheap lottery. |

Both existing positions are tiny lottery tickets ($0.27 and $0.28). They can be held to settlement — no action needed.

### Bankroll Note

Cash is **$0.44**. The vast majority of the bankroll ($69.15) is deployed in jobless claims positions (KXJOBLESSCLAIMS-26SEP17) settling today, plus ~$9.26 in Fed decision positions. Even if picks had qualified, sizing would be penny-scale at current cash. After jobless claims settle (8:30 AM ET today), bankroll should refresh for tomorrow's entries.

---

## Peak-Exit Watcher

**Not armed** — no picks to watch. Next opportunity: tomorrow (Sep 12) morning at 8:15 AM CT.

---

## Data Sources

- **NWS forecasts:** api.weather.gov gridpoints (BOU/63,62, OKX/33,42, MFL/110,50, LOT/76,73) — fetched 13:15 UTC Sep 11
- **NWS hourly:** Same gridpoints /forecast/hourly — fetched 13:15 UTC Sep 11
- **Kalshi prices:** Live API via Edge Scanner KalshiClient — fetched 13:15 UTC Sep 11
- **TWC bias:** +1.5°F (config.json strategy)
- **Storm cap:** -5°F applied to MIA (PoP 56% > 40%, thunderstorms in forecast, morning timing = full penalty)

## Methodology

1. Market center = YES-mid-weighted average of all band centers
2. Model center = NWS high + 1.5°F TWC bias; -5°F storm cap if PoP > 40% with storms in forecast; -2°F cloud cap if > 75% cover (not triggered today — MIA forecast says "Mostly sunny" despite storms)
3. Hard gates applied: RED FLAG (gap ≥ 2F), NO cushion (≥ 4F from market center, < 94c without ≥ 5F cushion), YES lottery (model within 1F of market, ≤ 2.2% bankroll, ≤ 3% aggregate), MIA low-side blacklist
4. All gates enforced — no exceptions taken