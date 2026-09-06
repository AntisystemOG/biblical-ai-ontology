# Peak-Exit Watch v2 — trajectory-based timing (Thad directive Sep 5)

**Purpose:** Improvements 3+4 from the timing plan: salvage on PHYSICS (obs_max + remaining_possible_climb vs win range), not the clock; confidence-priced exits on TWC rounding risk.

**Cron:** `peak-exit-watch`, half-hourly 13:00-17:00 CT daily ("0,30 13-16 * * *" + 17:00 pass). Silent unless it acts.

**Script (read-only; cron agent executes):**
```
C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe C:\Users\thadd\.openclaw\workspace\scripts\kalshi_peak_exit.py
```

## What it computes per position (today's KXHIGH markets, YES + NO)
- obs_max today (NWS station obs), TWC proxy = obs_max + 1.5
- remaining possible climb by hour: 13:00 +4F .. 16:00 +0.5F (physics cap)
- win range in proxy terms: YES band [lo+1.0, hi+1.9] | NO inverted | greater thr -> proxy >= thr+2.0 | less thr -> proxy <= thr+0.9
- verdicts: WINNING (hold / sell-coin-flip) | DEAD-trajectory (salvage now) | WATCH

## Execution rules (act then report; selling pre-authorized, buying forbidden)
| Verdict | Action |
|---|---|
| WINNING, bid >= 0.90 | HOLD to settlement |
| WINNING near edge (proxy within 0.4F of range edge), bid >= 0.65 | SELL at bid (rounding coin-flip priced - improvement 4) |
| DEAD (trajectory confirms) | SALVAGE all filled shares at bid (IoC). Skip if bid < 0.02 |
| WATCH | No action; report only if trajectory changed materially |

## Notes
- Replaces sep4-exit-watch (one-day cron, expired). This version: any day, any city, YES + NO sides.
- TWC border cases: verify https://weather.com/kalshi before borderline sells.
- The NO-side death test: NO dies iff proxy enters the band's proxy range (e.g., band 87-88 = proxy 88.0-89.9).