# Session Reference: Voice Input Fix Log

## Date: 2026-05-29
## Goal: Add voice input mic button to Hermes WebUI ChatInput.vue

### Bug 1 — Build Directory Error
**Symptom:**
```
vite v8.0.14 building client environment for production...
[UNRESOLVED_ENTRY] Cannot resolve entry module index.html.
```
**Cause:** Running `npx vite build --outDir dist/client` from `C:\Users\thadd` instead of the project root.
**Fix:** Must run from the project root where `vite.config.ts` is located.
```bash
cd C:\Users\thadd\hermes-web-ui
npx vite build --outDir dist/client
```

### Bug 2 — Undefined SCSS Variable
**Symptom:**
```
[sass] Undefined variable.
    background: $bg-hover;
                ^^^^^^^^^
  packages\client\src\components\layout\ProfileSelector.vue 289:17
```
**Cause:** `ProfileSelector.vue` referenced `$bg-hover` and `$primary-light`, but these were not defined in `variables.scss`.
**Fix:** Add to `packages/client/src/styles/variables.scss`:
- CSS custom properties in `:root` and `.dark` blocks
- SCSS variable aliases alongside existing variables

**Key lesson:** When Vite builds for production, any SCSS variable used anywhere in the client codebase must be declared in the shared `variables.scss`. Vite scans all `.vue` files for SCSS, and a single undefined variable fails the entire build.

**Correct ordering in `variables.scss`:**
1. Add CSS custom properties first in `:root` and `.dark`
2. Add SCSS variable aliases without overwriting existing blocks

### Patch Summary (what was changed)
- `ChatInput.vue`: Added voice recognition script + mic button template + `.voice-btn-listening` CSS
- `variables.scss`: Added `--bg-hover`, `--primary-light` CSS vars + `$bg-hover`, `$primary-light` SCSS aliases
- No changes to server-side code needed

### Verification Steps
1. Build client: `npx vite build --outDir dist/client` (from project root)
2. Restart server: `pkill -f "node dist/server/index.js"; nohup node dist/server/index.js &`
3. Open WebUI in Chrome/Edge on `https://` or `localhost`
4. Click mic button in chat input → allow mic → speak
5. Mic button pulses red when listening; text streams into textarea
