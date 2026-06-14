---
title: Hermes Web & Desktop UI Setup
name: hermes-desktop-setup
category: devops
description: Set up the EKKOLearnAI Vue Web UI or the fathah Electron desktop app for Hermes Agent, including auth, WSL networking, and desktop shortcuts.
pinned: false
---

# Hermes Web & Desktop UI Setup

Multiple UI shells exist for Hermes Agent. This skill covers:
- **EKKOLearnAI `hermes-web-ui`** — Vue 3 + Vite + Koa standalone Web server (recommended, browser-based, no Electron hassle)
- **NousResearch `hermes-agent` dashboard** — FastAPI/React built-in dashboard (less maintained)
- **fathah `hermes-desktop`** — Electron app (deprecated for WSL due to Node module cross-platform issues)

Preferred path for this user: **EKKOLearnAI Vue Web UI**.

---

## EKKOLearnAI Web UI (`hermes-web-ui`)

Repo: `https://github.com/EKKOLearnAI/hermes-web-ui` | npm: `hermes-web-ui`

### Prerequisites
- **Node >=23.0.0** (strict; system default 22.x will not work)
- Works natively in WSL; no Windows cross-compilation headaches
- Self-contained Koa server at `packages/server/src/`

### Quick Start (WSL)

```bash
# 1. Get Node 23+
curl -fsSL https://nodejs.org/dist/v26.1.0/node-v26.1.0-linux-x64.tar.xz -o /tmp/node.tar.xz
mkdir ~/node26 && tar xf /tmp/node.tar.xz -C ~/node26 --strip-components=1
~/node26/bin/node --version   # should be v23+

# 2. Clone and build
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git ~/hermes-web-ui-ekko
cd ~/hermes-web-ui-ekko
~/node26/bin/npm install      # auto-builds client + server in prepare hook

# 3. Start
HERMES_WEB_UI_HOME=$HOME/.hermes/webui \
  PORT=8648 \
  BIND_HOST=0.0.0.0 \
  WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace \
  ~/node26/bin/node dist/server/index.js
```

### Critical Env Vars

| Var | Default | Purpose |
|-----|---------|---------|
| `HERMES_WEB_UI_HOME` | `~/.hermes-web-ui` | Auth token, SQLite DB, uploads, logs |
| `PORT` | `8648` | Web UI listen port |
| `BIND_HOST` | `0.0.0.0` | Bind address (set `127.0.0.1` for local-only) |
| `WORKSPACE_BASE` | `/opt/data/workspace` | File browser root for workspace |
| `AUTH_DISABLED` | — | Set `1` to disable login screen |
| `AUTH_TOKEN` | — | Pre-set bearer token (skips auto-gen) |

### ⚠️ Auth Token Pitfalls

**Pitfall 1: `AUTH_DISABLED=1` must be exactly `"1"` — not `"yes"`, not `***`, not any other string.**
The Node server checks `process.env.AUTH_DISABLED === "1"` (strict equality). Setting `AUTH_DISABLED=yes` or `AUTH_DISABLED=***` leaves auth fully enabled, causing token prompts that reject all requests.

> Fix: Always export exactly `AUTH_DISABLED=1` before starting.

**Pitfall 2: `.token` file from a prior run overrides `AUTH_DISABLED`**
Setting `AUTH_DISABLED=1` **does NOT disable login if a `.token` file already exists** from a prior run. The server reads `.token` on startup and still requires authentication.

**Fixes:**
1. Delete the token before starting: `rm $HERMES_WEB_UI_HOME/.token`
2. OR pass the token in the URL query string: `http://<IP>:8648/#/?token=<token>`
3. OR set `AUTH_TOKEN=your-fixed-token` and share that URL
4. When auth is **completely disabled**, remove the `/#/?token=` fragment entirely from the `.bat` shortcut URL

### Windows Desktop Shortcut (Native `.lnk`)

A native `.lnk` shortcut is preferred over `.bat` — no console flash, no cmd escape issues, supports custom icons, and the `hermes-web-ui.mjs` CLI auto-opens the browser when health checks pass.

See `references/windows-lnk-shortcut.md` for the PowerShell creation script and pitfalls.

### Windows Desktop Shortcut (Legacy `.bat`)

Create `C:\Users\<user>\Desktop\Start Hermes WebUI.bat`:

```batch
@echo off
set WSL_IP=172.24.60.180
set PORT=8648
set TOKEN=YOUR_TOKEN_HERE

REM Check if already running
wsl ss -tlnp | findstr ":%PORT%" >nul
if %errorlevel% == 0 (
    start http://%WSL_IP%:%PORT%/#/?token=%TOKEN%
    exit /b 0
)

REM Start server in background
wsl env HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=%PORT% BIND_HOST=0.0.0.0 WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace /home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js > /dev/null 2>&1 &
**Verify endpoints before starting:**
```bash
KEY=$(grep OLLAMA_API_KEY ~/.hermes/.env | cut -d= -f2)
curl -sI "https://api.ollama.com/v1/models" -H "Authorization: Bearer $KEY"  # 301 — WRONG
curl -sI "https://ollama.com/v1/models" -H "Authorization: Bearer $KEY"     # 401/200 — CORRECT
```

### Correct Node Version Requirement

The `package.json` uses `"engines": { "node": ">=23.0.0" }`. Node 22.x fails. This user extracts Node 26.1.0 to `~/node26` and invokes it via `~/node26/bin/node` because the system default is 22.x.

### Bridge is Missing from `dist/`

The TypeScript build (`tsc`) does **not** include the Python agent bridge in `dist/`. If `dist/server/agent-bridge/hermes_bridge.py` is missing, the server cannot spawn the bridge and chat will be unresponsive.

**Fix:** Manually copy the bridge script into the dist tree after every build:
```bash
mkdir -p ~/hermes-web-ui-ekko/dist/server/agent-bridge/
cp ~/hermes-web-ui-ekko/packages/server/src/services/hermes/agent-bridge/hermes_bridge.py \
   ~/hermes-web-ui-ekko/dist/server/agent-bridge/
```

### Auth Token Pitfalls

Full detail in `references/hermes-web-ui-auth.md`. Key traps discovered in this session:

- **`AUTH_DISABLED` must be exactly `"1"`** — `"yes"`, `"true"`, or any masked value leaves auth ON.
- **`.token` file from a prior run overrides `AUTH_DISABLED`** — delete `.token` or auth stays required.
- **Browser cache**: The Vue frontend caches auth state. After disabling auth, hard-refresh (`Ctrl+Shift+R`) or use incognito mode. The old `token=` URL fragment triggers auth even when auth is disabled.
- **Env inheritance**: Starting the server from a different shell context than where you exported `AUTH_DISABLED=1` silently strips the variable. Use a wrapper script that explicitly exports all vars.

### Windows Desktop Shortcut (WSL IP)

A template is maintained in this skill: `templates/start-hermes-webui-wsl.bat`. Key points:
- **Auth disabled**: set `AUTH_DISABLED=1` and strip the `/#/?token=` URL fragment entirely.
- **Auth enabled**: set `AUTH_TOKEN=...` (or read `.token`) and keep the `/#/?token=` URL.
- **WSL IP is dynamic** — run `hostname -I | awk '{print $1}'` in WSL and update the `.bat` IP.
- **WSL server must be started from WSL** (not Windows `node.exe`), because the bridge spawns a Python venv process and needs the Linux environment.
- **Start server from a wrapper script** (`templates/start-server.sh`) exporting `AUTH_DISABLED=1` explicitly, rather than relying on interactive shell exports that may get lost on backgrounding.

### Pitfall: `wsl` with cmd-style `^` escaping silently fails to start server

**Symptom:** Double-clicking the `.bat` shortcut opens the browser but the page shows "can't be reached." The server never actually started.

**Root cause:** The batch file uses cmd-style `^` escape characters inside a `wsl` command, e.g.:
```batch
wsl env ... /home/thadd/node26/bin/node ... ^> /dev/null 2^>^&1 ^&
```
`wsl` passes arguments straight to bash. Bash does not recognize `^` as an escape character — it treats `^>` and `^&` as literal file names or operators. The server command crashes silently because `^` becomes literal.

**Fix:** Use `wsl bash -c` with a proper bash `nohup ... > /dev/null 2>&1 &` string:
```batch
wsl bash -c "export HERMES_WEB_UI_HOME=... PORT=...; nohup /home/thadd/node26/bin/node ... > /dev/null 2>&1 &"
```
Inside the `bash -c` string, standard bash redirections work correctly. See `references/wsl-bat-escaping.md` for full reproduction and fix.

> See `templates/start-hermes-webui-wsl.bat` for the current known-good template.

#### Alternative: Windows Internet Shortcut (`.url`)

If the user prefers a lighter-weight option (no batch file window flashes):

1. Create `C:\Users\<user>\Desktop\Spocks WebUI.url` with content:
   ```ini
   [InternetShortcut]
   URL=http://172.24.60.180:8648/
   IconFile=C:\Users\thadd\Desktop\spock-icon.ico
   IconIndex=0
   HotKey=0
   IDList=
   ```
2. Make auth permanently disabled via `start-server.sh` (see above) so no token query param is needed.
3. The `.url` file is tiny (~200 bytes), supports custom icons, and opens the default browser when double-clicked.

> The WSL IP in the `.url` file must be updated after WSL restarts or network changes. Use `ip addr show eth0` inside WSL to find the current IP.

### Architecture

- **Client:** Vue 3 + Vite + TypeScript + Monaco Editor + xterm.js terminal
- **Server:** Koa (`packages/server/src/index.ts`)
- **Socket.IO:** Real-time chat via `ChatRunSocket`, terminal via `node-pty`
- **Auth:** Token-based (`services/auth.ts`) — auto-generates 256-bit hex if absent
- **State DB:** SQLite under `$HERMES_WEB_UI_HOME`
- **Hermes bridge:** `services/hermes/agent-bridge.ts` discovers local Hermes

### Chat Unresponsive (Stale Session DB, HTTP 301, Bridge Worker Caching)

The Web UI loads and connects but the assistant never responds. Check in order:

**1. Stale Session DB overrides — old model/provider per row**
The `sessions` table caches `model`/`provider` per row. Existing conversations retain old values even after `config.yaml` changes, because the Node server (`handleBridgeRun.ts`) passes `sessionRow.model`/`provider` directly to the bridge, bypassing global config for that conversation.

```sql
UPDATE sessions SET model = 'kimi-k2.6:cloud', provider = 'ollama-launch';
```

**2. Ollama Cloud base URL returns HTTP 301**
If logs show `APIStatusError [HTTP 301]`, the Ollama Cloud base URL is wrong. The `api.ollama.com` hostname redirects to `ollama.com`; the API client does not follow the redirect.

- `https://api.ollama.com/v1/...` → **HTTP 301** (redirects to `https://ollama.com`)  
- `https://ollama.com/v1` → **correct endpoint**

**Fix locations:**
- `.env`: `OLLAMA_BASE_URL=https://ollama.com/v1`
- `~/.hermes/auth.json`: `credential_pool.ollama-cloud[].base_url = "https://ollama.com/v1"`

Verify endpoints before starting:
```bash
KEY=$(grep OLLAMA_API_KEY ~/.hermes/.env | cut -d= -f2)
curl -sI "https://api.ollama.com/v1/models" -H "Authorization: Bearer $KEY"  # 301 — WRONG
curl -sI "https://ollama.com/v1/models" -H "Authorization: Bearer $KEY"     # 401/200 — CORRECT
```

**3. Bridge Worker caches old config**
The Agent Bridge spawns a **persistent worker process** that reads `config.yaml` + `.env` **once at startup** and never re-reads them. Editing config files while the server is running leaves the worker with stale state. Restart is required.

```bash
# Kill all bridge processes (main + worker)
pkill -f hermes_bridge
```

The Node server auto-spawns a fresh bridge on the next chat message.

> Restart the Node server after DB changes.

```bash
curl http://127.0.0.1:8648/health
# {"status":"ok","platform":"hermes-agent","version":"v0.14.0","webui_version":"0.5.30"}
```

### Docker (Alternative)

```bash
WEBUI_IMAGE=ekkoye8888/hermes-web-ui docker compose up -d
# exposes port 6060
```

---

## Legacy: Electron Desktop App (fathah/hermes-desktop)

See `references/electron-setup.md` and `references/desktop-app-config.md` for historical steps. Abandoned for this user due to:
- WSL/Windows Node module format incompatibility (no `.cmd` wrappers)
- Accidental "Get Started" onboarding installs a second Hermes instance
- NSIS build failures on WSL (Windows-only tool)

## Quick Start (Electron — Deprecated)

1. **Clone and install** (must be from **Windows PowerShell/CMD**, not WSL):
   ```powershell
   git clone https://github.com/fathah/hermes-desktop.git
   cd hermes-desktop
   npm install
   npm run build
   ```

2. **Enable the `api_server` platform** in `~/.hermes/config.yaml`:
   ```yaml
   platforms:
     api_server:
       enabled: true
       extra:
         host: 127.0.0.1
         port: 8642
   ```

3. **Restart the Hermes gateway:** `hermes gateway run --replace`

4. **Run from PowerShell:** `npm run dev`

5. **Connect:** Click "Connect to Remote Hermes", URL `http://127.0.0.1:8642`, leave API Key empty.

## Resetting Electron App State

If you accidentally click **"Get Started"** and want to return to the Welcome screen:

```powershell
Remove-Item -Force "$env:USERPROFILE\.hermes\desktop.json"
```

Reopen the app — Welcome screen reappears.

## Electron Pitfalls

- **`'electron-vite' is not recognized` in PowerShell?** `node_modules` was installed from WSL (no `.cmd` wrappers). Delete `node_modules` and `npm install` from Windows.
- **"Cannot read properties of undefined" in browser?** The Electron preload script (`src/preload/index.ts`) injects `window.hermesAPI`. A regular browser doesn't have this API. Use Electron, not Chrome.
- **Windows app can't reach WSL on `127.0.0.1`?** WSL2 uses a virtual NIC; Windows `localhost` doesn't map. Use `0.0.0.0` + WSL IP, or set up Windows port forwarding.

## References

- `references/desktop-app-config.md` — Electron session-specific config snippets and verification logs
- `references/hermes-web-ui-auth.md` — Auth-token pitfall reproduction and fix
- `references/hermes-web-ui-desktop-shortcut.md` — Known-good Windows .bat template
- `references/webui-stale-session-fix.md` — Chat unresponsive due to stale session DB overrides (model/provider drift)