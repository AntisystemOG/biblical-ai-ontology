# sep4-lesson-apply

- **Type:** One-shot housekeeping job (auto-deletes after completion)
- **Created:** 2026-09-04 16:45 CDT — apply the Sep 4 cycle lessons to code
- **Schedule:** 2026-09-04 20:00 CDT, isolated run, model pinned ollama-cloud/glm-5.2, timeout 900s
- **Agent config path:** C:\Users\thadd\.openclaw\workspace\agents\sep4-lesson-apply.md

## Task list (payload)
1. **Lottery cap (pre-order gate):** patch `C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner\kalshi_pre_order_check.py` — add aggregate same-day YES-lottery cap: total exposure on positions with entry <= 30c must stay <= 3% of settled bankroll (per day, all cities combined). RED flag when breached. Never inline python on Windows — write patch script to `.openclaw/tmp` first. Test with a synthetic 8% order; it must flag.
2. **Spike rule (exit watcher):** patch `scripts\kalshi_sep4_exit.py` — for same-day lottery positions, if current bid >= 1.5x entry avg price AND station obs_max proxy is NOT within 1F of the win range, print `SPIKE-SELL candidate (take the money)`.
3. **Cost fix (position board):** patch `scripts\kalshi_position_table.py` — the Cost column showed $40.02 for a 75sh @ 4c position. Fix cost = shares x entry price with a sanity check; verify against API balance.
4. **MEMORY.md:** append the three rules to Operating Rules (one line each): (a) per-day YES-lottery cap <= 3% settled bankroll; (b) same-day lottery intraday bid spike >= 1.5x entry without station support = sell signal; (c) never extrapolate same-day weather settlement from overnight bids - TWC official daily max is the only truth.
5. Git add/commit/push all changes. Report files changed + test outputs.

## Context (why)
Sep 4 book: committed $7.22 on three YES lotteries (2-14% odds) - all lost -$6.47. Exit system worked (Denver salvage $0.75); entry discipline failed. NY's +66% morning spike was the day's best exit and was passed up. Claims streak 16/16 remains the only never-blink edge.