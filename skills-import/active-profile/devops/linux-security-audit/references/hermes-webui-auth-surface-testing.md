---
source: session 2026-05-22
context: Hermes WebUI auth audit — discovered auth was not actually enforced despite log claims
---

# Auth Surface Testing for Hermes WebUI

## The Discovery

During a deep security audit, we found that the WebUI server logged "Auth enabled" but the main page (`/`) and `/hermes/chat` loaded without any token validation. Only API routes (`/api/*`, `/v1/*`, `/upload`) returned 401 for missing tokens.

**This means:** An attacker on the LAN could load the SPA shell, see the UI, and probe endpoints — even if data access was blocked. The auth was "cosmetic" on the shell.

## Auth Architecture

The WebUI has **dual auth modes** that work independently:
1. **Token auth**: Passed as `?token=...` query parameter or in headers
2. **Password auth**: Username/password stored in `.credentials` file (hashed with bcrypt)

Both are enforced on API routes. The SPA shell loads regardless.

## Testing Pattern

### Step 1: Check what the server actually enforces
```bash
# SPA shell — likely returns 200 even without auth
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8648/'

# API endpoint without token — should be 401 or 429
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8648/api/hermes/sessions'

# API endpoint with fake token — should be 401 or 429
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8648/api/hermes/sessions?token=fake-token'

# API endpoint with real token — should be 200
TOKEN=$(cat ~/.hermes-web-ui/.token | tr -d '\n')
curl -s -o /dev/null -w '%{http_code}' "http://localhost:8648/api/hermes/sessions?token=$TOKEN"
```

### Step 2: Check password auth
```bash
# Check if password auth is configured
cat ~/.hermes-web-ui/.credentials 2>/dev/null | sed 's/"password": "[^"]*"/"password": "[REDACTED]"/'

# Check if rate limiter is active (locked IP means too many failed attempts)
cat ~/.hermes-web-ui/.login-lock.json 2>/dev/null
```

### Step 3: Check for dual token files
```bash
ls -la ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null
diff ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null && echo "Same" || echo "DIFFERENT"
```

## Rate Limiter Quirk

The WebUI uses an **in-memory rate limiter** that persists to `.login-lock.json`. Simply deleting the file won't clear the lock — the server re-writes it from memory.

**To clear:**
1. Restart the service: `systemctl --user restart hermes-webui.service`
2. Or write a clean lock file and wait for the server to pick it up

## Fixing Common Auth Issues

### Issue: Launcher passes wrong token
**Cause**: Launcher reads `~/.hermes/webui/.token` but server uses `~/.hermes-web-ui/.token`
**Fix**: Update launcher to read from correct path, or symlink:
```bash
ln -sf ~/.hermes-web-ui/.token ~/.hermes/webui/.token
```

### Issue: `AUTH_DISABLED=1` was set but user didn't realize
**Cause**: `start-server.sh` or systemd service has `AUTH_DISABLED=1`
**Fix**: Remove the env var and restart. The server checks for exact string `"1"`.

### Issue: Server says "Auth enabled" but fake token works
**Cause**: Token validation only happens on API routes, not on the SPA shell
**Fix**: This is by design in the WebUI architecture. To truly block access, bind to `127.0.0.1` only and add firewall rules.

### Issue: Real token returns 401 after fixes
**Cause**: Multiple token files with different values; server reads one, launcher passes another
**Fix**: Ensure both files match, or consolidate to a single canonical path.

## Post-Fix Verification

After applying auth fixes, verify all three states:
```bash
echo "=== Auth verification ==="
TOKEN=$(cat ~/.hermes-web-ui/.token | tr -d '\n')
echo "Real token: $(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8648/api/hermes/sessions?token=$TOKEN" 2>/dev/null)"
echo "Fake token: $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8648/api/hermes/sessions?token=fake-token' 2>/dev/null)"
echo "No token:   $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8648/api/hermes/sessions' 2>/dev/null)"
echo "Main page:  $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8648/' 2>/dev/null)"
```

Expected: Real=200, Fake=401/429, No token=401/429, Main page=200 (SPA shell loads without auth by design)
