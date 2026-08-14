# HEARTBEAT.md

## MANDATORY: Memory Check
Before doing anything else, check if today's memory file exists:
- If `memory/YYYY-MM-DD.md` doesn't exist for today, CREATE IT
- Scan recent conversation for anything worth logging: decisions, events, new info, errors, lessons
- If today's file exists, APPEND anything new since last entry
- This is NOT optional. If you skip this, you lose continuity.

## MANDATORY: Kalshi Job Market Scanner on First Login
When this is the first heartbeat of the day (check `memory/heartbeat-state.json` for `lastKalshiScan` date — if it's not today):
1. Wait 2 minutes after first login (use idle detection — if no user messages for 2 min)
2. Run the Kalshi Job Market Scanner: `cd "C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner" && C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe cli.py scan`
3. Search web for today's job market data: claims forecasts, NFP, unemployment rate, labor news
4. Save results to `data/scan_YYYY-MM-DD_morning.txt`
5. Report top picks to Thad
6. Update `memory/heartbeat-state.json` with `lastKalshiScan: "YYYY-MM-DD"`

The scanner also runs 3x daily via cron:
- **6:00 AM CDT** — Morning scan (pre-market, before claims close on Thursdays)
- **12:00 PM CDT** — Midday scan (post-release grading, afternoon opportunities)
- **8:00 PM CDT** — Evening review (pattern analysis, engine improvements, prep for tomorrow)

Heartbeat scan is a fallback if cron was missed. On Thursdays: MUST run before 7:25 AM CDT (claims markets close).

## Periodic Tasks
- Check if daily memory has been written today
- Review MEMORY.md for anything outdated (weekly)
- Check for stuck/timed-out sessions and report them to Thad

## Session Health
- If you find stuck sessions (status: timeout, abortedLastRun: true), report them
- When spawning subagents, ALWAYS set runTimeoutSeconds (default: 300 = 5 min)
- Never spawn subagents without a timeout — they hang forever otherwise