# WebUI Systems Comparison

Distinguishing the three WebUI systems found in this environment:

| System | Port | State Dir | Entry Point | Stack | Notes |
|--------|------|-----------|-------------|-------|-------|
| **Spock WebUI** | 8787 | `~/.spock/webui/` | `~/hermes-webui-new/server.py` | Python/Flask | Separate repo, systemd service, old skill in `spock-webui-admin` |
| **Hermes Dashboard** | 9119 | `~/.hermes/web_dist/` | `hermes dashboard` CLI | FastAPI + React | Built-in to Hermes CLI, runs from `hermes_cli.main dashboard` |
| **EKKOLearnAI WebUI** | 8648 | `~/.hermes/webui/` | `hermes-web-ui start` | Koa + Vue 3 + Socket.IO | Full-featured browser UI, Node >=23 required, separate npm install |

**Port collisions:** Spock (8787) and EKKOLearnAI (default 8648) do not conflict directly, but the systemd service and manual Python server can fight. Hermes dashboard (9119) is fully separate.

**State separation:** Each system maintains its own session database, model cache, and settings. Migrating from one to another means the new UI will not see existing sessions unless explicitly copied.

**Session "not found" error:** In Spock WebUI, if the systemd service `HERMES_WEBUI_STATE_DIR` points to `.spock/webui` but the actual session data lives in `.hermes/webui/sessions/`, `POST /api/chat/start` throws `KeyError` -> "Session not found" even though `/api/sessions` lists it. Fix: update the systemd service's `HERMES_WEBUI_STATE_DIR` environment variable to match where sessions are stored.
