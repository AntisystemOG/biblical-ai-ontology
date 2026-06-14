# SPA Token Injection Workaround

## Problem

Setting `AUTH_DISABLED=1` server-side disables the HTTP 401 check in Express/Koa middleware (`requireAuth`), but the client-side Vue router still routes all pages through the `LoginView.vue` component if `hasApiKey()` returns false or no session exists.

The SPA fetches `/api/auth/status` on mount. Even when `AUTH_DISABLED=1`, this endpoint returns `{"hasPasswordLogin": false, "username": null}`. The `LoginView.vue` does NOT auto-redirect on `AUTH_DISABLED=1` — it only checks `hasApiKey()` (localStorage token or URL token).

So the user sees a login/token prompt regardless of server-side auth disable.

## Fix: Auto-inject a dummy token in the launch URL

`main.ts` reads from `window.location.search` _before_ the router initializes:

```ts
const urlParams = new URLSearchParams(window.location.search)
const hashQuery = window.location.hash.split('?')[1]
const urlToken = urlParams.get('token') || (hashQuery ? new URLSearchParams(hashQuery).get('token') : null)
if (urlToken) {
  ;(window as any).__LOGIN_TOKEN__ = urlToken
}
```

Then `LoginView.vue` reads it:

```ts
const urlToken = (window as any).__LOGIN_TOKEN__ || "";
const token = ref(urlToken);
```

When `handleTokenLogin()` runs, it calls `setApiKey(key)` and routes to `/hermes/chat`.

### Solution

Because `AUTH_DISABLED=1` means the server accepts ANY bearer token (the middleware skips verification), passing a dummy token works:

```
http://localhost:8648/?token=fake-token
```

The SPA auto-detects `token=fake-token`, stores it, submits it, server accepts it, user is logged in.

## Implementation in Desktop Launcher

Update `.bat` launcher to append `?token=fake-token`:

```bat
start "" "http://localhost:8648/?token=fake-token"
```

If the server has `AUTH_DISABLED=1`, this always works.

If auth is NOT disabled, the `.bat` used to read `~/.hermes-web-ui/.token` and inject the real token. That approach is fragile (token can change, file access issues, whitespace in token). The dummy-token + auth-disabled combo is more robust for single-user desktop setups.

## Summary Table

| Method | Pros | Cons | When to use |
|---|---|---|---|
| `AUTH_DISABLED=1` + dummy URL token | 100% silent auto-login, no file reads | No security for multi-user | Single-user desktop |
| Real token read from `~/.hermes-web-ui/.token` | Actual auth if you want it | Fragile, needs token file, WSL-to-Windows file read can fail | If you need real auth later |
| `AUTH_DISABLED=1` alone (no URL token) | Server accepts everything | SPA still shows login | DON'T — doesn't work for SPA |

## Bottom Line

**For Desktop launchers in single-user environments:**
1. Set `AUTH_DISABLED=1` in server env
2. Launch browser with `?token=fake-token`
3. Both are required — neither alone is sufficient
