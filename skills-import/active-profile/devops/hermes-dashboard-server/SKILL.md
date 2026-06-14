---
name: hermes-dashboard-server
description: Lifecycle management for the built-in Hermes Agent web dashboard (FastAPI backend + Vite/React frontend). Covers start, stop, restart, health checks, build behavior, profile routing, and port-binding quirks.
trigger:
  - restart webui
  - restart dashboard
  - hermes dashboard
  - webui server
  - dashboard server
  - stop dashboard
  - start dashboard
  - dashboard not responding
  - port 9119
---

# Hermes Agent Dashboard Server

## What This Is

The **Hermes Agent Dashboard** is the built-in browser management surface shipped with the `hermes-agent` Python package. It is a FastAPI backend (`hermes_cli/web_server.py`) serving a Vite/React SPA (`web/` → `hermes_cli/web_dist/`).

**Important disambiguation**: In this environment, the user often calls this the "webui server", but the Hermes CLI command is **`hermes dashboard`**, not `hermes webui`. This is a separate product from the EKKOLearnAI Node/Koa WebUI covered by the `hermes-web-ui` skill (which runs on port 8648).

| Surface | Command | Backend | Default Port |
|---------|---------|---------|--------------|
| Hermes Agent Dashboard | `hermes dashboard` | FastAPI + uvicorn | 9119 |
| EKKOLearnAI WebUI | `hermes-web-ui` / `node dist/server/index.js` | Koa + Socket.IO | 8648 |

## Quick Lifecycle Commands

```bash
# Start on default port 9119, auto-open browser
hermes dashboard

# Start headless on a specific port
hermes dashboard --port 9119 --no-open

# Use an already-built web dist (avoids the npm/Vite build step)
hermes dashboard --port 9119 --no-open --skip-build

# Check if any dashboard is running
hermes dashboard --status

# Stop all running dashboard processes
hermes dashboard --stop

# Restart cleanly
hermes dashboard --stop
sleep 2
hermes dashboard --port 9119 --no-open --skip-build
```

## Common Flags

| Flag | Purpose |
|------|---------|
| `--port PORT` | Listen port (default `9119`; `0` lets the OS assign) |
| `--host HOST` | Bind address (default `127.0.0.1`) |
| `--no-open` | Do not open a browser tab automatically |
| `--skip-build` | Serve the existing `hermes_cli/web_dist` without rebuilding |
| `--insecure` | Allow binding to non-loopback (dangerous on untrusted networks) |
| `--isolated` | Run a dedicated per-profile dashboard instead of routing to the machine dashboard |
| `--status` | List running `hermes dashboard` processes and exit |
| `--stop` | Terminate running dashboard processes and exit |

## Build Behavior

- By default, `hermes dashboard` tries to build the SPA from the `web/` workspace (`npm install --workspace web && npm run build -w web`).
- The build can be slow or appear to hang on first launch in non-interactive / WSL contexts.
- If `hermes_cli/web_dist/index.html` already exists, use `--skip-build` to serve it directly.
- With `--skip-build`, the server verifies `web_dist/index.html` exists; if not, it exits with a clear error.

## Profile Routing

When a **named profile** launches the dashboard (`<profile> dashboard`), Hermes routes to a single **machine-level dashboard** by default:

1. If a machine dashboard is already listening on the target port, it opens `/?profile=<name>` and exits.
2. If not, it re-executes as `hermes -p default dashboard --open-profile <name>` so the UI preselects that profile.

Use `--isolated` to opt out and run a dedicated per-profile server.

## Verification

After `HERMES_DASHBOARD_READY port=...` appears, the uvicorn socket may still need a few seconds to fully bind. Verify with:

```bash
# Check listening socket
ss -tlnp | grep 9119

# HTTP health check
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9119/
# Expected: 200
```

## Pitfalls

1. **Wrong command name**: `hermes webui` does not exist. The correct command is `hermes dashboard`.
2. **Build hang**: Without `--skip-build`, first launch may hang in npm/Vite. Use `--skip-build` when a pre-built `web_dist` is available.
3. **Process table noise**: `hermes dashboard --status` reports the shell wrapper command, not just the Python process, so counts can look inflated.
4. **Stale ready message**: `HERMES_DASHBOARD_READY` prints after uvicorn startup; the port may not accept connections for another 1–3 seconds. Wait before running health checks.
5. **Auth gate on non-loopback binds**: Binding to `0.0.0.0` or a non-localhost address requires a registered dashboard auth provider or `--insecure`.

## References

- `references/dashboard-server-lifecycle.md` — Session-derived command transcript and real startup output.
