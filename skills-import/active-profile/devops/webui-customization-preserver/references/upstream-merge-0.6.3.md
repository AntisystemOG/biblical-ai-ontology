# Upstream Merge 0.6.3 — Session Notes (May 2026)

## Context

WebUI local version was `0.6.0`, npm registry showed `0.6.3` available. The local repo is a fork of `EKKOLearnAI/hermes-web-ui.git` at `AntisystemOG/hermes-web-ui.git` with Spock branding customizations.

## What upstream 0.6.3 brought

| Commit | Change | Impact |
|---|---|---|
| `d03d5e6` | Remove `AUTH_DISABLED` support entirely | Auth now permanently enforced — no bypass possible |
| `6647dc9` | Remove username from public `/api/auth/status` | Security hardening |
| `3cede6f` | Block thinking kaomoji from chat history | Cleaner message rendering |
| `e686f02` | Scope bridge terminal env to worker startup | Fixes Python env inheritance |
| `61b4151` | Increase login lock threshold | Fewer false lockouts |
| `a10e171` | Add history import controls | New feature |
| `acdf187` | Native navigation links (`RouteLinkItem`) | Accessibility + SPA routing |
| `07c4c1d` | Fix provider base URL env handling | Provider config bugfix |

## Merge Conflict

**File:** `packages/client/src/components/layout/AppSidebar.vue`
**Cause:** Both upstream and our local branch modified the logo section.
- **Ours:** `div` with `@click="router.push('/hermes/chat')"`, alt="Spock", text="Spock"
- **Upstream:** `RouteLinkItem` component with `:to="{ name: 'hermes.chat' }"`, alt="Hermes", text="Hermes"

**Resolution:** Combined both — kept upstream's `RouteLinkItem` (better accessibility + native navigation), kept our "Spock" alt text and logo text. No functionality lost.

## Post-Merge Customization Recovery

After `npm run build`, verify Spock assets are in `dist/`:

```bash
ls -la dist/client/logo.png
grep -o '<title>[^<]*</title>' dist/client/index.html
```

If missing, restore from `packages/client/public/` and rebuild:

```bash
cp packages/client/public/logo.png dist/client/logo.png
cp packages/client/public/favicon.ico dist/client/favicon.ico
cp packages/client/public/spock-avatar.png dist/client/spock-avatar.png
```

## Bridge Python Path

Upstream 0.6.3 still does NOT automatically set `HERMES_AGENT_BRIDGE_PYTHON`. After merge, the server MUST be started with:

```bash
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
```

Without this, the bridge falls back to system `python3` and fails with `No module named 'openai'`.

## Auth Changes in 0.6.3

`AUTH_DISABLED` is completely gone from the codebase. The `auth.ts` service no longer checks for it. The only auth modes are:
1. Token auth (`AUTH_TOKEN` env var)
2. Username/password (SQLite DB at `~/.hermes/webui/hermes-web-ui.db`)

This means the `unset AUTH_DISABLED` in launcher scripts is now a no-op — but keep it for backward compatibility with pre-0.6.3 branches.

## Merge Base

Merge base: `f61a1d9` (last common ancestor)
Our local commits after base: Spock branding, auth enforcement, favicon rebuild
Upstream commits after base: 0.6.1, 0.6.2, 0.6.3 development

## Files auto-merged cleanly

- `packages/client/src/views/LoginView.vue` — added lock reset hints
- `packages/client/src/api/client.ts` — upstream additions + our JWT expiry check
- `packages/server/src/controllers/auth.ts` — removed username leak + our changes
- `packages/client/src/components/hermes/chat/SessionListItem.vue` — upstream + Spock avatar

**⚠️ Files auto-merged DANGEROUSLY:**
- `packages/client/src/components/hermes/chat/MessageList.vue` — git auto-adopted upstream `.gif` imports, replacing our `.mp4` with "little girl thinking" GIF. **No merge conflict was raised** because both sides modified the same file but different lines. Always grep-check after merge.

## Post-Merge Asset Reference Corruption

Upstream `0.6.3` and `0.6.4` changed thinking indicator from `.mp4` video to `.gif` image. The git merge adopts this **silently** because:
1. Same file (`MessageList.vue`) was modified by both branches
2. Same variables (`thinkingImageLight`, `thinkingImageDark`)
3. Only the extension changed (`.gif` vs `.mp4`)
4. No overlapping line changes = git auto-merges without conflict

**Critical: upstream also adds NEW `.gif` source files** (`thinking-light.gif`, `thinking-dark.gif`) to `packages/client/src/assets/`. Our old `.mp4` files still exist there from pre-upgrade builds, so the source tree looks OK — but the imports in `MessageList.vue` now point to `.gif`, which Vite copies to `dist/` as `.gif` assets. The chat shows the upstream "thinking girl" animation instead of the Spock badge.

**Fix:**
1. Change `MessageList.vue` imports from `.gif` to `.mp4`
2. Change `<img>` element to `<video autoplay loop muted playsinline>`
3. **Delete** the upstream `.gif` files from `src/assets/` (they're dead weight)
4. Rebuild

```bash
cd /mnt/c/Users/thadd/hermes-web-ui

# Fix imports
sed -i 's/\.gif"/\.mp4"/g' packages/client/src/components/hermes/chat/MessageList.vue

# Fix element (better to use patch tool for exact match)
# <img ...> -> <video autoplay loop muted playsinline ... />

# Remove upstream .gif files
rm -f packages/client/src/assets/thinking-light.gif packages/client/src/assets/thinking-dark.gif

# Rebuild
npm run build
```

**Verification:**
```bash
# Ensure dist has NO .gif thinking assets
find dist/client/assets -name "thinking-*.gif" -type f 2>/dev/null \
  && echo "FAIL: .gif in dist" || echo "OK: no .gif in dist"

# Ensure dist HAS .mp4 thinking assets (Vite may deduplicate identical files to one hash)
find dist/client/assets -name "thinking-*.mp4" -type f 2>/dev/null \
  && echo "OK: .mp4 in dist" || echo "FAIL: no .mp4 in dist"

# Ensure compiled JS references .mp4 not .gif
grep -l "thinking.*\.gif" dist/client/assets/js/*.js 2>/dev/null | wc -l
# Expected: 0
grep -l "thinking.*\.mp4" dist/client/assets/js/*.js 2>/dev/null | wc -l
# Expected: 1
```

## Verification after merge

```bash
# 1. Build completes without errors
npm run build

# 2. Version string in dist matches
grep '"version"' dist/client/assets/index-*.js | head -1
# Expected: "0.6.3"

# 3. Spock assets present in dist
ls dist/client/logo.png dist/client/favicon.ico dist/client/spock-avatar.png

# 4. Server starts with correct env
export NODE_ENV=production
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
node dist/server/index.js

# 5. Health endpoint shows no update available
curl -sf http://localhost:8648/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['webui_version'] == '0.6.3', f\"Version mismatch: {d['webui_version']}\"
assert d['webui_update_available'] == False, 'Update still flagged'
print('OK')
"
```