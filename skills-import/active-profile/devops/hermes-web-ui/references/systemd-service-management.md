# Systemd Service Management for Hermes WebUI

**Date**: 2026-05-29
**Skill**: `hermes-web-ui` infrastructure management
**Symptom**: WebUI process unstable, multiple Node processes competing for port 8648, `EADDRINUSE` errors, watchdog and systemd fighting for control.

## The Setup

The WebUI is managed by a systemd **user** service at `~/.config/systemd/user/hermes-webui.service`:

```ini
[Unit]
Description=Spock WebUI (EKKOLearnAI)
After=network.target

[Service]
Type=simple
WorkingDirectory=/mnt/c/Users/thadd/hermes-web-ui
Environment="HERMES_HOME=/home/thadd/.hermes"
Environment="SPOCK_WEBUI_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3"
Environment="SPOCK_WEBUI_AGENT_DIR=/home/thadd/.hermes/hermes-agent"
Environment="SPOCK_WEBUI_STATE_DIR=/home/thadd/.hermes/webui"
Environment="BIND_HOST=127.0.0.1"
Environment="SPOCK_WEBUI_PORT=8648"
Environment="PATH=/home/thadd/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/thadd/.hermes/node/bin/node dist/server/index.js
Restart=on-failure
RestartSec=5
StandardOutput=append:/home/thadd/.spock/webui.log
StandardError=append:/home/thadd/.spock/webui.log

[Install]
WantedBy=default.target
```

## Key Environment Variables in the Service

| Variable | What It Controls |
|----------|---------------|
| `SPOCK_WEBUI_PYTHON` | The Python used by the WebUI's built-in `SpockWebUI` Python subprocess launcher — this is NOT the agent bridge worker |
| `HERMES_AGENT_BRIDGE_PYTHON` | (Must be added manually) The Python interpreter for the agent bridge subprocess spawned by `services/hermes/agent-bridge.ts`. Must have `openai`, `websockets`, etc. |
| `SPOCK_WEBUI_AGENT_DIR` | Points to the Hermes agent code directory |
| `SPOCK_WEBUI_STATE_DIR` | State directory for the WebUI's own files |
| `BIND_HOST` | `127.0.0.1` for local-only, `0.0.0.0` for LAN |
| `SPOCK_WEBUI_PORT` | WebUI listen port |

**Critical**: In this setup, `SPOCK_WEBUI_PYTHON` and `HERMES_AGENT_BRIDGE_PYTHON` are **different things** pointing to the same venv path, but in the original service file only `SPOCK_WEBUI_PYTHON` was present. The bridge fell back to system `python3`.

## Commands

```bash
# Check status
systemctl --user status hermes-webui.service

# Restart cleanly (stops, clears resources, restarts systemd-managed process)
systemctl --user daemon-reload
systemctl --user restart hermes-webui.service

# Stop (useful before manual debugging)
systemctl --user stop hermes-webui.service

# View logs
journalctl --user -u hermes-webui.service -f
# OR
tail -f /home/thadd/.spock/webui.log
```

## Systemd vs Watchdog Conflict

The WebUI has **two** potential managers:
1. **Systemd user service** (`hermes-webui.service`) — managed by `systemctl --user`
2. **Watchdog cron job** (`*/10 * * * * ~/.hermes/scripts/hermes-watchdog.sh`) — managed by `crontab`

When both are active:
- The cron job checks if `hermes-web-ui/dist/server/index.js` is running → finds the systemd process → reports "OK"
- BUT if the systemd process dies, systemd auto-restarts it (`Restart=on-failure`)
- If the watchdog ALSO restarts it, you get two Node processes briefly, then `EADDRINUSE`
- The watchdog's `nohup` spawn and systemd's cgroup management can leave orphaned processes

**Resolution**: Pick ONE manager. Either:
- Disable the cron watchdog: `crontab -e` and remove the hermes-watchdog line
- OR disable systemd auto-restart: change `Restart=on-failure` to `Restart=no` in the service file

This setup currently keeps **both**, which is fine as long as the watchdog uses a non-conflicting approach (check pgrep, but don't kill if systemd owns it).

## Adding HERMES_AGENT_BRIDGE_PYTHON to the Service

1. Edit `~/.config/systemd/user/hermes-webui.service`
2. Add under `[Service]`:
   ```ini
   Environment="HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3"
   ```
3. `systemctl --user daemon-reload`
4. `systemctl --user restart hermes-webui.service`
5. Verify:
   ```bash
   systemctl --user show hermes-webui.service | grep Environment
   # Should show the new var
   
   # Verify the child bridge process inherited it
   ps eww -p $(pgrep -f "hermes_bridge.py" | head -1) | grep HERMES_AGENT_BRIDGE_PYTHON
   ```

## Verification After Any Restart

```bash
# 1. Port is listening
ss -tlnp | grep 8648

# 2. Health endpoint responds
curl -s http://localhost:8648/health | grep status

# 3. PID is stable
echo "PID: $(lsof -ti:8648 | head -1)"
sleep 30
echo "PID after 30s: $(lsof -ti:8648 | head -1)"

# 4. Bridge worker uses venv python (not system python)
ps aux | grep "hermes_bridge.py" | grep -v grep | head -1
# Should show: /home/thadd/.hermes/hermes-agent/venv/bin/python3
```
