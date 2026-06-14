# EKKOLearnAI Web UI Auth & Token Pitfalls

## Problem

Setting `AUTH_DISABLED=1` environment variable does **NOT** disable login if a `.token` file already exists inside `HERMES_WEB_UI_HOME`.

## Pitfall: Strict Equality Check

The Node server checks `process.env.AUTH_DISABLED === "1"` (strict equality). Setting `AUTH_DISABLED=yes`, `AUTH_DISABLED=***`, or `AUTH_DISABLED=true` **leaves auth fully enabled**.

Always set exactly:
```bash
export AUTH_DISABLED=1
```

## How Auth Works

The auth service (`packages/server/src/services/auth.ts`) reads `.token` on startup. If the file exists, it requires authentication regardless of the `AUTH_DISABLED` flag. In practice:

1. First run without `AUTH_DISABLED` → server auto-generates `.token`
2. Subsequent run with `AUTH_DISABLED=yes` → login prompt still appears (auth NOT disabled)
3. Subsequent run with `AUTH_DISABLED=1` → login prompt still appears if `.token` exists

**Full fix:** Either delete `.token` or ensure `AUTH_DISABLED=1` AND `.token` does not exist.

## Fixes

**Option A — Delete token and run with exactly `AUTH_DISABLED=1`:**
```bash
rm $HERMES_WEB_UI_HOME/.token
export AUTH_DISABLED=1
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export PORT=8648
export BIND_HOST=0.0.0.0
node dist/server/index.js
```

**Option B — Pass token in URL query string (for desktop shortcuts with auth enabled):**
```
http://172.24.60.180:8648/#/?token=a77bf3c74a636540a70f290382784ace4ba67cbf7beba7174290810117fb8f01
```

**Option C — Pre-set a fixed token via env var (auth still enabled, token known):**
```bash
export AUTH_TOKEN=my-fixed-128-bit-hex-value
```
Then embed that fixed token in the shortcut URL.

## Code Context

In `bin/hermes-web-ui.mjs`:
```javascript
function ensureToken() {
  if (process.env.AUTH_DISABLED === '1' || process.env.AUTH_DISABLED === 'true') return null
  if (process.env.AUTH_TOKEN) return process.env.AUTH_TOKEN

  let token = getToken()
  if (!token) {
    mkdirSync(dirname(TOKEN_FILE), { recursive: true })
    token = randomBytes(32).toString('hex')
    writeFileSync(TOKEN_FILE, token + '\n', { mode: 0o600 })
  }
  return token
}
```

Note: Some versions check only `=== '1'`, making `true` also invalid.

## Session-Specific Bug (2026-05-19)

User set `AUTH_DISABLED=yes` but auth remained enabled. Server logs showed `"Auth enabled -- token: ..."`. Root cause: `AUTH_DISABLED` was not exactly `"1"` in the process environment. The `.env` file had `AUTH_DISABLED=***` (sensitive masking), but when the agent exported it via shell, the value became literal `yes`. After switching to `AUTH_DISABLED=1` and restarting, auth was properly disabled.

## Browser Cache Trap After Auth Disable

The server may have auth correctly disabled, but the **Vue frontend already cached the auth-required state** in memory/localStorage. The compiled JavaScript loads the initial auth status once and does not re-query `AUTH_DISABLED` on reconnect.

**Symptom:** Server logs show no "Auth enabled" message, API endpoints return 200 without tokens, but browser still shows "Please enter your access token" login screen.

**Fixes:**
1. **Hard-refresh** the browser: `Ctrl + Shift + R` (Chrome/Edge) or `Ctrl + F5` (Firefox)
2. Or **Clear site data** for the IP:port: DevTools → Application → Storage → Clear site data
3. Or open in an **incognito/private window** to bypass cached state

**Prevention (for `.bat` shortcuts):** When switching from auth-enabled to auth-disabled, remove the `/#/?token=` fragment entirely from the URL. The old `token=` query param in the hash fragment can trigger the auth flow even when auth is disabled.

## Environment Variable Inheritance Gotcha

Setting `export AUTH_DISABLED=1` in a shell does NOT guarantee the Node server sees it. Common failure modes:

1. **Backgrounding strips the env**: `~/node26/bin/node dist/server/index.js &` from a shell that didn't export the var → auth stays ON
2. **`.env` file masking**: If `.env` contains `AUTH_DISABLED=***` (redacted), importing the file may set the literal string `***`, not `1`
3. **Systemd/service env isolation**: The server started from a systemd unit or another process context won't inherit interactive shell exports

**Fix:** Always start the server from a wrapper script that explicitly exports all required variables:
```bash
#!/bin/bash
export AUTH_DISABLED=1
export HERMES_HOME=/home/thadd/.hermes
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export PORT=8648
export BIND_HOST=0.0.0.0
export WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace
cd /home/thadd/hermes-web-ui-ekko
exec /home/thadd/node26/bin/node dist/server/index.js
```
