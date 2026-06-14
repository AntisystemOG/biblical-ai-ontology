# Upstream Merge v0.6.4 → v0.6.11 Notes

## Overview

This was a clean merge with only 2 file conflicts, both in branding-sensitive locations:
- `packages/client/index.html` — upstream changed `<title>` back to `Hermes Studio`
- `packages/client/src/components/layout/AppSidebar.vue` — upstream changed logo alt/text back to `Hermes`

Both resolved by keeping HEAD (Spock branding) and accepting upstream for all other code.

## New Finding: Dynamic Title in ChatView.vue

**v0.6.11 introduced a new upstream file that the previous merge sessions never saw:**
`packages/client/src/views/hermes/ChatView.vue`

Inside it:
```typescript
const productTitle = 'Hermes Studio' // used for document.title updates
```

This is baked into the JS bundle at build time by Vite. Even though `index.html` has `<title>Spock</title>`, the SPA overrides it dynamically when navigating to the Chat view.

**Fix:** Patch the source, then rebuild:
```bash
sed -i "s/const productTitle = 'Hermes Studio'/const productTitle = 'Spock'/g" \
  packages/client/src/views/hermes/ChatView.vue
npm run build
```

**Verification after rebuild:**
```bash
grep -o "productTitle.*Spock" dist/client/assets/js/ChatView-*.js \
  && echo "OK: Spock baked into ChatView bundle" \
  || echo "FAIL: ChatView bundle still says Hermes Studio"
```

## Merge Strategy Used

```bash
git fetch origin
git tag  # identify v0.6.11
git branch backup-pre-v0.6.11-merge
git merge v0.6.11 --no-edit
```

No `--theirs` used, no post-checkout hook triggered. Manual resolution of 2 conflicts, then `git add && git merge --continue`.

## Service Path Correction

The systemd service `hermes-webui.service` had `WorkingDirectory=/mnt/c/Users/thadd/hermes-web-ui` pointing to an old v0.6.10 clone. The active repo is `/home/thadd/hermes-web-ui-ekko`.

**Fix:**
```bash
systemctl --user stop hermes-webui.service
# Edit ~/.config/systemd/user/hermes-webui.service
# Change WorkingDirectory to /home/thadd/hermes-web-ui-ekko
systemctl --user daemon-reload
systemctl --user start hermes-webui.service
```

## Package.json homepage reset

Upstream `v0.6.11` reset `"homepage": "https://hermes-studio.ai"` in `package.json`. Local was `"https://ekkolearnai.com"`.

**Fix after merge:**
```bash
sed -i 's|"homepage": "https://hermes-studio.ai"|"homepage": "https://ekkolearnai.com"|g' package.json
```

## Build Verification

Build time: ~2 minutes (npm ci) + ~1 minute (npm run build)

Post-build checks:
- `dist/client/index.html` contains `<title>Spock</title>`
- `dist/client/assets/js/ChatView-*.js` contains `Spock` not `Hermes Studio`
- `dist/client/logo.png` exists
- `dist/client/assets/mp4/thinking-*.mp4` exists
- No `.gif` contamination in dist

## Files That Survived (66 total)

All 66 customization files from pre-merge were still present post-merge:
- Spock branding: title, sidebar logo, favicon, avatar, thinking MP4s
- EKKO auth enforcement (login view auto-redirect removed)
- EKKO asset files (logo.png, favicon.ico, spock-avatar.png)
- i18n locale customizations (all 9 language files)
- Server-side auth/session/db customizations
- Profile/chat/group-chat store customizations
- Docker publish workflow
- GitHub preview settings panel

## No .gif contamination

`MessageList.vue` was NOT affected in this merge — no `.gif` references introduced. The asset reference check passed cleanly.

## Hermes Agent Co-Update

Done in parallel: Hermes Agent updated from v0.15.1 → v0.16.0 (495 commits).
Python constraint changed to `<3.14`, so venv recreated with Python 3.11.15.
Installed as editable into active agent venv at `~/.hermes/hermes-agent/venv`.

## Chat History Preservation Note

The WebUI data directory migration (`~/.hermes-web-ui/` → `~/.hermes/webui/`) happened concurrently with this update. The old DB contained 3 sessions (447 messages) not present in the new DB. These were merged by:
1. Identifying sessions in old DB missing from current DB
2. Copying session rows directly
3. Renumbering message IDs (old and new DBs both used auto-increment, causing collisions)
4. Updating `message_count` on restored sessions to match actual counts

All 21 cron jobs were paused before the update at user request (token drain prevention).

## Key Lessons

1. **Always grep for the literal upstream brand name (`Hermes Studio`) in the built dist output, not just in source files.** Vite bundles string literals from Vue components into minified JS. A source patch alone is invisible until `npm run build` runs.
2. **When merging upstream WebUI updates, always check for new files that didn't exist in your local branch.** They won't trigger merge conflicts but may contain upstream branding that gets baked into bundles silently.
3. **WebUI DB migrations between data directories require active merge, not just file copy.** Auto-increment IDs overlap; renumber messages during merge.
