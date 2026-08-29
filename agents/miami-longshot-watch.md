# Miami Longshot Settlement Watch (TEMPORARY — Aug 29 only)

**Remove this agent + cron after Aug 29 weather settlements grade (expected Sun morning).**
Addendum to REGISTRY.md table: cron name = `miami-longshot-watch` (matches this file).

## Purpose
Thad authorized holding two long shots (Aug 29, "don't get greedy, don't jump out stupid"):
- Miami 88-89 degree band, 43 YES shares, cost $2.70 (KXHIGHMIA-26AUG29-B88.5) — the live one, settles tonight
- NY 81-82 degree band, 5.1 YES shares, cost $0.54 (settle tonight)
- Fed "no hike" 12.8sh — Sept event, no intraday action

## Watch script
`C:\Users\thadd\.openclaw\workspace\scripts\watch_miami_hold.py`
(KMIA/NYC obs + NWS hourly + live Kalshi quotes in one run)

## Cron behavior
Every 90 min, isolated agentTurn:
1. Run the script (utf-8 env, -X utf8).
2. Alert Thad ONLY if: MIA band yes_bid <= 0.09 (dying), >= 0.35 (payout forming),
   KMIA obs >= 90 (band mathematically dead — pre-authorized loss cut per standing rule),
   NY obs >= 80 (secondary band live), or position missing from board (settled — verify TWC page https://weather.com/kalshi).
3. Otherwise reply NO_REPLY (silent).
Default discipline: HOLD to settlement. Selling winners = consult Thad first;
selling losers = pre-authorized, act then report.

## First-run notes (Aug 29 ~9:45 AM)
- MIA 88-89 YES: 43sh, cost $2.70, bid 0.20 (+$5.90 unrealized), market 21-24%, our model ~30-34%
  (TWC +1.5-2F bias on NWS 87-88 hourly peaks, storms p44-58% through peak heat).
- NY 81-82: 5%, sunk, hold.
- Cash $64.93 after Denver Aug28 NO settle (+$15.00). Account ~$80.57.

Remove via `cron remove` after settlement grades (Sun midday).