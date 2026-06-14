# Session 2026-05-24: v0.6.0 Auth Bootstrap and DB Path Behavior

## Context
Post-upgrade to v0.6.0, user reported the Settings UI showed a "Current Account" section with a "Change Password" button, but no actual account existed. This caused confusion and a security concern.

## Key Findings

### 1. Empty `users` Table = Anyone Can Claim Admin
The `users` table in the active DB had **0 rows**. The WebUI auth controller
(`auth.ts`) detects empty table and auto-bootstraps a `super_admin` on the very
first `POST /api/auth/login` call, using whatever username/password the request
provides. There is no pre-seeded default account.

**Security implication**: Since the server binds to `0.0.0.0:8648` (LAN accessible),
any device on the local network that hits `/login` before the legitimate owner
can become super_admin with arbitrary credentials. The "Current Account" UI
section displays Change Password / Logout buttons regardless of whether an account
exists — it is just a UI shell.

**Verification command**:
```bash
sqlite3 /mnt/c/Users/thadd/hermes-web-ui/packages/server/data/hermes-web-ui.db \
  "SELECT COUNT(*) FROM users;"
# 0 = vulnerable, 1+ = account exists
```

### 2. DB Path Is Conditional on `NODE_ENV`
Source file: `packages/server/src/db/index.ts` lines 10-14:
```typescript
const isDev = process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;
const isTest = process.env.NODE_ENV === 'test';
const dbDir = isDev || isTest
  ? path.join(process.cwd(), 'packages/server/data')
  : path.join(config.appHome, 'data');
```

- **Development** (default, no `NODE_ENV` set): `packages/server/data/hermes-web-ui.db`
- **Production** (`NODE_ENV=production`): `~/.hermes-web-ui/hermes-web-ui.db`

**Pitfall**: Starting the server manually from the repo directory creates the DB in
the repo-local path. If a systemd service later starts with `NODE_ENV=production`,
user accounts appear to vanish because the service reads a different DB file.

**Legacy DB check**: The old pre-v0.6.0 DB at `~/.hermes-web-ui/hermes-web-ui.db`
exists but has **no `users` table** (older schema). Do not expect to find legacy
accounts there.

### 3. `DEFAULT_PASSWORD` Constant Is Not the Login Password
In `users-store.ts`:
- `DEFAULT_USERNAME = 'admin'`
- `DEFAULT_PASSWORD = ***`

These constants are **only** used to flag `requiresCredentialChange=true` on the
bootstrapped user if their password still matches the hardcoded default. The first
login does NOT use these values — the user-provided credentials from the login
form become the actual account.

### 4. Correct Hash Format
The app uses `crypto.scrypt` with:
- `N = 16384`, `r = 8`, `p = 1`
- `keylen = 64`
- `salt = crypto.randomBytes(16).toString('hex')`
- Stored format: `scrypt:<salt>:<hash>` (hex)

Incorrect hash generation (e.g., `scryptSync` without matching parameters or wrong
format) causes `verifyPassword` to reject valid-looking passwords.

## Recovery / Remediation

### Immediate: Create the first user before anyone else can
Stop the server, insert a pre-hashed row, restart:
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
pkill -f "node dist/server/index.js" || true
sleep 1

hash=$(node -e "
  const crypto = require('crypto');
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync('YourNewStrongPass123!', salt, 64, { N:16384, r:8, p:1 }).toString('hex');
  console.log('scrypt:' + salt + ':' + hash);
")

sqlite3 packages/server/data/hermes-web-ui.db \
  "INSERT INTO users (username, password_hash, role, status, created_at, updated_at) \
   VALUES ('AntiSyStem', '$hash', 'super_admin', 'active', $(date +%s), $(date +%s));"

cd /mnt/c/Users/thadd/hermes-web-ui && node dist/server/index.js &
```

### Check which DB the running server is using
```bash
lsof -p $(pgrep -f "node dist/server/index.js") | grep hermes-web-ui.db
cat /proc/$(pgrep -f "node dist/server/index.js")/environ | tr '\0' '\n' | grep NODE_ENV
```
