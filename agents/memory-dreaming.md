# Memory Dreaming Agent

## Universal Rule (MANDATORY)
**Signal completion.** End EVERY run with a clear status:
- **"Done"** or **"Complete"** — task finished successfully
- **"Failed: [reason]"** — task could not complete
- **"Blocked: [what's blocking]"** — needs user intervention

Never leave the user wondering.

**Role:** Memory synthesis agent — reviews daily memories, extracts patterns, generates insights

## Schedule
Daily at 3:00 AM CDT

## Task
1. Read previous day's memory file (memory/YYYY-MM-DD.md)
2. Analyze for:
   - Recurring themes
   - Decisions made
   - Tasks completed
   - Patterns and insights
3. Generate dream-like narrative reflection
4. Write your dream report to the Daily Digest per the Daily Digest Output section below (section title: Memory Dream). Digest date = TODAY (the morning it runs), even though the dream covers yesterday's memory file
5. Update MEMORY.md with distilled learnings (weekly)

## Important Notes
- Runs during low-activity hours
- Synthesizes information without user input
- Writes narrative-style reflections into the Daily Digest
- Section title: Memory Dream

## Daily Digest Output (MANDATORY - replaces separate report files)

Thad reads ONE consolidated document per day (`Spocks Reports\Spock_Daily_YYYY-MM-DD.md`). Do NOT create separate report files. Do NOT generate PDFs.

1. Write your full markdown report to:
   `C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\memory_dream.md`
2. Run:
   `python "C:\Users\thadd\.openclaw\workspace\scripts\digest_append.py" --report "Memory Dream" --file "C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\digest\memory_dream.md"`
3. The script appends the section (or replaces it on rerun) and rebuilds the digest TOC. Its output must start with `OK:` - anything else means Failed.
- Helps with long-term memory consolidation