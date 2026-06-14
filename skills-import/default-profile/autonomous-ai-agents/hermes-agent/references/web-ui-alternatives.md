# Web UI Alternatives for Hermes Agent

The official `hermes dashboard` is not the only option. Several third-party web interfaces exist that wrap the same Hermes agent core with different UX.

## Third-Party Desktop Client (`fathah/hermes-desktop`)

A community Electron desktop app that connects to a local Hermes backend via the
`api_server` platform adapter.

- **Repo**: `https://github.com/fathah/hermes-desktop`
- **Connection**: `http://127.0.0.1:8642` (the `api_server` HTTP API)
- **Auth**: optional (empty for local, or `HERMES_GATEWAY_TOKEN` Bearer key)
- **Platform**: Windows / macOS / Linux (native Electron, not a web browser)
- **Requires**: the `api_server` platform enabled in `~/.hermes/config.yaml`

### Enabling `api_server` for desktop apps

Add to `~/.hermes/config.yaml`:
```yaml
platforms:
    api_server:
        enabled: true
        extra:
            host: 127.0.0.1
            port: 8642
```

Restart the gateway (`hermes gateway run --replace`) and verify:
```bash
curl http://127.0.0.1:8642/health
# → {"status": "ok", "platform": "hermes-agent"}
```

The Electron app auto-configures this block on first run if missing, but doing
it explicitly in config is faster and avoids Electron having to restart the
gateway itself.

### Desktop app connection screen
- **URL**: `http://127.0.0.1:8642`
- **API Key**: leave empty for unauthenticated local mode (the default when no
  `API_SERVER_KEY` or `platforms.api_server.key` is set), or paste the token
  from `HERMES_GATEWAY_TOKEN` in `~/.hermes/.env`.

### Quick install & dev mode (Windows)
```powershell
git clone https://github.com/fathah/hermes-desktop.git
cd hermes-desktop
npm install          # installs electron-vite + deps
npm run dev          # starts Vite dev server + Electron window
```

### Building Windows installer
```powershell
npm run build:win
# Dist output: dist/hermes-desktop Setup 0.4.3.exe
```

Requires NSIS on Windows (not available in WSL). From WSL, only
`dist/win-unpacked/` (raw binaries, no .exe) is produced.

### Why Electron instead of a browser
The app uses `ipcRenderer` APIs (`hermesAPI.onInstallProgress`, etc.) injected
via a preload script. These are **not** available in a regular browser, so opening
`http://127.0.0.1:5173` in Chrome will fail with `window.hermesAPI` undefined.

---

## nesquena/hermes-webui (7.8k stars, actively maintained)

- **Philosophy**: No build step, no framework, no bundler. Pure Python stdlib HTTP server + vanilla JS.
- **Layout**: Three-panel — left sidebar (sessions/navigation), center chat, right workspace file browser. Circular token-usage ring. Composer footer always visible.
- **Look**: Dark mode default, light mode toggle. Dark-themed with full profile support.
- **Features**: Inline file preview, session projects/tags, tool call cards, model/profile/workspace controls in footer.
- **Security**: Optional `HERMES_WEBUI_PASSWORD` env var.

### Quick install
```bash
git clone https://github.com/nesquena/hermes-webui.git hermes-webui
cd hermes-webui
python3 bootstrap.py
# Or: ./start.sh
```

### Persistent background run
```bash
./ctl.sh start              # daemon, PID at ~/.hermes/webui.pid
./ctl.sh status             # PID, uptime, bound host/port, log path
./ctl.sh logs --lines 100   # tail ~/.hermes/webui.log
./ctl.sh stop
```

### Environment variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `HERMES_WEBUI_HOST` | `127.0.0.1` | Bind address |
| `HERMES_WEBUI_PORT` | `8787` | Listen port |
| `HERMES_WEBUI_PASSWORD` | unset | HTTP Basic Auth password |
| `HERMES_WEBUI_SKIP_ONBOARDING` | `0` | Skip first-run wizard |
| `HERMES_WEBUI_AGENT_DIR` | auto-discovered | Path to hermes-agent clone |
| `HERMES_WEBUI_STATE_DIR` | `~/.hermes/webui` | SQLite state |
| `HERMES_WEBUI_DEFAULT_WORKSPACE` | `~/workspace` | File browser root |
| `HERMES_WEBUI_PYTHON` | auto-discovered | Python executable |

### Auto-discovery order (agent dir)
1. `HERMES_WEBUI_AGENT_DIR`
2. `$HERMES_HOME/hermes-agent`
3. Sibling `../hermes-agent`
4. `~/.hermes/hermes-agent`
5. `~/hermes-agent`
6. Resolve via live `hermes` CLI shebang (last resort)

Auto-discovery picks the **agent venv** first if it has both `yaml` and `AIAgent` importable, falling back to repo `.venv` then system `python3`.

## Comparison

| | Official `hermes dashboard` | `nesquena/hermes-webui` |
|--|---------------------------|-------------------|
| Framework | React 19 + Vite + Tailwind | Python stdlib + vanilla JS |
| Build step | `npm install && npm run build` | None |
| Default port | `9119` | `8787` |
| Layout | Config/status panels | Three-panel chat + file browser |
| Best for | Admin, config editing | Daily chat, file browsing |
| Start command | `hermes dashboard --skip-build` | `python3 server.py` or `./ctl.sh start` |

## Running both simultaneously

Because they use different ports (9119 vs 8787), both dashboards can run side-by-side. Kill stale processes if a port conflict arises:

```bash
# Find what's on a port
lsof -i :8787
ss -ltnp | grep 8787

# Kill gracefully
kill -15 <PID>
# Or force
kill -9 <PID>
```

## WSL-specific note

The bootstrap script tries to auto-open the browser via `gio open`. In WSL text mode this fails with `gio: http://localhost:8787: Operation not supported`. The server still starts fine; navigate to `http://localhost:8787` manually in your Windows browser, or use:

```bash
cmd.exe /c start http://127.0.0.1:8787
```
