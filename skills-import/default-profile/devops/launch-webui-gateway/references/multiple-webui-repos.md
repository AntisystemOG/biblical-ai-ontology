# Thad's WSL WebUI Repositories

Thad has multiple Hermes WebUI installations. **Always verify which is active before making changes.**

## Repositories

### 1. `~/hermes-webui-new` (Python Spock WebUI)
- **Stack:** Python 3 (`server.py`), vanilla JS frontend
- **Default port:** `127.0.0.1:8787` (override via env to `8648`)
- **Entry point:** `python3 server.py`
- **Env vars:** `SPOCK_WEBUI_HOST`, `SPOCK_WEBUI_PORT`
- **Git origin:** `hermes-webui-new` (local, may not have remote)
- **Status:** Python server, Spock branding

### 2. `~/hermes-web-ui-ekko` (Node.js EKKOLearnAI)
- **Stack:** Node.js 26+ (`dist/server/index.js`), Vue 3 + TypeScript frontend
- **Default port:** `8648`
- **Entry point:** `node dist/server/index.js`
- **Env vars:** `PORT`, `BIND_HOST`, `AUTH_DISABLED`, `HERMES_WEB_UI_HOME`, `WORKSPACE_BASE`
- **Git origin:** `https://github.com/EKKOLearnAI/hermes-web-ui.git`
- **Status:** Built from source, Node.js server

### 3. `~/hermes-webui` (Legacy Python)
- **Stack:** Older Python WebUI
- **Status:** Likely deprecated, not actively used

## Quick Identification

```bash
# What's running on 8648?
ss -tlnp | grep :8648

# What process type is listening?
lsof -i -P -n | grep :8648

# Which hermes-web dir has active server processes?
ps aux | grep -E "server\.py|node.*index" | grep -v grep
```

## Decision Tree

| User says | Likely means |
|-----------|-------------|
| "the web ui" / "the new web ui" / "EKKOLearnAI" | `~/hermes-web-ui-ekko` |
| "Spock WebUI" / "Python WebUI" | `~/hermes-webui-new` |
| "the webui gateway" | Ask: which repo? |

## Desktop Files

| File | Points to |
|------|-----------|
| `Start WebUI.bat` | Launches active WebUI, opens browser |
| `Spock WebUI.lnk` | Shortcut to batch file |
| `Spock WebUI.url` | Direct browser URL to `http://172.24.60.180:8648/` |

## Port Allocation

| Service | Port | Process |
|---------|------|---------|
| Hermes gateway | 8642 | `hermes gateway run` |
| EKKOLearnAI WebUI | 8648 | `node dist/server/index.js` |
| Spock Python WebUI | 8787 | `python3 server.py` |

## When in Doubt, Ask

If the user mentions "web ui" without specifying, ask:
> "Which WebUI — `hermes-web-ui-ekko` (Node.js/EKKOLearnAI, the one from GitHub) or `hermes-webui-new` (Python Spock)?"
