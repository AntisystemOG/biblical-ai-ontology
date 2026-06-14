# Cleaning Up Old / Orphaned WebUI Processes

## Context

Thad had an old Python-based WebUI server running on port 8787 from the
`hermes-webui-new` directory (an old wrong path that was superseded by
`/mnt/c/Users/thadd/hermes-web-ui`). The user asked to "remove
http://127.0.0.1:8787 and everything that goes with it."

## Detection

```bash
# Find process listening on the port
lsof -i :8787
# or
ss -tlnp | grep 8787

# Output showed:
# COMMAND   PID  USER FD   TYPE DEVICE SIZE/OFF NODE NAME
# python    661 thadd 4u  IPv4   5999      0t0  TCP localhost:8787 (LISTEN)
```

## Investigation

```bash
# What is this process?
ps -p 661 -o pid,ppid,cmd
# → 661  1 /home/thadd/.hermes/hermes-agent/venv/bin/python server.py

# Where is its cwd?
ls -la /proc/661/cwd
# → /home/thadd/hermes-webui-new

# No references in current Hermes config
grep -r "8787" /home/thadd/.hermes/  # → no matches
grep -r "hermes-webui-new" /home/thadd/.hermes/  # → no matches
```

The process is completely orphaned — no launcher, no cron job, no systemd
unit references it. It was a leftover from an old install at the wrong path.

## Cleanup

```bash
# Kill the process
kill 661

# Verify port is free
lsof -i :8787 || echo "Port 8787 is now free"
```

## Optional: Remove orphaned directory

The `/home/thadd/hermes-webui-new/` directory still exists but is unreferenced.
If disk space is a concern or to prevent accidental restarts:

```bash
# Cautious approach: rename first, delete later after confirming nothing breaks
mv /home/thadd/hermes-webui-new /home/thadd/hermes-webui-new.old
# After a few days of stability:
# rm -rf /home/thadd/hermes-webui-new.old
```

## Key Files for the Active WebUI (for comparison)

| Active | Old/Orphaned |
|--------|--------------|
| `/mnt/c/Users/thadd/hermes-web-ui` | `/home/thadd/hermes-webui-new` |
| Port 8648 | Port 8787 |
| Node.js + Vue | Python `server.py` |
| `~/.hermes/webui/.token` | `~/.spock/webui/.token` (old path) |

## Verification After Cleanup

```bash
# Only port 8648 should have a listener
lsof -i :8648 | grep node
lsof -i :8787 | grep -q . && echo "STILL RUNNING" || echo "Port 8787 clean"

# Active server should report v0.6.0+
curl -s http://localhost:8648/api/health | jq '.webui_version'
```
