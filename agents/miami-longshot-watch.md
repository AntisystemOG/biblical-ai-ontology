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

## STANDING ORDER (Thad, 10:00 AM Aug 29 — supersedes consult-first for these positions)
"If any signals come in that tell you we are NOT going to make the long shot, sell immediately."

Sell immediately (act, then report):
1. KMIA obs >= 90F -> sell ALL Miami (band {88,89} + <88 both mathematically dead; max is monotone)
2. KMIA/TWC integer read >= 88 -> <88 ticket dead: sell T88 into remaining bid; HOLD band (a TWC 88 or 89 read still WINS the band)
3. NYC obs >= 83F -> NY 81-82 dead -> dump pennies
- Price-drop alone is NOT falsification (Aug 27 lesson). Temp-based only, verified vs https://weather.com/kalshi.
- Selling winners: band bid >= 0.35 or T88 >= 0.30 -> alert + recommend take-profit, Thad decides.

## Position set (Aug 29 09:57)
- MIA 88-89 band YES 43sh (cost $2.70) — core long shot
- MIA <88 threshold YES 10.1sh @ 0.15 (KXHIGHMIA-26AUG29-T88, Thad added ~09:57, $1.49) — storm-washout ticket; combined MIA structure pays if the daily high lands anywhere ≤ 89 (rain-cap → <88 pays; partial cap → 88-89 band pays $43); only a clean 90+ day kills both (-$4.19 total MIA downside)
- Alert rules now: band bid <= 0.09 / >= 0.35, or T88 yes_bid <= 0.06 / >= 0.30, or KMIA obs >= 90 (all MIA positions dead → pre-authorized penny-dump), NY obs >= 80, position vanished (settled vs https://weather.com/kalshi)
- Note: TWC +1.5-2F bias is the enemy of the <88 bet specifically (NWS 87-88 peaks -> TWC ~89); its win needs a real washout. Band {88,89} remains the primary win path.

## First-run

- MIA 88-89 YES: 43sh, cost $2.70, bid 0.20 (+$5.90 unrealized), market 21-24%, our model ~30-34%
  (TWC +1.5-2F bias on NWS 87-88 hourly peaks, storms p44-58% through peak heat).
- NY 81-82: 5%, sunk, hold.
- Cash $64.93 after Denver Aug28 NO settle (+$15.00). Account ~$80.57.

Remove via `cron remove` after settlement grades (Sun midday).