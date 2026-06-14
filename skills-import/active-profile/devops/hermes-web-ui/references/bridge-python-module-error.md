# Bridge Python Module Error — Session Transcript

**Date**: 2026-05-29
**Skill**: `hermes-web-ui` troubleshooting
**Symptom**: WebUI `/health` is green, but every new chat session fails immediately with:
```
Error: Failed to initialize OpenAI client: No module named 'openai'
```

## Context

- WebUI server: Node.js v23.11.1, port 8648
- Agent bridge: Python subprocess spawned by `services/hermes/agent-bridge.ts`
- User's Hermes venv: `/home/thadd/.hermes/hermes-agent/venv/bin/python3` (has `openai`)
- System python: `/usr/bin/python3` (missing `openai`)

## Diagnosis Steps

1. Checked `HERMES_AGENT_BRIDGE_PYTHON` env var → **empty**
2. Tested system python → `ModuleNotFoundError: No module named 'openai'`
3. Tested venv python → `import openai` succeeds
4. Bridge workers spawned before env var was set → they inherited system python

## Resolution

```bash
# 1. Set env var
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3

# 2. Persist in .env
echo "HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3" >> ~/.hermes/.env

# 3. Kill existing WebUI processes
lsof -ti:8648 | xargs -r kill -9
sleep 2

# 4. Restart with env var set
cd /mnt/c/Users/thadd/hermes-web-ui && node bin/hermes-web-ui.mjs start
```

## Key Pitfalls

- **Order matters**: `HERMES_AGENT_BRIDGE_PYTHON` must be exported **before** `node bin/hermes-web-ui.mjs start`. Setting it after has no effect on already-spawned bridge workers.
- **.env persistence**: Add to `~/.hermes/.env` so it survives shell restarts. The WebUI server reads this file on startup.
- **Windows launcher**: `.bat` launchers need `set HERMES_AGENT_BRIDGE_PYTHON=...` before the `node` call.
- **.env location**: Add to `~/.hermes/.env`, NOT `~/.hermes-web-ui/.env`. The bridge reads from the Hermes home directory.
- **Multiple profile directories**: If running under a profile (e.g., `plc-coder`), the bridge may look at `/home/thadd/.hermes/profiles/plc-coder/.env` rather than `~/.hermes/.env`. Set the env var explicitly in the launch command or `.bat` file.
- **Systemd service file**: If using `systemctl --user` to manage the WebUI, add `Environment="HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3"` to `~/.config/systemd/user/hermes-webui.service` under the `[Service]` section, then run `systemctl --user daemon-reload && systemctl --user restart hermes-webui.service`. The env var in the service file takes precedence over shell `.env` when systemd starts the process.

## Port Conflict After Restart (EADDRINUSE)

If you get `FATAL: listen EADDRINUSE: address already in use 0.0.0.0:8648` after killing and restarting, the old Node process is still holding the port. The PID file in `~/.hermes-web-ui/server.pid` may be stale (tracking a dead process).

**Fix**: Kill by port, not by PID file:
```bash
lsof -ti:8648 | xargs -r kill -9
sleep 2
# Now verify port is clear before starting:
lsof -i:8648 || echo "Port free — safe to start"
```

**Do NOT rely on `hermes-web-ui stop`** when the process was killed externally or the PID file is stale. It will report "not running" while a Node process still holds the port.

## Verification

After restart, check the server log for the bridge startup line:
```
Bridge worker started: /home/thadd/.hermes/hermes-agent/venv/bin/python3 ...
```

If it shows `/usr/bin/python3`, the env var was not picked up.
