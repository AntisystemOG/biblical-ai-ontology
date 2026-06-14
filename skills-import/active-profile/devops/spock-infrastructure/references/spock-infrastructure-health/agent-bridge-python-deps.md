# Agent-Bridge Python Dependency Cascade — Session 2026-05-24

## Problem

WebUI server starts cleanly, `/health` returns OK, but every chat message fails silently or with a "disconnected" error.

## Diagnostic Path

1. **Check server log** — looks clean. Bootstrap succeeds. Port 8648 listening.
2. **Check bridge log** — `~/.hermes/profiles/devteam/home/.hermes-web-ui/logs/bridge.log`
   - Finds `{"ok":false,"error":"No module named 'dotenv'"}` repeatedly
   - PIDs in these log lines match the OLD server PID, not current one
3. **Check bridge processes** — `ps -ef | grep hermes_bridge | grep -v grep`
   - Multiple stale brokers from prior failed runs still alive
   - Their worker processes are also orphaned
4. **Verify system Python imports** — `python3 -c "import dotenv"` → fails
   - But venv Python has it: `/home/thadd/.hermes/hermes-agent/venv/bin/python -c "import dotenv"` → OK
5. **Root cause**: `hermes_bridge.py` worker spawn uses `sys.executable` which resolves to `/usr/bin/python3` (system Python 3.14), not the hermes-agent venv. The system interpreter is missing packages that hermes-agent now requires.

## Fix Applied

```bash
# Install missing packages into system Python (Ubuntu 25.04, Python 3.14)
sudo pip3 install --break-system-packages python-dotenv
sudo pip3 install --break-system-packages httpx

# Verify
python3 -c "import dotenv, httpx; print('OK')"

# Clean stale bridge processes (they keep serving old error state)
for pid in $(ps -ef | grep hermes_bridge | grep -v grep | awk '{print $2}'); do
    kill -9 $pid 2>/dev/null
done

# Restart WebUI server
cd /mnt/c/Users/thadd/hermes-web-ui && node bin/hermes-web-ui.mjs start
```

## Architecture Note

The bridge process tree:
- Node.js server (PID X) spawns → broker Python process (`hermes_bridge.py`)
- Broker spawns → worker Python process (one per profile, also `hermes_bridge.py --worker-profile`)
- Worker imports `hermes-agent` code from `~/.hermes/hermes-agent/`
- The worker uses whatever Python the broker used, which is `sys.executable` of the broker
- Broker is spawned by Node.js `child_process.spawn('python3', ...)` — this resolves via PATH, typically `/usr/bin/python3`

If `hermes-agent` grows new Python dependencies, the system interpreter must be updated even though the venv already has them.

## Prevention

- After any `hermes-agent` upgrade that adds new Python deps, immediately run:
  `python3 -c "import <new_dep>"` to verify system Python coverage
- Consider configuring the WebUI bridge to use the venv Python explicitly via `HERMES_AGENT_BRIDGE_PYTHON` env var (set to `/home/thadd/.hermes/hermes-agent/venv/bin/python`)
