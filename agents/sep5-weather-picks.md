# sep5-weather-picks

- **Type:** One-shot job (auto-deletes after completion)
- **Created:** 2026-09-04 16:55 CDT — Saturday Sep 5 weather book proposal with hardened gates
- **Schedule:** 2026-09-04 21:15 CDT, isolated run, model pinned ollama-cloud/glm-5.2, timeout 600s
- **Agent config path:** C:\Users\thadd\.openclaw\workspace\agents\sep5-weather-picks.md
- **Why this slot:** after the 8 PM lesson-apply code fixes (lottery cap + market-center flag) and after the 8:30 PM paper trader fetches fresh Saturday NWS evening forecasts.

## Task list (payload)
1. Fetch fresh NWS forecasts for Sep 5 (DEN / NYC / MIA / CHI) + live Kalshi band ladders via the Edge Scanner (`C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner`). Real API prices only — never simulate.
2. Compute market center from the live band ladder (YES-mid-weighted — the Sep 1 fix). Model center = NWS + 1.5F TWC bias.
3. HARD GATES (no exceptions):
   - NO-heavy core: NO on bands >= 4F from market center; never pay >= 94c for NO; never NO against > 85% consensus without a data advantage.
   - YES lotteries: only if model center within 1F of market center, entry <= 2.2% of bankroll (~$1.70), and aggregate per-day YES-lottery exposure <= 3% of settled bankroll (~$2.30 on a $77 book).
   - MIA blacklist: no Miami low-side lots (3 straight losses).
   - Model-vs-market center gap >= 2F = RED FLAG = skip (TWC double-count rule).
4. Output: Thad-friendly plain-English proposal, max 3 picks, dollar sizes, odds, why — or exactly "NO QUALIFIED PICKS for Sep 5". PROPOSAL ONLY — do NOT place orders; Thad approves all buys.
5. Save to `data/reports/sep5_picks.md` (workspace) and reply with the proposal text.

## Context
Sep 4 cycle: YES lotteries 0-for-3 days, -$6.47. Claims streak 16/16. Discipline: market center is law; the book defaults quiet unless the gate passes something real.