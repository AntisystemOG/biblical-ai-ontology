# Browser-Based Hermes Web UI Alternatives

## Context

This user's setup (WSL + Windows) abandoned the Electron desktop app due to:
1. `npm install` in WSL produces Unix `node_modules/.bin/` (no `.cmd` wrappers), causing `'electron-vite' is not recognized` in Windows PowerShell
2. Accidental click on "Get Started" triggered a local Windows Hermes install flow (~2GB) instead of connecting to existing WSL backend
3. No X display server available for Electron in WSL

## Available Web UIs

### Option A: `nesquena/hermes-webui` — Lightweight Python + Vanilla JS

- **Repo:** https://github.com/nesquena/hermes-webui
- **Stack:** Python3 backend, vanilla JavaScript frontend, no build step
- **Quickstart:** `python3 bootstrap.py` or `./start.sh`
- **Default port:** 8787
- **Node requirement:** None (Python)
- **Connection:** Proxies to existing Hermes gateway via `api_server` platform
- **Env vars needed:** `HERMES_WEBUI_AGENT_DIR`, `HERMES_WEBUI_STATE_DIR`
- **Best for:** Quick lightweight setup, no Node version concerns

### Option B: `EKKOLearnAI/hermes-web-ui` — Full-Featured Vue 3 Dashboard

- **Repo:** https://github.com/EKKOLearnAI/hermes-web-ui
- **Stack:** Vue 3 + TypeScript + Koa server + Socket.IO, monorepo (`packages/client`, `packages/server`)
- **Quickstart:** `npm install -g hermes-web-ui && hermes-web-ui start`
- **Default port:** 8648
- **Node requirement:** >= 23.0.0 (very strict — v22.22.3 rejected with `EBADENGINE`)
- **Connection:** Self-hosted server discovers models from `~/.hermes/auth.json`; talks to gateway via `api_server`
- **Env vars:** `HERMES_WEB_UI_HOME` (state dir), `BIND_HOST`, `PORT`, `CORS_ORIGINS`
- **Best for:** Full dashboard with analytics, cron management, multi-profile, file browser, group chat

## Connection Configuration (Both UIs)

Both UIs need the `api_server` gateway platform enabled. In `~/.hermes/config.yaml`:

```yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 0.0.0.0      # Required for Windows browser -> WSL backend
      port: 8642
      key: "your-api-key-here"  # Required when host=0.0.0.0
```

Then the UI backend (or directly the browser) connects to `http://172.x.x.x:8642` using the WSL IP reported by `ip addr show eth0`.

## Workspace Migration From OpenClaw

The OpenClaw workspace at `/mnt/c/Users/thadd/.openclaw/workspace/` contains:
- 74 items, ~44MB
- Core memory files: `MEMORY.md`, `SOUL.md`, `AGENTS.md`, `IDENTITY.md`, `USER.md`, `DREAMS.md`, `HEARTBEAT.md`, `SECURITY.md`
- Cron agents: `whale-watch`, `history-rhymes`, `daily-brief`, `trading-arena`, `financial-advisor`, `memory-dreaming`
- Scripts: `generate_brief.py`, `generate_dream.py`, `generate_pdf.py`, `html_to_pdf.py`, `top100_strategists_report.py`
- Data: `trading-arena/`, `reports/`, `memory/`, `analysis/`, `agents/`

To migrate, see `workspace-migration` skill. Built-in path: `hermes claw migrate --source /mnt/c/Users/thadd/.openclaw --preset full --migrate-secrets --overwrite --yes`
