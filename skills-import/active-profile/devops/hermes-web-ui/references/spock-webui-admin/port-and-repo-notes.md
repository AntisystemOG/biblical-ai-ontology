# WebUI Port Configuration and Multi-Repo Environment

## Port Override Pattern

The Spock WebUI (Python, `server.py`) defaults to `127.0.0.1:8787` via `api/config.py`:
```python
HOST = os.getenv("SPOCK_WEBUI_HOST", "127.0.0.1")
PORT = int(os.getenv("SPOCK_WEBUI_PORT", "8787"))
```

For LAN access (Windows browser → WSL), it must be overridden:
```bash
SPOCK_WEBUI_HOST=0.0.0.0 SPOCK_WEBUI_PORT=8648 python3 server.py
```

**Common pitfall:** The batch file or shortcut hardcodes `PORT=8648` but the server is actually on 8787 because the env var wasn't exported correctly. Always verify:
```bash
ss -tlnp | grep :8648   # confirm the port you expect
```

## Env Var Name Mismatch in Systemd Services

**Critical pitfall:** The server code (`api/config.py`) only recognizes `SPOCK_WEBUI_*` environment variables. A systemd service that sets `HERMES_WEBUI_HOST` or `HERMES_WEBUI_PORT` will be silently ignored — the server falls back to `127.0.0.1:8787`.

**Real example (Thad's broken service before fix):**
```ini
# WRONG — silently ignored
Environment="HERMES_WEBUI_HOST=127.0.0.1"
Environment="HERMES_WEBUI_PORT=8787"
```

**Correct form:**
```ini
Environment="SPOCK_WEBUI_HOST=0.0.0.0"
Environment="SPOCK_WEBUI_PORT=8648"
```

**Detection pattern:**
```bash
systemctl --user status hermes-webui.service   # shows "active (running)"
ss -tlnp | grep :8648                          # empty!
cat /proc/$(pgrep -f server.py)/environ | tr '\0' '\n' | grep -i spock  # shows HERMES_WEBUI_* only
```

**Fix:**
```bash
# Edit /home/thadd/.config/systemd/user/hermes-webui.service
# Change HERMES_WEBUI_* → SPOCK_WEBUI_*, set HOST=0.0.0.0 if LAN access needed
systemctl --user daemon-reload
systemctl --user restart hermes-webui.service
```

## Multi-Repo Environment (Thad's WSL)

Thad's system has **two active WebUI stacks** competing for the same port:

| Repo | Stack | Default | Override Env Vars |
|------|-------|---------|-------------------|
| `~/hermes-webui-new` | Python | `127.0.0.1:8787` | `SPOCK_WEBUI_HOST`, `SPOCK_WEBUI_PORT` |
| `~/hermes-web-ui-ekko` | Node.js | `0.0.0.0:8648` | `PORT`, `BIND_HOST` |

**Rule:** Before diagnosing "the WebUI isn't working", determine WHICH repo is supposed to be active. Check:
1. `ps aux | grep -E "server\.py|node.*index"` — what's running
2. `ss -tlnp | grep :8648` — what's listening
3. `Desktop/Start Hermes WebUI.bat` — what the shortcut launches

If both repos have been configured at different times, the shortcut/batch may reference the wrong one. The Node.js ekko stack was worked on extensively (May 19-20, 2026), then the Python `hermes-webui-new` became the active target.

## Quick Status Check

```bash
# What's running?
echo "=== Processes ==="
ps aux | grep -E "server\.py|node.*index" | grep -v grep
echo ""
echo "=== Listeners ==="
ss -tlnp | grep -E "8648|8787"
echo ""
echo "=== Desktop shortcut target ==="
cat "/mnt/c/Users/thadd/Desktop/Start Hermes WebUI.bat" 2>/dev/null | head -20
```
