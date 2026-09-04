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
- Runs every 30 minutes during market hours only
- Embed snapshot data directly in HTML (file:// protocol blocks fetch)
- Requires market hours check (skip on weekends/holidays)

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
