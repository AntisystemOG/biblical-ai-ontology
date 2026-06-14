# Security Audit & Auth Recovery — 2026-05-21

## Audit Findings — Relevant to WebUI

- **D:\ drive 100% full** — clean before services break.
- **Gateway port 8642 and WebUI port 8648 listen on 0.0.0.0** — fine on home LAN but restrict if ever exposed externally.
- **No iptables/ufw** — acceptable on WSL (Windows firewall handles it).
- **Two WebUI servers discovered:**

| Port | Server | Repo Path | Auth Status |
|------|--------|-----------|-------------|
| 8648 | EKKOLearnAI WebUI (Node) | `/mnt/c/Users/thadd/hermes-web-ui` | **Real token auth** (after fix) |
| 8787 | Old Spock WebUI (Python) | `/home/thadd/hermes-webui-new/server.py` | Unknown — separate server |

## Dual-Server Confusion

Thad's setup has **two separate WebUI implementations**:
1. **EKKOLearnAI WebUI** — Node.js, correct repo, the one he actually uses
2. **Old Spock WebUI** — Python Flask server in `~/hermes-webui-new/`. Legacy.

The systemd user service (`~/.config/systemd/user/hermes-webui.service`) was rewritten to point to the **correct** local Node.js build:
```ini
WorkingDirectory=/mnt/c/Users/thadd/hermes-web-ui
ExecStart=/home/thadd/.hermes/node/bin/node dist/server/index.js
```
NOT the old Python `server.py` path. Service is enabled for autostart.

## Auth Recovery Steps Applied

1. **Kill old server** — `kill 8244` (old index.js with auth disabled)
2. **Restart without AUTH_DISABLED** — background node process serving `/mnt/c/Users/thadd/hermes-web-ui`
3. **Verify token enforced** — `/health` with correct token returns full data; `/health` without token returns same data on public endpoints (WebUI doesn't fully block health endpoint, but WS/API require token)
4. **Update `.bat` launcher** — reads real token from WSL instead of hardcoding `fake-token`

## Launcher `.bat` Requirements

```bat
:: Fetch real token from WSL
for /f "tokens=*" %%a in ('wsl bash -lc "cat /home/thadd/.hermes/webui/.token 2>/dev/null || echo NONE"') do set WSLTOKEN=%%a

:: Start server WITHOUT AUTH_DISABLED in environment
wsl bash -lc 'cd /mnt/c/Users/thadd/hermes-web-ui && nohup node bin/hermes-web-ui.mjs start > ~/.hermes-web-ui/server.log 2>&1 &'

:: Open browser with real token
start "" "http://localhost:8648/?token=%WSLTOKEN%"
```

## Process Cleanup After Restart

The WebUI spawns `hermes_bridge.py` child processes via IPC sockets. When the server crashes or is killed, these bridge processes often become orphaned and will respawn or compete with new instances. After any WebUI restart:

1. Check for duplicate bridge processes:
   ```bash
   ps aux | grep "hermes_bridge\|agent-bridge" | grep -v grep
   ```
2. Kill orphaned PIDs that don't belong to the current server:
   ```bash
   # The active bridge runs from the same node_modules path as the current server
   # Orphans often run from the old repo path /mnt/c/Users/thadd/hermes-web-ui/dist/server/agent-bridge/
   kill <orphan_pid>
   ```
3. Verify only one bridge remains:
   ```bash
   ps aux | grep "hermes_bridge" | grep -v grep | wc -l  # Should be 1
   ```

## State Snapshot Note

Four pre-update state snapshots contain old `.env` files with historical secrets:
- `/home/thadd/.hermes/state-snapshots/2026*/*/.env`
These should be rotated or deleted periodically.

## File Permissions Fix Applied

`/home/thadd/.hermes/SOUL.md` was found world-writable (777). Recommended: `chmod 644`.
