# Enabling Username/Password Auth After v0.6.0 Upgrade

## Problem

After upgrading the WebUI to v0.6.0+, the login endpoint returns:
```json
{"error":"Auth is disabled on this server"}
```

Even though the `users` table exists in the database and the Settings panel shows a "Current Account" section, no login is possible.

## Root Cause: `AUTH_DISABLED` Environment Variable

The WebUI auth system is controlled by `AUTH_DISABLED`:
- `AUTH_DISABLED=1` or `true` → `getToken()` returns `null`. Login endpoint rejects all attempts. Bearer tokens not required.
- `AUTH_DISABLED` unset or empty → Auth active. Bearer token enforced on API routes. Username/password login available if user exists.

**Critical finding**: The variable can be set in **three places** that stack:
1. `~/.hermes/.env` — Hermes master environment file
2. `~/.hermes/webui/start-server.sh` — Launcher script that sources `.env` then **overrides** with `export AUTH_DISABLED=1`
3. **Parent process environment** — The `hermes` Python daemon (PID ~618) passes its environment to all child processes. This is the hardest layer to detect because it's invisible in config files.

## Why `unset AUTH_DISABLED` Doesn't Work

When starting the server via `bash -lic "unset AUTH_DISABLED; node dist/server/index.js"`, the `unset` command runs in a subshell that inherits the parent environment. However, if the `hermes` daemon process itself has `AUTH_DISABLED=1` in its environment, that variable propagates through the shell spawn chain and the Node.js process still sees it.

**Verification:** Check the running Node.js process environment directly:
```bash
cat /proc/$(pgrep -f "node dist/server/index.js")/environ | tr '\0' '\n' | grep AUTH
# Shows: AUTH_DISABLED=1 even though you "unset" it
```

## Correct Fix: `env -u AUTH_DISABLED`

The `env -u` command **explicitly removes** the variable from the spawned process environment before the shell starts:

```bash
# Kill existing server (may need both PIDs — see note below)
pkill -f "node dist/server/index.js" || true
sleep 2

# Start with AUTH_DISABLED completely stripped
env -u AUTH_DISABLED bash -lic 'cd /mnt/c/Users/thadd/hermes-web-ui && node dist/server/index.js'
```

Also clean up config files so future restarts don't re-enable it:
```bash
# Comment out in master .env
sed -i 's/^AUTH_DISABLED=1/# AUTH_DISABLED=1/' ~/.hermes/.env

# Comment out override in launcher script
sed -i 's/^export AUTH_DISABLED=1/# export AUTH_DISABLED=1/' ~/.hermes/webui/start-server.sh
```

## Background Process Kill Pitfall

When the server is started with `bash -lic "node dist/server/index.js"`, there are **two processes**:
1. The `bash` wrapper process (parent)
2. The `node dist/server/index.js` child process

`pkill -f "node dist/server/index.js"` may only kill the child, leaving the bash wrapper as a zombie or re-spawning. The port may stay occupied.

**Correct kill sequence:**
```bash
# Find both PIDs
ps aux | grep "node dist/server" | grep -v grep
# Example output:
# thadd  10152  0.0  0.0  6172  5056 ?  Ss  04:03  bash -lic ... node dist/server/index.js
# thadd  10164  0.2  1.6  9743640  130396 ?  Sl  04:03  node dist/server/index.js

# Kill both
kill -15 10152 10164 2>/dev/null || true
sleep 2
kill -9 10152 10164 2>/dev/null || true  # Force if still alive
sleep 2
ps aux | grep "node dist/server" | grep -v grep || echo "Server killed"
```

## Verification Commands

After restarting without `AUTH_DISABLED`:

```bash
# Auth system status
curl -sf http://localhost:8648/api/auth/status
# Expected: {"hasPasswordLogin":true,"username":"AntiSyStem","hasUsers":true}

# Login test
curl -s -X POST http://localhost:8648/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"AntiSyStem","password":"<password>"}'
# Expected: {"token":"eyJhbG..."}

# Me endpoint (with JWT)
curl -s http://localhost:8648/api/auth/me \
  -H "Authorization: Bearer <token>"
# Expected: {"user":{"id":1,"username":"AntiSyStem","role":"super_admin",...}}
```

**Note:** `/api/health` may not exist or may return differently. Use `/api/auth/status` as the definitive auth verification endpoint.

## Database Path Note

The SQLite DB location depends on `NODE_ENV`:
- **Development** (default, no env set): `packages/server/data/hermes-web-ui.db`
- **Production** (`NODE_ENV=production`): `~/.hermes-web-ui/hermes-web-ui.db`

If accounts appear missing after restart, verify which DB the server opened:
```bash
lsof -p $(pgrep -f "node dist/server/index.js") | grep hermes-web-ui.db
```

## Session Context

This technique was discovered during the v0.6.0 upgrade on 2026-05-24 when the `AntiSyStem` super_admin account existed in the DB but login was rejected with "Auth is disabled." The `unset` approach failed because the Hermes parent process (PID 618) had `AUTH_DISABLED=1` in its environment. `env -u` successfully stripped it at spawn time.
