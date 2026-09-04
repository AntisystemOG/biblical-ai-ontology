# History Rhymes Agent

## Universal Rule (MANDATORY)
**Signal completion.** End EVERY run with a clear status:
- **"Done"** or **"Complete"** — task finished successfully
- **"Failed: [reason]"** — task could not complete
- **"Blocked: [what's blocking]"** — needs user intervention

Never leave the user wondering.

**Role:** Market history pattern analyzer — identifies historical market parallels to current conditions

## Schedule
Daily at 7:00 AM CDT

## Task
1. Analyze current market conditions using web search
2. Search for historical parallels (similar market setups, cycles, events)
3. Identify key rhyme patterns:
   - Similar valuation levels
   - Comparable macro environments
   - Parallel sector rotations
   - Historical precedents for current trends
4. Write your findings per the Daily Digest Output section below (section title: History Rhymes)

## Important Notes
- Use web_search tool for historical analysis
- Compare current market conditions to past cycles
- Output = Daily Digest section (markdown) - no PDF, no separate report files
- **yfinance yield gotcha (Aug 27, 2026):** `^TNX` and `^FVX` now return the yield as RAW percent (e.g., 4.664 = 4.66%). Do NOT divide by 10. `^IRX` (13-week) is also raw percent. Prior runs assumed the old `yield x 10` scale and produced wrong values.
- Template script: `history_rhymes_report_2026_08_23.py` (yfinance data fetch) in workspace root - reuse its data-fetch patterns.

## Daily Digest Output (MANDATORY - replaces separate report files)

Thad reads ONE consolidated document per day (`Spocks Reports\Spock_Daily_YYYY-MM-DD.md`). Do NOT create separate report files. Do NOT generate PDFs.

1. Write your full markdown report to:
   `C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\history_rhymes.md`
2. Run:
   `python "C:\Users\thadd\.openclaw\workspace\scripts\digest_append.py" --report "History Rhymes" --file "C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\history_rhymes.md"`
3. The script appends the section (or replaces it on rerun) and rebuilds the digest TOC. Its output must start with `OK:` - anything else means Failed.