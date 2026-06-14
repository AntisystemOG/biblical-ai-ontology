# WebUI Username/Password System Reference

## Auth Architecture Overview

The Spock WebUI at `/mnt/c/Users/thadd/hermes-web-ui` supports **two independent auth layers**:

1. **URL Token Auth** — `?token=...` query param auto-generated on server start.
   - Stored at `~/.hermes/webui/.token` (mode `0600`, 64-char hex)
   - Read by both server (to compare) and launcher `.bat` (to pass in URL)
   - When `AUTH_DISABLED=1` env var is set, token enforcement is bypassed

2. **Username/Password Login** — User-account system in SQLite (added around v0.5.x).
   - **Database**: `packages/server/data/hermes-web-ui.db` (SQLite)
   - **Table**: `users` (created at bootstrap if missing)
   - **Default first user**: `admin` / `123456` (auto-bootstraps on first login attempt)
   - **Role**: `super_admin` or `admin`
   - **JWT**: `issueUserJwt(user)` issues a user-scoped JWT on successful login
   - **Endpoints**: `POST /api/auth/login`, `POST /api/auth/change-password`, `GET /api/auth/me`

## Key Source Files

| File | Purpose |
|------|---------|
| `packages/server/src/controllers/auth.ts` | Express routes for login, change-password, change-username, me, setup. Contains `login()`, `changePassword()`, `changeUsername()`, `currentUser()`, `authStatus()`. |
| `packages/server/src/db/hermes/users-store.ts` | `hashPassword()` (scrypt), `verifyPassword()`, `updateUserPassword()`, `updateUsername()`, `bootstrapDefaultSuperAdmin()`, SQLite queries |
| `packages/server/src/services/login-limiter.ts` | IP-based rate limiting for login attempts (`checkPassword()`, `recordPasswordFailure()`, `recordPasswordSuccess()`) |
| `packages/server/src/middleware/user-auth.ts` | JWT verification middleware (`issueUserJwt()`, `verifyUserJwt()`) |

## Password Hash Format

Hashes are stored as: `scrypt:<salt_hex>:<hash_hex>`

- Algorithm: `crypto.scryptSync(password, salt, 64)` (Node.js built-in)
- Salt: 16 random bytes as hex (`crypto.randomBytes(16).toString('hex')`)
- Key length: 64 bytes
- `verifyPassword()` uses `timingSafeEqual()` to prevent timing attacks

Example hash generation (same logic as `users-store.ts`):
```bash
node -e "
  const crypto = require('crypto');
  function hashPassword(pw) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(pw, salt, 64).toString('hex');
    return 'scrypt:' + salt + ':' + hash;
  }
  console.log(hashPassword('YourNewPassword123!'));
"
```

## Direct DB Password Reset (server stopped)

The safest approach when you don't know the current password — stops the server to avoid SQLite lock contention:

```bash
cd /mnt/c/Users/thadd/hermes-web-ui

# 1. Stop the server
pkill -f "node dist/server/index.js" || true
sleep 1

# 2. Generate new scrypt hash
new_password="YourNewPass123!"
hash=$(node -e "
  const crypto = require('crypto');
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync('$new_password', salt, 64).toString('hex');
  console.log('scrypt:' + salt + ':' + hash);
")

# 3. Update the DB (targets first user, usually id=1)
sqlite3 packages/server/data/hermes-web-ui.db \
  "UPDATE users SET password_hash='$hash', updated_at=$(date +%s) WHERE id=1;"

# 4. Restart
cd /mnt/c/Users/thadd/hermes-web-ui && node dist/server/index.js &
```

## Change Password via API (when logged in)

Requires an active JWT session:

```bash
# Step 1: Obtain JWT via login
curl -sf http://localhost:8648/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"AntiSyStem","password":"<current_pass>"}' \
  | jq -r '.token'

# Step 2: Change password via authenticated endpoint
curl -sf http://localhost:8648/api/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt_from_step_1>" \
  -d '{"currentPassword":"<current_pass>","newPassword":"<new_pass>"}'
```

### Change username (when logged in)

Same JWT-based endpoint:

```bash
curl -sf http://localhost:8648/api/auth/change-username \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt>" \
  -d '{"currentPassword":"<current_pass>","newUsername":"<new_name>"}'
```

## Check Current User Account

```bash
# Query the SQLite DB directly
sqlite3 /mnt/c/Users/thadd/hermes-web-ui/packages/server/data/hermes-web-ui.db \
  "SELECT id, username, role, status, created_at, last_login_at FROM users;"
```

## Default Credentials Warning

The WebUI auto-creates a `super_admin` with username `admin` and password `123456`
when the first login attempt hits an empty `users` table. This is defined by the
constants `DEFAULT_USERNAME = 'admin'` and `DEFAULT_PASSWORD = '123456'` in
`users-store.ts`. Change this immediately after setup.

## Pitfall: Dual Token File Divergence

Some legacy launcher `.bat` files read from `~/.hermes-web-ui/.token` while the
server reads from `~/.hermes/webui/.token`. If they differ, the launcher passes a
stale token.

**Fix**: Update the `.bat` to read the correct path:
```batch
FOR /F "delims=" %%i IN ('wsl cat /home/thadd/.hermes/webui/.token') DO set WSLTOKEN=%%i
```

## Database Schema (users table)

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| username | TEXT NOT NULL UNIQUE | Login name |
| password_hash | TEXT NOT NULL | `scrypt:salt:hash` |
| role | TEXT NOT NULL | `super_admin` \| `admin` |
| status | TEXT NOT NULL | `active` \| `disabled` |
| created_at | INTEGER | Unix timestamp (seconds) |
| updated_at | INTEGER | Unix timestamp |
| last_login_at | INTEGER \| NULL | Last successful login |

## Bootstrapping Behavior

`auth.ts` line 86-88 shows the bootstrap logic:
```typescript
const existingUserCount = countUsers();
const user = existingUserCount === 0
  ? bootstrapDefaultSuperAdmin(username, password)
  : findUserByUsername(username);
```

The `bootstrapDefaultSuperAdmin(username, password)` function in `users-store.ts`
creates a new user with the provided username and password, assigned as `super_admin`.
If the first login attempt uses a custom username (e.g., `AntiSyStem`), that becomes
the primary account instead of `admin`.

**Note**: The `authStatus()` endpoint always reports `hasPasswordLogin: true`
regardless of whether users exist — this is because the system supports local
accounts natively.