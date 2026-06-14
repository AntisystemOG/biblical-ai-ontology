# Upstream Merge 0.6.4 — Session Notes (May 2026)

## Context

WebUI local version was `0.6.0` (Spock fork), upstream had released `v0.6.1` through `v0.6.4` on `EKKOLearnAI/hermes-web-ui.git`.

## Merge Strategy

```bash
git fetch origin --tags
git merge v0.6.4 --no-edit
```

## Conflicts

Only **1 conflict**: `packages/client/src/components/layout/AppSidebar.vue`

**Root cause:** Same as v0.6.3 — both branches modified the logo section.
- **Ours:** `div` with `@click="router.push('/hermes/chat')"`, alt="Spock", text="Spock"
- **Upstream:** `RouteLinkItem` with `:to="{ name: 'hermes.chat' }"`, alt="Hermes", text="Hermes"

**Resolution:** Combined both — kept upstream's `RouteLinkItem` component (better accessibility + native navigation), kept our "Spock" alt text and logo text.

```vue
<RouteLinkItem class="sidebar-logo" :to="{ name: 'hermes.chat' }">
  <img :src="logoPath" alt="Spock" class="logo-img" />
  <span class="logo-text">Spock</span>
  <!-- <video class="logo-dance" ... /> -->
</RouteLinkItem>
```

## Auto-Merged Files That Required Manual Fix

### `MessageList.vue` — `.gif` → `.mp4` Revert (AGAIN)

Same silent corruption as v0.6.3. Git auto-adopted upstream's `.gif` imports because:
- Same variables (`thinkingImageLight`, `thinkingImageDark`)
- Same file modified by both branches
- Only extension changed (`.gif` vs `.mp4`)
- No overlapping lines = auto-merge without conflict

**What upstream added:**
- New files: `packages/client/src/assets/thinking-light.gif` (6.4MB), `thinking-dark.gif` (6.0MB)
- `MessageList.vue` imports changed from `.mp4` to `.gif`
- `<img>` element kept (no `autoplay/loop/muted/playsinline` needed for GIF)

**Our `.mp4` files still existed** in `src/assets/` (49KB each) but were no longer imported.

**Fix applied:**
```bash
# 1. Fix imports in MessageList.vue
sed -i 's/thinking-light\.gif/thinking-light.mp4/g' packages/client/src/components/hermes/chat/MessageList.vue
sed -i 's/thinking-dark\.gif/thinking-dark.mp4/g' packages/client/src/components/hermes/chat/MessageList.vue

# 2. Change <img> to <video> element
# (used patch tool — exact match in SKILL.md main file)

# 3. Remove upstream .gif files (dead weight)
rm -f packages/client/src/assets/thinking-light.gif
rm -f packages/client/src/assets/thinking-dark.gif
```

**Note:** Both `.mp4` files have identical content (49,370 bytes). Vite deduplicates them in build output to a single hashed file. This is correct — the build produces `thinking-dark-B_T3hcgV.mp4` only.

## Files That Auto-Merged Cleanly and Stayed Correct

| File | Our Change | Upstream Change | Result |
|---|---|---|---|
| `router/index.ts` | Auth redirect to login | Route additions | ✓ Both preserved |
| `LoginView.vue` | No auto-redirect | Lock reset hints | ✓ Both preserved |
| `client.ts` | JWT expiry in `hasApiKey()` | API additions | ✓ Both preserved |
| `main.ts` | No URL token extract | App setup | ✓ Both preserved |
| `ProfileAvatar.vue` | `/spock-avatar.png` default | Component refactor | ✓ Both preserved (moved to `profiles/` subdir) |
| `SessionListItem.vue` | `profileAvatar` computed | Style updates | ✓ Both preserved |
| `index.html` | `<title>Spock</title>` | Meta tags | ✓ Both preserved |

## Version Update

`package.json` version string updated manually post-merge:
```bash
sed -i 's/"version": "0.6.0"/"version": "0.6.4"/' package.json
```

## Build

```bash
export PATH=/home/thadd/node26/bin:$PATH
npm run build
```

**Timing breakdown:**
- `vue-tsc -b`: ~2 minutes (type checking)
- `vite build`: ~1 minute 22 seconds (rolldown warning about chunk sizes)
- `tsc --noEmit` + `build-server.mjs`: ~12 seconds
- **Total: ~4 minutes**

**Output:**
- `dist/client/` — SPA assets, 24MB total
- `dist/server/index.js` — 6.9MB (with map 10.1MB)

## Dist Verification Checklist

- [x] `dist/client/logo.png` — 726KB, Spock logo
- [x] `dist/client/favicon.ico` — 123KB
- [x] `dist/client/spock-avatar.png` — 726KB
- [x] `dist/client/assets/mp4/thinking-dark-B_T3hcgV.mp4` — present
- [x] No `.gif` files in `dist/client/assets/` — 0 found
- [x] No `.gif` references in compiled JS — `grep -l "thinking.*\.gif"` returns 0 files
- [x] `.mp4` references in compiled JS — `grep -l "thinking.*\.mp4"` returns 1 file
- [x] `<title>Spock</title>` in `dist/client/index.html`

## Server Restart

**Critical env vars (unchanged from 0.6.3):**
```bash
unset AUTH_DISABLED              # still good practice even though upstream removed the check
export NODE_ENV=production        # prevents dev DB creation
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export PORT=8648
export BIND_HOST=0.0.0.0
```

**Bridge started correctly:**
```
[agent-bridge] starting: /home/thadd/hermes-agent-ui/venv/bin/python3 ...
[agent-bridge] ready at ipc:///tmp/hermes-agent-bridge.sock
```

**Listen:** `0.0.0.0:8648` (LAN accessible)

## Post-Start Verification

- [x] `curl /api/auth/status` → `{"hasPasswordLogin":true,"hasUsers":true}`
- [x] Login with `AntiSyStem` / `AllisfairinWarandLove` → 252-char JWT token
- [x] `curl /api/auth/me` → `{"user":{"id":1,"username":"AntiSyStem","role":"super_admin",...}}`
- [x] `logo.png` and `spock-avatar.png` serve HTTP 200
- [x] Chat session starts successfully

## LLM Config Verification (New in v0.6.4)

**v0.6.4 changed API routes.** Old `/api/models` and `/api/providers` moved to `/api/hermes/...`. The client-side store already uses the new routes, but direct `curl` checks must be updated.

| Old Route (pre-0.6.4) | New Route (0.6.4+) |
|---|---|
| `/api/models` | `/api/hermes/available-models` |
| `/api/providers` | `/api/hermes/config/providers` |

**Verify model config survived:**
```bash
token=$(cat ~/.hermes/webui/.token)
curl -sf http://localhost:8648/api/hermes/available-models \
  -H "Authorization: Bearer *** | jq '{default: .default, default_provider: .default_provider}'
# Expected: {"default":"kimi-k2.6","default_provider":"ollama-cloud"}
```

**Source of truth:** `~/.hermes/profiles/<profile>/config.yaml` — `model.default` and `model.provider` keys. The `models_cache.json` at `~/.hermes/webui/` is a cache only.

## Lessons for Future Upgrades

1. **The `.gif` → `.mp4` corruption is persistent.** Every upstream release (0.6.3, 0.6.4) changes the thinking indicator format. This will likely happen again in 0.6.5+. Always grep-check `MessageList.vue` after merge.

2. **`AppSidebar.vue` logo conflict is also persistent.** Upstream will keep changing this section. Resolution pattern: keep upstream's structural element (`RouteLinkItem` / `<a>` / etc.), keep our text content ("Spock").

3. **Vite deduplicates identical `.mp4` files.** Don't panic if only one hashed `.mp4` appears in dist — check byte size matches source.

4. **Build time is stable at ~4 minutes.** Plan accordingly; don't expect faster.

5. **Upstream 0.6.4 did not change auth structure.** Same env requirements as 0.6.3.

6. **API routes may change between releases.** What was `/api/models` in 0.6.0 became `/api/hermes/available-models` in 0.6.4. Always check the server routes after upgrade if API consumers break.
