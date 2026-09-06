# Daily Weather Picks — 2026-09-06 (Sunday)

**Generated:** 2026-09-06 08:15 AM CT (13:15 UTC)
**Bankroll:** $54.53 (all cash, no open positions)
**NWS fetch:** forecast.weather.gov JSON API, ~13:15 UTC
**Kalshi prices:** Live API via Edge Scanner KalshiClient, ~13:15 UTC

---

## NO QUALIFIED PICKS for 2026-09-06

---

## City Analysis

### DEN (Denver)
| Metric | Value |
|---|---|
| NWS High | 94°F |
| POP | 20% (slight chance t-storms after 3pm) |
| Market Center | 91.2°F (50% YES crossover, interpolated between 91/93 strikes) |
| Model Center | 95.5°F (NWS 94 + 1.5 TWC bias, no storm cap — POP < 40%) |
| Gap | **4.2°F — RED FLAG** |

**Verdict: SKIP.** Model runs 4.2°F hotter than market. TWC double-count rule triggered — the market is pricing a cooler outcome than NWS implies, likely on storm potential that the model doesn't fully capture. Gap ≥ 2°F = hard skip.

**Band ladder (live API):**
| Strike | YES mid | NO ask | Dist from MC |
|---|---|---|---|
| 89 | 0.185 | 0.82 | 2.2°F |
| 91 | 0.555 | 0.45 | 0.2°F |
| 93 | 0.115 | 0.89 | 1.8°F |
| 95 | 0.015 | 0.99 | 3.8°F |

No NO-heavy bands ≥ 4°F from market center at acceptable pricing. Strike 95 at 3.8°F away, NO ask 0.99 (too expensive, < 5F cushion).

---

### NYC (New York)
| Metric | Value |
|---|---|
| NWS High | 74°F |
| POP | 20% (slight chance showers before 2pm) |
| Market Center | 75.2°F (interpolated between 75/77 strikes) |
| Model Center | 75.5°F (NWS 74 + 1.5 TWC bias, no storm cap, no cloud cap) |
| Gap | **0.3°F — OK** |

**Verdict: PROCEED to gate checks, but no qualifying picks emerge.**

**Band ladder (live API):**
| Strike | YES mid | NO ask | Dist from MC |
|---|---|---|---|
| 73 | 0.365 | 0.64 | 2.2°F |
| 75 | 0.535 | 0.47 | 0.2°F |
| 77 | 0.110 | 0.90 | 1.8°F |
| 79 | 0.005 | 1.00 | 3.8°F |

- **NO-heavy core:** No bands ≥ 4°F from market center. Strike 79 is 3.8°F away (just under 4°F threshold) and NO ask is $1.00 (untradable). No qualifying NO picks.
- **YES lottery:** Model within 1F of market (0.3°F gap — passes). However:
  - Strike 73 YES at 0.37: Model says high ~75.5, so YES > 73 should win. But at 37c this is a moderate favorite, not a lottery, and the 73-strike YES isn't in the "sure things" program (which targets 5-8% bankroll at high-probability prices ≥ 80c).
  - Strike 75 YES at 0.54: Model 75.5 barely above 75. Coin-flip territory — high variance, not a validated program pick.
  - Strikes 77/79 YES: Model 75.5 < 77 and < 79 — model says NO, skip.
  - **YES lottery track record: 0-for-3 live days (not in validated programs).** Per discipline, pass.

---

### MIA (Miami)
| Metric | Value |
|---|---|
| NWS High | 89°F |
| POP | 60% (storms likely 3-5pm) |
| Market Center | 90.5°F (interpolated between 90/92 strikes) |
| Model Center | 85.5°F (NWS 89 + 1.5 TWC − 5 storm cap, POP > 40%) |
| Gap | **5.0°F — RED FLAG** |

**Verdict: SKIP.** Storm cap pulls model 5°F below market. Market is pricing high ~90-91, model says storm-cooled 85.5. Gap ≥ 2°F = hard skip. **MIA blacklist also active** — no Miami low-side lots regardless.

**Band ladder (live API):**
| Strike | YES mid | NO ask | Dist from MC |
|---|---|---|---|
| 86 | 0.065 | 0.94 | 4.5°F |
| 88 | 0.095 | 0.92 | 2.5°F |
| 90 | 0.565 | 0.44 | 0.5°F |
| 92 | 0.285 | 0.73 | 1.5°F |
| 93 | 0.045 | 0.96 | 2.5°F |

Strike 86 NO at 0.94 with 4.5°F cushion — looks close, but cushion < 5F and no_ask ≥ 94c → rejected by hard gate. MIA blacklist also blocks low-side plays.

---

### CHI (Chicago)
| Metric | Value |
|---|---|
| NWS High | 72°F |
| POP | 0% (sunny, clear) |
| Market Center | 79.2°F (interpolated between 79/81 strikes) |
| Model Center | 73.5°F (NWS 72 + 1.5 TWC bias, no storm cap, no cloud cap) |
| Gap | **5.7°F — RED FLAG** |

**Verdict: SKIP.** NWS says 72°F with east-northeast wind at 10 mph (lake breeze). Market is pricing 79°F — a massive 5.7°F gap. The market is likely pricing a warm-up the NWS hasn't fully incorporated, or the TWC (Weather Company) data the market resolves on runs hotter. Either way, gap ≥ 2°F = hard skip per TWC double-count rule.

**Band ladder (live API):**
| Strike | YES mid | NO ask | Dist from MC |
|---|---|---|---|
| 75 | 0.060 | 0.95 | 4.2°F |
| 77 | 0.275 | 0.73 | 2.2°F |
| 79 | 0.545 | 0.47 | 0.2°F |
| 81 | 0.125 | 0.88 | 1.8°F |
| 82 | 0.005 | 1.00 | 2.8°F |

Strike 75 NO at 0.95 with 4.2°F cushion — but no_ask ≥ 94c and cushion < 5F → rejected by hard gate.

---

## Summary

| City | NWS | Model | Market | Gap | Status |
|---|---|---|---|---|---|
| DEN | 94°F | 95.5°F | 91.2°F | 4.2°F | 🔴 RED FLAG — skip |
| NYC | 74°F | 75.5°F | 75.2°F | 0.3°F | ✅ Gap OK, but no qualifying picks |
| MIA | 89°F | 85.5°F | 90.5°F | 5.0°F | 🔴 RED FLAG — skip + MIA blacklist |
| CHI | 72°F | 73.5°F | 79.2°F | 5.7°F | 🔴 RED FLAG — skip |

**Result: NO QUALIFIED PICKS for 2026-09-06**

All cash held. Three of four cities flagged red on the model-vs-market gap (TWC double-count rule). NYC passed the gap check but had no NO-heavy bands ≥ 4°F from market center at acceptable pricing, and YES lottery plays are not in the validated programs (0-for-3 live track record). Discipline says hold.

---

## Peak-Exit Watcher
**Not armed** — no entries today, nothing to watch.

---

*Data sources: NWS forecast.weather.gov (fetched 13:15 UTC), Kalshi live API via Edge Scanner KalshiClient (fetched 13:15 UTC). Real API prices only — no simulations. Proposal only — Thad approves all buys.*