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
5. Update C:\Users\thadd\OneDrive\Desktop\Spocks Reports\market\trading_arena.html

## Important Notes
- Runs every 30 minutes during market hours only
- Embed snapshot data directly in HTML (file:// protocol blocks fetch)
- Requires market hours check (skip on weekends/holidays)