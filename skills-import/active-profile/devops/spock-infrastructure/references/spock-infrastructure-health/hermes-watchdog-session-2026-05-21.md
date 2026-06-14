---
source: session 2026-05-21
skill: spock-infrastructure-health
---

# Session: Hermes External Watchdog Implementation

## Context

User asked: *"Create a watchdog timer that restarts Hermes if it's not running, set timer every 10 minutes."*

## Architecture Lesson: Internal Cron Cannot Restart Hermes

A `hermes cron create` job cannot resurrect a dead Hermes process — the scheduler dies with the process. An **external** layer is required.

## What Was Built

| Component | Location | Purpose |
|-----------|----------|---------|
| Shell watchdog script | `~/.hermes/scripts/hermes-watchdog.sh` | Checks `pgrep` for gateway + WebUI, restarts with `nohup` if dead |
| System crontab | `crontab -e` → `*/10 * * * *` | Triggers watchdog every 10 min outside Hermes runtime |
| Start shortcut | `C:\Users\thadd\Desktop\Start Hermes Watchdog.lnk` | Enables cron + immediate check |
| Stop shortcut | `C:\Users\thadd\Desktop\Stop Hermes Watchdog.lnk` | Disables cron (does NOT stop Hermes) |
| Log | `~/.hermes/logs/watchdog.log` | Silent when healthy, reports "NOT running — restarting" on failure |

## Key Commands

**Verify watchdog is installed:**
```bash
crontab -l | grep hermes-watchdog
```

**Manual test:**
```bash
/home/thadd/.hermes/scripts/hermes-watchdog.sh
tail -2 /home/thadd/.hermes/logs/watchdog.log
```

**First-run verification (from this session):**
```
[2026-05-21 07:58:09] Gateway OK
[2026-05-21 07:58:10] WebUI OK
```

## Process Detection Pattern Used

```bash
pgrep -f "hermes_cli.main gateway run"   # Hermes gateway
pgrep -f "hermes-webui-new/server.py"    # WebUI server
```

Both checked. If either is missing:
1. `pkill` any orphaned processes (clean slate)
2. `sleep 2` (avoid port conflict)
3. `nohup ... &` (detached from terminal)

## Environment Details (for reproduction)

- WSL2, no systemd service
- Hermes venv: `/home/thadd/.hermes/hermes-agent/venv/bin/`
- WebUI path: `/home/thadd/hermes-webui-new/server.py`
- User: `thadd`
- Desktop folder: `C:\Users\thadd\Desktop\Hermes\`
