# twc-update-probe

- **Type:** TEMPORARY recurring cron — remove after cadence is documented (~24-48h)
- **Created:** 2026-08-29 07:30 CDT (Thad directive: we need the settlement page's update timing)
- **Schedule:** every 20 min, isolated run, delivery none (silent), failureAlert after 3
- **Model:** ollama-cloud/glm-5.2 (pinned), timeoutSeconds 180
- **Script:** `C:\Users\thadd\.openclaw\workspace\scripts\twc_update_probe.py`
- **Log:** `C:\Users\thadd\.openclaw\workspace\scripts\twc_probe_log.csv`
- **Target:** https://weather.com/kalshi ("The Weather Company | Kalshi Weather Data" — official settlement source, stored 2026-08-29)

## Job message (payload)
Run exactly:
`C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe C:\Users\thadd\.openclaw\workspace\scripts\twc_update_probe.py`
Reply with ONLY the single JSON line it prints. No analysis, no commentary. On error, reply with the error text only.

## Purpose
1. Measure how often the TWC settlement page actually updates (content-hash delta between 20-min samples).
2. Build an intraday running-high dataset per city for pattern detection (TWC vs NWS bias, high-lock timing).
3. Feed the future cut-loss monitor: TWC's own number piercing an open band's losing edge while heating hours remain = settlement-grade falsification = authorized cut signal (losing weather cuts pre-authorized; never cut on odds noise alone).

## Settlement clocks (for reference)
- Kalshi daily-high markets close 2:00 AM CDT; result expected by ~2:00 PM CDT; historically graded overnight (money landed by 7:22 AM on Aug 29).
- Daily high effectively locks ~5-7 PM local — last meaningful cut window before overnight grade.