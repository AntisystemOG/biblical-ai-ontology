---
source: session 2026-05-22
context: Spock WebUI "disconnected" + auth audit findings
---

# WebUI Disconnected + Auth Not Enforced

## The Core Trap

When the WebUI shows "Disconnected," the first instinct is to assume the server crashed. But the server may be running fine — the browser tab was connected to an **old server process** that was cleanly shut down. A simple page reload connects to the new instance.

**Detection:**
```bash
# Server IS running on port 8648
ss -tlnp | grep 8648
# → LISTEN 127.0.0.1:8648 node PID

# But browser still shows "Disconnected"
# → Old WebSocket was tied to a dead process. Reload the page.
```

**Fix:** Reload the browser page (F5 or close/reopen tab). No server restart needed.

---

## Auth Not Actually Enforced

During the same session, we discovered the WebUI server logged "Auth enabled" but the SPA shell (`/`) loaded without any token validation. Only API routes returned 401 for missing tokens.

### Auth Architecture

The WebUI has **dual auth modes**:
1. **Token auth**: Passed as `?token=...` query parameter
2. **Password auth**: Username/password in `.credentials` file (bcrypt hashed)

Both are enforced on API routes only. The SPA shell loads regardless.

### Testing Pattern

```bash
# SPA shell — returns 200 even without auth (by design)
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8648/'

# API without token — MUST be 401/429
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8648/api/hermes/sessions'

# API with fake token — MUST be 401/429
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8648/api/hermes/sessions?token=fake-token'

# API with real token — MUST be 200
TOKEN=$(cat ~/.hermes-web-ui/.token | tr -d '\n')
curl -s -o /dev/null -w '%{http_code}' "http://localhost:8648/api/hermes/sessions?token=$TOKEN"
```

### Rate Limiter Quirk

The WebUI uses an **in-memory rate limiter** that persists to `.login-lock.json`. Deleting the file won't clear the lock — the server re-writes it from memory.

**To clear:** Restart the service:
```bash
systemctl --user restart hermes-webui.service
```

### Dual Token File Syndrome

Two token file locations can diverge:
- **Server reads**: `~/.hermes-web-ui/.token` (canonical)
- **Some launchers read**: `~/.hermes/webui/.token` (legacy, may be stale)

Always diff both files. If they differ, the launcher passes a stale token.

```bash
diff ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null && echo "Same" || echo "DIFFERENT"
```

Fix: Update launcher batch file to read from `~/.hermes-web-ui/.token`.

## Historical Context

In session 2026-05-22, the user reported "web ui is showing disconnected" after a security audit. The server had been restarted during the audit (PID changed from 22294 → 28354). The browser tab was still connected to the old WebSocket. A reload fixed it. During the same session, we also fixed:
- Wrong token file path in launcher
- Auth not enforced on SPA shell (bind to localhost + firewall as defense)
- `npm audit fix --force` breaking the build (TypeScript errors)
- Orphaned bridge processes after restarts
