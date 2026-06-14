# Pre-Update System Prep

Before running `hermes update` (core) or `git pull && npm run build` (WebUI), shut
down all running services. Skipping this leads to token conflicts, file locks,
and failed restarts.

## 1. Stop the Gateway

The gateway locks the Telegram bot token in polling mode. If the old process is
still alive when a new one starts, Telegram rejects the connection:

```
[Telegram] Telegram bot token already in use (PID 386). Stop the other gateway first.
```

Kill it before updating:

```bash
# Foreground / tmux / manual mode:
pkill -f "hermes.*gateway run"

# systemd service mode:
systemctl --user stop hermes-gateway
```

Verify nothing holds the token:

```bash
ps aux | grep -E "gateway run|hermes_bridge" | grep -v grep
```

Expected: empty output.

## 2. Stop the WebUI Server

Prevents file locks on `dist/` and `node_modules/` during rebuild:

```bash
pkill -f "node.*dist/server/index.js"
pkill -f "hermes_bridge"
```

Wait 2–3 seconds for the Node process to fully release ports:

```bash
sleep 3
curl -sf http://127.0.0.1:8648/health && echo "STILL UP" || echo "DOWN"
```

## 3. Run Core Update

```bash
hermes update --backup --yes
```

The `--backup` flag creates a timestamped backup automatically. Do NOT manually
copy files — the installer handles this.

## 4. Update WebUI (separate repo)

If you maintain a custom fork (e.g. under `/mnt/c/Users/thadd/hermes-web-ui`):

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
git fetch origin
git pull origin main

# If you have a post-checkout hook, it may auto-restore branding.
# If not, run the skill restore script:
# bash ~/.hermes/profiles/plc-coder/skills/devops/webui-customization-preserver/scripts/restore.sh

# Rebuild
~/node26/bin/npm run build
```

## 5. Restart Services

```bash
# Gateway — use tmux on WSL for persistence across terminal closes
tmux new-session -d -s hermes-gateway 'hermes -p spock gateway run'

# WebUI
cd /mnt/c/Users/thadd/hermes-web-ui
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export HERMES_WEB_UI_DISABLE_UPDATE_CHECK=true
/home/thadd/node26/bin/node dist/server/index.js
```

## Gateway Shutdown Diagnosis Pattern

If the gateway keeps shutting down **after** an update, check for a stale token
holder:

```bash
grep -i "already in use" ~/.hermes/profiles/spock/logs/gateway.log | tail -5
```

If a PID is cited (e.g. `PID 386`), check if it still exists:

```bash
ps -p 386 -o pid,cmd 2>/dev/null || echo "PID 386 is dead — token will release soon"
```

Telegram holds the token for ~5 minutes after process death. If the watchdog
cron fires every 15 minutes and hits this window, the restart will fail until
the token is released. Consider pausing the watchdog temporarily:

```bash
hermes cron pause cee59de8a25d   # gateway-watchdog
```
