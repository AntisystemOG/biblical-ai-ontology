# Thad's OpenClaw Workspace Structure

**Path:** `/mnt/c/Users/thadd/.openclaw/workspace/` (WSL mounted Windows filesystem)
**Size:** ~44MB, 74 items
**Git repo:** https://github.com/AntisystemOG/spock-workspace (git pull/push workflow)

## Core Memory Files (Read in Priority Order)

| File | Purpose |
|------|---------|
| `SOUL.md` | Agent persona, values, truth principle, Christian worldview |
| `USER.md` | User profile: Thad, night shift, America/Chicago, family (Ashley, Sarah) |
| `IDENTITY.md` | Identity and behavioral rules |
| `MEMORY.md` | Curated long-term memory: portfolio (~$503K), predictions, master trend intelligence |
| `AGENTS.md` | Session startup rules, naming conventions, autonomy rules |
| `HEARTBEAT.md` | Proactive check rules, health checks |
| `DREAMS.md` | Memory synthesis / dream diary |
| `SECURITY.md` | Security rules, audio verification requirement |
| `TOOLS.md` | Local system specifics, installed binaries, env vars |

## Active Cron Agents (6 original + 4 migrated to Hermes + 2 Hermes-only = 12 total)

| Agent | Schedule | Purpose |
|-------|----------|---------|
| whale-watch | Daily 6:00 AM | Hedge fund 13F overlap tracker |
| history-rhymes | Daily 7:00 AM | Market history pattern analyzer |
| daily-brief | Daily 8:00 AM | Ground News cross-spectrum summary |
| financial-advisor | Monday 9:00 AM | Value investing screener |
| memory-dreaming | Daily 3:00 AM | Memory synthesis / dream diary |
| trading-arena | M-F market hours every 30min | Trading simulation dashboard |
| top-100-strategists | Daily 9:00 AM | Hedge fund conviction analysis |
| long-term-holds | Monday 10:00 AM | Inflation-beating asset allocator |
| master-trend-intelligence | Monday 6:00 AM | Predictive synthesis survival engine |
| truth-based-trading | First Monday of month | Fee-aware SPIVA-based strategy |
| gateway-watchdog | Every 15 min | Hermes gateway health monitor |
| openclaw-sync | M-F every 30 min | Git pull workspace sync |

## Key Scripts

- `generate_brief.py` — Daily brief content generator
- `generate_dream.py` — Memory dreaming content generator
- `generate_pdf.py` / `html_to_pdf.py` — Report PDF generation
- `trading_arena_run.py` / `trading_arena_simulation.py` — Trading simulation
- `whale_watch_report.py` — Whale watch report generation
- `top100_strategists_report.py` — Top 100 strategists report

## Data Directories

- `agents/` — Agent config files
- `reports/` — Generated reports
- `memory/` — Daily memory logs
- `analysis/` — Analysis outputs
- `trading-arena/` / `trading_arena/` — Trading simulation state and data
- `scripts/` / `tools/` — Utility scripts
- `skills/` — OpenClaw SKILL.md files (platform-agnostic, reusable)

## Portfolio Context (From MEMORY.md)

- Total ~$503K: Energy 38%, Tech/Semiconductors 16%, Crypto/Blockchain 5%, Quality/Defensive 3%, Speculative 5%, Cash/Money Market 60%
- Retirement ~$4K
- Never share financial data without audio verification

## System Context

- **WSL** Ubuntu 26.04 on Windows host
- **Node:** v22.22.3 at `/home/thadd/.hermes/node/bin/node`
- **Gateway:** Hermes running in WSL, api_server on `0.0.0.0:8642` with key
- **Telegram bot:** `spockog` configured
- **Ollama Pro:** Active (tokens expire monthly, use freely)
- **Two PCs:** Work Dell, home PC with RTX 3060 Ti
