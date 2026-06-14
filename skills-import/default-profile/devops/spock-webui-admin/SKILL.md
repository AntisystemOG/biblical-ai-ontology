---
title: Spock WebUI Administration
name: spock-webui-admin
trigger: |
  Any task involving the Spock WebUI at port 8787 (or custom port): provider
  configuration, model selection, troubleshooting "No LLM provider configured",
  fixing empty model dropdowns, auth/key management for web sessions, or
  inspecting/modifying WebUI session state.
description: |
  Thad's EKKOLearnAI WebUI is a Node.js/Vue-based application running from
  `/mnt/c/Users/thadd/hermes-web-ui/`. It does NOT read model configuration
  from the CLI agent's running config directly; it caches provider/model state
  in its own JSON files at `~/.hermes/webui/` and exposes REST endpoints for
  configuration. This skill covers how to read and modify that state, manage auth
  tokens, customize UI elements (avatars, branding), and troubleshoot issues.
---

# Spock WebUI Administration

## Architecture

- **Server**: `server.py` from the spock-webui repo. Usually runs via systemd or
  manual start on a configured port (default 8787).
- **State dir**: `~/.spock/webui/` (override with `SPOCK_WEBUI_STATE_DIR` env var).
- **Config source**: Reads `~/.spock/config.yaml` for base settings, but provider
  keys are stored in `~/.spock/.env`.
- **Separate from CLI agent**: The WebUI has its own model cache, session index,
  and settings. Changes via `hermes model` CLI do NOT automatically propagate
  to active WebUI sessions.

## Key State Files

| File | Purpose |
|------|---------|
| `~/.spock/webui/models_cache.json` | `active_provider`, `default_model`, provider groups |
| `~/.spock/webui/settings.json` | WebUI user preferences including `default_model` |
| `~/.spock/webui/sessions/<id>.json` | Per-session model, provider, messages |
| `~/.spock/webui/sessions/_index.json` | Index of all sessions with model/provider fields |
| `~/.spock/.env` | Provider API keys (managed via `/api/providers` POST) |
| `~/.spock/config.yaml` | Base config (shared with CLI agent) |
| `~/.spock/webui/.token` | Auth token for browser auto-login (`?token=...`) |

## REST API Endpoints for Configuration

### GET /api/providers
Returns all providers with `has_key`, `models`, `configurable` flags.

### GET /api/models
Returns the active provider, default model, and grouped model list.
If `active_provider` is null and `default_model` is empty, the UI shows nothing.

### GET /api/settings
Returns WebUI settings including `default_model`, `theme`, `onboarding_completed`.

### POST /api/providers
Set or update a provider API key. Body:
```json
{"provider": "opencode-go", "api_key": "sk-..."}
```
If `api_key` is empty string/null, the key is removed.
Writes to `~/.spock/.env` using the standard env var name for that provider.

### POST /api/default-model
Set the global default model. Body:
```json
{"model": "kimi-k2.6"}
```

## Authentication

The WebUI stores a single auth token at `~/.spock/webui/.token` (600 perms, 64-char hex). The browser shortcut reads this file and appends `?token=<token>` to open the page directly.

### Regenerate token
```bash
# Generate new token
token=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "$token" > ~/.hermes-web-ui/.token
chmod 600 ~/.hermes-web-ui/.token

# Also update the legacy path if it exists (some launchers read from here)
cp ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null || true

# Restart server (adjust PID and workdir for your stack)
kill <server_pid>  # or systemctl --user restart hermes-webui.service
# Server auto-reads .token on next startup
```

### Dual token file syndrome
The Hermes WebUI ecosystem has **two token file locations** that can diverge:
- **Server reads**: `~/.hermes-web-ui/.token` (active, in the WebUI repo/state dir)
- **Some launchers read**: `~/.hermes/webui/.token` (legacy path, may be stale)

Always `diff` both files. If they differ, the launcher passes a stale token while the server expects the new one. Fix: update the launcher to read from the correct path, or symlink them.
```bash
# Check both files
diff ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null && echo "Same" || echo "DIFFERENT"

# Fix launcher (Windows batch) to read correct path
# In Launch Hermes WebUI.bat, change:
#   FOR /F "delims=" %%i IN ('wsl cat /home/thadd/.hermes/webui/.token') DO set WSLTOKEN=%%i
# To:
#   FOR /F "delims=" %%i IN ('wsl cat /home/thadd/.hermes-web-ui/.token') DO set WSLTOKEN=%%i
```

### Disable auth entirely
**WARNING:** This is a major security risk. Auth is enforced on API routes but the SPA shell (`/`) still loads without auth. An attacker on the LAN can load the UI and probe it. Only use this on fully isolated systems.

If you must disable auth, remove `AUTH_DISABLED=1` from `start-server.sh` or the systemd service env. The server checks for this exact string — anything else leaves auth enabled.

### Auth state verification
```bash
cat /proc/$(pgrep -f server.py)/environ 2>/dev/null | tr '\0' '\n' | grep -iE "auth|token|disabled"
cat ~/.spock/webui/.token
```

## Common Issues & Fixes

### "No LLM provider configured" error in chat
**Cause**: Session JSON has `model_provider: null` or the provider has no key.
**Fix chain**:
1. Check current provider state: `GET /api/models`
2. If `active_provider` is null, set a default model: `POST /api/default-model`
3. If provider needs a key, set it: `POST /api/providers`
4. For stale sessions, update the session JSON directly:
   - Edit `~/.spock/webui/sessions/<id>.json`: set `model` and `model_provider`
   - Also update `~/.spock/webui/sessions/_index.json` to match
   - Also update `~/.spock/webui/models_cache.json` for the global default

### Empty model dropdown
**Cause**: `models_cache.json` has `active_provider: null` and `default_model: ""`.
**Fix**: `POST /api/default-model` with the desired model ID. The WebUI will then
build model groups around that provider.

### Provider shows models but "has_key: false"
**Cause**: The provider's API key is not set in `~/.spock/.env`.
**Fix**: `POST /api/providers` with the key. The WebUI writes it to `.env` and
invalidates the model cache.

## Direct State File Editing

When the API is unavailable or you need to bulk-fix many sessions, edit the JSON
state files directly. Important: keep all three files in sync for the same session:

1. `sessions/<id>.json` — `model` and `model_provider` fields
2. `sessions/_index.json` — matching entries for the same session
3. `models_cache.json` — global `active_provider` and `default_model`

Always restart the WebUI or wait for the next page load after direct file edits;
the server caches config in memory.

## Provider ID Reference

| Provider | Env Var | Key Endpoint |
|----------|---------|--------------|
| opencode-go | `OPENCODE_GO_API_KEY` | `/api/providers` |
| opencode-zen | `OPENCODE_ZEN_API_KEY` | `/api/providers` |
| kimi-coding | `KIMI_API_KEY` | `/api/providers` |
| ollama | (none, local) | N/A |
| ollama-cloud | `OLLAMA_API_KEY` | `/api/providers` |
| anthropic | `ANTHROPIC_API_KEY` | `/api/providers` |
| openai | `OPENAI_API_KEY` | `/api/providers` |

## Thad-Specific Paths

Thad's WebUI uses `~/.hermes/webui/` for state (not `~/.spock/webui/`), and the source repo is at `/mnt/c/Users/thadd/hermes-web-ui` (EKKOLearnAI / Spock branded). The active stack is Node.js-based (not Python `server.py`).

Key files in Thad's environment:
| File | Path |
|------|------|
| State dir | `~/.hermes/webui/` |
| Auth token | `~/.hermes/webui/.token` |
| Source repo | `/mnt/c/Users/thadd/hermes-web-ui` |
| Launcher | `/mnt/c/Users/thadd/Desktop/Launch Hermes WebUI.bat` |
| Server start script | `~/.hermes/webui/start-server.sh` (port 8648, AUTH_DISABLED=1) |

## Profile Lifecycle in WebUI

### Creating CLI profiles that appear in the WebUI
The WebUI discovers profiles by calling `hermesCli.listProfiles()`, which reads the same disk state as `hermes profile list`. **Any profile created via CLI automatically appears in the WebUI sidebar** after a page refresh — no manual registration needed.

1. **Create:** `hermes profile create <name>` (or `--clone` to copy an existing profile's config/skills)
2. **Configure:** Edit `~/.hermes/profiles/<name>/config.yaml`, write a targeted `SOUL.md`, and populate `workspace/`
3. **Access:** Switch to the new profile in the WebUI sidebar, or run `<name> chat` from CLI

### Themed profiles as job-function agents
Profiles can be tailored to a specific role rather than just a project. To make a "job-function" profile:
- Write a `SOUL.md` encoding that role's expertise (e.g., business communicator, security auditor)
- Curate `workspace/` with reference docs, templates, and metrics
- Add relevant `skills/` for that domain

This pattern lets a single Hermes installation serve multiple personas that management or teammates switch between in the WebUI.

## references/
- `references/dual-token-file-paths.md` — Two `.token` file locations and how they diverge.
- `references/session-json-structure.md` — Per-session JSON fields for model/provider.
- `references/git-push-workflow.md` — How to push WebUI customizations to Thad's `spock` fork.
- `references/webui-avatar-customization.md` — Replacing multiavatar with static Spock images, ProfileAvatar component contract, dist-patch technique, stale build pitfall, favicon.ico conversion.
- `references/webui-system-differences.md` — Spock WebUI vs Hermes dashboard vs EKKOLearnAI WebUI.
- `references/api-endpoints.md` — Full endpoint list and response shapes.
- `references/port-and-repo-notes.md` — Thad's multi-repo environment, port overrides, env var name mismatch.
- `references/provider-ids.md` — Canonical provider IDs and model IDs.
