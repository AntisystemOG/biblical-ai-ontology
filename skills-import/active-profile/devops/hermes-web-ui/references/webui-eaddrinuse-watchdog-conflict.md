# WebUI EADDRINUSE & Watchdog Port Conflict

**Date**: 2026-05-29
**Skill**: `hermes-web-ui` troubleshooting
**Symptom**: WebUI chat fails with `Error: listen EADDRINUSE: address already in use 0.0.0.0:8648`, or search/tools hang indefinitely.

## Chain of Failures

1. **Duplicate cron jobs** — Two identical `*/10 * * * * /bin/bash /home/thadd/.hermes/scripts/hermes-watchdog.sh` entries in crontab.
2. **Watchdog script flaws**:
   - Uses `python` instead of `python3` for `HERMES_AGENT_BRIDGE_PYTHON` → bridge workers spawn with system python (missing `openai`)
   - Does NOT clear port 8648 before starting → if a Node process is still shutting down, `nohup node ...` gets `EADDRINUSE`
   - Uses `node bin/hermes-web-ui.mjs start` which tracks a PID file; if the file is stale, the CLI falsely reports "already running" and exits
3. **Orphaned Node processes** — The `.mjs` CLI starts Node, writes PID, then Node crashes on `EADDRINUSE`. The `.mjs` CLI exits but the crash log says "already running". On next watchdog tick, `pgrep` finds a different Node process (from the other watchdog or a manual start), thinks everything is fine, and does nothing.
4. **Result**: Port 8648 is held by a Node process that is NOT the one the PID file tracks. The WebUI appears healthy to the watchdog but is actually unstable. Chat tool calls get dropped when the process eventually dies.

## Diagnosis Commands

```bash
# Check for duplicate cron entries
crontab -l | grep -c "watchdog"   # should be 1

# Check if the PID file matches a real process
cat ~/.hermes-web-ui/server.pid 2>/dev/null | xargs -r ps -o pid,comm,etime 2>/dev/null

# Check what's ACTUALLY on port 8648
lsof -ti:8648 | xargs -r ps -o pid,comm,etime 2>/dev/null

# Check watchdog log for restart loops
tail -50 ~/.hermes/logs/watchdog.log | grep -E "NOT running|restarted"
```

## Fix Checklist

1. **Remove duplicate cron jobs**:
   ```bash
   (crontab -l | grep -v "hermes-watchdog" && echo "*/10 * * * * /bin/bash /home/thadd/.hermes/scripts/hermes-watchdog.sh # HERMES_WATCHDOG") | crontab -
   ```
2. **Patch the watchdog script** (`~/.hermes/scripts/hermes-watchdog.sh`):
   - Change `export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python` to `.../python3`
   - Add before `nohup`:
     ```bash
     lsof -ti:8648 | xargs -r kill -9 2>/dev/null
     sleep 1
     ```
   - Change `nohup node bin/hermes-web-ui.mjs start ...` to `nohup /home/thadd/.hermes/node/bin/node dist/server/index.js ...` (bypasses the PID-tracking CLI)
3. **Kill all Node processes on 8648 and restart manually**:
   ```bash
   lsof -ti:8648 | xargs -r kill -9
   sleep 2
   cd /mnt/c/Users/thadd/hermes-web-ui
   export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3
   unset AUTH_DISABLED
   /home/thadd/.hermes/node/bin/node dist/server/index.js
   ```
4. **Verify stability**:
   ```bash
   # Wait 30 seconds, then check the PID hasn't changed
   PID1=$(lsof -ti:8648 | head -1)
   sleep 30
   PID2=$(lsof -ti:8648 | head -1)
   [ "$PID1" = "$PID2" ] && echo "PID stable — OK" || echo "PID changed — still unstable"
   ```

## Key Lesson

When the WebUI search/tools hang but backend processes are healthy, the problem is almost always **WebUI process instability** (crashing, restarting, or port conflicts), not a stuck tool. Check the watchdog log first — it reveals the real story.

### Systemd Service vs Watchdog

If the WebUI is managed by a systemd user service (`hermes-webui.service`), **the service is the authoritative process**, not the watchdog cron job or manual `node` invocations. Killing the systemd-controlled PID directly causes systemd to restart it (due to `Restart=on-failure`), creating a restart loop that competes with any manual or watchdog restarts.

**Diagnosis**:
```bash
systemctl --user status hermes-webui.service
# Look for: "restart counter is at N"
# Or: "Scheduled restart job, restart counter is at 5"
```

**Fix**:
1. Disable systemd service auto-restart temporarily: `systemctl --user stop hermes-webui.service`
2. Kill any remaining Node processes on port 8648: `lsof -ti:8648 | xargs -r kill -9`
3. Fix the systemd service file (`~/.config/systemd/user/hermes-webui.service`) if needed
4. `systemctl --user daemon-reload && systemctl --user restart hermes-webui.service`

### Kill by Port, Not by PID

The `.mjs` CLI wrapper writes a PID file at `~/.hermes-web-ui/server.pid`, but the PID may not match the actual Node process holding port 8648 (especially after crashes or when systemd auto-restarts). Always kill by port:
```bash
lsof -ti:8648 | xargs -r kill -9
sleep 2
# Verify no process remains
lsof -i:8648 || echo "Port clear"
```