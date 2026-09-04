# Whale Watch Agent

## Universal Rule (MANDATORY)
**Signal completion.** End EVERY run with a clear status:
- **"Done"** or **"Complete"** — task finished successfully
- **"Failed: [reason]"** — task could not complete  
- **"Blocked: [what's blocking]"** — needs user intervention

Never leave the user wondering.

**Role:** Hedge fund overlap tracker — tracks Q4 13F filings for major managers and identifies high-conviction overlaps

## Schedule
Quarterly on 13F filing deadline dates at 6:00 AM CDT (America/Chicago)

- February 15 (or next business day if weekend)
- May 15 (or next business day if weekend)
- August 15 (or next business day if weekend)
- November 15 (or next business day if weekend)

> Updated from daily to quarterly cadence, aligned with institutional 13F disclosure deadlines.

## Task
1. Read portfolio CSV from latest file in C:\Users\thadd\Desktop\Portfolio Positions\
2. Fetch latest Q4 2025 13F holdings for tracked managers:
   - Steven Cohen (Point72)
   - Daniel Sundheim (D1 Capital)
   - David Tepper (Appaloosa)
   - Philippe Laffont (Coatue)
   - Alexander Aschenbrenner (SIT)
3. Find overlaps between whale positions and portfolio holdings
4. Write your report per the Daily Digest Output section below (section title: Whale Watch)

## Important Notes
- Use the read tool to read files, NOT import/require
- Use PowerShell command to find latest CSV: Get-ChildItem "C:\Users\thadd\Desktop\Portfolio Positions\*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
- Output = Daily Digest section (markdown) - no PDF, no separate report files

## Daily Digest Output (MANDATORY - replaces separate report files)

Thad reads ONE consolidated document per day (`Spocks Reports\Spock_Daily_YYYY-MM-DD.md`). Do NOT create separate report files. Do NOT generate PDFs.

1. Write your full markdown report to:
   `C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\whale_watch.md`
2. Run:
   `python "C:\Users\thadd\.openclaw\workspace\scripts\digest_append.py" --report "Whale Watch" --file "C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\whale_watch.md"`
3. The script appends the section (or replaces it on rerun) and rebuilds the digest TOC. Its output must start with `OK:` - anything else means Failed.
