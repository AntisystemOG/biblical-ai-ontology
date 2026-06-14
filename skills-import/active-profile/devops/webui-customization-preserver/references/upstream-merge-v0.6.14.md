# Upstream Merge v0.6.11 → v0.6.14 Notes

## Overview

Repo: `/home/thadd/hermes-web-ui-ekko` (fork of `EKKOLearnAI/hermes-web-ui`)
Base tag: `v0.6.11`
Target tag: `v0.6.14`
Hermes core: `v0.16.0` already installed

The merge had 5 conflicts, all in files the local branch had customized:
- `packages/client/index.html` — title
- `packages/client/src/api/hermes/chat.ts` — reasoning effort field
- `packages/client/src/components/hermes/chat/ChatInput.vue` — reasoning effort UI import
- `packages/client/src/components/hermes/chat/MessageList.vue` — layout + thinking media
- `packages/client/src/stores/hermes/chat.ts` — reasoning effort logic

## Strategy

1. Committed the existing local customizations first (so the merge had a clean HEAD).
2. Merged `v0.6.14`.
3. For reasoning effort: upstream v0.6.14 shipped a native per-session `reasoningEffort` feature using `NPopselect` and per-session `localStorage`. Adopted upstream and removed the redundant local global-default `NSelect` patch.
4. For branding: manually resolved `index.html` to keep `<title>Spock</title>`.
5. For `MessageList.vue`: accepted upstream structure, then patched:
   - imports back to `.mp4`
   - `<img>` thinking indicator back to `<video autoplay loop muted playsinline>`
   - empty-state `alt: "Hermes"` → `alt: "Spock"`
6. Deleted upstream's new `.gif` thinking assets (`thinking-light.gif`, `thinking-dark.gif`, 6 MB each).
7. Replaced `.mp4` assets with the current Star Trek badge video from `/mnt/c/Users/thadd/.hermes/images/startrek badge.mp4`.
8. Found and patched a new upstream branding surface: `DesktopTitleBar.vue` had `Hermes Studio` in the desktop title bar.

## New Branding Surfaces in v0.6.14

| File | Upstream value | Custom value |
|---|---|---|
| `packages/client/index.html` | `<title>Hermes Studio</title>` | `Spock` |
| `packages/client/src/views/hermes/ChatView.vue` | `const productTitle = 'Hermes Studio'` | `Spock` |
| `packages/client/src/components/layout/AppSidebar.vue` | `alt="Hermes"` / `>Hermes<` | `Spock` |
| `packages/client/src/components/layout/DesktopTitleBar.vue` | `Hermes Studio` | `Spock` |
| `packages/client/src/components/hermes/chat/MessageList.vue` | `alt: "Hermes"` | `alt: "Spock"` |

## Provider Presets Preserved

`packages/server/src/shared/providers.ts` was auto-merged without conflict. Local `kimi-k2.7-code` entries survived across all provider groups:
- Kimi China / Kimi.com coding endpoints
- OpenRouter
- Vercel AI Gateway
- Ollama-cloud

Verified with: `grep -n "kimi-k2.7-code" packages/server/src/shared/providers.ts`

## Build

```bash
cd /home/thadd/hermes-web-ui-ekko
/home/thadd/.hermes/node/bin/npm install
/home/thadd/.hermes/node/bin/npm run build
```

Build completed in ~15 s (client) + 706 ms (server).

## Post-Build Verification

```bash
# Static assets
ls -la dist/client/logo.png
ls -la dist/client/assets/mp4/thinking-*.mp4
find dist/client/assets -name "*.gif" -type f   # should be empty

# Bundle branding
grep -o "productTitle.*Spock" dist/client/assets/js/ChatView-*.js
grep -o "desktop-titlebar__title.*Spock" dist/client/assets/js/index-*.js
grep -o 'logo-img.*alt:"Spock"' dist/client/assets/js/index-*.js

# index.html title
grep "<title>" dist/client/index.html
```

All passed.

## Restart

```bash
systemctl --user restart hermes-webui.service
```

Health check confirmed:
```json
{
  "status": "ok",
  "webui_version": "0.6.14",
  "webui_update_available": false,
  "agent_bridge": { "status": "ready", "reachable": true }
}
```

Production DB intact: 1 user, 11 sessions at `~/.hermes/webui/hermes-web-ui.db`.

## i18n Release Notes Still Mention Hermes Studio

All 10 locale files still contain upstream release-note strings like "Restart Hermes Studio to use it." These are not page titles or primary branding surfaces. They remain as upstream-authored release notes unless the user asks to localize them.

## Key Lessons

1. **Always grep for `Hermes Studio` in the entire client source after a merge.** New upstream files (DesktopTitleBar, ChatView, MessageList empty-state) can slip in without merge conflicts.
2. **Adopt upstream when it supersedes a local customization.** v0.6.14's native reasoning effort feature made the old local patch redundant. Keeping both creates maintenance debt.
3. **Verify bundled output, not just source files.** Vite bakes `DesktopTitleBar.vue` and `ChatView.vue` strings into `index-*.js` and `ChatView-*.js`.
4. **Remove upstream `.gif` bloat when restoring `.mp4`.** Upstream v0.6.14 added 6 MB `.gif` thinking animations; deleting them keeps the bundle lean.
5. **Commit local customizations before merging.** This makes conflict resolution clearer and lets you use `git checkout --theirs` on files where upstream is strictly better.
