# daily-weather-picks

- **Type:** Recurring daily cron (standing — the locked entry-timing mechanism)
- **Created:** 2026-09-06 06:55 CDT (Thad 06:48: use the validated approach for tomorrow, only if timing is locked)
- **Schedule:** daily 8:15 AM CT (cron `15 8 * * *`, America/Chicago), isolated run, model ollama/glm-5.2:cloud, timeout 600s, delivery announce
- **Agent config path:** C:\Users\thadd\.openclaw\workspace\agents\daily-weather-picks.md

## Task list (payload)
1. Fetch fresh NWS forecasts for TODAY (DEN/NYC/MIA/CHI) + live Kalshi band ladders via the Edge Scanner (`C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner`). Real API prices only — never simulate. If the API fails, report and hold cash.
2. Compute market center (YES-mid-weighted) + model center (NWS + 1.5F TWC bias; storm cap -5F if storm probability >40%, cloud -2F if >75% cover).
3. HARD GATES (no exceptions):
   - NO-heavy core: NO on bands >= 4F from market center; never pay >= 94c without >= 5F cushion; never NO against > 85% consensus without a data advantage.
   - YES lotteries: only if model center within 1F of market center AND entry <= 2.2% of bankroll AND aggregate per-day YES-lottery exposure <= 3% of settled bankroll (gate enforces: kalshi_pre_order_check.py `_same_day_lottery_exposure`).
   - MIA blacklist: no Miami low-side lots.
   - Model-vs-market center gap >= 2F = RED FLAG = skip (TWC double-count rule).
4. Output: Thad-friendly proposal, max 3 picks, dollar sizes, odds, why + the peak-window hours for the exit watcher — or exactly "NO QUALIFIED PICKS for <date>". PROPOSAL ONLY — do NOT place orders; Thad approves all buys.
5. Save to `data/reports/daily_picks_<date>.md` and reply with the proposal text.

## Context
- Timing discipline (Sep 4 lesson): entries morning-of after overnight NWS settles — never night-before commitments except maker prices the morning would accept.
- Validated programs only: sure-things (5-8%), NO core bands, claims weekly clock (16/16). Lotteries capped (paper 1/14; 0-for-3 live days).
- Peak-exit watcher v2 arms same-day (13:00-16:30 CT half-hourly); exit plans written at entry.
- All three Sep 4 lesson fixes verified in code 2026-09-06 06:47 (spike rule, lottery cap, cost fix).