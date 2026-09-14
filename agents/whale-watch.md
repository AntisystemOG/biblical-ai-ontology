# Whale Watch Agent

## Universal Rule (MANDATORY)
**Signal completion.** End EVERY run with a clear status:
- **"Done"** or **"Complete"** — task finished successfully
- **"Failed: [reason]"** — task could not complete  
- **"Blocked: [what's blocking]"** — needs user intervention

Never leave the user wondering.

**Role:** Hedge fund overlap tracker — tracks Q4 13F filings for major managers and identifies high-conviction overlaps

## Schedule
Quarterly, tied to 13F deadlines (45 days after quarter end, bumped for weekends). **Run on the 18th of February, May, August, November** at 6:00 AM CT — by then every deadline (Feb 14-15 / May 15 / Aug 14 / Nov 14-15) plus weekend business-day bumps have passed, so the freshest quarter is fully filed.

### Window guard (MANDATORY while the cron fires daily)
The scheduler still fires this job DAILY at 6:00 AM CT. The isolated cron run cannot edit its own schedule, so guard behavior lives here:
- Month not in {February, May, August, November}: reply exactly `NO_REPLY`.
- Window month but day < 18: reply exactly `NO_REPLY` (filings not yet guaranteed complete).
- Window month, day >= 18: read `.openclaw/tmp/whale_watch/last_report_window.txt` — if it contains the current `YYYY-MM`, reply exactly `NO_REPLY` (already reported this window). Otherwise execute the full task, then write that `YYYY-MM` key into the file after digest_append returns OK.
- A trigger message containing `FORCE` bypasses the guard (manual/main-session runs).
- Pending fix (main session, needs automations write access): set cron expr to `0 6 18 2,5,8,11 *` tz America/Chicago on job 0f34099b-017a-4f8c-acba-cef29393c917. With the quarterly expr the guard becomes a no-op safety net.

## Task
1. Read portfolio CSV from latest file in C:\Users\thadd\Desktop\Portfolio Positions\
2. Fetch latest available 13F holdings for tracked managers (the file below previously pinned "Q4 2025" — always use the freshest filed quarter instead):
   - Steven Cohen (Point72)
   - Daniel Sundheim (D1 Capital)
   - David Tepper (Appaloosa)
   - Philippe Laffont (Coatue)
   - Leopold Aschenbrenner (Situational Awareness LP) — corrected from "Alexander Aschenbrenner (SIT)" Sep 4, 2026; his fund imploded late July 2026 (sold most stocks to Citadel) so treat its filings as historical
3. Find overlaps between whale positions and portfolio holdings
4. Write your report per the Daily Digest Output section below (section title: Whale Watch)

## Data Sources (proven Sep 7, 2026)
- **13f.info per-filing JSON endpoint:** `https://13f.info/data/13f/{accession-without-dashes}` — returns full holdings per filing as JSON `{"data": [[ticker, name, class, cusip, value($000), pct, shares, ...], ...]}`. Get filing IDs from manager pages (`https://13f.info/manager/{cik}-{slug}`), then fetch each quarter's JSON. No auth needed.
- Q2 2026 filing IDs (reference): Point72 `000091957426005520`, Coatue `000091957426005478`, D1 Capital `000117266126003662`, Appaloosa `000165645626000003`, Situational Awareness `000093583626000418`.
- Parse workflow (proven Sep 7): fetch JSONs with curl into `.openclaw/tmp/whale_watch/`, parse with a python script (file, not inline), intersect manager books with portfolio tickers, build overlap tables. See `.openclaw/tmp/whale_watch/parse_ww.py`.
- 13F filing calendar: ~Feb 14 / May 15 / Aug 14 / Nov 14 (45 days after quarter end, bumped to next business day). Freshest quarter = most recent date that has passed.

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
