# Agent Registry

## Active Crons (Kalshi Weather)

| Cron Name | Schedule | Status | Notes |
|-----------|----------|--------|-------|
| kalshi-weather-morning-scan | 5:00 AM CDT daily | ✅ Active (Aug 25) | Timing-aware storm penalties |

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

## Scheduled Agents (Crons)\r\n\r\nAll cron names match their agent file names exactly. Only `truth-based-trading` and `whale-watch` are active. All others are paused/disabled.

| Cron Name | Agent File | Schedule (America/Chicago) | Purpose | Status |
|-----------|------------|----------------------------|---------|
| `whale-watch` | `agents/whale-watch.md` | Daily 6:00 AM | Hedge fund 13F overlap tracker |
| `history-rhymes` | `agents/history-rhymes.md` | Daily 7:00 AM | Historical market parallel analyzer |
| `daily-brief` | `agents/daily-brief.md` | Daily 8:00 AM | Ground News style morning brief |
| `financial-advisor` | `agents/financial-advisor.md` | Monday 9:00 AM | Value investing screener |
| `memory-dreaming` | `agents/memory-dreaming.md` | Daily 3:00 AM | Memory synthesis / dream report |
| `trading-arena` | `agents/trading-arena.md` | M–F 8:00–15:30 every 30 min | Live trading simulation dashboard |
| `top-100-strategists` | `agents/top-100-strategists.md` | Daily 9:00 AM | Hedge fund holdings analyst |
| `long-term-holds` | `agents/long-term-holds.md` | Monday 10:00 AM | Inflation-beating asset synthesizer |
| `truth-based-trading` | `agents/truth-based-trading.md` | First Monday monthly | Retirement strategy synthesizer |
| `kalshi-aug28-deploy` | — (one-shot system event) | Aug 27, 8:00 PM CDT, self-deletes | Thad-authorized deployment of 1-2 more Aug 28 weather positions |

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
