---
source: session 2026-05-20
context: Spock WebUI "isn't loading"
---

# WebUI Down vs. Broken: Diagnostic Guide

## The Core Trap

When a user says "the WebUI isn't loading" or "crashed," the first instinct is to investigate code changes, build errors, or configuration drift. However, the most common cause is simply that the Node server process is not running. It was cleanly shut down (SIGTERM) in a prior session and never restarted.

## Diagnostic Steps in Order

**Step 1: Check if anything is listening on port 8648**
```bash
ss -tlnp | grep 8648
```
- Empty -> server is down. Restart it.
- Shows node PID -> server is alive. Investigate routes/API errors.

**Step 2: Start the server**
```bash
bash /home/thadd/.hermes/webui/start-server.sh
```

**Step 3: Verify**
```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://172.24.60.180:8648/
```

**Step 4: Read logs if still dead**
```bash
tail -30 /home/thadd/.hermes/webui/logs/server.log
```

## Historical Context

In session 2026-05-20, the server log showed a clean SIGTERM shutdown. The previous session had done work then cleanly stopped the process. The next day, the browser shortcut opened to an unresponsive server because the process was simply gone. Fix: 30 seconds to restart. No code changes, no rebuild, no config edits.

## Pitfall: Don't Confuse "Not Running" with "Broken"

| Symptom | Likely Cause | Fix |
|---------|-----------|-----|
| "Unable to connect" or spins forever | Server down | Start it |
| WebUI UI visible but no AI response | Bridge/model issue | Check bridge logs |
| 500 or blank page | Code error | Read logs |
| Old assets after logo change | Stale dist/ or cache | Rebuild + hard refresh |
