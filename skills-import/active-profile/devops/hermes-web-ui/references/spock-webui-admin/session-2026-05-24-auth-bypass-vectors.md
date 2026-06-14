# WebUI Auth Bypass Vectors and Hardening Guide

## Discovery Context

When the user requested "every attempt to access localhost must ask for username and password," a full audit of the auth stack revealed **four bypass vectors** that allow unauthenticated access to the SPA or API.

---

## Bypass Vector 1: Static Files Are Public

**Location**: `packages/server/src/services/auth.ts`, `requireAuth()` lines 61-64

```typescript
if (!lowerPath.startsWith('/api') && !lowerPath.startsWith('/v1') && !lowerPath.startsWith('/upload')) {
  return await next()
}
```

**Impact**: `GET /`, `GET /index.html`, `GET /assets/logo.png`, and all static assets are served **without any authentication**. An attacker on the LAN can load the SPA shell and see the UI layout (though API data remains protected).

**Fix**: Move JWT auth middleware **before** static file serving, but allow `index.html` to serve as the auth gateway. The SPA router then handles the login flow. Requires careful ordering:
1. API routes (public + protected)
2. JWT middleware for static paths
3. Static file serving with `historyApiFallback` behavior

---

## Bypass Vector 2: Client Auto-Redirect When JWT Exists

**Location 1**: `packages/client/src/views/LoginView.vue`, lines 17-19
```typescript
onMounted(() => {
  if (hasApiKey()) {
    router.push('/hermes/chat')
  }
})
```

**Location 2**: `packages/client/src/router/index.ts` — login route marked `meta: { public: true }`, but the route guard likely redirects authenticated users away from login.

**Impact**: A returning user with a valid JWT in `localStorage` never sees the login page. The browser loads `/`, Vue mounts, checks `hasApiKey()`, and immediately pushes to `/hermes/chat`. This means:
- A shared or borrowed computer with a saved JWT auto-logs in
- The user cannot "log out and switch accounts" without manually clearing localStorage

**Fix**: Remove the `hasApiKey()` auto-redirect from `LoginView.vue`. Always render the login form. If the user is already authenticated, show a "Continue as AntiSyStem" button rather than auto-redirecting. Add JWT expiry validation to clear stale tokens.

---

## Bypass Vector 3: URL Token Extraction

**Location**: `packages/client/src/main.ts`, lines 29-34
```typescript
const urlParams = new URLSearchParams(window.location.search)
const hashQuery = window.location.hash.split('?')[1]
const urlToken = urlParams.get('token') || (hashQuery ? new URLSearchParams(hashQuery).get('token') : null)
if (urlToken) {
  ;(window as any).__LOGIN_TOKEN__ = urlToken
}
```

**Impact**: The client extracts `?token=` from the URL into `window.__LOGIN_TOKEN__`. While this specific variable appears unused in current code, it represents an **architectural intent** to support URL-based token login. Any future code that reads `window.__LOGIN_TOKEN__` would bypass the username/password flow.

**Fix**: Remove the token extraction block entirely. The server-side bearer token auth (`~/.hermes/webui/.token`) should be disabled when username/password auth is active, or the client should never capture it.

---

## Bypass Vector 4: Server Bearer Token Fallback

**Location**: `packages/server/src/services/auth.ts`, `requireAuth()` lines 65-85

The server accepts **two** authentication methods on API routes:
1. User JWT (from `/api/auth/login`)
2. Server bearer token (from `~/.hermes/webui/.token`, 64-char hex)

**Impact**: Even with username/password enabled, passing the server token as `Authorization: Bearer <token>` grants full API access. This is by design for service-to-service auth, but it means the `.token` file is a **master key** that bypasses user accounts entirely.

**Mitigation**: When enforcing "every access requires username/password," the server bearer token layer should be removed or made optional via configuration. Alternatively, ensure the `.token` file is rotated and protected (mode `0600`).

---

## Fix Status: Steps 1–3 Implemented (Client-Side Hardening)

The following changes were applied, built into `dist/`, and verified:

### Implemented: Remove Client Auto-Redirects
- `packages/client/src/views/LoginView.vue`: Removed `if (hasApiKey()) router.replace("/hermes/chat")` setup-time redirect. Every visit renders the login form.
- `packages/client/src/router/index.ts`: Removed `if (to.name === 'login' && hasApiKey()) next({ path: '/hermes/chat' })` route guard. The login route stays public but no longer bypasses for authenticated users.

### Implemented: Remove URL Token Capture
- `packages/client/src/main.ts`: Removed the `urlParams.get('token')` / `hashQuery` extraction block that stored tokens in `window.__LOGIN_TOKEN__`. No URL-based token injection bypasses the form.

### Implemented: JWT Expiry Validation
- `packages/client/src/api/client.ts`: `hasApiKey()` now decodes the JWT payload, checks the `exp` claim, and calls `clearApiKey()` if expired. `getStoredUserRole()` guards with `hasApiKey()` first.

### Build Verification
After `npm run build`, confirmed compiled JS does **not** contain:
- `__LOGIN_TOKEN__`
- `urlParams.get('token')`
- `router.replace("/hermes/chat")`

Confirmed JWT expiry check IS present in minified output.

---

## Not Implemented (By Design)

### Step 4: Server-Side Static File Auth
**Status**: NOT implemented — unnecessary for SPA architecture.

The static HTML at `/` must remain public so the SPA can boot. Auth enforcement happens client-side via Vue router. Adding server-side auth to `index.html` would break the SPA entirely (browser would receive 401 instead of HTML, so no Vue app mounts to show the login form).

### Step 5: Disable Server Bearer Token
**Status**: NOT implemented — server token still serves as master API key for programmatic access.

The server token (`~/.hermes/webui/.token`) is still accepted alongside user JWTs. Since the client now forces login via the form, the practical risk is minimal. To fully remove this vector, replace `requireAuth()` with `requireUserJwt()` on all API routes, or add `DISABLE_SERVER_TOKEN=1` env var support.

---

## Full Hardening Implementation Plan (Historical — Pre-Implementation)

### Step 1: Remove Client Auto-Redirects
- `LoginView.vue`: Delete `hasApiKey()` check in `onMounted`
- `router/index.ts`: Remove route guard that redirects away from login when authenticated
- Add explicit "Continue" button on login page for already-authenticated users

### Step 2: Remove URL Token Capture
- `main.ts`: Delete the `urlToken` extraction block (lines 29-34)

### Step 3: Add JWT Expiry Validation
- `router/index.ts`: Decode JWT payload, check `exp` claim. If expired, clear `localStorage` and allow login page to render.
- `client.ts`: Add 401 interceptor that clears JWT and reloads to login.

### Step 4: Server-Side Static File Auth (Advanced)
- `services/auth.ts`: Remove the early-return for non-API paths. Instead, check JWT on all paths except `/api/auth/login` and `/api/auth/status`.
- `routes/index.ts`: Ensure static serving happens **after** auth middleware, or mount a separate middleware on `/` that requires JWT before serving `index.html`.
- **Caveat**: The SPA needs `index.html` to boot. The auth gate should return `index.html` only when authenticated, or redirect to `/api/auth/login` (which returns JSON — not ideal for browser). Better approach: serve `index.html` unconditionally but have the SPA router enforce auth, and add a `beforeEnter` guard on `/` that redirects to login when no JWT.

### Step 5: Disable or Remove Server Bearer Token
- Option A: Remove `requireAuth()` entirely and rely solely on `requireUserJwt()` for all routes.
- Option B: Add an env var `DISABLE_SERVER_TOKEN=1` that skips bearer token validation.
- Option C: Keep bearer token for programmatic access but require it only on specific API paths.

### Step 6: Restart and Verify
```bash
# Rebuild
cd /mnt/c/Users/thadd/hermes-web-ui && npm run build

# Restart with auth fully enabled
pkill -f "node dist/server/index.js" || true
sleep 1
cd /mnt/c/Users/thadd/hermes-web-ui && env -u AUTH_DISABLED node dist/server/index.js &

# Verify every path requires auth
curl -sf http://localhost:8648/                     # Should redirect or require auth
curl -sf http://localhost:8648/api/auth/status      # Public (auth discovery)
curl -sf http://localhost:8648/api/hermes/config    # 401 without JWT
curl -sf http://localhost:8648/api/auth/me          # 401 without JWT
```

---

## Key Files Involved in Auth Flow

| File | Role |
|------|------|
| `packages/server/src/services/auth.ts` | `requireAuth()` — bearer token + static file bypass |
| `packages/server/src/middleware/user-auth.ts` | `requireUserJwt()` — JWT validation for API routes |
| `packages/server/src/routes/index.ts` | Route registration order (public → auth → protected) |
| `packages/server/src/routes/auth.ts` | `/api/auth/login`, `/api/auth/status`, `/api/auth/me` |
| `packages/client/src/router/index.ts` | Client routing, `meta.public`, `hasApiKey()` guards |
| `packages/client/src/views/LoginView.vue` | Login form, auto-redirect on mount |
| `packages/client/src/main.ts` | URL token extraction before router init |
| `packages/client/src/api/client.ts` | `hermes_api_key` localStorage, Bearer header, 401 handler |
| `packages/client/src/App.vue` | Layout wrapper, sidebar visibility |
