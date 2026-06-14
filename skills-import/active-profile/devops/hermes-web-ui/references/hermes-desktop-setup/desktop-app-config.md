# Session: hermes-desktop-setup (2026-05-19)

## Environment
- WSL on Windows host
- Hermes gateway already running (PID 520, Telegram connected)
- Repo cloned to: `/mnt/c/Users/thadd/.openclaw/workspace/hermes-desktop`

## Config Added (Initial — localhost only)

In `~/.hermes/config.yaml`, inserted before `display:` block at line 213:

```yaml
platforms:
    api_server:
        enabled: true
        extra:
            host: 127.0.0.1
            port: 8642
```

## Config Updated (Cross-platform — Windows app → WSL backend)

To allow the Windows Electron app to reach Hermes running inside WSL2, the `api_server` must bind to all interfaces. The gateway **requires** an API key when binding to `0.0.0.0` for security.

```yaml
platforms:
    api_server:
        enabled: true
        extra:
            host: 0.0.0.0
            port: 8642
            key: local-desktop-key-2026
```

Restart gateway after config change.

## Gateway Restart

Killed old gateway and started fresh:
```bash
hermes gateway run --replace
```

Log verification (`~/.hermes/logs/gateway.log`):
```
2026-05-19 16:07:20,745 INFO gateway.run: Connecting to api_server...
2026-05-19 16:07:20,763 INFO gateway.platforms.api_server: [Api_Server]
  API server listening on http://127.0.0.1:8642 (model: hermes-agent)
2026-05-19 16:07:20,775 INFO gateway.run: √ api_server connected
```

## Port Verification

```bash
ss -tlnp | grep 8642
# → LISTEN 0 128 127.0.0.1:8642 users:(("hermes",pid=7498,fd=19))
```

## Desktop App Connection Details

| Mode | URL | API Key | Notes |
|------|-----|---------|-------|
| Local (same machine, no WSL) | `http://127.0.0.1:8642` | empty | Gateway on `127.0.0.1` |
| Windows app → WSL backend | `http://<WSL_IP>:8642` | `local-desktop-key-2026` | Gateway on `0.0.0.0` with key |
| Windows app → WSL (port proxy) | `http://127.0.0.1:8642` | `local-desktop-key-2026` | After `netsh interface portproxy` |

WSL IP: `172.24.60.180` (obtained via `ip addr show eth0` — changes on reboot)

## App State File

The desktop app saves connection mode to `desktop.json` inside `HERMES_HOME`:
- Windows: `%USERPROFILE%\.hermes\desktop.json`
- Linux/WSL: `~/.hermes/desktop.json`

If you accidentally click **"Get Started"** (triggers local install mode) and want to return to the Welcome screen:
1. Close app completely
2. Delete `desktop.json`
3. Reopen app — Welcome screen reappears with "Connect to Remote Hermes" button

## Key File Paths

| File | Purpose |
|------|---------|
| `~/.hermes/config.yaml` | Main Hermes config (line ~213 display block) |
| `~/.hermes/hermes-agent/gateway/platforms/api_server.py` | HTTP API adapter (default host 127.0.0.1, port 8642) |
| `~/.hermes/gateway_state.json` | Gateway PID/state tracking |
| `~/.hermes/logs/gateway.log` | Startup/connect logs |
| `~/.hermes/desktop.json` | Desktop app connection state |
| `hermes-desktop/src/main/hermes.ts` | Hardcodes `LOCAL_API_URL = "http://127.0.0.1:8642"` |
| `hermes-desktop/src/preload/index.ts` | Injects `window.hermesAPI` (Electron-only) |
| `hermes-desktop/src/main/config.ts` | Reads `desktop.json` from `HERMES_HOME` |
| `hermes-desktop/src/renderer/src/App.tsx` | Screen flow: splash → welcome → install/setup → main |
| `hermes-desktop/src/renderer/src/screens/Welcome/Welcome.tsx` | Welcome screen with "Get Started" / "Connect via SSH" / "Connect to Remote Hermes" |

## Next Step for User

Run desktop app from **Windows PowerShell/CMD** (not WSL):
```powershell
cd C:\Users\thadd\.openclaw\workspace\hermes-desktop
npm run dev
```
Then click **"Connect to Remote Hermes"** (NOT "Get Started") and enter:
- URL: `http://172.24.60.180:8642`
- API Key: `local-desktop-key-2026`
