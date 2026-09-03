# Kalshi Morning Brief — consolidated daily scan (5:45 AM Mon-Fri)

**Purpose:** ONE morning job that replaces the old trio (the-edge-morning + kalshi-daily-predictions + kalshi-job-morning, all fired 5:30-6:00 AM on a 2-core laptop). Consolidated 2026-09-03 during the cron audit. Old jobs are DISABLED (not deleted) for rollback.

**Sequence:** positions -> grading -> claims digest -> weather boards -> max-2 web searches -> one compact brief.

## Steps (the cron runs these; agent file is the reference)
1. `python C:\Users\thadd\.openclaw\workspace\scripts\kalshi_position_table.py` - cash + open positions + verdicts
2. `python grade_predictions.py` in Kalshi Edge Scanner - learning loop
3. `python -X utf8 digest.py claims` in Kalshi Edge Scanner - ladder + edge
4. `python C:\Users\thadd\.openclaw\workspace\scripts\kalshi_weather_boards.py` - weather boards vs NWS
5. Web (max 2 searches): overnight labor news, weather pattern shifts
6. ONE compact plain-English brief (fixed-width, under 14 lines)

## Standing rules baked into the brief
- SILENCE RULE: nothing actionable or changed -> output exactly NO_REPLY
- Verify digest claims history against FRED before trusting (Edge cron once claimed 209K when FRED says 203K for week ending Aug 22)
- PROMPT-LAW: odds movement alone is never an exit; settlement-grade falsification only
- Kalshi universal: real API prices or hold cash
- Pre-order gate (kalshi_pre_order_check.py) before ANY order; never buy bands 2F+ above market center; MIA blacklist active
- Buying = consult Thad first. Selling losing weather positions = act then report.

## Rollback
If this brief fails 2 mornings in a row: re-enable the-edge-morning, kalshi-daily-predictions, kalshi-job-morning (disabled 2026-09-03, payloads intact with [PROMPT-LAW] text), then debug this one.