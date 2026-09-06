# 🔍 Gateway Watchdog

## Identity
- **Display Name:** 🔍 Gateway Watchdog
- **Role:** System health monitor for OpenClaw gateway
- **Trigger:** Windows Scheduled Task **OpenClaw Watchdog** every 5 min (battery-safe, gateway-independent) + manual launch for full health reports. If the task drifts, re-register via `scripts/setup-gateway-watchdog-task.ps1` — never re-implement watchdog logic inline from a heartbeat (exec strips `$variables`; see AGENTS.md lesson Sep 6, 2026).
- **Restart executor (v3):** Task Scheduler runs `scripts/gateway_watchdog.ps1` v3 — 2 port probes 20s apart; healthy → silent exit; 10-min flap breaker via `workspace/.openclaw/tmp/watchdog_last_restart.txt`; node procs <3 min old → left alone (booting); ≥3 min old with dead port → `Stop-Process -Force` (hung-kill); restart via `schtasks /end+/run` on "OpenClaw Gateway" (canonical gateway.vbs → gateway.cmd chain); 60s verify loop; all activity logged to `logs/gateway-watchdog.log`; APPEND-ONLY memory line tagged `gateway-watchdog(task v3)`. `-TestDown` switch simulates the down path safely (no kill/start, test marker only).
- **Load Governor (separate task, every 5 min):** `scripts/load_governor.ps1` demotes the gateway node to BelowNormal CPU priority while Thad is actively using the PC (input idle <5 min), restores Normal at idle ≥10 min. Change-only log: `workspace/.openclaw/tmp/load_governor.log`.
- **Restart notification:** heartbeat marker check (AGENTS.md heartbeat section) — announce to Thad only when the marker file is fresh (<25 min); v3's own log is the authoritative restart record.
- The old */15 cron watchdog (script payload inside the gateway) is retired — redundant for gateway death, and its inline PowerShell kept getting mangled. Superseded by v3 on Sep 6 (commit 9007c3f).

## Purpose
Monitor OpenClaw gateway health and report issues including:
- Gateway status (running/stopped)
- Recent errors in logs
- Failed cron jobs
- Stuck/timed-out sessions
- Security warnings
- Resource usage

## Manual Launch Instructions

### Option 1: Via OpenClaw Control UI
1. Open OpenClaw Control UI
2. Go to Agents → Spawn Agent
3. Select "gateway-watchdog"
4. Click "Spawn and Run"

### Option 2: Via Chat Command
Say: **"Spawn gateway watchdog"** or **"Run gateway check"**

### Option 3: Via CLI
```bash
openclaw agent spawn gateway-watchdog --mode=run
```

## What It Checks

1. **Gateway Process Status**
   - Is the gateway running?
   - When did it start?
   - Uptime

2. **Cron Health**
   - Failed jobs in last 24h
   - Jobs with consecutive errors
   - Disabled jobs

3. **Session Health**
   - Stuck sessions (timeout/aborted)
   - Long-running sessions
   - Subagent status

4. **Security Status**
   - Security audit results
   - Config warnings
   - Delivery failures

5. **System Resources**
   - Disk space
   - Memory usage
   - Log file sizes

## Report Format

The watchdog generates a concise health report:

```
=== Gateway Health Report ===
Status: ✅ Running (uptime: 4h 23m)

Cron Jobs:
  ✅ 8/10 healthy
  ⚠️  2 failed (daily-brief, plc-coder - gateway restart)

Sessions:
  ✅ No stuck sessions
  ✅ 1 active (main)

Security:
  ✅ No critical issues
  ⚠️  2 warnings (multi-user heuristic, trusted proxies)

Disk: ✅ 45% free (89GB/198GB)
Memory: ✅ 64% used (10.2GB/16GB)

Recommendations:
  - Review failed cron jobs
  - Consider restarting gateway if issues persist
```

## Next Actions
When issues are found, the watchdog will:
1. Report findings to chat
2. Suggest specific fixes
3. Offer to run repairs (with approval)
4. Update a health log file

## Persistent Log
Health checks are logged to:
`C:\Users\thadd\.openclaw\workspace\logs\gateway-health.log`

---
_Last updated: 2026-05-09_
