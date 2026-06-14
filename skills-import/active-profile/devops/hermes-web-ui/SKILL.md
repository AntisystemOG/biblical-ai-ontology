---
name: hermes-web-ui
description: Complete lifecycle for the EKKOLearnAI Hermes Web UI — setup, development, theming/rebranding, auth management, troubleshooting, and desktop shortcuts. Covers Node version handling, auth tokens, stale sessions, bridge dependencies, provider configuration, and Windows launcher creation. NOTE — this is the SEPARATE Node/Koa WebUI project, not the built-in `hermes dashboard` FastAPI dashboard.
trigger:
  - web ui setup
  - hermes webui
  - spock webui
  - webui auth
  - web-ui branding
  - webui logo
  - webui not responding
  - webui desktop shortcut
---

# Hermes Web UI — Complete Management Guide

## Overview

The EKKOLearnAI Hermes Web UI is a Vue 3 + Vite + Node.js/Koa browser-based interface for Hermes Agent. It runs from `/mnt/c/Users/thadd/hermes-web-ui/` and is preferred over the Electron desktop app (deprecated for this WSL + Windows setup due to Node module cross-platform issues).

**Do not confuse this with the built-in Hermes Agent Dashboard.** There are two browser surfaces in this environment:

| Surface | Command / Launcher | Backend | Default Port |
|---------|-------------------|---------|--------------|
| **EKKOLearnAI WebUI** (this skill) | `node bin/hermes-web-ui.mjs start` or `hermes-web-ui` | Koa + Socket.IO | 8648 |
| **Hermes Agent Dashboard** | `hermes dashboard` | FastAPI + uvicorn | 9119 |

If the user says "restart webui server" or "restart dashboard" and you are unsure which they mean, check which port they expect (8648 vs 9119), or default to `hermes dashboard` because the Hermes CLI wrapper exposes that command natively. For the built-in dashboard lifecycle, see the **`hermes-dashboard-server`** skill.

## Architecture Quick Reference

- **Client**: Vue 3 + Vite + TypeScript + Naive UI (`n-` prefix components) + Monaco Editor + xterm.js
- **Server**: Koa (`packages/server/src/index.ts`)
- **Socket.IO**: Real-time chat (`ChatRunSocket`), terminal via `node-pty`
- **Auth**: Token-based (`services/auth.ts`) or username/password (SQLite)
- **State DB**: SQLite under `$HERMES_WEB_UI_HOME`
- **Hermes bridge**: `services/hermes/agent-bridge.ts` spawns Python agent worker
- **Public assets**: `packages/client/public/` (served at root `/`)
- **CWD for commands**: `/home/thadd/hermes-web-ui-ekko` (or user's copy)

## Node Version Requirement

The `package.json` uses `"engines": { "node": ">=23.0.0" }`. Node 22.x **will fail**. This user extracts Node 26.1.0 to `~/node26` and invokes it via `~/node26/bin/node` because the system default is 22.x.

```bash
curl -fsSL https://nodejs.org/dist/v26.1.0/node-v26.1.0-linux-x64.tar.xz -o /tmp/node.tar.xz
mkdir ~/node26 && tar xf /tmp/node.tar.xz -C ~/node26 --strip-components=1
~/node26/bin/node --version   # should be v23+
```

## Setup & Build Quick Start

```bash
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git ~/hermes-web-ui-ekko
cd ~/hermes-web-ui-ekko
~/node26/bin/npm install      # auto-builds client + server in prepare hook

HERMES_WEB_UI_HOME=$HOME/.hermes/webui \
  PORT=8648 \
  BIND_HOST=0.0.0.0 \
  WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace \
  ~/node26/bin/node dist/server/index.js
```

**CLI Entry Point**: The packaged CLI is `bin/hermes-web-ui.mjs` (ES module), not `.js`.  
When running directly with Node: `node bin/hermes-web-ui.mjs start` — **never** `node bin/hermes-web-ui.js start` (module-not-found error).

**Critical Env Vars**

| Var | Default | Purpose |
|-----|---------|---------|
| `HERMES_WEB_UI_HOME` | `~/.hermes-web-ui` | Auth token, SQLite DB, uploads, logs |
| `PORT` | `8648` | Web UI listen port |
| `BIND_HOST` | `0.0.0.0` | Bind address (set `127.0.0.1` for local-only) |
| `WORKSPACE_BASE` | `/opt/data/workspace` | File browser root for workspace |
| `HERMES_AGENT_BRIDGE_PYTHON` | — | Path to Python interpreter for agent bridge (must have `openai`, `websockets`, etc.) |
| `AUTH_TOKEN` | — | Pre-set bearer token (skips auto-gen) |

⚠️ **`AUTH_DISABLED` was removed in WebUI v0.6.3, but the env var is still checked in `auth.ts`.** Any value (even `0` or `false`) disables username/password auth and returns `"Auth is disabled on this server"`. This is a **silent inheritance bug** — if the parent shell has `AUTH_DISABLED` set from a previous session or launcher, the server inherits it and all logins fail.

**Always explicitly unset before launch:**
```bash
unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
/home/thadd/node26/bin/node dist/server/index.js
```

**Detection:**
```bash
# Check if AUTH_DISABLED is present in the server's environment
grep -a AUTH_DISABLED /proc/$(pgrep -f "node.*dist/server/index.js")/environ 2>/dev/null | tr '\0' '\n'

# Or check login response
curl -sf http://127.0.0.1:8648/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq -r '.message // .error'
# If it says "Auth is disabled on this server", this is the bug
```

**Full diagnosis and recovery:** See `references/auth-troubleshooting.md` and the `webui-customization-preserver` skill section "Critical: AUTH_DISABLED Inheritance Bug".

## Authentication

### URL Token Auth

The server auto-generates a 256-bit hex token at `~/.hermes/webui/.token` (new path; older launchers may still look at `~/.hermes-web-ui/.token`). Browser shortcuts append `?token=<token>` for auto-login.

**Dual token file syndrome**: `~/.hermes/webui/.token` (active) and `~/.hermes-web-ui/.token` (legacy) can diverge. Always `diff` both and update launchers to read from the correct path.

```bash
# Regenerate
token=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "$token" > ~/.hermes/webui/.token
chmod 600 ~/.hermes/webui/.token
```

### Username/Password (v0.6.0+)

SQLite-based user accounts. When `users` table is **empty**, the first `POST /api/auth/login` bootstraps the super_admin with those credentials — **anyone on the LAN can claim it**. Create the first user immediately after any fresh install.

**Password change** (logged in with JWT):
```bash
# 1. Obtain JWT
curl -sf http://localhost:8648/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"AntiSyStem","password":"<current>"}' | jq -r '.token'

# 2. Change password
curl -sf http://localhost:8648/api/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt>" \
  -d '{"currentPassword":"<old>","newPassword":"<new>"}'
```

**Direct DB password reset** (server stopped):
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
pkill -f "node dist/server/index.js" || true; sleep 1

hash=$(node -e "
  const crypto = require('crypto');
  const salt = crypto.randomBytes(16).toString('hex');
  const keylen = 64, N = 16384, r = 8, p = 1;
  const hash = crypto.scryptSync('YourNewPass123!', salt, keylen, { N, r, p }).toString('hex');
  console.log('scrypt:' + salt + ':' + hash);
")

sqlite3 packages/server/data/hermes-web-ui.db \
  "UPDATE users SET password_hash='$hash', updated_at=$(date +%s), requires_credential_change=0 WHERE id=1;"

node dist/server/index.js &
```

### Dev vs Production DB Path

| Mode | DB Path |
|------|---------|
| `development` (default) | `packages/server/data/hermes-web-ui.db` |
| `production` | `~/.hermes/webui/hermes-web-ui.db` |

If you start the server without `NODE_ENV=production`, user accounts are created in the repo-local dev DB. A later service with `NODE_ENV=production` uses a **different, empty** DB. Always verify which DB is active with `lsof -p <server_pid> | grep hermes-web-ui.db`.

**Always start the server with `NODE_ENV=production`** to ensure persistent accounts:
```bash
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export PORT=8648
/home/thadd/node26/bin/node dist/server/index.js
```

**Never start from `/home/thadd` without `NODE_ENV=production`** — this creates a separate dev DB at `/home/thadd/packages/server/data/` that shadows the production accounts.

### Post-Update DB Migration Check
After any WebUI update or service file change, check for orphaned databases. The data directory changed from `~/.hermes-web-ui/` (legacy) to `~/.hermes/webui/` (v0.6.4+). An old DB at the legacy path may contain sessions not in the current DB, making chat history appear lost.

**Detection:**
```bash
find /home/thadd -name "hermes-web-ui.db" -type f 2>/dev/null | grep -v node_modules | grep -v .cache
```
If more than one file is found, compare session counts and merge missing sessions. See the `webui-customization-preserver` skill, section "Verification Checklist" → "Check for orphaned WebUI databases after data directory migration" and its reference file `references/webui-db-migration-data-loss-prevention.md` for the full merge procedure.

See `references/auth-troubleshooting.md` for full auth diagnosis — login lockouts, empty users table, password hash mismatches, and DB path confusion. For post-update merge workflows (e.g., merging upstream 0.6.3 while preserving customizations), see `references/upstream-merge-0.6.3.md` in the `webui-customization-preserver` skill.

## Provider & Model Configuration

The WebUI server builds the model list dynamically from three sources:
1. Built-in provider presets in `packages/server/src/shared/providers.ts`.
2. Per-profile `config.yaml` (`model.default`, `providers.*.models`, `custom_providers`).
3. The provider-model catalog cache at `~/.hermes/webui/cache/provider-model-catalog.json` for live-fetched providers (`ollama-cloud`, `openrouter`, `cliproxyapi`, `lmstudio`, `nvidia`).

**Legacy file to ignore:** `~/.hermes/webui/models_cache.json` is a stale artifact from WebUI ≤ v0.51.x. Current WebUI (v0.6.10+) does **not** read it. If you see `_webui_version: "v0.51.x"` inside, it is leftover data and can be removed after verifying the current server is running.

### Key REST Endpoints

- `GET /api/hermes/available-models` — grouped available models + current default per active profile
- `GET /api/hermes/available-models?profile=<name>` — same for a specific profile
- `POST /api/hermes/provider-models` — fetch live models from a provider endpoint
- `POST /api/hermes/provider-models/cache/refresh` — refresh live catalogs
- `PUT /api/hermes/config/model` — set global default: `{"default": "kimi-k2.7-code:cloud", "provider": "ollama-launch"}`
- `POST /api/hermes/config/providers` — add a custom provider

See `references/webui-config-api-recipes.md` for copy-paste `curl` commands for these endpoints, including JWT generation from `~/.hermes/webui/.token`.

### `providers:` vs `custom_providers:` — WebUI Only Sees the Latter

The Hermes CLI uses a keyed `providers:` section in `config.yaml`, e.g.:
```yaml
providers:
  ollama-launch:
    api: http://127.0.0.1:11434/v1
    models:
      - kimi-k2.7-code:cloud
```

**The WebUI model dropdown does NOT read `providers:` entries.** It builds custom provider groups only from the legacy list-shaped `custom_providers:` array. If a provider exists only under `providers:`, it will be missing from the WebUI dropdown and the default will fall back to whatever built-in provider is available (usually `ollama-cloud` with its cached catalog).

To expose a local Ollama provider in the WebUI, add it to `custom_providers:`:
```yaml
custom_providers:
  - name: ollama-launch
    base_url: http://127.0.0.1:11434/v1
    model: kimi-k2.7-code:cloud
    api_key: ollama   # WebUI requires a non-empty api_key for custom providers even when the endpoint does not
```

⚠️ **The WebUI server requires `api_key` for every custom provider** unless the provider key is in the built-in `OPTIONAL_API_KEY_PROVIDERS` set (`cliproxyapi`, `xai-oauth`, `openai-codex`). Local Ollama does not need a real API key, but the UI's `POST /api/hermes/config/providers` endpoint returns `400 Missing API key` if the field is empty. Use a placeholder such as `ollama` for local endpoints.

### Custom Ollama Providers

A local Ollama instance configured in `config.yaml` like this:
```yaml
providers:
  ollama-launch:
    api: http://127.0.0.1:11434/v1
    models:
      - kimi-k2.7-code:cloud
```
appears in the WebUI as a **custom** provider group (`custom:ollama`) **only if it is also listed under `custom_providers:`**. The group will contain only the model(s) explicitly listed in `config.yaml`. To expose additional models, either add them to the `models` list or use the **Models** page to refresh from `http://127.0.0.1:11434/v1/models`.

### Model Name Mismatch (`:cloud` suffix)

Ollama model tags like `:cloud` are **not** returned by `/v1/models`; Ollama exposes the base name (e.g., `kimi-k2.7-code`). If the Hermes CLI config uses the tagged name `kimi-k2.7-code:cloud`, the WebUI may fail to match it against the live catalog and fall back to an older cached default. Two fixes:

1. **Keep the tagged name** and add it to the provider's `models` list in `config.yaml` so it is explicitly included.
2. **Use the base name** in `model.default` if you want the WebUI live catalog to match it automatically.

### Stale Session Overrides

The `sessions` table caches `model`/`provider` per row. Existing conversations retain old values even after global config changes. The Node server (`handleBridgeRun.ts`) passes `sessionRow.model`/`provider` directly to the bridge, bypassing global config for that conversation.

```sql
UPDATE sessions SET model = 'kimi-k2.6:cloud', provider = 'ollama-launch';
```

Restart the Node server after DB changes.

### "Can't Start a New Chat" / New-Chat Modal Stuck

If the WebUI appears to use the right model but the **New Chat** button does nothing or the modal cannot confirm, the likely cause is that the active profile's default model/provider pair does not exist in the WebUI's available-model groups. The modal pre-fills `newChatProfile`, `newChatProvider`, and `newChatModel` from `profileModelGroups` (`packages/client/src/components/hermes/chat/ChatPanel.vue`). If the configured default provider is missing from those groups, the modal ends up with an empty/invalid selection and the confirm button stays disabled.

Fix: ensure the desired provider appears in `/api/hermes/available-models?profile=<name>` (see the `providers:` vs `custom_providers:` section above), then refresh the WebUI or trigger **Models → Refresh Cache**.

## Theming & Rebranding

### Logo Replacement

All logo references point to `/logo.png` served from `packages/client/public/logo.png`:

| Element | File | Reference |
|---------|------|-----------|
| Sidebar top-left | `AppSidebar.vue` | `const logoPath = '/logo.png'` |
| Login page | `LoginView.vue` | `<img src="/logo.png" width="80" height="80">` |
| Assistant chat avatar | `MessageItem.vue` | `src="/logo.png"` |
| Chat empty state | `MessageList.vue` | `<img src="/logo.png" class="empty-logo">` |
| Mobile drawer | `App.vue` | `<img src="/logo.png" style="width: 24px">` |

**Steps**:
1. `cp /path/to/new-logo.png packages/client/public/logo.png`
2. `cp /path/to/new-logo.png packages/client/src/assets/logo.png`
3. **Rebuild** (or for quick testing: copy to `dist/client/logo.png` and restart)

⚠️ If running from a pre-built `dist/` (e.g., Windows `.bat` launcher), changes to `packages/client/public/` **do NOT take effect** until a rebuild.

### Thinking / Typing Indicator

The streaming AI indicator is a **looping `<video>`**, not an image. Source files:

| Variant | Path | Imported As |
|---------|------|-------------|
| Light | `packages/client/src/assets/thinking-light.mp4` | `thinkingVideoLight` |
| Dark | `packages/client/src/assets/thinking-dark.mp4` | `thinkingVideoDark` |

**Replace**: Overwrite both files, then rebuild. Vite copies them to `dist/client/assets/mp4/` with a content hash. Only a rebuild updates the live served file.

### Reproducible re-apply after upstream update

Load the **`webui-customization-preserver`** skill for the full recovery workflow, or run the quick script:

```bash
bash ~/.hermes/profiles/plc-coder/skills/devops/webui-customization-preserver/scripts/restore.sh
```

This restores logo, thinking videos, rebuilds, and verifies `dist/` output in one shot.

**Critical post-merge pitfall:** Upstream may silently replace your `.mp4` thinking videos with `.gif` imports in `MessageList.vue`. Git merges the file without conflict because the import lines changed (same variable name, different extension). After any upstream merge, always verify:

```bash
cd /home/thadd/hermes-web-ui-ekko
grep -n "thinking.*\.gif" packages/client/src/components/hermes/chat/MessageList.vue \
  && echo "WARNING: .gif imports detected — need to restore .mp4" \
  || echo "OK: no .gif imports"
```

For full details see `references/upstream-merge-0.6.3.md` in the `webui-customization-preserver` skill.

## Desktop Shortcuts (Windows)

### Native `.lnk` (Recommended)

No console flash, supports custom icons, `hermes-web-ui.mjs` CLI auto-opens browser.

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\thadd\Desktop\Spock WebUI.lnk")
$Shortcut.TargetPath = "C:\Users\thadd\hermes-web-ui\packages\server\bin\hermes-web-ui.mjs"
$Shortcut.Arguments = "start"
$Shortcut.IconLocation = "C:\Users\thadd\Desktop\spock-icon.ico,0"
$Shortcut.WorkingDirectory = "C:\Users\thadd\hermes-web-ui"
$Shortcut.Save()
```

### Legacy `.bat`

If auth is **disabled**, strip `/#/?token=` from the URL entirely:
```batch
@echo off
set WSL_IP=172.24.60.180
set PORT=8648

wsl bash -c "export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=8648 BIND_HOST=0.0.0.0 AUTH_DISABLED= AUTH_DISABLED=1; nohup /home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js > /dev/null 2>&1 &"
timeout /t 2 >nul
start http://%WSL_IP%:%PORT%/
```

> Use `wsl bash -c` with proper bash `nohup ... > /dev/null 2>&1 &` — cmd `^` escapes inside `wsl` fail because bash treats `^` as literal.

### Windows Internet Shortcut (`.url`)

Tiny, icon-capable, no batch window:
```ini
[InternetShortcut]
URL=http://172.24.60.180:8648/
IconFile=C:\Users\thadd\Desktop\spock-icon.ico
IconIndex=0
```

## Common Issues

### Jobs / Cron Scheduling UI
The Jobs tab (`JobsView.vue`) uses a raw cron expression input (`NInput`) with a tiny preset dropdown. The backend Hermes CLI actually supports natural language (`every 30m`), ISO timestamps (`2026-06-01T09:00:00`), and structured interval objects (`kind: 'interval', minutes: 30`). The UI never exposes these easier modes.

**For the full implementation details (state structure, time helpers, cron generation, reverse parsing, build verification):**
See `references/schedule-builder-implementation.md` — complete build log with code snippets and pitfall notes.

**For the investigation that led to this design:**
See `references/jobs-scheduling-ui-investigation.md` — backend capabilities, structured type definitions, and why the old preset dropdown was insufficient.

**Symptom**: The `search_files` tool (or any tool) appears stuck — infinite spinner, no results, no error. The agent log shows the tool call was issued but never completed.

**Root cause**: The WebUI Node server process is being killed and restarted by an external watchdog (cron job, systemd, or duplicate `watchdog.sh` instances). If the server dies mid-request, the agent bridge worker's response is lost and the UI waits indefinitely.

**Diagnosis**:
```bash
# 1. Check watchdog logs for restart loops
tail -50 ~/.hermes/logs/watchdog.log
# Look for: "WebUI NOT running — restarting..." appearing every 10 min

# 2. Check for duplicate watchdog processes
ps aux | grep -c "watchdog"
# If > 1, multiple watchdogs are fighting each other

# 3. Check if the WebUI port is actually listening
lsof -ti:8648 | xargs ps -o pid,etime,comm 2>/dev/null
# If the PID changes every few minutes, the process is unstable
```

**Fix**:
1. Stop all watchdogs and WebUI processes:
   ```bash
   hermes-web-ui stop
   pkill -f "watchdog"
   pkill -f "node dist/server/index.js"
   ```
2. Restart cleanly with a single watchdog (or disable the cron job if manually managing):
   ```bash
   hermes-web-ui start
   ```
3. If the issue persists, check `~/.hermes/logs/gateway.log` for startup conflicts (e.g., Telegram bot token already in use by another gateway PID).

**Key insight**: There is no stuck `ripgrep` or `search_files` process on the backend. The backend processes (agent bridge, pyright LSP) are healthy. The hang is always a dropped connection caused by the WebUI server restart.

For the full chain-of-failure diagnosis and recovery steps, see `references/webui-eaddrinuse-watchdog-conflict.md`.

### Systemd Service Conflict
When using `systemctl --user` to manage the WebUI alongside a watchdog cron job, the two can fight for port 8648. See `references/systemd-service-management.md` for the resolution: fix the service file, add missing env vars (like `HERMES_AGENT_BRIDGE_PYTHON`), pick one manager (systemd OR watchdog), and verify with `systemctl --user status`.

### Chat Fails But /health Is OK (Agent-Bridge Python Deps)

Symptom: Server starts, `/health` green, every chat 500s on `/chat-run`.
Cause: Python bridge worker missing deps (e.g., `python-dotenv`, `httpx`).
Fix: Installmissing packages (`sudo pip3 install --break-system-packages <pkg>`), kill stale bridge processes (`pkill -f hermes_bridge`), restart server.

### HTTP 301 on Ollama Cloud

Wrong base URL: `https://api.ollama.com/v1/...` redirects. Correct: `https://ollama.com/v1`
Fix in `.env`: `OLLAMA_BASE_URL=https://ollama.com/v1` and in `~/.hermes/auth.json` credential pool.

### Bridge Worker Caches Old Config

The bridge worker reads `config.yaml` + `.env` **once at startup** and never re-reads. Editing config while running leaves stale state. Restart server after config changes.

### WSL IP Is Dynamic

WSL2 VM IP changes every reboot. Update the `.bat`/`.url` IP after restart, or use Windows `netsh` port forwarding so Windows `localhost:8648` → WSL.

### Auth Bypass Vectors (FIXED in v0.6.0; PERMANENTLY CLOSED in v0.6.3)

Four bypass vectors were discovered and fixed:
1. **Static files public** — accepted as SPA requirement (shell loads without auth)
2. **Client auto-redirect to login** — removed (v0.6.0)
3. **URL token extraction** — removed (v0.6.0)
4. **Server bearer token fallback** — still active for programmatic access

In **v0.6.3**, `AUTH_DISABLED` support was completely removed from the codebase. The `auth.ts` service no longer checks for it. The only auth modes are:
1. Token auth (`AUTH_TOKEN` env var)
2. Username/password (SQLite DB at `~/.hermes/webui/hermes-web-ui.db`)

This means the `unset AUTH_DISABLED` in launcher scripts is now a no-op for 0.6.3+ — but keep it for backward compatibility if you ever downgrade or switch branches.

### Disabling the Update Check
When running from a locally merged `main` branch ahead of the npm publication (e.g., local is `0.6.6` but npm only has `0.6.5`), the banner fires constantly because `local !== npm_latest`. In this situation, **disable the check entirely**:

```bash
export HERMES_WEB_UI_DISABLE_UPDATE_CHECK=true
```

**Required env var to add to launcher scripts.** The WebUI sets `webui_update_available: false` and `webui_latest: ""` when this is set.

## Version Checking

The WebUI server queries `https://registry.npmjs.org/hermes-web-ui/latest` every 30 minutes to check for updates. The response is compared against the local `package.json` version string. If they differ, `webui_update_available: true` appears in the health endpoint.

**When an update is available:**
1. The npm registry version is published from the **upstream** `EKKOLearnAI/hermes-web-ui` repo.
2. Your local repo may be a fork (`AntisystemOG/hermes-web-ui.git` in this case) that hasn't pulled upstream changes.
3. To update, add the upstream remote and merge:

```bash
cd /home/thadd/hermes-web-ui-ekko
git remote add upstream https://github.com/EKKOLearnAI/hermes-web-ui.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
```

**Expect merge conflicts** in files you've customized (e.g., `AppSidebar.vue`, `LoginView.vue`, `router/index.ts`). Resolve them preserving your branding while accepting upstream improvements.

**After merge:**
1. `npm install` — may pull new dependencies
2. `npm run build` — rebuilds client + server
3. Verify customizations in `dist/` (logo, favicon, title, thinking videos)
4. Restart server with all required env vars

For detailed merge procedures and conflict resolution recipes, see `references/upstream-merge-0.6.3.md` in the `webui-customization-preserver` skill.

## Bridge Python & Module Errors

Symptom: Server starts, `/health` OK, but new chat sessions fail with:
```
Failed to initialize OpenAI client: No module named 'openai'
```

**Root cause:** `HERMES_AGENT_BRIDGE_PYTHON` is unset, so the WebUI bridge spawns workers with system `python3` which lacks `openai`, `websockets`, and other Hermes dependencies. The venv python has them.

**Diagnosis:**
```bash
# Check which python the bridge is using
echo $HERMES_AGENT_BRIDGE_PYTHON   # empty = broken
which python3 && python3 -c "import openai" 2>&1 || echo "system python MISSING openai"
/home/thadd/.hermes/hermes-agent/venv/bin/python3 -c "import openai" 2>&1 || echo "venv python MISSING openai"
```

**Fix (immediate):**
```bash
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3
```

**Fix (persistent — add to `~/.hermes/.env`):**
```bash
echo "HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3" >> ~/.hermes/.env
```

**Then restart WebUI cleanly:**
```bash
# Kill by port, not by PID file (PID file may be stale)
lsof -ti:8648 | xargs -r kill -9
sleep 2
cd /mnt/c/Users/thadd/hermes-web-ui && node bin/hermes-web-ui.mjs start
```

⚠️ **`HERMES_AGENT_BRIDGE_PYTHON`** must be set **before** the WebUI server starts. Setting it after the bridge worker has already spawned has no effect — workers are long-lived per session. Always restart the server after changing this env var.

For the full error transcript and recovery steps, see `references/bridge-python-module-error.md`.

## Voice / Speech-to-Text (Not Implemented)

The Hermes WebUI **does not currently include voice input** (speech-to-text). A full-text search of `/packages/client/src` for `microphone`, `mic`, `voice`, `speech`, `audio`, or `recorder` returns **zero matches**.

### Adding Voice Input

The standard browser-native approach would be:
1. Use the **Web Speech API** (`webkitSpeechRecognition` / `SpeechRecognition`)
2. Add a microphone button to the chat input component:
   - **Path**: `packages/client/src/components/hermes/chat/ChatInput.vue`
3. On click, start the speech recognizer, stream interim results into the text input, and submit on final result.

No backend changes are required — transcription happens entirely in the browser.

### Relevant Client Source Files

| Component | Path |
|-----------|------|
| Chat input box | `packages/client/src/components/hermes/chat/ChatInput.vue` |
| Chat panel wrapper | `packages/client/src/components/hermes/chat/ChatPanel.vue` |
| Message list / empty state | `packages/client/src/components/hermes/chat/MessageList.vue` |
| Individual message bubble | `packages/client/src/components/hermes/chat/MessageItem.vue` |
| Group chat input | `packages/client/src/components/hermes/group-chat/GroupChatInput.vue` |

### Awareness Note for Agents
When a user opens a conversation with phrases like *"speak directly to you,"* *"instead of typing,"* *"talk to you,"* *"voice input,"* or *"microphone,"* **assume they are using the Hermes WebUI** and that voice input is not yet implemented. Do not assume a generic text-only chat context.

## Verification Checklist
- [ ] `dist/server/agent-bridge/hermes_bridge.py` exists after build
- [ ] `AUTH_DISABLED` is exactly `"1"` if disabling auth
- [ ] `.token` files match between `~/.hermes/webui/.token` and launcher read path
- [ ] `~/.hermes/webui/models_cache.json` is either absent or from the current WebUI version (legacy v0.51.x files are safe to remove)
- [ ] `~/.hermes/webui/cache/provider-model-catalog.json` reflects the desired providers
- [ ] No stale session rows with wrong model/provider
- [ ] Ollama base URL is `https://ollama.com/v1`
- [ ] Server restarted after any DB or config change
