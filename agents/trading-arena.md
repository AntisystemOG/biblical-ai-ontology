# Trading Arena Agent

## Universal Rule (MANDATORY)
**Signal completion.** End EVERY run with a clear status:
- **"Done"** or **"Complete"** — task finished successfully
- **"Failed: [reason]"** — task could not complete
- **"Blocked: [what's blocking]"** — needs user intervention

Never leave the user wondering.

**Role:** Live trading simulation — 5 AI agents compete with different strategies, track performance vs S&P 500

## Schedule
Monday-Friday, 8:30 AM - 3:00 PM CDT, every 30 minutes during market hours

## Task
1. Run 5 AI traders with different strategies:
   - Turtle (trend following)
   - Shark (momentum)
   - Owl (value)
   - Wolf (sector rotation)
   - Fox (contrarian)
2. Each starts with $10,000
3. Compare performance to S&P 500 benchmark
4. Generate HTML dashboard with live standings
5. Update C:\Users\thadd\.openclaw\workspace\Spocks Reports\market\trading_arena.html

## Important Notes
- **Canonical runner:** `trading_arena.py` at the WORKSPACE ROOT (state: `.openclaw/tmp/trading_arena_state.json`, tracks run_count; writes OneDrive dashboard; mirror to `Spocks Reports\market\trading_arena.html`). Run it via a wrapper like `.openclaw/tmp/arena_run_HHMM_MMDD.py` (see 1200 Sep 9 example): SPY-bar holiday check -> `import trading_arena as ta; ta.main()` -> copy OneDrive HTML to the workspace mirror.
- **LEGACY — do NOT run:** `scripts/update_trading_arena.py`. It writes a different compact dashboard and no shared state (it silently reset-looking output on Sep 9, 11:30). Never use it for arena runs.
- Runs every 30 minutes during market hours only
- Embed snapshot data directly in HTML (file:// protocol blocks fetch)
- Requires market hours check (skip on weekends/holidays). 2026 US market holidays (NYSE closed, skip the whole day): Thu Jan 1, Mon Jan 19 (MLK), Mon Feb 16 (Washington), Fri Apr 3 (Good Friday), Mon May 25 (Memorial), Fri Jun 19 (Juneteenth), Fri Jul 3 (observed), Mon Sep 7 (Labor Day), Thu Nov 26 (Thanksgiving), Fri Dec 25 (Christmas). Quick verify: last SPY daily bar date — if it is not today, treat as a non-trading day and skip (no trader runs, no HTML update, no digest touch).

## Daily Digest Output (MANDATORY)

The HTML dashboard stays as-is (one file, updated in place every run). The Daily Digest (`Spocks Reports\Spock_Daily_YYYY-MM-DD.md`) gets a section ONLY on the final run of the day:

- If local time is 2:30 PM CT or later: append a "Trading Arena" section with the final standings (each trader's dollar P&L vs start, rank, S&P 500 comparison, best/worst strategy of the day).
- Before 2:30 PM CT: update the HTML only - do NOT touch the digest.

Procedure (final run only):
1. Write the standings markdown to:
   `C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\trading_arena.md`
2. Run:
   `python "C:\Users\thadd\.openclaw\workspace\scripts\digest_append.py" --report "Trading Arena" --file "C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\trading_arena.md"`
3. The script appends the section (or replaces it on rerun) and rebuilds the digest TOC. Its output must start with `OK:` - anything else means Failed.
