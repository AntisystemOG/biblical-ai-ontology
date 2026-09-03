# Kalshi Cron Audit Report

**Date:** 2026-09-03, 5:15 AM CT
**Scope:** All Kalshi-related scheduled jobs - goal alignment, health, consolidation
**Trigger:** Thad directive: "make sure they are working towards the same goal and maybe combine jobs where relevant"

---

## 1. Goal Alignment Statement

Every Kalshi job must serve the core purpose: **accurate predictions (4/5 target) -> disciplined execution -> bankroll compounding ($28 -> ~$73.74 since Aug 16) -> every miss becomes a coded rule.** Jobs that silently collect dead data, duplicate each other at 6 AM on a 2-core laptop, or fail nightly work against that purpose and were fixed or removed.

## 2. Inventory After Cleanup (26 active jobs -> 19 active, 40 -> 33 total)

| Job | Schedule | Status before | Action taken | Goal served |
|---|---|---|---|---|
| kalshi-morning-brief | 5:45 AM Mon-Fri | NEW | Created (consolidates 3 jobs) | Prediction + execution |
| the-edge-morning | 5:30 AM Mon-Fri | FAILED 3x (broken model pin) | Disabled (rolled into brief) | - |
| kalshi-daily-predictions | 6 AM daily | FAILED (broken model pin) | Disabled (rolled into brief) | - |
| kalshi-job-morning | 6 AM daily | FAILED (broken model pin) | Disabled (rolled into brief) | - |
| kalshi-position-monitor | Hourly | OK | Keep | Discipline (stop-loss/giveback) |
| kalshi-price-snapshots | Every 4h | SKIPPED (bad model pin) | Pin cleared + payload rewritten to dynamic event discovery (was snapping dead Aug-20 claims market) | Learning data |
| the-edge-nightly | 9 PM Mon-Thu | OK | Keep | Pick prep |
| weather-paper-trader | 8 PM daily | OK | Keep | Prediction engine |
| kalshi-longshot-tracker | Nightly | OK | Keep | Lotto candidates |
| kalshi-weekly-review | Sat 10 AM | OK | Keep | Learning loop |
| kalshi-prompt-evolution | Fri | OK | Keep | Learning loop |
| twc-update-probe | Cron | OK | Keep | Settlement-source watch |
| kalshi-buy-alert-aug18/19, aug19-morning | Dead one-shots | Disabled since Aug | DELETED | Cleanup |
| kalshi-pre-close-check | Dead one-shot | Disabled | DELETED | Cleanup |
| kalshi-weather-morning-scan | 5 AM daily | Disabled (delivery broken) | DELETED (superseded) | Cleanup |
| miami-longshot-watch | Stale payload | Disabled | DELETED (kalshi-longshot-tracker owns this lane) | Cleanup |
| lotto-exit-watch | Disabled | Disabled | DELETED (position-monitor owns giveback exits) | Cleanup |
| ny-watch | One-day watcher | Completed Aug 31/Sep 1 | Removed earlier (Sep 1) | Completed |

## 3. Root-Cause Fixes Applied

### 3.1 Broken model pins (why 3 jobs failed every morning)
The Aug 31 PROMPT-LAW program pinned jobs to model `ollama-cloud/glm-5.2`. The OpenClaw update changed the model-policy allowlist to the new naming (`ollama/glm-5.2:cloud` family), so every pinned job was REJECTED at preflight before running. Three morning jobs failed consecutively (the-edge-morning 3x).

**Fix:** cleared the model override on the-edge-morning, kalshi-daily-predictions, kalshi-job-morning, kalshi-price-snapshots. Jobs now inherit the gateway default (ollama/glm-5.3-flash:cloud), which is proven working on this host. Lesson: model pins break silently when the provider naming changes - prefer clearing overrides unless a job genuinely needs a specific model.

### 3.2 Snapshot collector snapping dead markets
kalshi-price-snapshots hard-coded `KXJOBLESSCLAIMS-26AUG20`, `KXCPI-26AUG`, `KXCPICORE-26AUG` - the claims event expired Aug 20. It "succeeded" for weeks while collecting nothing useful (silent failure mode).

**Fix:** new script `scripts/kalshi_snapshots.py` discovers active events dynamically per series (claims / CPI / CPI-core / Fed), snaps up to 2 per series, verified live: 7 active events found including KXJOBLESSCLAIMS-26SEP03 (closes Sep 3, 7:25 AM CT).

### 3.3 Three jobs firing at once on a 2-core laptop
The 5:30 / 6:00 / 6:00 AM trio each ran the claims digest + web searches independently (the "BUDGET RULE" comment inside kalshi-job-morning documented the problem). Now ONE job at 5:45 AM with a hard web-search budget of 2.

## 4. Goal-Aligned Job Map (what serves what)

| Goal layer | Jobs |
|---|---|
| Predict (engine) | weather-paper-trader, the-edge-nightly, kalshi-longshot-tracker, kalshi-price-snapshots |
| Decide/execute | kalshi-morning-brief, kalshi-position-monitor, gateway-watchdog |
| Learn | kalshi-weekly-review, kalshi-prompt-evolution, memory-dreaming |
| Settlement truth | twc-update-probe |
| Removed (noise) | 7 dead jobs listed above |

## 5. Verification & Rollback

- kalshi-morning-brief force-run test executed Sep 3 ~5:08 AM (results logged in memory + Telegram delivery).
- Superseded jobs are DISABLED, not deleted; payloads intact with PROMPT-LAW text. Rollback = set enabled:true (see agents/kalshi-morning-brief.md).
- REGISTRY.md updated to match.

## 6. The One Prediction Database (Thad directive, Sep 3 5:13 AM)

"All Jobs should be working toward making a better prediction model. That means one database that they can each make changes to."

**Implemented same morning:** `data/kalshi_model.db` (SQLite WAL, git-backed) with shared API `scripts/kalshi_db.py`.

| Table | Contents | Who writes |
|---|---|---|
| predictions | every pick: source, kind, event, market, side, shares, odds, model_prob vs market_prob, settled result + P&L | paper trader, morning brief, longshot tracker, manual trades |
| forecasts | model forecast history (city-day centers) + graded outcomes | weather_daily, grading steps |
| learnings | lessons + rule changes with hits/misses counters | grading, weekly review, prompt evolution |
| model_state | THE LIVING MODEL PARAMS: claims weights (Kalshi 0.70/analyst 0.10/recent 0.20), sigma 3.5K, TWC +1.5F, sizing caps, target accuracy 80% | learning loop writes; every job READS (never hardcode) |
| snapshots | 4h price history for timing analysis (3,305 rows migrated) | kalshi-price-snapshots (dual-write) |

**Migration done Sep 3:** 44 forecast records, 27 band picks, 1 grading record, 10 signal-accuracy rows, 3,305 snapshots. Zero skips.

**Why this matters:** every job now contributes to ONE model. The morning brief syncs everything (STEP 2b), reads accuracy vs the 80% target, and reads model params from the DB. The learning loop updates weights in the DB, and the next prediction uses them. Prediction -> grade -> learn -> adjust weights -> predict better. The loop is closed and inspectable in one file.

## 7. Open Items (not cron-scoped but surfaced)

- Backups: doctor reports NO successful backup ever; 2 attempts produced zero archives. Needs a working backup path (workspace is git-backed, which covers code but not gateway state).
- openclaw status CLI hung twice on this box (unverified cause).
- Sep 10 claims cycle: normal week (Labor Day falls after it closes); Sep 17 cycle is the holiday-distorted one - plan smaller size there.