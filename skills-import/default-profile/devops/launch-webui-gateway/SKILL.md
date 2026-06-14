---
name: launch-webui-gateway
description: Start the Spock WebUI server bound to 0.0.0.0 for LAN access. Handles cleanup of old instances, port conflicts, and prints the reachable URL.
title: Launch Spock WebUI Gateway
version: 1.0.0
summary: Start the Spock WebUI server bound to 0.0.0.0 for LAN access. Handles cleanup of old instances, port conflicts, and prints the reachable URL.
trigger: When the user wants to start the WebUI gateway, asks if it's running, or wants remote access to the WebUI.
---

# Launch Spock WebUI Gateway

## Purpose

Start the Spock WebUI (Hermes WebUI) HTTP server so it is reachable from the local network, not just localhost. The server normally binds to `127.0.0.1:8787` by default, which blocks remote access. This skill rebinds it to `0.0.0.0:8648` (or a configurable port) and cleans up stale processes.

## Environment & Paths

| Variable | Default | Description |
|----------|---------|-------------|
| `SPOCK_WEBUI_HOST` | `0.0.0.0` | Bind address |
| `SPOCK_WEBUI_PORT` | `8648` | Listen port |
| `SPOCK_WEBUI_REPO` | `/home/thadd/hermes-webui-new` | Path to `server.py` |
| `SPOCK_WEBUI_PYTHON` | `/home/thadd/.hermes/hermes-agent/venv/bin/python3` | Python executable |

## Repo Verification (MANDATORY — do not skip)

Thad's WSL has **multiple WebUI repositories**. Before making any change, verify which one is active:

```bash
# Check what's actually listening on the port
ss -tlnp | grep :8648 || lsof -i -P -n | grep LISTEN
# Check which server.py / node process is running
ps aux | grep -E "server\.py|node.*index|hermes-web" | grep -v grep
```

| Repo | Stack | Default Port | Entry Point |
|------|-------|-------------|-------------|
| `~/hermes-webui-new` | Python (`server.py`) | 8787 (env: 8648) | `python3 server.py` |
| `~/hermes-web-ui-ekko` | Node.js (`dist/server/index.js`) | 8648 | `node dist/server/index.js` |
| `~/hermes-webui` | Older Python | — | — |

**Rule:** If the user says "the new web ui", verify whether they mean `hermes-webui-new` (Python, `server.py`) or `hermes-web-ui-ekko` (Node.js, worked on yesterday). When in doubt, ask: "Which repo — `hermes-webui-new` (Python) or `hermes-web-ui-ekko` (Node.js)?"

## Prerequisites

- `lsof`, `ss`, or `netstat` available to detect port conflicts
- The WebUI repo exists at the configured path with `api/config.py` defining `HOST` and `PORT`

## Steps

1. **Detect existing listeners**
   ```bash
   lsof -i -P -n | grep :${PORT} || ss -tlnp | grep :${PORT}
   ```
   If something is already on the desired port, identify the PID.

2. **Kill stale WebUI server processes** (only `server.py` instances, never the gateway)
   ```bash
   ps aux | grep "server\.py" | grep -v grep
   # kill <PID> for each stale server.py
   ```

3. **Launch with environment overrides**
   ```bash
   cd ${SPOCK_WEBUI_REPO}
   SPOCK_WEBUI_HOST=${HOST} SPOCK_WEBUI_PORT=${PORT} ${PYTHON} server.py
   ```
   Run as a background process (use `background=true` terminal mode or `hermes cronjob`).

4. **Verify**
   ```bash
   ss -tlnp | grep :${PORT}
   ```
   Confirm `0.0.0.0:${PORT}` (or configured host) shows `python3` or `python` as the listener.

5. **Report**
   Print the reachable URL(s):
   ```
   http://${HOST_IP}:${PORT}/
   ```
   If `HOST` is `0.0.0.0`, also print the LAN IP (`hostname -I` or `ip addr`).

## Port Conflict Handling

- If the desired port is occupied by another `server.py` → kill it, then start
- If occupied by a different service → print a warning and suggest an alternate port
- To use a different port, set `SPOCK_WEBUI_PORT=<port>` before launch

## Multi-Repo Environment (Thad's WSL)

Thad's system has **multiple WebUI repos**. See `references/multiple-webui-repos.md` for the full comparison and decision tree. Always verify which repo is active before making changes.

Quick check:
```bash
ps aux | grep -E "server\.py|node.*index" | grep -v grep
ss -tlnp | grep :8648
```

| Repo | Stack | Default Port | Entry Point |
|------|-------|-------------|-------------|
| `~/hermes-webui-new` | Python (`server.py`) | 8787 (env: 8648) | `python3 server.py` |
| `~/hermes-web-ui-ekko` | Node.js (`dist/server/index.js`) | 8648 | `node dist/server/index.js` |

## Systemd Service Configuration

When running via systemd user service, env vars must be set in the service unit file. The server code in `api/config.py` only reads `SPOCK_WEBUI_*` — **not** `HERMES_WEBUI_*`.

### Correct service unit env vars
```ini
[Service]
Environment="SPOCK_WEBUI_HOST=0.0.0.0"
Environment="SPOCK_WEBUI_PORT=8648"
Environment="SPOCK_WEBUI_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3"
Environment="SPOCK_WEBUI_AGENT_DIR=/home/thadd/.hermes/hermes-agent"
Environment="SPOCK_WEBUI_STATE_DIR=/home/thadd/.hermes/webui"
ExecStart=/home/thadd/.hermes/hermes-agent/venv/bin/python3 /home/thadd/hermes-webui-new/server.py
```

### Common systemd pitfall: `HERMES_WEBUI_*` vs `SPOCK_WEBUI_*`
If the service file uses `HERMES_WEBUI_HOST` or `HERMES_WEBUI_PORT`, the server silently ignores them and falls back to `127.0.0.1:8787`. The service shows `active (running)` but nothing listens on the expected port.

**Detection:**
```bash
systemctl --user status hermes-webui.service   # shows "active"
ss -tlnp | grep :8648                          # empty — wrong port
cat /proc/$(pgrep -f server.py)/environ | tr '\0' '\n' | grep -i spock
```

**Fix:** Edit `/home/thadd/.config/systemd/user/hermes-webui.service`, change `HERMES_WEBUI_*` to `SPOCK_WEBUI_*`, then:
```bash
systemctl --user daemon-reload
systemctl --user restart hermes-webui.service
```

### Verify after restart
```bash
ss -tlnp | grep :8648                           # should show python3 on 0.0.0.0:8648
curl -s -o /dev/null -w "%{http_code}" http://$(hostname -I | awk '{print $1}'):8648/
# → 200
```

## Windows Desktop Launcher Pattern

For WSL-based deployments, create a PowerShell launcher that:
1. Ensures WSL is running (`wsl.exe --exec true`)
2. Auto-detects current WSL IP (`hostname -I`)
3. Verifies/starts systemd services (`systemctl --user start hermes-webui.service`)
4. Polls HTTP until the WebUI responds
5. Opens Chrome in app mode

Template: `templates/windows-launcher.ps1`

To create a Windows shortcut (.lnk) pointing to the launcher:
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut('C:\Users\<user>\Desktop\Spock WebUI.lnk')
$shortcut.TargetPath = 'powershell.exe'
$shortcut.Arguments = '-ExecutionPolicy Bypass -File "C:\Users\<user>\Desktop\Spock-WebUI-Launcher.ps1"'
$shortcut.IconLocation = 'C:\Users\<user>\Desktop\spock-icon.ico'
$shortcut.Save()
```

## Security Note

Binding to `0.0.0.0` exposes the WebUI to your local network. The WebUI should have authentication enabled (`is_auth_enabled()` in `api/auth.py`) if running on an untrusted network. If no password is set, `server.py` prints a loud warning on startup when bound to a non-loopback address.

## One-liner (quick start)

```bash
cd /home/thadd/hermes-webui-new && \
  SPOCK_WEBUI_HOST=0.0.0.0 SPOCK_WEBUI_PORT=8648 \
  /home/thadd/.hermes/hermes-agent/venv/bin/python3 server.py
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Address already in use" | Old server still running | Kill stale PID and retry |
| Gateway not reachable | Firewall or wrong interface | Check `ip addr` and `ss -tlnp` |
| Blank page / 404 | Wrong repo path | Verify `api/` directory exists next to `server.py` |
| TLS error | Missing cert/key | Set `SPOCK_WEBUI_TLS_CERT` and `SPOCK_WEBUI_TLS_KEY` or disable TLS |
