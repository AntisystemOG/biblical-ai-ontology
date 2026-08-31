# lotto-exit-watch

## Task
Intraday falsification guard for open Kalshi lottery/weather legs. Prevents the
Aug-28-miss pattern: a long shot tanking intraday with nobody watching.

Run this command (set $env:PYTHONIOENCODING='utf-8' first):

& 'C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe' -X utf8 'C:\Users\thadd\.openclaw\workspace\scripts\lotto_exit_watch.py'

## What the script does
- Pulls live positions + station obs (KMDW, KNYC via api.weather.gov)
- Applies falsification matrix: sells DEAD legs immediately (losing-position exits are
  pre-authorized by Thad — act, then report)
- Alerts on big profitable bids (>= 0.60) — recommend hold toward par
- Prints NO_REPLY when all legs alive and quiet

## Your output rule
If the script output starts with NO_REPLY or is empty/quiet -> reply exactly NO_REPLY.
If it contains SOLD/DEAD/ALERT lines -> report them to Thad in a short plain-English
table (bets described plainly, dollar prices, under 10 lines). Never message on quiet runs.
Never sell based on odds noise alone - only the script's falsification triggers.

Agent config: C:\Users\thadd\.openclaw\workspace\agents\lotto-exit-watch.md