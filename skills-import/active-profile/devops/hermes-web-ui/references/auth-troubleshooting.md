# WebUI Auth Troubleshooting — Username/Password Login Failures

## Symptom: Login page rejects valid password

### Root Causes (in order of frequency)

#### 0. `AUTH_DISABLED` Inherited from Parent Shell (v0.6.3+ Silent Bug)

Even though `AUTH_DISABLED` env var support was conceptually removed in v0.6.3, the `auth.ts` service still checks for its presence. **Any non-empty value** (including `0`, `false`, or empty string inherited from a parent shell) disables username/password auth and the login endpoint returns `500 "Auth is disabled on this server"`.

This is a **silent inheritance bug** — if the parent shell has `AUTH_DISABLED` set from a previous debugging session, `.bashrc` export, or an old launcher `.bat`, child processes inherit it and all logins fail even though the production DB has valid user records.

**How to check:**
```bash
# Check the server process environment
cat /proc/$(pgrep -f "node.*dist/server/index.js" | head -1)/environ | tr '\0' '\n' | grep AUTH_DISABLED
```

If it prints **anything at all** (even `AUTH_DISABLED=0` or `AUTH_DISABLED=false`), auth is disabled.

**Fix:**
```bash
pkill -f "node.*dist/server/index.js"
sleep 2
unset AUTH_DISABLED  # critical: must be explicit, not just omitted
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
/home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js
```

**Permanent fix for launcher scripts:** Update `.bat` and `.sh` launchers to include `unset AUTH_DISABLED` (or `set AUTH_DISABLED=` in Windows batch) before starting the server.

#### 1. Server Using Wrong DB (Dev vs Production Path)

The server DB path depends on `NODE_ENV`:

| `NODE_ENV` | DB Path | Notes |
|---|---|---|
| **not set** (default = dev) | `process.cwd()/packages/server/data/hermes-web-ui.db` | Running from `/home/thadd` → `/home/thadd/packages/server/data/hermes-web-ui.db` |
| `production` | `config.appHome` = `~/.hermes/webui/` | The persistent, correct location |

**How to check which DB the server is using:**
```bash
# Find the server process
pgrep -f "node.*dist/server/index.js"

# Check its working directory
readlink /proc/$(pgrep -f "node.*dist/server/index.js" | head -1)/cwd
```

If CWD is `/home/thadd` and `NODE_ENV` is NOT set to `production`, the server creates a new empty dev DB at `/home/thadd/packages/server/data/hermes-web-ui.db` instead of using the existing production DB.

**Fix:** Always start the server with `NODE_ENV=production`:
```bash
export NODE_ENV=production HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=8648 BIND_HOST=0.0.0.0
/home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js
```

#### 2. Users Table Empty / Never Bootstrapped

The first user account is created by the **first successful `POST /api/auth/login` request** when the `users` table is empty. If this was never done (or was done on a dev DB that got wiped), the table exists but has zero rows.

**How to check:**
```python
# Use Python (sqlite3 CLI may not be installed)
import sqlite3
conn = sqlite3.connect("/home/thadd/.hermes/webui/hermes-web-ui.db")
cursor = conn.cursor()
cursor.execute("SELECT id, username, role FROM users;")
print(cursor.fetchall())  # [] = empty, needs bootstrap
conn.close()
```

**Fix — Bootstrap via first login POST:**
```bash
curl -sf http://localhost:8648/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"AntiSyStem","password":"YourPassword123!"}'
```

**Fix — Direct DB insert (server must be stopped):**
```bash
pkill -f "node.*dist/server/index.js"
sleep 2

# Generate scrypt hash using Node (matches auth.ts)
hash=$(/home/thadd/node26/bin/node -e "
  const crypto = require('crypto');
  const salt = crypto.randomBytes(16).toString('hex');
  const h = crypto.scryptSync('YourPassword123!', salt, 64, { N: 16384, r: 8, p: 1 }).toString('hex');
  console.log('scrypt:' + salt + ':' + h);
")

# Insert via Python (sqlite3 CLI often not installed)
python3 -c "
import sqlite3, time
conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
conn.execute('''
  INSERT INTO users (id, username, password_hash, role, status, created_at, updated_at)
  VALUES (1, 'AntiSyStem', ?, 'super_admin', 'active', ?, ?)
''', ('$hash', int(time.time()), int(time.time())))
conn.commit()
conn.close()
print('User created')
"
```

#### 3. Login Lockout (Rate Limiting)

After 3 failed attempts from an IP, the server locks logins for a cooldown period.

**Symptom:** Password is correct but login silently fails or returns 429.

**How to check:**
```bash
cat /home/thadd/.hermes/webui/.login-lock.json
```

Output shows `passwordIpMap` with `failures`, `lockedUntil`, and `firstFailureAt` timestamps.

**Fix — Clear the lock file:**
```bash
rm -f /home/thadd/.hermes/webui/.login-lock.json
```

Then restart the server (it reads the lock file at startup).

#### 4. Password Hash Mismatch (Algorithm Change)

If the password was set with an older server version, the hash algorithm may have changed. The current auth.ts uses scrypt with specific parameters.

**Fix — Direct DB password reset (server stopped):**
```bash
pkill -f "node.*dist/server/index.js"
python3 -c "
import sqlite3, subprocess, time

# Generate new scrypt hash
result = subprocess.run([
  '/home/thadd/node26/bin/node', '-e',
  \"const c=require('crypto');const s=c.randomBytes(16).toString('hex');console.log('scrypt:'+s+':'+c.scryptSync('NewPass123!',s,64,{N:16384,r:8,p:1}).toString('hex'));\"
], capture_output=True, text=True)
hash = result.stdout.strip()

conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
conn.execute('UPDATE users SET password_hash=?, updated_at=? WHERE id=1', (hash, int(time.time())))
conn.commit()
conn.close()
print('Password updated')
"
```

## Diagnostic Flowchart

```
Login rejected
    ↓
Check server process env for AUTH_DISABLED? → YES → unset it, restart server
    ↓ NO
Check .login-lock.json exists? → YES → rm it, restart server
    ↓ NO
Check server DB path (lsof or cwd check) → dev path? → Restart with NODE_ENV=production
    ↓ production path
Check users table has rows → NO → Bootstrap via curl POST or direct DB insert
    ↓ YES
Password hash mismatch → Reset via Node scrypt script
```

## Prevention

**Always start the server with `NODE_ENV=production`:**
```bash
#!/bin/bash
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export PORT=8648
export BIND_HOST=0.0.0.0
export WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace

/home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js \
  >> /home/thadd/.hermes/webui/logs/server.log 2>&1
```

**Never start from `/home/thadd` without `NODE_ENV=production`** — this creates a separate dev DB at `/home/thadd/packages/server/data/` that shadows the production accounts.

## Key Log Locations

| Log | Path |
|---|---|
| Server stdout | `/home/thadd/.hermes/webui/logs/server.log` |
| Login lock state | `/home/thadd/.hermes/webui/.login-lock.json` |
| Active DB (dev) | `cwd/packages/server/data/hermes-web-ui.db` |
| Active DB (production) | `~/.hermes/webui/hermes-web-ui.db` |
