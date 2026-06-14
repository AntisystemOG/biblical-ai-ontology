# WebUI Search Tool Hang — Diagnostic Transcript

**Date**: 2026-05-29
**Symptom**: `search_files` tool call in WebUI chat spins indefinitely, no results, no error.

## What Was Checked

1. **Gateway health**: `curl http://localhost:8648/health` → `{"status":"ok", ...}`  
   ✅ Gateway is running, API responsive.

2. **Backend processes**: `ps aux` shows:  
   - PID 393/398 — Hermes gateway (stable, hours uptime)  
   - PID 613, 103424, 111998 — Agent bridge workers (healthy, normal CPU)  
   - PID 103963 — Pyright LSP (normal)  
   ✅ No hung `ripgrep`/`rg`/`search` processes.

3. **Tool list via API**: `curl /api/v1/tools` → `{"error":"Unauthorized"}`  
   ⚠️ Token auth required; not a debugging endpoint.

4. **Agent logs**: `~/.hermes/logs/agent.log` shows tool calls completing normally in prior sessions (9s, 1.5s, 0.8s). No stuck tool calls in current session.

5. **Watchdog logs**: `~/.hermes/logs/watchdog.log` reveals the real problem:  
   ```
   [2026-05-29 22:20:01] WebUI NOT running — restarting...
   [2026-05-29 22:20:01] WebUI restarted (PID 106798)
   [2026-05-29 22:30:01] WebUI NOT running — restarting...
   [2026-05-29 22:30:01] WebUI restarted (PID 109668)
   ```
   ❌ WebUI is being killed and restarted every ~10 minutes by a watchdog cron job. When it dies mid-request, the chat UI never receives the tool result.

6. **Gateway conflict**: `~/.hermes/logs/gateway_watchdog_restart.log` shows:  
   ```
   Telegram bot token already in use (PID 4146)
   ```
   Another gateway instance is holding the Telegram token, causing one watchdog to crash-loop.

## Root Cause

Multiple watchdog instances (or a cron job + manual launcher) are competing. One watchdog thinks the WebUI is dead, kills it, and restarts it — dropping in-flight requests.

## Resolution Steps

1. Kill **all** node processes on port 8648 (not just the one the PID file tracks):
   ```bash
   lsof -ti:8648 | xargs -r kill -9
   sleep 2
   ```
2. Check for **duplicate cron jobs**:
   ```bash
   crontab -l | grep -c "watchdog"   # should be 1, not 2+
   ```
3. Fix the watchdog script (`~/.hermes/scripts/hermes-watchdog.sh`):
   - Use `python3` (not `python`) for `HERMES_AGENT_BRIDGE_PYTHON`
   - Clear port 8648 before starting to prevent `EADDRINUSE`
   - Use `node dist/server/index.js` directly instead of the `.mjs` CLI wrapper when the PID file is stale
4. Restart cleanly:
   ```bash
   cd /mnt/c/Users/thadd/hermes-web-ui
   export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3
   unset AUTH_DISABLED
   node bin/hermes-web-ui.mjs start
   ```
5. Verify with `curl http://localhost:8648/health` and confirm the PID is stable for > 1 minute.

## CLI Entry Point Note

The WebUI CLI entry point is `bin/hermes-web-ui.mjs` (ES module), NOT `bin/hermes-web-ui.js`.  
Attempting `node bin/hermes-web-ui.js start` produces:
```
Error: Cannot find module '/mnt/c/Users/thadd/hermes-web-ui/bin/hermes-web-ui.js'
```
Always use: `node bin/hermes-web-ui.mjs start`
