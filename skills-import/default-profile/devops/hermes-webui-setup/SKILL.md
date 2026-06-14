---
name: hermes-webui-setup
id: hermes-webui-setup
title: Hermes WebUI Setup and Troubleshooting
description: Complete setup, configuration, and debugging of the EKKOLearnAI/hermes-web-ui repository on WSL with Ollama Cloud or local inference. Covers Node v26, agent bridge, auth disable, provider/model fixes, dev mode, production deployment, and common failure modes.
trigger:
  - set up hermes web ui
  - install hermes webui
  - webui chat not working
  - web ui unresponsive
  - agent bridge error
  - access token not working
  - fix hermes webui
  - ollama 301 error
  - hermes web ui dev mode
  - create desktop shortcut for webui
  - launch webui from desktop
  - webui shortcut not working
  - webui customize logo
  - webui rebrand spock
  - thinking avatar video
  - copy prebuilt dist
---

This skill is for **THAD'S** Hermes WebUI environment. It is NOT a generic install guide.

When Thad says **"web ui"** or **"webui"** without further qualification, he ALWAYS refers exclusively to the EKKOLearnAI/hermes-web-ui repository at `/mnt/c/Users/thadd/hermes-web-ui`. Do NOT disambiguate to other web interfaces, dashboards, or tools. Default all "webui" / "web ui" queries directly to this repo.

## Prerequisites
- WSL or Linux host
- Hermes Agent already installed (`~/.hermes/` with `config.yaml`, `.env`)
- Git, curl available

### Discovering your current Node setup
See `references/node-upgrade-tarball.md` for the full Node upgrade path.
Also included: `scripts/check-node-and-upgrade.sh` — a self-service probe-and-upgrade script.

```bash
# Find the active Node binary and its real install path
which node && readlink -f $(which node) && dirname $(which node)
# Example output pointing to a managed install (not system apt):
# /home/thadd/.local/bin/node
# /home/thadd/.hermes/node/bin/node
# /home/thadd/.local/bin
```

## 1. Clone & Build

```bash
# Clone
cd ~
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git ~/hermes-web-ui-ekko

# Install Node v26 (repo requires >=23)
cd /tmp && wget https://nodejs.org/dist/v26.1.0/node-v26.1.0-linux-x64.tar.xz
tar -xf node-v26.1.0-linux-x64.tar.xz -C ~
mv ~/node-v26.1.0-linux-x64 ~/node26
~/node26/bin/node --version   # verify v26.1.0

# Build
cd ~/hermes-web-ui-ekko
~/node26/bin/npm install
```

### Upgrading Node in a managed install directory
If Node was installed by unpacking a tarball to a custom directory (e.g., `~/.hermes/node/`) and symlinked into `~/.local/bin/`, upgrade in-place:

```bash
# 1. Stop all Node processes (web UI server, etc.)
pkill -f "dist/server/index.js"
pkill -f "hermes_bridge"
sleep 2
ss -tlnp | grep 8648  # confirm port is free

# 2. Download latest v23 (or v26) tarball
cd /tmp
curl -fsSL -o node-new.tar.xz https://nodejs.org/dist/latest-v23.x/node-v23.X.X-linux-x64.tar.xz

# 3. Back up old install
mv ~/.hermes/node ~/.hermes/node-backup-$(node --version | tr -d 'v')

# 4. Extract new Node over the old path
mkdir -p ~/.hermes/node
cd ~/.hermes/node && tar -xf /tmp/node-new.tar.xz --strip-components=1

# 5. Verify
node --version   # e.g., v23.11.1
npm --version
```

## 2. Fix Missing Agent Bridge in dist/

The build output is missing the Python bridge script. Copy it manually:

```bash
mkdir -p ~/hermes-web-ui-ekko/dist/server/agent-bridge
cp ~/hermes-web-ui-ekko/packages/server/src/services/hermes/agent-bridge/hermes_bridge.py \
   ~/hermes-web-ui-ekko/dist/server/agent-bridge/
```

## 3. Configure Auth Disable (CRITICAL)

**Must be exactly `AUTH_DISABLED=1`** — the server code checks `=== "1"`.

```bash
# Add to ~/.hermes/.env
echo "AUTH_DISABLED=1" >> ~/.hermes/.env

# Also ensure it's set when starting the server
```

- `AUTH_DISABLED=yes` — **does NOT work**
- `AUTH_DISABLED=true` — **does NOT work**
- `AUTH_DISABLED=1` — **correct**

### Token & Credential Hygiene (CRITICAL)

`.hermes/.env` is the single store for all sensitive tokens (Ollama, Telegram, ElevenLabs, GitHub PAT, Brave API key). Treat it like a vault.

**Rule 1: Append, never overwrite**
```bash
# WRONG — wipes all existing tokens
echo "GITHUB_PAT=token" > ~/.hermes/.env

# RIGHT — preserves existing keys
echo "GITHUB_PAT=token" >> ~/.hermes/.env
```

**Rule 2: Edit with `nano`, never reconstruct from chat**
Credentials in chat transcripts are **redacted** (`***`). Pasting what you see in chat will corrupt the file with literal `***` values. If `.env` is damaged, restore from a known clean backup (`.env.bak.pre-brave`) using Python raw write, or re-enter tokens manually in `nano`. Never try to reconstruct from redacted transcript output.

**Rule 3: Never expose tokens in chat**
If a token must be passed to a subprocess (e.g., git push), use a short-lived inline pattern and immediately clean up:
```bash
source ~/.hermes/.env && \
  cd /path/to/repo && \
  git remote set-url origin "https://${GITHUB_PAT}@github.com/USER/REPO.git" && \
  git push && \
  git remote set-url origin "https://github.com/USER/REPO.git"
```
After pushing, **verify the remote is cleaned**: `git remote -v` must NOT show the token.

**Rule 4: Revoke exposed tokens immediately**
If a token was accidentally pasted in chat or terminal history, treat it as burned:
- Revoke the token at GitHub (or respective provider) settings
- Generate a new token
- Replace in `~/.hermes/.env` via `nano`

## 4. Configure Ollama Cloud Provider

Ollama Cloud base URL is **`https://ollama.com/v1`**, NOT `https://api.ollama.com`.
The latter returns HTTP 301 redirects which break the API client.

```bash
# ~/.hermes/.env
OLLAMA_BASE_URL=https://ollama.com/v1
OLLAMA_API_KEY=<your_key>
```

```yaml
# ~/.hermes/config.yaml
model:
  default: kimi-k2.6
  provider: ollama-cloud
providers:
  ollama-cloud:
    api: https://ollama.com/v1
    default_model: kimi-k2.6
    models:
      - kimi-k2.6
```

**Verify the endpoint works:**
```bash
curl -s https://ollama.com/v1/models -H "Authorization: Bearer $OLLAMA_API_KEY"
```

## 5. Fix auth.json Base URL

If auth.json has stale `base_url` for the credential pool, update it:

```bash
python3 -c "
import json, os
with open(os.path.expanduser('~/.hermes/auth.json')) as f: a=json.load(f)
if a.get('credential_pool',{}).get('ollama-cloud'):
    for e in a['credential_pool']['ollama-cloud']:
        e['base_url'] = 'https://ollama.com/v1'
with open(os.path.expanduser('~/.hermes/auth.json'),'w') as f: json.dump(a,f,indent=2)
"
```

## 6. Create Start Script

Create `/home/thadd/.hermes/webui/start-server.sh`. The `set -a`/`set +a` pattern exports every `.env` variable into the script's environment. If you hardcode another `export AUTH_DISABLED=...` after sourcing, it will override the value from `.env`.

```bash
#!/bin/bash
export HERMES_HOME=/home/thadd/.hermes
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export PORT=8648
export BIND_HOST=0.0.0.0
export WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace

# Source .env so AUTH_DISABLED=1 is loaded (exports all variables)
set -a
. "$HERMES_HOME/.env"
set +a

# Do NOT add a second 'export AUTH_DISABLED=...' here — it overrides .env
cd /home/thadd/hermes-web-ui-ekko
exec /home/thadd/node26/bin/node dist/server/index.js
```

### Pitfall: accidental `***` or `yes`/`true` override
A common copy-paste error is pasting the redacted placeholder `***` literally into the start script or `.env`. The server checks `AUTH_DISABLED === "1"`; `***`, `yes`, and `true` all silently re-enable token auth.

**Check the actual file values:**
```bash
grep "^AUTH_DISABLED" ~/.hermes/.env
grep "AUTH_DISABLED" ~/.hermes/webui/start-server.sh | grep -v "^#"
```
Both must output `AUTH_DISABLED=1` exactly. If the second line printed nothing, the script correctly sourced `.env` without a hardcoded override. If it outputs anything other than `AUTH_DISABLED=1`, patch it.

## 7. Start Server (Production)

```bash
# Kill old processes first
pkill -f "dist/server/index.js"
pkill -f "hermes_bridge"
sleep 1

# Start new server
bash /home/thadd/.hermes/webui/start-server.sh > /home/thadd/.hermes/webui/logs/server.log 2>&1 &

# Verify
sleep 3
curl -s http://127.0.0.1:8648/health
```

Expected output should NOT contain "Auth enabled".

## 8. Dev Mode (Hot-Reload, No Rebuild)

**This is the workflow for iterating on UI changes.** Dev mode serves from source files directly and auto-refreshes the browser on save. Production `dist/` is not used.

### Architecture
- **Backend API** (port 8648): Hermes bridge, HTTP API, WebSockets — must be running
- **Vite Dev Client** (port 5173): Hot-reloads Vue/TS source instantly
- **Proxy config** in `vite.config.ts` forwards `/api` and `/v1` calls to port 8648

### When to use Dev Mode
- Tweak sidebar text, logo, colors, component logic
- Iterative front-end branding changes
- Any change requiring multiple save/test cycles

### When NOT to use Dev Mode
- Single logo swap on production deployment → just replace `dist/client/logo.png` and restart
- Final delivery → `npm run build` and relaunch from desktop icon

### Step-by-Step Dev Mode Launch

**1. Kill existing production server (port 8648)**
```bash
pkill -f "dist/server/index.js"
sleep 1
ss -tlnp | grep 8648   # should be empty
```

**2. Start backend API server on 8648 (in background)**
```bash
env HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=8648 BIND_HOST=127.0.0.1 WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace AUTH_DISABLED=1 /home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js &
sleep 4
curl -s http://127.0.0.1:8648/health   # verify ok
```

**3. Start Vite dev client on 5173 (in background)**
```bash
cd /home/thadd/hermes-web-ui-ekko
npx vite --host --port 5173 &
sleep 3
ss -tlnp | grep 5173   # should show node listening
```

**4. Open browser**
`http://172.24.60.180:5173` (or `http://127.0.0.1:5173`)

**5. Edit source files** (`packages/client/src/**/*.vue`, `.ts`, `.scss`)
Save → browser auto-refreshes instantly. No build step.

**6. When satisfied, build permanent**
```bash
npm run build   # rebuilds dist/
```
Then relaunch from desktop icon (`Start Hermes WebUI.bat`) which starts from `dist/`.

### Dev Mode vs. Production

| Aspect | Production (`dist/`) | Dev Mode (Vite) |
|---|---|---|
| Entry point | `node dist/server/index.js` | Backend + `vite --host` |
| Static assets | `dist/client/` | `packages/client/src/` |
| Rebuild required? | Yes, every change | No, hot reload |
| Proxy `/api` | Server handles directly | `vite.config.ts` proxy to 8648 |
| Performance | Minified, optimized | Source maps, unminified |
| Port | 8648 (combined) | 8648 (backend) + 5173 (dev) |

### `npm run dev` does NOT exist in this repo

The `package.json` scripts define `npm run dev` as `"concurrently \"npm run dev:server\" \"npm run dev:client\""`, but the repository does **not** include the `dev:server` / `dev:client` configuration out-of-the-box. The `dev` script will fail if run.

**Actual dev mode setup:** run the backend API server and Vite dev client as two separate processes (see below). Production mode (`dist/`) is started with `node dist/server/index.js`.

`npm start` runs `"vite --host --port 8648"` per `package.json`. It is **not** production mode. It is a Vite dev server that serves the frontend SPA directly on port 8648, but it **lacks the agent bridge, WebSockets, and API routes** that `dist/server/index.js` provides. Only use `npm start` when you need a quick frontend-only preview of source files with hot reload. Never confuse it with `node dist/server/index.js` or `node bin/hermes-web-ui.mjs start`.

## 9. Verify Auth is Actually Disabled

```bash
# Check server log for NO "Auth enabled" line
grep "Auth enabled" /home/thadd/.hermes/webui/logs/server.log
# Should return nothing if auth is truly disabled

# Check API endpoints work without token
curl -s http://127.0.0.1:8648/api/auth/status
curl -s http://127.0.0.1:8648/api/hermes/config/models
```

**Browser cache issue:** If the browser still shows a token prompt after server-side auth is disabled, it's cached frontend state. Hard-refresh with `Ctrl + Shift + R` or open incognito window.

## Common Errors

### Chat "thinking" forever, local endpoint OK
**Cause:** Local Ollama has zero models (`{"models":[]}`), OR stale bridge workers from old server runs are intercepting IPC.
**Fix:** Check `curl http://localhost:11434/api/tags`. If empty, switch to `ollama-cloud` provider. Also kill ALL old bridge workers before restart:
```bash
pkill -f "hermes_bridge"
sleep 1
# Verify only the new server's bridge remains
pgrep -f "hermes_bridge"
```

### HTTP 301 from api.ollama.com
**Cause:** Wrong base URL.
**Fix:** Use `https://ollama.com/v1`

### "Auth enabled" in logs despite env var set
**Cause:** Used `yes` or `true` instead of `1`, or a hardcoded override in the start script overrides the `.env` value. Also possible: literal redacted placeholder `***` was pasted into `.env` or the start script.
**Fix:** Ensure `AUTH_DISABLED=1` exactly, and check `start-server.sh` doesn't hardcode a different value. See `references/auth-debugging.md` for full diagnostic path, including credential-file protection bypass and redaction-leak pitfalls.

### "no API key was found" for ollama-cloud (bridge log)
**Cause:** `.env` contains `OLLAMA_API_KEY=***` (a literal redacted placeholder) or is empty.
**Fix:** Restore `.env` from a clean backup (`.env.bak.pre-brave`) via Python raw write. Never reconstruct secrets from redacted chat output. See `references/auth-debugging.md`.

### Chat says "thinking" but never responds
**Cause:** Agent bridge using wrong model/provider, hitting HTTP 301, OR local Ollama is alive but has zero models (`{"models":[]}`).
**Fix:** Check `~/.hermes/config.yaml`, verify Ollama endpoint. If local Ollama is empty, either pull a model or switch to `ollama-cloud` provider. Update session DB if needed:
```python
import sqlite3
c = sqlite3.connect('/home/thadd/packages/server/data/hermes-web-ui.db')
c.execute("UPDATE sessions SET model='kimi-k2.6', provider='olla
ma-cloud'")
c.commit()
```

### "Token required" in browser after server restart
**Cause:** Frontend cached auth state.
**Fix:** Hard-refresh browser or clear site data. Server-side auth is already disabled.

### SPA auto-redirects to /login even with AUTH_DISABLED=1
**Cause:** The client-side Vue SPA doesn't know auth is disabled on the server until it receives a 401 on an API call, then redirects to `/login`. It won't serve the chat UI without a token.

**Fix — pass a dummy token via URL:**
The SPA's `main.ts` picks up `token` from URL or `window.__LOGIN_TOKEN__` and auto-submits it. When `AUTH_DISABLED=1` is active server-side, any token is accepted. Append `?token=fake-token` to the URL:

```
http://localhost:8648/?token=fake-token
```

The SPA auto-submit, server says "OK", session continues. No login page.

**In a Windows `.bat` launcher:**
```bat
@echo off
setlocal EnableDelayedExpansion
 set URL=http://127.0.0.1:8648
 :: Check if auth is needed by querying auth status
 for /f "delims=" %%a in ('curl -sf http://127.0.0.1:8648/api/auth/status') do set AUTH_STATUS=%%a
 echo !AUTH_STATUS! | findstr "hasPasswordLogin" >nul
 if !errorlevel!==0 (
     :: SPA will demand token — inject fake one
     set URL=http://127.0.0.1:8648/?token=fake-token
 )
 start "" "!URL!"
```

### "Web UI crashed" after cosmetic changes (logo, title, sidebar text)
**Symptom:** User reports "changes we made are making it crash." Recent edits: `index.html` title, `logo.png`, `AppSidebar.vue` alt/text, `chunkSizeWarningLimit`.

**Actual cause:** The server process was stopped (e.g., previous session ended with SIGTERM) and was never restarted. The cosmetic code changes were harmless — the service was simply down. The changes in `package.json` specify `"node": ">=23.0.0"` and the active Node was v22.22.3, so `npm run build` would fail with an engine mismatch, but the *running* server from a prior `dist/` build was unaffected by this — it was just absent.

**Diagnostic:**
```bash
ss -tlnp | grep 8648   # verify port is empty
# If empty, server is down — NOT a crash from recent code
```

**Fix:**
```bash
# If port is free, just start it:
cd /home/thadd/hermes-web-ui-ekko
PORT=8648 NODE_ENV=production node dist/server/index.js &
# Or use the CLI wrapper:
node bin/hermes-web-ui.mjs start 8648
```

**If Node version is too old for `npm run build`:**
```bash
node --version
# If < 23, do the in-place upgrade (see §1 Prerequisites and `references/node-upgrade-tarball.md`).
# After Node 23+ is active, rebuild:
npm run build
```

**Rule:** Always verify process existence (`ss -tlnp`) before blaming recent code changes.

### Server was killed by a previous agent session on exit
**Symptom:** Port 8648 is empty. The last session ended with the server running, but now it's gone.

**Actual cause:** If the server was started inside the agent's foreground or background terminal and the agent session terminated, the process group may have been killed. A server launched via `node bin/hermes-web-ui.mjs start` writes a PID file and runs detached, surviving agent exits. A server started with a raw `node dist/server/index.js` (with no `nohup` or `disown`) is tied to the agent's terminal session.

**Fix:** Prefer the CLI wrapper for durable startup:
```bash
node bin/hermes-web-ui.mjs start 8648
# This daemonizes, writes PID file, redirects logs, and survives terminal closure.
```

**Rule:** Always verify process existence (`ss -tlnp`) before blaming recent code changes.

### Server was killed by a previous agent session on exit
**Symptom:** Port 8648 is empty. The last session ended with the server running, but now it's gone.

**Actual cause:** If the server was started inside the agent's foreground or background terminal and the agent session terminated, the process group may have been killed. A server launched via `node bin/hermes-web-ui.mjs start` writes a PID file and runs detached, surviving agent exits. A server started with a raw `node dist/server/index.js` (with no `nohup` or `disown`) is tied to the agent's terminal session.

**Fix:** Prefer the CLI wrapper for durable startup:
```bash
node bin/hermes-web-ui.mjs start 8648
# This daemonizes, writes PID file, redirects logs, and survives terminal closure.
```

---

## 10. Re-branding the WebUI

### Fast path: production post-build swap (no rebuild)

If running from `dist/` via desktop `.bat`/`.ps1` launcher:

```bash
# Replace compiled sidebar/login/empty-state logo
cp /path/to/new-logo.png ~/hermes-web-ui-ekko/dist/client/logo.png

# Also replace source assets for future builds
cp /path/to/new-logo.png ~/hermes-web-ui-ekko/packages/client/public/logo.png
cp /path/to/new-logo.png ~/hermes-web-ui-ekko/packages/client/src/assets/logo.png
```

Then **kill the server** and restart. Hard-refresh browser (`Ctrl + Shift + R`) after restart.

### Source-level re-branding (dev mode workflow)

Edit source files in `packages/client/src/`, save, and let Vite hot-reload:

| What | Source File | Rebuild? |
|------|------------|----------|
| Sidebar logo + text | `packages/client/src/components/layout/AppSidebar.vue` | No (dev mode) |
| Browser tab title | `packages/client/index.html` | No (dev mode) |
| Login screen logo | `packages/client/src/views/LoginView.vue` | No (dev mode) |
| Chat empty state | `packages/client/src/components/hermes/chat/MessageList.vue` | No (dev mode) |
| Built assets served | `dist/client/` | Yes (`npm run build`) |

### Surgical text replacement in compiled JS (post-build)

**Replace ONLY user-facing strings** — titles, alt text, empty-state messages. NOT internal identifiers, API routes, variable names, config strings.

```bash
# Example: replace user-visible titles in compiled JS bundles
sed -i 's/title:"Hermes Web UI"/title:"Spock Web UI"/g' \
  ~/hermes-web-ui-ekko/dist/client/assets/js/index-*.js
sed -i 's/emptyState:"Start a conversation with Hermes Agent"/emptyState:"Start a conversation with Spock"/g' \
  ~/hermes-web-ui-ekko/dist/client/assets/js/index-*.js
sed -i 's/alt:"Hermes",class:"empty-logo"/alt:"Spock",class:"empty-logo"/g' \
  ~/hermes-web-ui-ekko/dist/client/assets/js/index-*.js
```

~150+ internal references should be left alone.

### Custom thinking avatar video

The SPA shows a looping MP4 video when the assistant is "thinking." Files are `thinking-light.mp4` (light theme) and `thinking-dark.mp4` (dark theme).

If a single video works for both themes, copy it to both files:

```bash
# Replace with your custom video (e.g., Star Trek badge)
SOURCE_VIDEO="/path/to/startrek-badge.mp4"
cp "$SOURCE_VIDEO" packages/client/src/assets/thinking-light.mp4
cp "$SOURCE_VIDEO" packages/client/src/assets/thinking-dark.mp4
# Also copy to public for direct serving
cp "$SOURCE_VIDEO" packages/client/public/thinking-light.mp4
cp "$SOURCE_VIDEO" packages/client/public/thinking-dark.mp4
```

After copying, build with `npm run build`. The videos get hashed into `dist/client/assets/mp4/thinking-light-*.mp4`.

**Build failure fallback:** If `npm run build` fails (e.g., missing rolldown native binding on WSL), **copy a pre-built custom `dist/client/` from another repo** that already has the customizations baked in:

```bash
# Assuming hermes-web-ui-ekko has a pre-built dist with customizations
cp -r /home/thadd/hermes-web-ui-ekko/dist/client/* \
      /mnt/c/Users/thadd/hermes-web-ui/dist/client/
```

This preserves custom assets (logo, thinking video, compiled HTML title) without needing a local build. Use this when:
- `npm run build` fails (missing native bindings, wrong Node version)
- The custom `dist/` is from the user's fork (`AntisystemOG/hermes-web-ui`) which already has Spock branding

### Verify branding

1. Restart server (kill old; start new)
2. **Hard-refresh browser: `Ctrl + Shift + R`**
3. Check: tab title, sidebar logo alt text, empty-state message, login screen title

---

## Relevant Files

| File | Purpose |
|------|---------|
| `packages/client/index.html` | Browser tab title (source) |
| `packages/client/src/components/layout/AppSidebar.vue` | Sidebar logo + text (source) |
| `packages/client/src/views/LoginView.vue` | Login screen logo |
| `packages/client/src/components/hermes/chat/MessageList.vue` | Empty chat logo |
| `packages/client/public/logo.png` | Logo asset (served at /logo.png) |
| `dist/client/logo.png` | Compiled sidebar logo |
| `dist/client/index.html` | Compiled `<title>` tag |
| `vite.config.ts` | Dev server proxy config, build settings |
| `vite.config.website.ts` | Website-specific build config (chunk size limit, etc.) |
| `~/.hermes/webui/start-server.sh` | Production startup script |
| `references/node-upgrade-tarball.md` | Node in-place upgrade steps |
| `scripts/check-node-and-upgrade.sh` | Self-service Node version probe + upgrade |
| `references/source-rebrand-guide.md` | Step-by-step source-level branding changes |
| `references/rebrand-ui.md` | Post-build rebrand (compiled JS surgery) |
| `references/auth-debugging.md` | Auth-disabled diagnostics, token-injection launcher patterns |
| `references/thinking-avatar-customization.md` | Thinking video replacement + build-fallback |
| `references/thad-multi-repo-environment.md` | Thad's WSL has multiple WebUI repos. **Must-read before ANY launch or shortcut creation.** |
| `references/launcher-shortcut-pattern.md` | Correct Windows Desktop `.lnk` pattern for WSL-bound Hermes WebUI. VBS wrapper, PowerShell builder, stale-process cleanup, token injection. |
| `references/systemd-auto-respawn-wrong-server.md` | systemd user service trapping port 8648 |
| `templates/launch-hermes-webui.bat` | Debug-first Desktop `.bat` with server health check + optional token injection |

## 11. Windows Desktop Launcher (Visible .bat First)

When the user wants a Desktop shortcut that opens the Hermes WebUI browser, start with a **visible `.bat` file** for debugging. Only after it works consistently, upgrade to a silent `.lnk` (VBS wrapper or PowerShell).

### Debug-first `.bat` pattern

Create `C:\Users\thadd\Desktop\Launch Hermes WebUI.bat`:

```bat
@echo off
setlocal EnableDelayedExpansion

echo Checking Hermes WebUI on port 8648...

:: Check if server is already running
curl -sf http://127.0.0.1:8648/health >nul 2>nul
if %errorlevel% == 0 (
    echo Server already running — opening browser...
    goto OPEN_BROWSER
)

:: Not running — start it via WSL
echo Starting Hermes WebUI server...
wsl bash -lc "cd /mnt/c/Users/thadd/hermes-web-ui && nohup node bin/hermes-web-ui.mjs start > ~/.hermes-web-ui/server.log 2>&1 &"

:: Wait up to 30 seconds
echo Waiting for server to start...
set RETRIES=0
:WAIT_LOOP
    timeout /t 1 /nobreak >nul
    curl -sf http://127.0.0.1:8648/health >nul 2>nul
    if %errorlevel% == 0 goto OPEN_BROWSER
    set /a RETRIES+=1
    if !RETRIES! lss 30 goto WAIT_LOOP

echo ERROR: Server failed to start within 30 seconds.
echo Check logs: wsl tail -n 20 ~/.hermes-web-ui/server.log
pause
exit /b 1

:OPEN_BROWSER
:: If auth is enabled, auto-inject dummy token from WSL
for /f "delims=" %%a in ('wsl bash -lc "curl -s http://127.0.0.1:8648/api/auth/status | grep hasPasswordLogin || echo noauth"') do (
    set AUTH_STATUS=%%a
)
set AUTH_STATUS=!AUTH_STATUS: =!
echo !AUTH_STATUS! | findstr "false" >nul
if !errorlevel! == 0 (
     :: Auth disabled — open without token (but SPA still needs ?token for auto-submit)
     start "" "http://localhost:8648/?token=fake-token"
) else (
     :: Auth token required
     for /f "delims=" %%b in ('wsl cat ~/.hermes-web-ui/.token') do (
         set TOKEN=%%b
     )
     set TOKEN=!TOKEN: =!
     if "!TOKEN!"=="" (
         start "" "http://localhost:8648/"
     ) else (
         start "" "http://localhost:8648/?token=!TOKEN!"
     )
)
exit /b 0
```

**Why visible `.bat` first?**
- Windows `wsl.exe` argument parsing is brittle; `.bat` lets the user see exactly what fails.
- If `wsl` command is not found, the `.bat` shows the error instead of silently doing nothing.
- If the server doesn't start, the timeout error and log path are visible.

### Pitfall: Windows `start` command with quoted string
Windows `cmd /c start` interprets the **first quoted argument as the window title**, not the URL. Always use `start "" "http://localhost:8648"` (empty title `""` before quoted URL).

### When auth is enabled: token injection vs. disabling

If the server does **not** have `AUTH_DISABLED=1` set, the browser will show a token login screen. Two fixes:

1. **Disable auth (recommended for single-user desktop):**
   ```bash
   echo "AUTH_DISABLED=1" >> ~/.hermes/.env
   ```
   The `.bat` above will then open `http://localhost:8648/?token=fake-token`.

2. **Auto-inject the real token via URL:**
   The `.bat` reads `~/.hermes-web-ui/.token` from WSL and appends `?token=...`.

### Upgrading to a clean `.lnk` (after `.bat` is confirmed)

Once the `.bat` works reliably, create a hidden VBS wrapper and `.lnk` shortcut. See `references/launcher-shortcut-pattern.md` for the VBS+PowerShell `.lnk` pattern. The `.bat` can be retired or kept as a fallback.

---

## 12. Build Failure Fallback: Copy Pre-built dist

When `npm run build` (or `npx vite build`) fails due to missing native bindings (`rolldown`), wrong Node version, or other environment issues, and the user needs customizations (logo, thinking video, title, sidebar text) deployed immediately:

**Prerequisite:** The user must have a secondary repo or fork that already has a working pre-built `dist/` with the desired customizations.

**Steps:**

```bash
# 1. Kill current server
pkill -f "dist/server/index.js"
sleep 2

# 2. Back up current dist (optional)
cp -r /mnt/c/Users/thadd/hermes-web-ui/dist/client /mnt/c/Users/thadd/hermes-web-ui/dist/client.bak.$(date +%s) 2>/dev/null

# 3. Copy pre-built custom dist from the secondary repo
#    (e.g., hermes-web-ui-ekko which is built from the user's fork)
cp -r /home/thadd/hermes-web-ui-ekko/dist/client/* \
      /mnt/c/Users/thadd/hermes-web-ui/dist/client/

# 4. Verify the copied HTML has expected customizations
#    (e.g., <title>Spock</title>, custom logo sizes)
grep "title" /mnt/c/Users/thadd/hermes-web-ui/dist/client/index.html | head -3
ls -la /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/mp4/

# 5. Restart server with auth disabled
export AUTH_DISABLED=1
cd /mnt/c/Users/thadd/hermes-web-ui
nohup node bin/hermes-web-ui.mjs start > ~/.hermes-web-ui/server.log 2>&1 &
sleep 3
curl -s http://127.0.0.1:8648/ | grep -i "title\|spock\|hermes" | head -3
```

**When to use this:**
- `npm run build` fails with `Error: Cannot find native binding` (rolldown missing)
- Node version is too old and cannot be upgraded immediately
- Time-critical deployment; user needs working customizations now
- The secondary repo's `dist/` is up-to-date enough for the user's needs

**When NOT to use this:**
- Build works fine → just use `npm run build`
- The secondary repo's `dist/` is stale by weeks and may have known bugs

**Trade-off:**
- Pro: Instant working UI with all customizations
- Con: `dist/client` may reflect older upstream code; source changes won't show until build is fixed

### Merging Customizations via Git (Cleaner Long-term)

If the user has a fork with customizations committed (e.g., `AntisystemOG/hermes-web-ui` with commit `f636b1b`):

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
git remote add spock https://github.com/AntisystemOG/hermes-web-ui.git
git fetch spock main --depth=20
# Cherry-pick or restore specific files from the fork's commit
git restore --source=spock/main \
  packages/client/index.html \
  packages/client/public/logo.png \
  packages/client/src/assets/logo.png \
  packages/client/src/assets/thinking-dark.mp4 \
  packages/client/src/assets/thinking-light.mp4 \
  packages/client/src/components/layout/AppSidebar.vue \
  vite.config.website.ts
```

This brings the **source files** in sync with the fork. Still requires build for `dist/client`.

---

## Key Model Names for Ollama Cloud
- `kimi-k2.6` — Kimi K2.6 (no `:cloud` suffix)
- `cogito-2.1:671b` — Cogito
- `deepseek-v4-pro` — DeepSeek V4 Pro
- `gemini-3-flash-preview` — Gemini Flash

**Note:** The `:cloud` suffix (e.g. `kimi-k2.6:cloud`) is for the **local** `ollama-launch` provider pointing to local Ollama instance, NOT Ollama Cloud.
