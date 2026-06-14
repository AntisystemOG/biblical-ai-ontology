# OpenClaw → Hermes Workspace Mapping

## Directory Structure

```
/mnt/c/Users/thadd/.openclaw/
├── workspace/                    # Git-backed workspace (source of truth)
│   ├── agents/                   # Agent config files (.md)
│   │   ├── SOUL.md              # Persona, values, vibe
│   │   ├── USER.md              # User profile
│   │   ├── AGENTS.md            # Session startup rules
│   │   ├── HEARTBEAT.md         # Proactive check rules
│   │   ├── TOOLS.md             # Local system details
│   │   ├── MEMORY.md            # Curated long-term memory
│   │   ├── REGISTRY.md          # Agent/cron name mapping
│   │   ├── whale-watch.md
│   │   ├── history-rhymes.md
│   │   ├── daily-brief.md
│   │   ├── trading-arena.md
│   │   ├── financial-advisor.md
│   │   ├── memory-dreaming.md
│   │   ├── top-100-strategists.md
│   │   ├── long-term-holds.md
│   │   ├── master-trend-intelligence.md
│   │   ├── plctool-coder.md
│   │   └── coder.md
│   ├── memory/                   # Daily log files
│   │   └── YYYY-MM-DD.md
│   ├── skills/                   # OpenClaw skills (SKILL.md)
│   ├── scripts/                  # Automation scripts (.ps1)
│   ├── Spocks Reports/            # Generated reports
│   │   ├── whale_watch/
│   │   ├── history_rhymes/
│   │   ├── daily_brief/
│   │   ├── financial_advisor/
│   │   ├── memory_dreaming/
│   │   ├── strategists/
│   │   ├── long_term_holds/
│   │   └── market/
│   └── agents/                   # Cron jobs reference this
└── cron/                         # Cron state (jobs.json, jobs-state.json)
```

## Path Translation

| OpenClaw (Windows) | Hermes (WSL) |
|---|---|
| `C:\\Users\\thadd\\OneDrive\\Desktop\\Spocks Reports` | `/mnt/c/Users/thadd/OneDrive/Desktop/Spocks Reports` |
| `C:\\Users\\thadd\\Desktop\\Portfolio Positions` | `/mnt/c/Users/thadd/Desktop/Portfolio Positions` |
| `C:\\Users\\thadd\\.openclaw\\workspace\\agents` | `/mnt/c/Users/thadd/.openclaw/workspace/agents` |
| `C:\\Users\\thadd\\.openclaw\\workspace\\memory` | `/mnt/c/Users/thadd/.openclaw/workspace/memory` |

## Agent → Cron Schedule Mapping

| Agent | OpenClaw Schedule | Hermes Cron |
|---|---|---|
| whale-watch | Daily 6:00 AM CDT | `0 6 * * *` |
| history-rhymes | Daily 7:00 AM CDT | `0 7 * * *` |
| daily-brief | Daily 8:00 AM CDT | `0 8 * * *` |
| financial-advisor | Monday 9:00 AM CDT | `0 9 * * 1` |
| memory-dreaming | Daily 3:00 AM CDT | `0 3 * * *` |
| top-100-strategists | Daily 9:00 AM CDT | `0 9 * * *` |
| long-term-holds | Monday 10:00 AM CDT | `0 10 * * 1` |
| master-trend-intel | Monday 6:00 AM CDT | `0 6 * * 1` |
| trading-arena | M-F 8:30-15:00 every 30min | `*/30 8-14 * * 1-5` |
| plctool-coder | Every 4 hours (0,4,8,12,16,20) | `0 */4 * * *` |
| coder | Every 4 hours (1,5,9,13,17,21) | `0 1,5,9,13,17,21 * * *` |

## Agent Prompt Templates

### Whale Watch
Reads portfolio CSV → searches 13F filings for Cohen, Sundheim, Tepper, Laffont, Aschenbrenner → finds overlaps → saves markdown report.

### Daily Brief
Ground News cross-spectrum methodology. Searches Left (CNN), Center (Reuters), Right (Fox) per story. Identifies convergent facts, blindspots, likely reality. Generates report with portfolio impact section.

### Trading Arena
Simulation only — Python scripts run every 30 min during market hours. Not a true agent-based cron in OpenClaw. Dashboard is HTML with embedded snapshot data (file:// protocol blocks fetch).

### Memory Dreaming
Reads yesterday's memory file → extracts themes, decisions, patterns → writes poetic dream-like reflection → distills key learnings into MEMORY.md.

## Universal Rules (from AGENTS.md)

Every agent MUST end with status:
- `Done` / `Complete` — success
- `Failed: [reason]` — failure
- `Blocked: [what's blocking]` — needs user

Never leave the user wondering.

## Git Workflow

Always:
1. `git pull origin main` before starting
2. `git add . && git commit -m "update" && git push origin main` after significant work

Repo: `https://github.com/AntisystemOG/spock-workspace`
