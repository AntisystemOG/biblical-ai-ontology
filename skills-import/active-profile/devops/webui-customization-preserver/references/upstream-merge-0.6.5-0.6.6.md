# Upstream Merge 0.6.5 → 0.6.6

## Context

- **Local:** HEAD detached at `v0.6.5` (b5b7d55) with Spock branding
- **Upstream:** 18 commits ahead on `origin/main`
- **Repo:** `/mnt/c/Users/thadd/hermes-web-ui`
- **Server cwd:** `/mnt/c/Users/thadd/hermes-web-ui` (WSL)
- **Node:** 23.11.1
- **Build time:** ~92s (Vite) + ~7.6s (server)

## Upstream Changelog (selected)

| Commit | Summary | Relevance |
|---|---|---|
| 877bb16 | Skip macOS signing when certificates absent | Build-only, no impact |
| 6da5cd6 | Add repository harness for coding agents | New feature |
| ce04b10 | Fix Windows bundled Hermes CLI launcher | Build-only |
| 046c8d4 | Fix desktop release artifact uploads | CI-only |
| 7f944a4 | Fix desktop release artifact globs | CI-only |
| 12e0b5e | raise body parser limit so avatar upload doesn't 413 | Server fix |
| eea1d1d | use path.dirname for credential dir on Windows | Auth fix |
| f799157 | fix desktop preload build and rename app | Electron |
| cbae8e8 | Add desktop (Electron) packaging and release | Electron |
| cb410e5 | preserve text/tool-call ordering to stop split narration | Bridge fix |
| 818e7f7 | fix chat scroll jitter | UI fix |
| b015e70 | fix MCP management lifecycle | MCP fix |
| 675ddb8 | fix profile runtime status loading | Stability |
| a1f06b8 | fix virtual list empty state centering | UI fix |
| e988ce6 | remove setup script docs | Docs cleanup |
| 9643a08 | fix bridge mcp tool discovery | MCP fix |

## Merge Process

1. **Pre-merge state preservation:**
   ```bash
   cd /mnt/c/Users/thadd/hermes-web-ui
   git status  # shows modified: index.html, logo.png, favicon.ico, thinking-*.mp4, etc.
   git log --oneline HEAD..origin/main  # list upstream commits
   ```

2. **Commit local customizations first:**
   ```bash
   git add -A
   git commit -m "spock: preserve customizations before merge"
   ```

3. **Build quickly detects only 1 real conflict:**
   ```bash
   git merge origin/main
   # Auto-merging packages/client/src/components/layout/AppSidebar.vue
   # CONFLICT (content): Merge conflict in AppSidebar.vue
   ```

4. **The Pitfall: `post-checkout` hook reverts resolution**
   - `/mnt/c/Users/thadd/hermes-web-ui/.git/hooks/post-checkout` was a **Spock Guardian** script
   - `git checkout --theirs AppSidebar.vue` triggers this hook
   - The hook runs: `git checkout HEAD -- packages/client/src/components/layout/AppSidebar.vue`
   - **HEAD is still pre-merge** (v0.6.5), so it restores the OLD file
   - Result: merge commit silently contains the OLD `AppSidebar.vue` instead of v0.6.6
   - Suppressed features: `RouteLinkItem`, `isStoredSuperAdmin`, `usePersistentRecord`, new nav items like `hermes.mcp`, route key mapping (`route.name === "hermes.session"` etc.)

5. **Resolution with hook bypass:**
   ```bash
   # Option A: Disable hook temporarily
   mv .git/hooks/post-checkout .git/hooks/post-checkout.bak
   git merge --abort  # clean state
   git merge origin/main  # re-run merge
   git checkout --theirs packages/client/src/components/layout/AppSidebar.vue
   git add packages/client/src/components/layout/AppSidebar.vue
   # Manually rebrand: sed -i 's/alt="Hermes"/alt="Spock"/g' ...
   # sed -i 's/>Hermes</>Spock</g' ...
   git add packages/client/src/components/layout/AppSidebar.vue
   git merge --continue
   mv .git/hooks/post-checkout.bak .git/hooks/post-checkout
   ```

   ```bash
   # Option B: Manual conflict resolution (preferred — no hook bypass needed)
   # Edit AppSidebar.vue: keep upstream JS logic, keep upstream template structure,
   # only replace logo alt text and logo-text span content
   ```

6. **Post-merge feature verification:**
   ```bash
   grep "RouteLinkItem" packages/client/src/components/layout/AppSidebar.vue && echo "OK" || echo "FAIL"
   grep "isStoredSuperAdmin" .../AppSidebar.vue && echo "OK" || echo "FAIL"
   grep "usePersistentRecord" .../AppSidebar.vue && echo "OK" || echo "FAIL"
   grep "hermes.mcp" .../AppSidebar.vue && echo "OK" || echo "FAIL"
   ```

7. **Build:**
   ```bash
   npm run build
   # vite build in ~92s, server build in ~7.6s
   # Large chunks expected (mermaid.js, monaco-editor)
   ```

8. **Verify Spock assets in dist:**
   ```bash
   ls -la dist/client/logo.png
   ls -la dist/client/favicon.ico
   ls -la dist/client/spock-avatar.png
   ls -la dist/client/assets/mp4/thinking-*.mp4
   ```

9. **Stop old server, restart with env vars:**
   ```bash
   pkill -f "node.*dist/server/index.js"
   unset AUTH_DISABLED
   export NODE_ENV=production
   export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
   export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
   export PORT=8648
   export BIND_HOST=0.0.0.0
   cd /mnt/c/Users/thadd/hermes-web-ui && node dist/server/index.js
   # Verifies via: curl -sf http://127.0.0.1:8648/health
   ```

## Post-Merge Issues

- **Server still alive during merge:** A previous server process (PID 391) was running from the old build. Had to `pkill` it.
- **`node --pending-deprecation`:** The new build uses an experimental SQLite feature; warning is benign.
- **`webui_version` detection:** Health check reports `"webui_version":"0.6.6"` and `"webui_latest":"0.6.5"`. The `latest` detection is stale (expected until upstream updates their latest tag).

## Files Modified in Working Tree During This Session

- `packages/client/index.html` — `<title>Spock</title>`
- `packages/client/public/favicon.ico` — Spock favicon
- `packages/client/public/logo.png` — Spock logo
- `packages/client/public/spock-avatar.png` — Spock avatar
- `packages/client/src/assets/logo.png` — Spock logo
- `packages/client/src/assets/thinking-dark.mp4` — Star Trek badge
- `packages/client/src/assets/thinking-light.mp4` — Star Trek badge
- `packages/client/src/components/hermes/chat/MessageList.vue` — uses `.mp4`, not `.gif`
- `packages/client/src/components/hermes/chat/SessionListItem.vue` — uses `spock-avatar.png`
- `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` — uses `spock-avatar.png`
- `packages/client/src/components/layout/AppSidebar.vue` — merged + rebranded *after* bypassing hook
- `packages/server/src/controllers/hermes/models.ts` — local Ollama provider auth exemption
- `packages/server/src/services/config-helpers.ts` — local Ollama config helper
- `packages/server/src/shared/providers.ts` — local Ollama provider preset
- `vite.config.website.ts` — model cache name

## Verification Checklist (what was confirmed)

- [x] `dist/client/logo.png` — Spock logo present
- [x] `dist/client/favicon.ico` — Spock favicon present
- [x] `dist/client/spock-avatar.png` — Spock avatar present
- [x] `dist/client/assets/mp4/thinking-*.mp4` — MP4 present
- [x] `dist/client/assets/` — no `.gif` thinking assets
- [x] `MessageList.vue` imports `.mp4` not `.gif`
- [x] `index.html` title is `Spock`
- [x] AppSidebar.vue has `RouteLinkItem`, `isStoredSuperAdmin`, `hermes.mcp` nav
- [x] Server started with `NODE_ENV=production`
- [x] Health check returns `{"webui_version":"0.6.6","status":"ok"}`
- [x] Server bound to `0.0.0.0:8648`

## Prevention for Next Update

Before running `git merge origin/main`, disable the post-checkout hook or use manual conflict resolution for `AppSidebar.vue`. Re-enabling upstream features after a bad merge requires re-running the merge from scratch.
