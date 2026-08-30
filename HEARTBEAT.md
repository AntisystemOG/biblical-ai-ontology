# HEARTBEAT.md

## MANDATORY: Memory Check
Before doing anything else, check if today's memory file exists:
- If `memory/YYYY-MM-DD.md` doesn't exist for today, CREATE IT
- Scan recent conversation for anything worth logging: decisions, events, new info, errors, lessons
- If today's file exists, APPEND anything new since last entry
- This is NOT optional. If you skip this, you lose continuity.

## MANDATORY: Kalshi Scanner on First Login (Updated Aug 16 — Timing-Aware)
When this is the first heartbeat of the day (check `memory/heartbeat-state.json` for `lastKalshiScan` date — if it's not today):
1. Wait 2 minutes after first login (use idle detection — if no user messages for 2 min)
2. Run the Kalshi Job Market Scanner: `cd "C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner" && C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe cli.py scan`
3. Search web for today's job market data: claims forecasts, NFP, unemployment rate, labor news
4. Save results to `C:\Users\thadd\.openclaw\workspace\data\kalshi\scan_YYYY-MM-DD_morning.txt` (workspace path - the write tool is workspace-restricted; never save under C:\AI Projects via the write tool)
5. Report top picks to Thad
6. Update `memory/heartbeat-state.json` with `lastKalshiScan: "YYYY-MM-DD"`

### Timing-Aware Behavior (NEW)
**What day of the week is it?** The scanner's behavior changes based on proximity to Thursday claims release:

- **Monday (T-3):** Buy window opens. Verify prediction quality. Log baseline prices. Don't rush to buy — only if edge >10%.
- **Tuesday (T-2):** Price check. Compare to Monday baseline. Sweet spot entry if edge >5%. Prices stabilized but not yet tightened.
- **Wednesday (T-1):** LAST CHANCE to pre-position. Verify forecast is still valid. Execute if edge >5% and confidence >80%. Don't wait for Thursday morning — algos dominate the first seconds after release.
- **Thursday (T-0):** Claims release day. Markets close at 7:25 AM CDT. If not positioned by 6:45 AM, final call. If edge <5%, PASS — capital preservation > forcing it. If already positioned, hold to settlement.
- **Friday:** Post-release grading. Run `python grade_predictions.py` to update learning loop.

**Key rule:** Getting the prediction right is #1. When we purchase is #2. Hold to settlement. Use maker/limit orders (free). Never force a trade.

The scanner also runs 3x daily via cron:
- **6:00 AM CDT** — Morning scan (pre-market, before claims close on Thursdays)
- **12:00 PM CDT** — Midday scan (post-release grading, afternoon opportunities)
- **8:00 PM CDT** — Evening review (pattern analysis, engine improvements, prep for tomorrow)

### Reminder Ladder (automated crons for claims week)
- **T-3 (Mon 9:30 AM):** Buy window open — verify prediction, log prices
- **T-2 (Tue 9:30 AM):** Price check — compare to T-3, sweet spot entry
- **T-1 (Wed 9:30 AM):** Last chance — execute if edge >5%, confidence >80%
- **T-0 (Thu 6:45 AM):** Final call — buy or pass, markets close in 25 min

Heartbeat scan is a fallback if cron was missed. On Thursdays: MUST run before 7:25 AM CDT (claims markets close).

## Gateway Down Recovery (Added Aug 16)
When the gateway restarts after being down, cron jobs that were missed get rescheduled automatically. Before letting stale jobs fire:
1. Check `cron list` for any jobs with `lastRunStatus: null` and a past `nextRunAtMs`
2. If a timing reminder (T-3/T-2/T-1/T-0) was missed but we're still in the buy window: run it manually
3. If the claims release already happened (Thursday past 7:30 AM CDT): skip missed buy alerts, run grading instead
4. **Ask Thad before forcing any missed job** — he may not want stale alerts firing
5. Log what was missed and what was recovered in today's memory file

## Periodic Tasks
- Check if daily memory has been written today
- Review MEMORY.md for anything outdated (weekly)
- Check for stuck/timed-out sessions and report them to Thad

## Session Health
- If you find stuck sessions (status: timeout, abortedLastRun: true), report them
- When spawning subagents, ALWAYS set runTimeoutSeconds (default: 300 = 5 min)
- Never spawn subagents without a timeout — they hang forever otherwise