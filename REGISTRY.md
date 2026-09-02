# Agent Registry

## Active Crons (Kalshi Weather)

| Cron Name | Schedule | Status | Notes |
|-----------|----------|--------|-------|
| kalshi-weather-morning-scan | 5:00 AM CDT daily | Active (Aug 25) | Timing-aware storm penalties |
| ny-watch | Hourly 11:00-19:00 CT, Aug 31 2026 only | Removed (Sep 1) | NY band exit watcher; agent `agents/ny-watch.md`; script `scripts/ny_watch_0831.py`; rule-table exits, act-then-report. Market KXHIGHNY-26AUG31 settled 09-01 07:00Z; job fired hourly past its window on Sep 1 and was removed at 21:48 CT Sep 1 (verdict SELL-DEAD on Sep 1 weather data was inapplicable to settled market; no trade possible or executed) |

---

This file tracks all agents in the workspace and their purpose.

## How to Spawn Agents

### 🔧 PLCTools Coder (Coding Assistant)
**CRITICAL: The active project is in `C:\Users\thadd\Documents\Degater PLC Tool BST33 and 35`**

NOT the old `PLCTools` folder.

**Quick spawn command:**
```
sessions_spawn(
  task="Spawn PLCTools coding assistant for BST33/35",
  label="plctool-coder",
  mode="run",
  runtime="subagent",
  cwd="C:\Users\thadd\Documents\Degater PLC Tool BST33 and 35"
)
```

**What it does:**
- Spawns a fresh subagent that reads `C:\Users\thadd\Documents\Degater PLC Tool BST33 and 35\PROJECT_MEMORY.md` first
- Maintains persistent memory via the PROJECT_MEMORY.md file
- Focused ONLY on coding tasks for the BST33/35 PLCTools project

**Persistent memory location:** `C:\Users\thadd\Documents\Degater PLC Tool BST33 and 35\PROJECT_MEMORY.md`

## Active Agents

| Agent File | Purpose | Spawn Command |
|------------|---------|---------------|
| `plctool-coder.md` | Dedicated coding assistant for PLCTool project | `sessions_spawn(label="plctool-coder", mode="run", runtime="subagent")` |

## Scheduled Agents (Crons)\r\n\r\nAll cron names match their agent file names exactly. Only `truth-based-trading` and `whale-watch` are active. All others are paused/disabled unless noted.

| Cron Name | Agent File | Schedule (America/Chicago) | Purpose | Status |
|-----------|------------|----------------------------|---------|
| `whale-watch` | `agents/whale-watch.md` | Daily 6:00 AM | Hedge fund 13F overlap tracker | ✅ Active |
| `history-rhymes` | `agents/history-rhymes.md` | Daily 7:00 AM | Historical market parallel analyzer | ✅ Active |
| `daily-brief` | `agents/daily-brief.md` | Daily 8:00 AM | Ground News style morning brief | ✅ Active |
| `financial-advisor` | `agents/financial-advisor.md` | Monday 9:00 AM | Value investing screener | ✅ Active |
| `memory-dreaming` | `agents/memory-dreaming.md` | Daily 3:00 AM | Memory synthesis / dream report | ✅ Active |
| `trading-arena` | `agents/trading-arena.md` | M–F 8:30–15:00 every 30 min | Live trading simulation dashboard | ✅ Active |
| `top-100-strategists` | `agents/top-100-strategists.md` | Daily 9:00 AM | Hedge fund holdings analyst | ✅ Active |
| `long-term-holds` | `agents/long-term-holds.md` | Monday 10:00 AM | Inflation-beating asset synthesizer | ✅ Active |
| `truth-based-trading` | `agents/truth-based-trading.md` | First Monday monthly | Retirement strategy synthesizer | ✅ Active |
| `kalshi-aug28-deploy` | - (one-shot system event) | Aug 27, 8:00 PM CDT, self-deletes | Thad-authorized deployment of 1-2 more Aug 28 weather positions | ✅ Active |
| `kalshi-longshot-tracker` | `agents/kalshi-longshot-tracker.md` | Daily 8:45 PM CDT | Long-shot scanner: bands <= $0.30 with model edge, paper $1 stakes, settlement grading. Silent unless settlement or edge >= 0.30 | ✅ Active |

## Naming Convention
- All agent files use `kebab-case.md`
- Cron names match agent file names exactly
- No abbreviations or truncation



## 2026-08-28 05:15 - Cron silence pass (Thad directive)
- Thad: no unsolicited updates; silent unless he asks or something changed (settlement, fill, action needed).
- kalshi-position-monitor: silent-by-default (NO_REPLY unless settlement/fill/action-needed); exit discipline updated (never SELL on odds noise).
- gateway-watchdog: healthy = NO_REPLY (no more Gateway Healthy pings).
- kalshi-job-morning/midday/evening + kalshi-daily-predictions + the-edge-morning/nightly: silent unless actionable; plain-English tables when reporting.
- kalshi-weather-morning-scan: DISABLED (broken Telegram delivery target - requires chatId - 5 consecutive errors; covered by position monitor + paper trader).

## 2026-08-28 06:09 - New one-time job: prompt-hardening
- Agent file: agents/prompt-hardening.md (matches cron name, kebab-case per convention).
- Schedule: ONE-TIME at 2026-08-31 04:30 CDT (09:30 UTC) - isolated run, announces to Telegram, self-deletes after run.
- Trigger: Thad switches LLM models; unpinned crons inherit session defaults and different models misread prompts (Aug 28 5:30 AM false SELL was this exact failure mode).
- Does: appends [PROMPT-LAW] blocks to every cron prompt (idempotent via marker), pins explicit model ollama-cloud/glm-5.2 on jobs missing one, verifies each patch.
- Fallback: if cron mutations are restricted in the isolated run, writes hardened prompts to agents/prompt-hardening-output.md for manual application.
- Cleanup: remove nothing manually unless fallback path was used; job self-deletes after successful run.

## 2026-08-29 07:30 - New recurring job: twc-update-probe
- Agent file: agents/twc-update-probe.md (matches cron name, kebab-case).
- Schedule: every 20 min, isolated agentTurn, delivery none (silent), model pinned ollama-cloud/glm-5.2, timeout 180s, failureAlert after 3.
- Does: samples https://weather.com/kalshi (official TWC settlement page), appends ts/hash/cache-headers/deg-readings to scripts/twc_probe_log.csv.
- Purpose: measure page update cadence + build intraday running-high dataset for pattern detection and cut-loss timing (Thad directive 2026-08-29 07:23).
- Lifetime: TEMPORARY - remove after cadence documented (~24-48h) or fold into position monitor.

---

## Temporary Watch (added Aug 29, ~09:50)

| Cron Name | Agent File | Schedule (America/Chicago) | Purpose | Status |
|-----------|------------|----------------------------|---------|--------|
| `miami-longshot-watch` | `agents/miami-longshot-watch.md` | Every 90 min (system event, silent unless alert) | Intraday guard on MIA 88-89 YES 43sh + NY 81-82 tail through Aug 29 settlement. Script: scripts/watch_miami_hold.py. REMOVE after settlement grades. | ? Active |

## 2026-08-29 11:40 - miami-longshot-watch tightened + judgment authority granted
- Schedule: every 20 min -> every 10 min through tonight's Aug 29 settlement (Thad: close eye 3-6 PM, things may change rapidly).
- Standing order amended: judgment sells authorized (protect profit when a winner bleeds >30% from high with live falsification path). Band 88-89 stays the huge-success leg (90F falsification only; alert at bid >= 0.50).
- kalshi-longshot-tracker delivery fixed (to: telegram:6358625036); nightly scan will report again at 20:45.

## lotto-exit-watch (Aug 31, 00:59 CDT)
- Agent file: agents/lotto-exit-watch.md | Cron: lotto-exit-watch (*/20 6-19 * * * CDT, isolated, Telegram announce, silent=NO_REPLY)
- Script: scripts/lotto_exit_watch.py — sells dead lottery legs pre-authorized (Thad's losing-position grant), alerts on big bids
- Guarding: CHI <89 (4sh @0.35), NY 80-81 (14sh @0.10), NY 82-83 (12sh @0.04), settle Sep 1
- miami-longshot-watch: RETIRED Aug 31 (Aug 29 mandate spent)

## 2026-09-02 03:20 CDT - gateway error triage + model-provider cleanup (Spock)
- Root cause of log error storm: dead ollama-cloud/* model ids in openclaw.json fallbacks/allowlists + twc-update-probe payload pin (ollama-cloud/glm-5.2); valid ids are ollama/<model>:cloud. Remapped all refs (backup: openclaw.json.bak-20260902); removed stale auth profile ollama-cloud:default; added models.providers.ollama.timeoutSeconds=180.
- twc-update-probe payload.model -> ollama/glm-5.2:cloud (automations partial patch).
- Skills fixed: crypto-prices + telegram-notify SKILL.md given required frontmatter description (were erroring 10-23x/day on skills scan).
- Gateway restart scheduled 03:20:30 CT one-shot (gateway-restart-apply-20260902) to apply config; port probe + fallback start included.
- 20 startup_failed stability snapshots Aug 31-Sep 1 were the legacy sessions.json migration blocker; migration already completed, gateway running clean since Sep 1 evening.
