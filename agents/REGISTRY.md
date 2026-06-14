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

## Active Agents

| Agent | Cron Name | Schedule | Purpose |
|-------|-----------|----------|---------|
| whale-watch | whale-watch | Daily 6:00 AM CDT | Hedge fund overlap tracker |
| history-rhymes | history-rhymes | Daily 7:00 AM CDT | Market history pattern analyzer |
| daily-brief | daily-brief | Daily 8:00 AM CDT | Morning intelligence summary |
| trading-arena | trading-arena | M-F 8:30AM-3PM CDT every 30min | Trading simulation |
| financial-advisor | financial-advisor | Monday 9:00 AM CDT | Value investing screener |
| memory-dreaming | memory-dreaming | Daily 3:00 AM CDT | Memory synthesis |
| top-100-strategists | top-100-strategists | Daily 9:00 AM CDT | Hedge fund long-term vs short analysis |
| long-term-holds | long-term-holds | Monday 10:00 AM CDT | Inflation-beating asset synthesizer |
| master-trend-intelligence | master-trend-intelligence | Monday 6:00 AM CDT | Predictive synthesis for survival and growth |
| plctool-coder | plc-coder-auto-spawn | Every 4 hours (0,4,8,12,16,20) | PLC coding assistant |
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