# Agent Registry

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

## Naming Convention
- All agent files use `kebab-case.md`
- Cron names match agent file names exactly
- No abbreviations or truncation


