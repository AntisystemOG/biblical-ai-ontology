# Sep 4 Ridge-Bet Exit Watch — city peak windows

**Purpose:** Thad directive Sep 3: "build an exit strategy if things go sideways. Each city hits its highest temp at a predictable time — that's when we look at the odds again and determine hold vs settle for a loss or less profit."

**Cron:** `sep4-exit-watch`, hourly 11:00-19:00 CT on **Sep 4 only** (cities peak 13-16 CT; markets settle 2 AM Sat).

**Open positions (Sep 4):** DEN >95 YES (7.53 filled + 67.47 resting @ 4c), DEN 94-95 YES (15 resting @ 23c), NY 86-87 YES (11 filled @ 13c), MIA 93-94 YES (5+ filled, 17 resting @ 12c).

## Script (run first, read-only)
```
C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe C:\Users\thadd\.openclaw\workspace\scripts\kalshi_sep4_exit.py
```
Prints per city: obs latest/max, TWC proxy (obs+1.5), peak window status, live book, and a verdict per market.

**IMPORTANT: script assumes run date = settlement date (Sep 4).** Running it Sep 3 compares today's obs against tomorrow's markets — data is informational only, verdicts ignore.

## Win ranges (proxy terms: proxy = obs_max + 1.5; TWC integer T maps to proxy [T+1.0, T+1.9])
| Market | Wins when proxy... |
|---|---|
| DEN T95 (>95, i.e. 96+) | >= 97.0 |
| DEN B94.5 (94-95) | 95.0 - 96.9 |
| NY B86.5 (86-87) | 87.0 - 88.9 |
| MIA B93.5 (93-94) | 94.0 - 95.9 |

## Execution rules (in order; act then report)
| # | Condition | Action |
|---|---|---|
| 1 | Verdict DEAD or DEAD-EARLY on a HOLDING | SELL all filled shares at bid (IoC). If bid < 0.02, skip (nothing to salvage), say so |
| 2 | Verdict DEAD on a RESTING unfilled order | CANCEL it (never buy a dead band) |
| 3 | Verdict WINNING and bid >= 0.90 | HOLD to settlement (no fee at 1.00, never sell a 95c+ winner) |
| 4 | Verdict WINNING and bid 0.40-0.90 | Optional profit-lock: sell allowed if bid giveback >30% from intraday high; default HOLD (peak math locked) |
| 5 | Verdict CLOSE/WATCH | No action; report only if moved materially |
| 5b | EARLY-DEATH TIMING (Thad: do not lose everything): if by 14:00 CT the proxy is 3F+ BELOW a win range AND obs climb rate cannot reach it (would need more than ~4F in the remaining peak window), treat as DEAD NOW - salvage sell at current bid instead of waiting for peak close (bids die fast post-peak; early salvage recovers more) |
| 6 | All cities peak passed (after 17:00 CT) | Final pass: salvage dead positions, cancel unfilled resting orders whose band is dead; report final board |
| 7 | DEN pair hedge: 94-95 + 96+ together cover proxy 95.0 through 96.9 AND >= 97.0. Both die ONLY if proxy ends below 95.0 (TWC <= 93) - in that case salvage BOTH immediately (rule 5b applies from 14:00 CT) |

## Authority
- Selling losing/weather positions + cancelling resting orders: PRE-AUTHORIZED (act, then report).
- Buying more = ask first. No new positions.
- TWC border cases (proxy within 0.9F of range edge): check https://weather.com/kalshi before acting.

## Settlement
All four settle 2026-09-05T07:00Z (2 AM CT Fri night). Settles on TWC: CLIDEN / KMDW / KNYC / CLIMIA.