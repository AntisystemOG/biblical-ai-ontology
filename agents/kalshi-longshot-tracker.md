# Agent: kalshi-longshot-tracker

**Purpose:** Daily long-shot scan of Kalshi weather markets. Finds bands/thresholds
priced <= $0.30 where our model (NWS adjusted + TWC +1.5F bias, sigma 1.7F) gives a
probability meaningfully higher than the real ask. Paper-stakes $1 per shot (max 5/day,
max 1/city), grades at settlement, builds ROI stats by edge bucket — so we learn
whether long shots pay BEFORE risking real money.

**Script:** `C:\Users\thadd\.openclaw\workspace\scripts\kalshi_longshot_tracker.py`
**Data:** `C:\Users\thadd\.openclaw\workspace\data\longshots\`
**Cron:** `kalshi-longshot-tracker` — daily 8:45 PM CDT (after weather-paper-trader)

**Hard rules baked in:**
- YES semantics parsed from `rules_primary`, never from the ticker (T-tickers can be
  either side — this exact mistake caused the Aug 26 Denver loss).
- Real Kalshi API prices only; if the API fails, report and hold cash.
- Paper stakes only until Thad approves live long-shot sizing.

**Silent monitoring:** replies NO_REPLY on quiet nights; reports only when a bet
settles or an exceptional edge (>= +0.30) appears.