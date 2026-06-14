# Hermes Agent Dashboard Server — Session-Derived Lifecycle Notes

## Source of these notes

Captured from a live restart of the Hermes Agent dashboard server in WSL on 2026-06-13. The user asked: "restart webui server please". The actual Hermes CLI command is `hermes dashboard`, not `hermes webui`.

## Environment

- Hermes source checkout: `/home/thadd/hermes-agent-ui/`
- Active runtime venv: `/home/thadd/.hermes/hermes-agent/venv/`
- Web dist path: `/home/thadd/hermes-agent-ui/hermes_cli/web_dist/`
- Default dashboard port: `9119`
- Hermes CLI wrapper: `/home/thadd/.local/bin/hermes` → `/home/thadd/.hermes/hermes-agent/venv/bin/hermes`

## Restart transcript

```bash
# 1. Stop any running dashboard
hermes dashboard --stop

# 2. Start headless, serving pre-built dist
hermes dashboard --port 9119 --no-open --skip-build
```

### Startup output

```text
→ Skipping web UI build (--skip-build); using dist at /home/thadd/hermes-agent-ui/hermes_cli/web_dist
HERMES_DASHBOARD_READY port=9119
  Hermes Web UI → http://127.0.0.1:9119
```

### Verification

```bash
ss -tlnp | grep 9119
# LISTEN 0  2048  127.0.0.1:9119  0.0.0.0:*  users:(("hermes",pid=...,fd=7))

curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9119/
# 200
```

## Observed quirks

1. `hermes dashboard --status` reports the shell wrapper command, not just the Python process, so it may show 1 process even when the underlying uvicorn server is the real worker.
2. Port binding can lag slightly behind the `HERMES_DASHBOARD_READY` message. Wait 2–5 seconds before running health checks.
3. The `hermes dashboard` command from a named profile re-executes as `-p default dashboard --open-profile <profile>` to route all profiles through a single machine dashboard.

## Files and paths

- Server code: `/home/thadd/hermes-agent-ui/hermes_cli/web_server.py`
- Subcommand handler: `/home/thadd/hermes-agent-ui/hermes_cli/main.py` (function `cmd_dashboard`)
- Built SPA: `/home/thadd/hermes-agent-ui/hermes_cli/web_dist/`
- SPA source: `/home/thadd/hermes-agent-ui/web/`
