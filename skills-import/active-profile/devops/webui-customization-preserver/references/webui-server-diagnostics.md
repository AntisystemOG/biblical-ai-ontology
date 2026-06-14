# WebUI Server Diagnostics

Quick commands to verify whether the WebUI server is actually healthy, not just "running."

## Full Status Check (One-liner)

```bash
#!/bin/bash
echo "=== Service Status ==="
systemctl --user status hermes-webui.service --no-pager 2>&1 | head -5

echo ""
echo "=== Process Check ==="
pgrep -af "node.*dist/server/index.js" 2>/dev/null || echo "No server process found"

echo ""
echo "=== Port Listen ==="
ss -tlnp 2>/dev/null | grep 8648 || netstat -tlnp 2>/dev/null | grep 8648 || echo "Port 8648 not listening"

echo ""
echo "=== Health Check ==="
curl -sf --max-time 10 http://127.0.0.1:8648/health 2>&1 && echo "HEALTHY" || echo "UNREACHABLE"

echo ""
echo "=== Page Title ==="
curl -s --max-time 10 http://127.0.0.1:8648/ | grep -oP '<title>[^<]+</title>' | head -1 || echo "Could not fetch title"

echo ""
echo "=== Active DB ==="
ls -lh ~/.hermes/webui/hermes-web-ui.db 2>&1

echo ""
echo "=== Recent Server Log ==="
tail -5 ~/.hermes/webui/logs/server.log 2>/dev/null || echo "No log file"
```

## Common Failure Modes

### Process running but port not listening
The Node process may be alive but crashed internally (e.g., port already in use, or it exited the event loop). Check `journalctl` for the actual error:

```bash
journalctl --user -u hermes-webui.service --since "5 minutes ago" --no-pager
```

### Port listening but health check fails
`curl -sf` silently fails on non-2xx status codes. Use verbose curl to see the actual HTTP response:

```bash
curl -v --max-time 10 http://127.0.0.1:8648/health
```

### Wrong DB in use (dev vs production)
If the server was started without `NODE_ENV=production`, it uses a dev DB at `packages/server/data/hermes-web-ui.db` instead of `~/.hermes/webui/hermes-web-ui.db`. Detect which DB the process actually has open:

```bash
lsof -p $(pgrep -f "node.*dist/server/index.js") | grep -i "\.db"
```

### Server env vars inherited from parent shell
The `AUTH_DISABLED` and `NODE_ENV` variables leak from the shell that launched systemd or the service. Check the process environment directly:

```bash
grep -a AUTH_DISABLED /proc/$(pgrep -f "node.*dist/server/index.js")/environ 2>/dev/null | tr '\0' '\n'
```

## Log File Descriptor Mapping

When running under systemd, stdout/stderr may be redirected to a different path than the internal logger. Check the process's open file descriptors:

```bash
ls -l /proc/$(pgrep -f "node.*dist/server/index.js")/fd/ | grep -E "log|server"
```

This reveals whether logs are going to `~/.spock/webui.log` (systemd redirect) vs `~/.hermes/webui/logs/server.log` (internal Winston logger).