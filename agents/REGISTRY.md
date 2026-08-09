# Agent & Cron Registry

Single source of truth for all agents and their associated cron jobs.

## Universal Rules (MANDATORY for ALL agents/crons)

**Signal completion.** Every agent and cron must end with a clear signal:
- Reply with **"Done"** or **"Complete"** when finished successfully
- If you **cannot complete**, explicitly state: **"Failed: [reason]"** or **"Blocked: [what's blocking]"**
- Never leave the user wondering if work is still in progress
- This applies to ALL crons, agents, and manual tasks

## Naming Convention
- Agent files: `kebab-case.md` (e.g., `whale-watch.md`)
- Cron names: Must match agent file name exactly (e.g., `whale-watch`)
- No abbreviations or truncation

## Active Agents\r\n\r\n> Only `truth-based-trading` and `whale-watch` are active. All other agents are paused/disabled.\r\n\r\n| Agent | Cron Name | Schedule | Purpose | Status |
|-------|-----------|----------|---------|
| whale-watch | whale-watch | Quarterly 13F deadlines (Feb/May/Aug/Nov 15) 6:00 AM CDT | Hedge fund overlap tracker | Active |
| history-rhymes | history-rhymes | Daily 7:00 AM CDT | Market history pattern analyzer | Paused/Disabled |
| daily-brief | daily-brief | Daily 8:00 AM CDT | Morning intelligence summary | Paused/Disabled |
| trading-arena | trading-arena | M-F 8:30AM-3PM CDT every 30min | Trading simulation | Paused/Disabled |
| financial-advisor | financial-advisor | Monday 9:00 AM CDT | Value investing screener | Paused/Disabled |
| memory-dreaming | memory-dreaming | Daily 3:00 AM CDT | Memory synthesis | Paused/Disabled |
| top-100-strategists | top-100-strategists | Daily 9:00 AM CDT | Hedge fund long-term vs short analysis | Paused/Disabled |
| long-term-holds | long-term-holds | Monday 10:00 AM CDT | Inflation-beating asset synthesizer | Paused/Disabled |
| master-trend-intelligence | master-trend-intelligence | Monday 6:00 AM CDT | Predictive synthesis for survival and growth | Paused/Disabled |
| plctool-coder | plc-coder-auto-spawn | Every 4 hours (0,4,8,12,16,20) | PLC coding assistant | Paused/Disabled |
| coder | coder-auto-spawn | Every 4 hours (1,5,9,13,17,21) | General coding assistant (persistent memory) |

## Agent File Template (Required Header)

Every agent file must start with:

```markdown
# Agent: [name]

## Universal Rule (MANDATORY)
**Signal completion.** End EVERY run with a clear status:
- **"Done"** or **"Complete"** — task finished successfully
- **"Failed: [reason]"** — task could not complete
- **"Blocked: [what's blocking]"** — needs user intervention

Never leave the user wondering.

## Purpose
[Brief description of what this agent does]

## Output Location
[Where reports/results go]
```

## Agent File Locations
All agent configs: `C:\Users\thadd\.openclaw\workspace\agents\<name>.md`

## Memory Files
- `coder-memory.md` — General Coder's persistent memory across sessions

## Last Updated
2026-05-13

