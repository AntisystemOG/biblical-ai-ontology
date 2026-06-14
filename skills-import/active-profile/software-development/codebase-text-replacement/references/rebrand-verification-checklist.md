# Rebrand Verification Checklist

After every file-level rename is complete, run this checklist before declaring the rebrand done.

## Source verification
- [ ] `rg -i 'oldname' /path/to/project` returns zero hits (including comments)
- [ ] `rg -i 'old-name|old_name|__OLDNAME__' /path/to/project` returns zero hits
- [ ] `rg -i 'openOldName' /path/to/project` returns zero hits (camelCase merge survivors)
- [ ] Server-side templates checked for injected strings (e.g., `__HERMES_CONFIG__`)
- [ ] `manifest.json` name/short_name/description updated

## Runtime verification
- [ ] Browser hard-refresh: `Ctrl+Shift+R` (or DevTools → Network → Disable cache → refresh)
- [ ] Service Worker unregistered: DevTools → Application → Service Workers → Unregister
- [ ] Site data cleared: DevTools → Application → Storage → Clear site data
- [ ] `localStorage` inspected for any cached default strings (e.g., `localStorage.getItem('hermes-theme')`)
- [ ] PWA test: uninstall/reinstall if manifest name changed

## Cross-file contract check
- [ ] Frontend `X-OldName-Token` header matches backend rename
- [ ] WebSocket message types / event names updated on both sides
- [ ] API path segments consistent
- [ ] `localStorage` keys updated OR migration shim added

## Common gotchas
- Placeholder text in `<textarea placeholder="Message OldName…">`
- `<title>` tag and `<meta name="apple-mobile-web-app-title">`
- ARIA labels (`aria-label="OldName Dashboard"`)
- Offline / error messages (`"OldName agent is not responding"`)
- Default `botName` fallback string in JS code (`window._botName || 'OldName'`)
