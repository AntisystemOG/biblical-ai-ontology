# HEARTBEAT.md

## MANDATORY: Memory Check
Before doing anything else, check if today's memory file exists:
- If `memory/YYYY-MM-DD.md` doesn't exist for today, CREATE IT
- Scan recent conversation for anything worth logging: decisions, events, new info, errors, lessons
- If today's file exists, APPEND anything new since last entry
- This is NOT optional. If you skip this, you lose continuity.

## Periodic Tasks
- Check if daily memory has been written today
- Review MEMORY.md for anything outdated (weekly)
- Check for stuck/timed-out sessions and report them to Thad

## Session Health
- If you find stuck sessions (status: timeout, abortedLastRun: true), report them
- When spawning subagents, ALWAYS set runTimeoutSeconds (default: 300 = 5 min)
- Never spawn subagents without a timeout — they hang forever otherwise