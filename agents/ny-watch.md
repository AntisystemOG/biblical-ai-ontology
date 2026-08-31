# NY Weather Band Watch — Aug 31, 2026

**Purpose:** Watch open NY weather positions (KXHIGHNY-26AUG31) through the day and execute the exit rules without over-holding or panic-selling. Cron: `ny-watch`, hourly 11:00-19:00 CT on Aug 31, 2026 only.

**Live positions (update after any trade):**
- `KXHIGHNY-26AUG31-B80.5` YES — 14.89 sh @ ~9.9c avg (14 sh pre-existing ~10c + 0.89 sh @ 6c, 9:17 AM)
- `KXHIGHNY-26AUG31-B80.5` YES — 23 sh maker resting @ 6c (order 01a05834, unfilled, free if fills)
- `KXHIGHNY-26AUG31-B82.5` YES — 12 sh @ 4c (pre-existing)
- Related same-day: `KXHIGHCHI-26AUG31-T89` YES — 4 sh @ 35c (not NY, but same settle window)

## Watcher script (run first, read-only)
```
C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe C:\Users\thadd\.openclaw\workspace\scripts\ny_watch_0831.py
```
It prints: KNYC obs (latest + today max), TWC proxy (+1.5F), live book, positions, and a verdict.

## Exit Rule Table (execute in this order, act then report)
| # | Condition | Action |
|---|---|---|
| 1 | TWC-proxy reading **> 81F** (band dead, max only rises) | Cancel resting order, SELL all NY band shares at bid (IoC), report after |
| 2 | Reading **inside 78-80F**, bid >= 40c | HOLD — winning path, ride to settlement |
| 3 | Intraday bid high >= 30c AND current bid < 70% of that high AND (reading > 80F or clock >= 17:30 CT) | SELL to lock profit (giveback rule) |
| 4 | After 19:00 CT, reading stuck <= 79F | Sell if bid >= 25c; else hold to settlement and say so |
| 5 | Reading 80-81F or proxy-max inside band | HOLD to settlement — no fee at 1.00, never sell a 95c+ winner |

## Hard rules
- Never sell a position when TWC-proxy max is inside 80-81 (that is the win).
- If resting order auto-cancels again, do NOT chase above 8c without asking Thad.
- SELLING = pre-authorized by Thad (act, then report). Buying more = ask first.
- Only message when: executed a trade, verdict changed, or bid/reading moved materially (>2c or >2F). Otherwise suppress.

## Settlement
Settles on The Weather Company reading for CLINYC (Central Park). Check https://weather.com/kalshi pre-close. Close: 2026-09-01T07:00:00Z (2 AM CT).