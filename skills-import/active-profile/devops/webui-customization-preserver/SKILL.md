---
name: webui-customization-preserver
description: "Preserve and re-apply WebUI customizations (Spock branding, auth, logos, videos) after npm rebuilds or git pulls. Fast, focused, no fluff."
trigger:
  - webui customization lost
  - rebuild wiped logo
  - logo gone after update
  - thinking video missing
  - spock branding reset
  - webui rebrand after build
  - npm run build lost customizations
  - hermes webui update preserve
  - webui customizations
---

# WebUI Customization Preserver

Fast recovery for when `npm run build`, `git pull`, or `hermes update` wipes your WebUI customizations.

## Default Policy: Preserve Unless Security

All Spock/EKKO customizations (branding, auth, assets, i18n) are preserved by default across upstream merges and rebuilds. The only exception is when an upstream security fix directly conflicts with a customization — in that case, apply the security fix and re-apply the customization afterward. Do NOT ask the user "should I keep the customizations?" — the answer is always yes unless a security concern is identified.

## What Gets Lost on Rebuild

| Customization | Why it disappears | Location |
|---|---|---|
| Spock logo (`logo.png`) | Vite copies `public/` to `dist/client/` with content hashing | `packages/client/public/logo.png` |
| Thinking videos | Same — copied to `dist/client/assets/mp4/` with hash | `packages/client/src/assets/thinking-light.mp4` |
| Auth token path | Server code change may read from different path | `~/.hermes/webui/.token` vs `~/.hermes-web-ui/.token` |
| Model cache | Server restart may regenerate `models_cache.json` | `~/.hermes/webui/models_cache.json` |
| Favicon / title | `index.html` in `packages/client/index.html` gets re-templated | `packages/client/index.html` |
| Dynamic tab title | New upstream file `ChatView.vue` sets `productTitle = 'Hermes Studio'` baked into JS bundle | `packages/client/src/views/hermes/ChatView.vue` |
| Desktop title bar | New upstream `DesktopTitleBar.vue` shows `Hermes Studio` in the Electron/desktop title bar | `packages/client/src/components/layout/DesktopTitleBar.vue` |
| Empty-state logo alt | `MessageList.vue` empty-state `alt="Hermes"` is visible on first load / empty chat | `packages/client/src/components/hermes/chat/MessageList.vue` |

## Before Updating: Shut Down Running Services

The WebUI server and Hermes gateway must be stopped before updating. If they are
left running, the Telegram bot token stays locked (causing "already in use"
errors on restart) and file locks can corrupt the `dist/` rebuild. See
`references/pre-update-system-prep.md` for exact shutdown commands and the
5-minute token release timing.

## Quick Recovery — One Script

**Step 0: Check if upstream already has your assets**
The WebUI source may already include Spock branding. Always verify before attempting restoration:

```bash
ls -la /home/thadd/hermes-web-ui/packages/client/public/ | grep -E "spock|logo|favicon"
ls -la /home/thadd/hermes-web-ui/packages/client/src/assets/ | grep thinking
```

If `spock-avatar.png`, `logo.png`, and `thinking-*.mp4` are present and have recent timestamps, the upstream already includes your branding. You only need to verify they made it into `dist/` after `npm run build`:

```bash
ls -la /home/thadd/hermes-web-ui/dist/client/logo.png
ls -la /home/thadd/hermes-web-ui/dist/client/assets/mp4/thinking-*.mp4
```

**If assets are missing from upstream**, run the full restore:

## Quick Recovery — One Script

Run this after any `git pull`, `npm install`, or `npm run build`:

```bash
#!/bin/bash
set -e

WEBUI_DIR="/home/thadd/hermes-web-ui-ekko"
IMAGES_DIR="/mnt/c/Users/thadd/.hermes/images"

echo "[1/5] Stopping server..."
pkill -f "node.*dist/server/index.js" || true
sleep 2

echo "[2/5] Restoring Spock logo..."
cp "$IMAGES_DIR/logo.png" "$WEBUI_DIR/packages/client/public/logo.png"
cp "$IMAGES_DIR/logo.png" "$WEBUI_DIR/packages/client/src/assets/logo.png"

echo "[3/5] Restoring thinking videos..."
cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-light.mp4"
cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-dark.mp4"

echo "[4/5] Rebuilding..."
cd "$WEBUI_DIR"
/home/thadd/.hermes/node/bin/npm run build 2>&1 | tail -5

echo "[5/5] Verifying dist output..."
test -f "$WEBUI_DIR/dist/client/logo.png" && echo "  ✓ logo.png in dist"
test -f "$WEBUI_DIR/dist/client/assets/mp4/thinking-"*.mp4 && echo "  ✓ thinking video in dist"

echo ""
echo "Done. Restart the server with:"
echo "  systemctl --user restart hermes-webui.service"
```

Save as `~/.hermes/profiles/plc-coder/skills/devops/webui-customization-preserver/scripts/restore.sh` and run with `bash restore.sh`.

## Pitfalls

### Stale systemd WorkingDirectory after repo migration
The systemd service `hermes-webui.service` may have `WorkingDirectory` pointing to an old checkout path (e.g. `/mnt/c/Users/thadd/hermes-web-ui` from a previous Windows-side clone). After migrating the authoritative repo to a WSL path (e.g. `/home/thadd/hermes-web-ui-ekko`), the service continues to run the old build.

**Detection:**
```bash
systemctl --user cat hermes-webui.service | grep WorkingDirectory
# Compare with: git -C /home/thadd/hermes-web-ui-ekko log --oneline -1
```

**Fix:**
```bash
systemctl --user stop hermes-webui.service
# Edit ~/.config/systemd/user/hermes-webui.service — change WorkingDirectory
systemctl --user daemon-reload
systemctl --user start hermes-webui.service
```

### Vite bakes string literals into JS bundles
Vue components with hardcoded strings (e.g. `const productTitle = 'Hermes Studio'` in `ChatView.vue`) are compiled by Vite into minified JS at build time. Editing the `.vue` source file has **no effect** on the running server until `npm run build` is executed. Always verify the built `dist/client/assets/js/` bundle contains the corrected string, not just the source file.

**Detection:**
```bash
grep -o "productTitle.*Spock" dist/client/assets/js/ChatView-*.js \
  && echo "OK: Spock baked into ChatView bundle" \
  || echo "FAIL: ChatView bundle still says Hermes Studio"
```

### New upstream files may introduce hidden branding
Upstream releases sometimes add entirely new Vue components that set dynamic page titles or brand labels. These files do NOT trigger merge conflicts (they didn't exist in your local branch), so `git merge` silently adopts them. After `npm run build`, the upstream brand name appears in the UI even though `index.html` and `AppSidebar.vue` were preserved.

**The v0.6.11 `ChatView.vue` Dynamic Title Pitfall:**
`packages/client/src/views/hermes/ChatView.vue` was introduced in v0.6.11 with:
```typescript
const productTitle = 'Hermes Studio'
```
This string is baked into the minified JS bundle by Vite at build time. Even though `index.html` has `<title>Spock</title>`, the SPA overrides `document.title` dynamically when navigating to the Chat view. The only way to catch this is to grep the **built dist output**, not just source files.

**The v0.6.14 `DesktopTitleBar.vue` Pitfall:**
`packages/client/src/components/layout/DesktopTitleBar.vue` was introduced (or heavily revised) in v0.6.14 and hardcodes:
```html
<span class="desktop-titlebar__title">Hermes Studio</span>
```
It is bundled into `index-*.js` by Vite. It appears in the Electron/desktop title bar and is user-visible even when the browser tab title and sidebar say "Spock". Patch it before build.

**The v0.6.14 `MessageList.vue` Empty-State Pitfall:**
Upstream v0.6.14 refactored `MessageList.vue` to use a computed `emptyState` object. The default branch returns `alt: "Hermes"` for the empty-chat logo. Because the alt text is not a conflict marker (it's just a string literal), the merge auto-adopts the upstream value. Patch it to `alt: "Spock"` and verify in the built bundle.

**Detection (post-merge, pre-build):**
```bash
grep -rn "Hermes Studio" packages/client/src/ 2>/dev/null
grep -rn 'alt: "Hermes"' packages/client/src/components/hermes/chat/MessageList.vue 2>/dev/null
```

**Detection (post-build, critical):**
```bash
grep -o "productTitle.*Spock" dist/client/assets/js/ChatView-*.js \
  && echo "OK: Spock baked into ChatView bundle" \
  || echo "FAIL: ChatView bundle still says Hermes Studio"

grep -o "desktop-titlebar__title.*Spock" dist/client/assets/js/index-*.js \
  && echo "OK: Spock baked into desktop title bar bundle" \
  || echo "FAIL: desktop title bar still says Hermes Studio"
```

**Fix:**
```bash
sed -i "s/const productTitle = 'Hermes Studio'/const productTitle = 'Spock'/g" \
  packages/client/src/views/hermes/ChatView.vue
sed -i 's/<span class="desktop-titlebar__title">Hermes Studio<\/span>/<span class="desktop-titlebar__title">Spock<\/span>/g' \
  packages/client/src/components/layout/DesktopTitleBar.vue
npm run build
```

### Upstream may supersede a local customization with a better implementation
Before blindly re-applying an old local customization, check whether upstream has added an equivalent or better native feature. Example: v0.6.14 added per-session `reasoningEffort` with `NPopselect` and per-session `localStorage` persistence, superseding an earlier local global-default `NSelect` implementation. In that case adopt upstream's feature, remove the redundant local patch, and preserve any data/model customizations (e.g., `kimi-k2.7-code` provider entries) that upstream still lacks.

### Empty stashes accumulate after every `hermes update`
`hermes update` auto-stashes the working tree before `git pull` **even when there are no changes**. This leaves empty stash entries in the reflog (e.g. `stash@{0}: On main: hermes-update-autostash-20260521-122403`) that never get popped. Over time they clutter `git stash list`.

**Detection:**
```bash
git -C /home/thadd/hermes-agent-ui stash list
git -C /home/thadd/hermes-agent-ui stash show -p stash@{0}
# Blank output means the stash is empty
```

**Cleanup after confirming the stash is empty:**
```bash
# Drop one empty stash
git -C /home/thadd/hermes-agent-ui stash drop stash@{0}
# Or drop all stashes if they are all empty
```

Do not drop stashes blindly — always check if they have content first.

### `hermes update` timer should be generous
The `hermes update` command triggers `npm install` which produces hundreds of engine-check warnings that scroll for 30-60 seconds before the actual install finishes. A 60-second timeout on the shell command will cut it off mid-install and leave the repo in a half-upgraded state. Use at least 300 seconds.

### `hermes update` fails with "Python interpreter not found at venv/bin/python3"
The update command tries to reinstall the editable package inside the active venv. If the venv's Python interpreter has been removed or upgraded (e.g., system Python moved from 3.13 to 3.14), the update fails mid-install. See `references/hermes-core-update-with-webui.md` → "Pitfall: Venv points to a missing Python interpreter" for detection commands and the exact fix.

### Don't overthink "how does `hermes update` work"
When asked to "run hermes update," just run `hermes update` (or `hermes update --backup --yes`).
I spent time grepping `hermes_cli/main.py` and `hermes_cli/skills_hub.py`
looking for the update command implementation instead of executing it. The
user's intent was clear — get the update done, not reverse-engineer the CLI.

### Don't manually backup files that the update handles
`hermes update --backup --yes` already snapshots configs, SOUL.md, MEMORY.md,
and skins. Manual `cp` is redundant and can miss files (e.g. `.env` files
require different permissions). Trust `--backup` unless the user explicitly
asks for a custom backup path.

### The update command was paused, not abandoned
This session stalled mid-update after diagnosing the gateway shutdown. The
pre-update shutdown was complete (gateway and WebUI stopped) and the backup
was complete, but `hermes update` was never run. A future session should
resume from step 3 (`hermes update --backup --yes`) rather than re-doing step
1 (shutdown), which may interfere with a new gateway already running.

## Manual Steps (if script fails)

### 1. Logo

```bash
cp /mnt/c/Users/thadd/.hermes/images/logo.png /home/thadd/hermes-web-ui/packages/client/public/logo.png
cp /mnt/c/Users/thadd/.hermes/images/logo.png /home/thadd/hermes-web-ui/packages/client/src/assets/logo.png
cd /home/thadd/hermes-web-ui && ~/node26/bin/npm run build
```

### 2. Thinking Videos

```bash
cp /mnt/c/Users/thadd/.hermes/images/startrek\ badge.mp4 /home/thadd/hermes-web-ui/packages/client/src/assets/thinking-light.mp4
cp /mnt/c/Users/thadd/.hermes/images/startrek\ badge.mp4 /home/thadd/hermes-web-ui/packages/client/src/assets/thinking-dark.mp4
cd /home/thadd/hermes-web-ui && ~/node26/bin/npm run build
```

### 3. Verify dist

```bash
ls -la /home/thadd/hermes-web-ui/dist/client/logo.png
ls -la /home/thadd/hermes-web-ui/dist/client/assets/mp4/thinking-*.mp4
```

## Auth Token Path Fix

After updates, the server may look for `.token` in a different path. Check both:

```bash
echo "=== Active token ==="
cat ~/.hermes/webui/.token 2>/dev/null || echo "NOT FOUND at ~/.hermes/webui/.token"

echo "=== Legacy token ==="
cat ~/.hermes-web-ui/.token 2>/dev/null || echo "NOT FOUND at ~/.hermes-web-ui/.token"

echo "=== Launcher reads from ==="
grep -o '\.token' /mnt/c/Users/thadd/Desktop/Launch\ Hermes\ WebUI.bat 2>/dev/null || echo "Check .bat manually"
```

If they differ, sync them:

```bash
token=$(cat ~/.hermes/webui/.token)
echo "$token" > ~/.hermes-web-ui/.token
chmod 600 ~/.hermes-webui/.token ~/.hermes-web-ui/.token
```

## Post-Upgrade LLM Config Verification

**v0.6.4 changed API routes.** Old `/api/models` and `/api/providers` moved to `/api/hermes/...`. The client-side store (`app.ts`) already uses the new routes, but direct `curl` checks and any custom scripts must be updated.

| Old Route (pre-0.6.4) | New Route (0.6.4+) |
|---|---|
| `/api/models` | `/api/hermes/available-models` |
| `/api/providers` | `/api/hermes/config/providers` |

**Verify model config survived the upgrade:**

```bash
token=$(cat ~/.hermes/webui/.token)

# Check model config via new route
curl -sf http://localhost:8648/api/hermes/available-models \
  -H "Authorization: Bearer $token" | jq '{default: .default, default_provider: .default_provider}'

# Expected: {"default":"kimi-k2.6","default_provider":"ollama-cloud"}

# Also verify the source of truth — config.yaml on disk
grep -A2 "^model:" ~/.hermes/profiles/$(cat ~/.hermes/active_profile 2>/dev/null || echo default)/config.yaml
```

**If the model or provider was reset**, the WebUI settings panel is the safest place to re-select. The `models_cache.json` at `~/.hermes/webui/models_cache.json` is a cache — the real config lives in `~/.hermes/profiles/<profile>/config.yaml`.

**If missing, re-set via the WebUI settings panel or:**

```bash
token=$(cat ~/.hermes/webui/.token)
curl -sf http://localhost:8648/api/hermes/config/models \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d '{"default":"kimi-k2.6","provider":"ollama-cloud"}'
```

## Prevention: Post-Build Hook

Add to `package.json` > `scripts`:

```json
{
  "scripts": {
    "build": "vite build && npm run restore-customizations",
    "restore-customizations": "bash scripts/restore-customizations.sh"
  }
}
```

Then create `scripts/restore-customizations.sh`:

```bash
#!/bin/bash
# Runs AFTER vite build, copies custom assets into dist/
cp /mnt/c/Users/thadd/.hermes/images/logo.png dist/client/logo.png
cp /mnt/c/Users/thadd/.hermes/images/startrek\ badge.mp4 dist/client/assets/thinking-light.mp4
cp /mnt/c/Users/thadd/.hermes/images/startrek\ badge.mp4 dist/client/assets/thinking-dark.mp4
```

## Merge Conflict Danger: `AppSidebar.vue`

This file always conflicts during upstream merges because it contains Spock branding (`Spock` text, `alt="Spock"`) while upstream uses `Hermes`.

**The Pitfall (May 2026, v0.6.5 → v0.6.6):**
During an in-progress merge, using `git checkout --theirs packages/client/src/components/layout/AppSidebar.vue` triggers any `post-checkout` git hook. If the hook runs `git checkout HEAD -- AppSidebar.vue` to restore Spock branding, **HEAD is still the old pre-merge commit**, so the file is reverted to the old version — **not** the upstream v0.6.6 version. Adding and committing then embeds the old file into the merge, silently losing upstream navigation fixes (`RouteLinkItem`, `isStoredSuperAdmin`, route key mapping, etc.).

**Correct Resolution Sequence:**
1. After `git merge origin/main` produces a conflict in `AppSidebar.vue`:
2. **DO NOT use `--theirs`** (triggers the revert hook)
3. Instead, manually resolve the conflict markers:
   - Keep upstream's JavaScript/TypeScript logic (imports, computed properties, functions)
   - Keep upstream's template structure (nav items, new route links)
   - Only replace `alt="Hermes"` → `alt="Spock"` and `>Hermes<` → `>Spock<` in the logo section
4. Save, `git add`, `git merge --continue`
5. OR: rename the hook temporarily:
   ```bash
   mv .git/hooks/post-checkout .git/hooks/post-checkout.bak
   git checkout --theirs packages/client/src/components/layout/AppSidebar.vue
   mv .git/hooks/post-checkout.bak .git/hooks/post-checkout
   # Now manually rebrand: sed ...
   ```

**Post-Merge Feature Verification (greppable upstream features):**
```bash
grep "RouteLinkItem" packages/client/src/components/layout/AppSidebar.vue && echo "OK: RouteLinkItem present" || echo "FAIL: missing RouteLinkItem"
grep "isStoredSuperAdmin" packages/client/src/components/layout/AppSidebar.vue && echo "OK: isStoredSuperAdmin present" || echo "FAIL: missing isStoredSuperAdmin"
grep "usePersistentRecord" packages/client/src/components/layout/AppSidebar.vue && echo "OK: usePersistentRecord present" || echo "FAIL: missing usePersistentRecord"
grep "hermes.mcp" packages/client/src/components/layout/AppSidebar.vue && echo "OK: MCP nav present" || echo "FAIL: missing MCP nav"
```

## Verification Checklist (MANDATORY before declaring merge complete)

Run these checks **before** telling the user the update is done:

- [ ] **Check for hidden branding in new upstream files:**
  ```bash
  grep -rn "Hermes Studio" packages/client/src/ 2>/dev/null \
    && echo "WARNING: hidden branding found — patch before build" \
    || echo "OK: no hidden branding"
  ```
  New upstream files (like `ChatView.vue` in v0.6.11) do NOT trigger merge conflicts but contain upstream brand strings baked into JS bundles by Vite.

- [ ] **Check `MessageList.vue` imports `.mp4` not `.gif`:**
  ```bash
  grep -n "thinking.*\.gif" /home/thadd/hermes-web-ui/packages/client/src/components/hermes/chat/MessageList.vue \
    && echo "FAIL: .gif imports found" || echo "OK: no .gif"
  ```
  If this prints anything, STOP — fix `MessageList.vue` first (see "Post-Merge Asset Reference Corruption Check" below).

- [ ] **Verify LLM config survived the upgrade:**
  ```bash
  token=$(cat ~/.hermes/webui/.token)
  curl -sf http://localhost:8648/api/hermes/available-models \
    -H "Authorization: Bearer *** | jq '{default: .default, default_provider: .default_provider}'
  ```
  Expected: `{"default":"kimi-k2.6","default_provider":"ollama-cloud"}`. If wrong, the model/provider may have been reset — re-set via WebUI settings panel.

- [ ] **Check for orphaned WebUI databases after data directory migration:**
  ```bash
  find /home/thadd -name "hermes-web-ui.db" -type f 2>/dev/null | grep -v node_modules | grep -v .cache
  ```
  If more than one DB exists, use the automated tools:
  ```bash
  # Detection + merge + JSON sync + restart
  bash /home/thadd/.hermes/scripts/webui-recall-sessions.sh
  ```
  The legacy path `~/.hermes-web-ui/hermes-web-ui.db` and the current
  path `~/.hermes/webui/hermes-web-ui.db` are both checked automatically.
  See `references/webui-chat-recall-tool-guide.md` for full details.
  **If the old DB has sessions not in the current DB, merge them BEFORE the
  user notices their history is gone.**

- [ ] `dist/client/index.html` contains `<title>Spock</title>` and the boot fallback uses `/logo.png`
- [ ] `dist/client/assets/js/ChatView-*.js` contains `Spock` not `Hermes Studio`
- [ ] `dist/client/assets/js/index-*.js` contains `desktop-titlebar__title.*Spock` (no `Hermes Studio` in desktop title bar)
- [ ] `dist/client/assets/js/index-*.js` contains `logo-img` with `alt:"Spock"` (AppSidebar branding)
- [ ] `dist/client/assets/js/MessageList-*.js` (or `index-*.js` if inlined) uses `.mp4` for thinking video, not `.gif`
- [ ] `dist/client/logo.png` exists and is your logo
- [ ] `dist/client/assets/mp4/thinking-*.mp4` exists and is your video
- [ ] `dist/client/assets/` does NOT contain `thinking-*.gif` (upstream may have replaced .mp4 with .gif)
- [ ] `~/.hermes/webui/.token` matches launcher read path
- [ ] Server restarted **with `NODE_ENV=production`**
- [ ] Server restarted with `HERMES_AGENT_BRIDGE_PYTHON` set to Hermes venv Python
- [ ] Login works with existing credentials (not silently using empty dev DB)
- [ ] Health check shows `webui_update_available: false`
  ```bash
  curl -sf http://127.0.0.1:8648/health | grep '"webui_update_available":false'
  ```
  **If true:** The local build is ahead of the npm published version (e.g. `0.6.6` local vs `0.6.5` on npm). Restart the server with `HERMES_WEB_UI_DISABLE_UPDATE_CHECK=true` to suppress the banner. The comparison is `!==`, not `<`, so newer local versions still trigger it.

## Post-Merge Asset Reference Corruption Check

After merging upstream WebUI updates, **git may not flag conflicts** even though upstream changed asset imports in Vue components. The merge auto-adopts upstream imports, replacing your custom `.mp4` with upstream `.gif` files.

**Files to verify after every upstream merge:**

```bash
`/home/thadd/hermes-web-ui`

# Check MessageList.vue imports — upstream may have switched .mp4 → .gif
grep -n "thinking.*\.gif" packages/client/src/components/hermes/chat/MessageList.vue \
  && echo "WARNING: .gif imports detected — need to restore .mp4" \
  || echo "OK: no .gif imports"

# Check for any remaining .gif thinking references anywhere
grep -rn "thinking.*\.gif" packages/client/src/ 2>/dev/null \
  && echo "WARNING: .gif references found in source" \
  || echo "OK: source is clean"
```

**If `.gif` imports are found**, patch `MessageList.vue`:

```bash
# Replace .gif imports with .mp4
sed -i 's/thinking-light\.gif/thinking-light.mp4/g' packages/client/src/components/hermes/chat/MessageList.vue
sed -i 's/thinking-dark\.gif/thinking-dark.mp4/g' packages/client/src/components/hermes/chat/MessageList.vue

# Replace <img> with <video> element
sed -i 's/<img$/<video/g' packages/client/src/components/hermes/chat/MessageList.vue
sed -i 's/alt=""//g' packages/client/src/components/hermes/chat/MessageList.vue
sed -i 's/class="thinking-video">/class="thinking-video"\n          autoplay\n          loop\n          muted\n          playsinline\n        \/>/g' packages/client/src/components/hermes/chat/MessageList.vue
```

**Better: use the exact patch from this session:**

In `packages/client/src/components/hermes/chat/MessageList.vue`:
1. Change imports:
   ```typescript
   import thinkingImageLight from "@/assets/thinking-light.mp4";
   import thinkingImageDark from "@/assets/thinking-dark.mp4";
   ```
2. Change `<img>` to `<video>`:
   ```html
   <video
     :src="isDark ? thinkingImageDark : thinkingImageLight"
     autoplay
     loop
     muted
     playsinline
     aria-hidden="true"
     class="thinking-video"
   />
   ```

Then rebuild:
```bash
cd /home/thadd/hermes-web-ui && ~/node26/bin/npm run build
```

**Verify dist has only .mp4:**
```bash
find dist/client/assets -name "thinking-*.gif" -type f 2>/dev/null \
  && echo "FAIL: .gif in dist" || echo "OK: no .gif in dist"
find dist/client/assets -name "thinking-*.mp4" -type f 2>/dev/null \
  && echo "OK: .mp4 in dist" || echo "FAIL: no .mp4 in dist"
```

## The `_index.json` Session List Problem

After updating the WebUI or migrating data between databases, the sidebar session list may appear empty or incomplete even though the database contains all sessions. This happens because the WebUI maintains **two separate session sources**:

| Source | What it stores | Where it lives |
|---|---|---|
| `_index.json` | Session list for the WebUI sidebar | `~/.hermes/webui/sessions/_index.json` |
| SQLite DB | Full session metadata + messages | `~/.hermes/webui/hermes-web-ui.db` |

The WebUI's `/api/sessions` endpoint primarily reads from `_index.json`. CLI sessions (source=cli) are stored in the SQLite DB but **will not appear** in the sidebar unless `_index.json` is synced or `show_cli_sessions` is enabled.

**Detection:**
```bash
# Check JSON index entries
python3 -c "import json; data=json.load(open('/home/thadd/.hermes/webui/sessions/_index.json')); print(len(data), 'sessions in _index.json')"

# Check DB entries
python3 -c "import sqlite3; conn=sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db'); c=conn.cursor(); c.execute('SELECT COUNT(*) FROM sessions'); print(c.fetchone()[0], 'sessions in DB'); conn.close()"
```
If the numbers differ significantly, the `_index.json` is stale.

**Fix Option 1 — Enable CLI session display (fastest):**
See the `Post-Update Server Start` section for the `settings.json` snippet.

**Fix Option 2 — Rebuild `_index.json` from DB:**
Use the standalone `webui-db-sync.py` script instead of inline Python:

```bash
# Stop server first
systemctl --user stop hermes-webui.service

# Sync DB sessions into JSON files + _index.json
python3 /home/thadd/.hermes/profiles/plc-coder/scripts/webui-db-sync.py

# Restart server
systemctl --user start hermes-webui.service
```

For full documentation, including the `webui-chat-recall.py` merge tool,
see `references/webui-chat-recall-tool-guide.md`.

### When to use each fix
- **Settings fix (Option 1):** Use when the session data is already in the DB (after DB merge) and you just need CLI sessions to be visible. No restart required.
- **Index rebuild (Option 2):** Use when `_index.json` is corrupted, empty, or out of sync with the DB. Requires server restart.

## Post-Update Server Start

**Always use `NODE_ENV=production`** when starting after updates, and **set `HERMES_AGENT_BRIDGE_PYTHON`** to the Hermes venv Python (required for `openai`, `websockets`, and other bridge dependencies).

Also set **`HERMES_WEB_UI_DISABLE_UPDATE_CHECK=true`** to suppress the "update available" banner. This is required when your local build is merged from upstream `main` ahead of the last npm publish — the server fetches the npm registry version (e.g. `0.6.5`) and compares it to your local version (e.g. `0.6.6`). Since `0.6.5 !== 0.6.6`, the banner fires constantly. The env var disables the check entirely.

```bash
pkill -f "node.*dist/server/index.js" || true; sleep 2

unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export PORT=8648
export BIND_HOST=0.0.0.0
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export HERMES_WEB_UI_DISABLE_UPDATE_CHECK=true
export WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace

cd /home/thadd/hermes-web-ui
/home/thadd/node26/bin/node dist/server/index.js \
  >> /home/thadd/.hermes/webui/logs/server.log 2>&1 &

sleep 3
curl -sf http://127.0.0.1:8648/health && echo "Server UP"
```

**Without `NODE_ENV=production`:**
- Server creates a new dev DB at `cwd/packages/server/data/hermes-web-ui.db`
- Your user accounts are NOT migrated
- Login fails because the `users` table is empty
- `.login-lock.json` is created in the wrong location

If you already started without production mode:
1. Stop the server (`pkill -f "node.*dist/server/index.js"`)
2. Clear the wrong DB (optional): `rm /home/thadd/packages/server/data/hermes-web-ui.db`
3. Restart with `NODE_ENV=production`
4. If login still fails, check `references/auth-troubleshooting.md` in the `hermes-web-ui` skill

## Critical: `AUTH_DISABLED` Inheritance Bug

**The Problem (May 2026):**
After a WebUI update, the login page refused all passwords even though the correct credentials were stored in the production DB (`~/.hermes/webui/hermes-web-ui.db`). Additionally, new chat sessions failed with:

```
Error: Failed to initialize OpenAI client: No module named 'openai'
```

The root cause was **two separate environment issues** that combined to disable auth and break the agent bridge:

### 1. `AUTH_DISABLED` Inherited from Parent Shell

The server was launched from a shell that had `AUTH_DISABLED` set (either from a `.bashrc` export, a Desktop launcher `.bat`, or a previous session). When `packages/server/src/services/auth.ts:18` checks for this env var, **any value** (even `0` or `false`) disables username/password auth and returns `"Auth is disabled on this server"`.

**Detection:**
```bash
# Check if AUTH_DISABLED is present in the server's environment
grep -a AUTH_DISABLED /proc/$(pgrep -f "node.*dist/server/index.js")/environ 2>/dev/null | tr '\0' '\n'

# Or check the active login response
curl -sf http://127.0.0.1:8648/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq -r '.message // .error'
# If it says "Auth is disabled on this server", this is the bug
```

**Fix:**
```bash
# Stop the server
pkill -f "node.*dist/server/index.js" || true; sleep 2

# Unset AUTH_DISABLED explicitly (just in case)
unset AUTH_DISABLED

# Restart with NODE_ENV=production AND no AUTH_DISABLED
`/home/thadd/hermes-web-ui`
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export PORT=8648
export BIND_HOST=0.0.0.0
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
/home/thadd/node26/bin/node dist/server/index.js
```

### 2. Server Running Without `NODE_ENV=production`

When the server starts without `NODE_ENV=production` (see Post-Update Server Start section above), it uses a dev DB at `packages/server/data/hermes-web-ui.db` instead of `~/.hermes/webui/hermes-web-ui.db`. The dev DB has an empty `users` table, so every login attempt fails and creates `.login-lock.json` in the wrong location.

**Detection:**
```bash
# Check which DB the server is actually using
lsof -p $(pgrep -f "node.*dist/server/index.js") | grep -i "\.db"
# If it shows packages/server/data/hermes-web-ui.db, it's in dev mode
```

**Fix:**
```bash
# Stop the server
pkill -f "node.*dist/server/index.js" || true; sleep 2

# Clear the lock file that may have been created in the wrong location
rm -f /home/thadd/packages/server/data/.login-lock.json
rm -f /home/thadd/.hermes/webui/.login-lock.json

# Optionally clear the dev DB so it can't confuse things later
rm -f /home/thadd/packages/server/data/hermes-web-ui.db

# Restart with NODE_ENV=production
`/home/thadd/hermes-web-ui`
unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
/home/thadd/node26/bin/node dist/server/index.js

# Verify login works
curl -sf http://127.0.0.1:8648/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"AntiSyStem","password":"AllisfairinWarandLove"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('token') else d.get('error','fail'))"
```

### Prevention Checklist

Before launching the server after any update:

- [ ] `echo $AUTH_DISABLED` — must print nothing (not `0`, not `false`, not empty string)
- [ ] `echo $NODE_ENV` — must print `production`
- [ ] `ls -la ~/.hermes/webui/hermes-web-ui.db` — must exist and be non-empty
- [ ] `ls -la packages/server/data/hermes-web-ui.db` — should NOT exist (or is a stale dev DB)
- [ ] `echo $HERMES_AGENT_BRIDGE_PYTHON` — must point to a Python that has `openai`, `websockets`, etc. installed (typically `/home/thadd/hermes-agent-ui/venv/bin/python3`)

### Permanent Fix: Launcher Scripts

Update your Desktop launchers to explicitly unset `AUTH_DISABLED`:

**`Launch Hermes WebUI.bat` (Windows):**
```batch
@echo off
REM Force auth enabled and production mode
set AUTH_DISABLED=
set NODE_ENV=production
set HERMES_WEB_UI_HOME=C:\Users\thadd\.hermes\webui
set PORT=8648

REM Use WSL to start the server
wsl -d Ubuntu-22.04 -e bash -lic "unset AUTH_DISABLED; export NODE_ENV=production; export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui; export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3; cd /home/thadd/hermes-web-ui-ekko && /home/thadd/node26/bin/node dist/server/index.js"
```

**Linux/WSL shortcut:**
```bash
#!/bin/bash
# Save as ~/bin/start-webui.sh
unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export PORT=8648
export BIND_HOST=0.0.0.0

`/home/thadd/hermes-web-ui`
exec /home/thadd/node26/bin/node dist/server/index.js
```

The `unset AUTH_DISABLED` is critical because parent shells (especially if you previously ran the server with auth disabled for debugging) may leak this variable into child processes.

## Bridge Python Module Errors

**Symptoms in server logs:**
```
Failed to initialize OpenAI client: No module named 'openai'
No module named 'websockets'
```

**Root cause:** The WebUI agent bridge spawns Python subprocesses. By default it uses `sys.executable` from the broker process. If the broker is launched with system `python3` (`/usr/bin/python3`), workers inherit that interpreter, which lacks the `openai`, `websockets`, and other packages installed in the Hermes venv.

**Detection:**
```bash
# Check what Python the bridge broker is using
ps aux | grep -E "hermes_bridge.*endpoint" | grep -v grep
# If it shows /usr/bin/python3 or /usr/bin/env python3, it's wrong

# Check what Python workers use after a chat starts
ps aux | grep -E "hermes_bridge.*worker" | grep -v grep
```

**Fix:**
```bash
# Stop the server
pkill -f "node.*dist/server/index.js" || true; sleep 2

# Restart with explicit bridge Python path
`/home/thadd/hermes-web-ui`
unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export PORT=8648
export BIND_HOST=0.0.0.0
/home/thadd/node26/bin/node dist/server/index.js
```

**Verify:**
```bash
# After starting a chat, check worker Python path
ps aux | grep -E "hermes_bridge.*worker" | grep -v grep
# Should show: /home/thadd/hermes-agent-ui/venv/bin/python3

# Verify openai is importable in that interpreter
/home/thadd/hermes-agent-ui/venv/bin/python3 -c "import openai; print('openai', openai.__version__)"
```

**Prevention:** Always include `HERMES_AGENT_BRIDGE_PYTHON` in the server start environment. The WebUI update process (`npm run build`) does not preserve or validate this path.

## Profile Switching in WebUI

**Problem:** Selecting a different profile from the WebUI sidebar dropdown does **not** change the profile of the currently open session. The existing session continues to run under its original profile.

**Symptoms:**
- You select `plc-coder` from the dropdown
- Agent responds with wrong persona (`devteam`)  
- Bridge worker logs show `[hermes-bridge-worker:devteam]` instead of `[hermes-bridge-worker:plc-coder]`
- Agent says "I am running under the devteam profile"

**Root cause:** The WebUI stores `profile` per-session in `hermes-web-ui.db`. The dropdown only affects **new sessions**.

**Detection — check DB:**
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
c = conn.cursor()
c.execute('SELECT id, profile, title, started_at FROM sessions ORDER BY started_at DESC LIMIT 5')
for row in c.fetchall():
    print(f'{row[0]} | profile: {row[1] or \"default\"} | {row[2]}')
conn.close()
"
```
If the active session shows `profile: devteam` (or any profile other than what the dropdown shows), that's the mismatch.

**Detection — check bridge worker logs:**
```bash
tail -20 /home/thadd/.hermes/webui/logs/server.log | grep "bridge-worker"
# Look for: [hermes-bridge-worker:devteam] vs [hermes-bridge-worker:plc-coder]
```

**Fix Option 1 — Start New Chat (Recommended):**
1. Select desired profile from dropdown **first**
2. Click **"New Chat"**
3. This creates a session with the selected profile
4. Bridge spawns a new worker with correct profile

**Fix Option 2 — Update DB directly (preserve session history):**
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
c = conn.cursor()
# Update specific session
c.execute(\"UPDATE sessions SET profile = 'plc-coder' WHERE id = 'YOUR_SESSION_ID'\")
# Or update all sessions for a profile
c.execute(\"UPDATE sessions SET profile = 'plc-coder' WHERE profile = 'devteam'\")
conn.commit()
print(f'Updated {c.rowcount} session(s)')
conn.close()
"
```

**Caveat:** Updating the DB only fixes the session record. The currently running bridge worker will still be the old profile until a new chat spawns a new worker.

**Fix Option 3 — Restart server + new chat (if worker stuck):**
```bash
pkill -f "node.*dist/server/index.js" || true; sleep 2
unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
cd /home/thadd/hermes-web-ui-ekko && /home/thadd/node26/bin/node dist/server/index.js
# Then in WebUI: select correct profile → New Chat
```

**Prevention workflow:**
1. Select profile from dropdown **first**
2. Then click **"New Chat"**
3. Verify agent responds with correct persona

**Full reference:** See `references/profile-switching-workaround.md`

- **`references/local-ollama-provider-setup.md`** — Step-by-step for making a local Ollama server (`http://127.0.0.1:11434`) visible in the WebUI model dropdown. Covers all three server-side registries (PROVIDER_PRESETS, PROVIDER_ENV_MAP, auth exemptions) plus live model fetching and local model installation.

- **`references/upstream-merge-v0.6.14.md`** — Notes from merging upstream v0.6.11 → v0.6.14. New branding surfaces: `DesktopTitleBar.vue`, `MessageList.vue` empty-state alt. Reasoning-effort feature became native in upstream, so local patch was dropped. `.gif` thinking assets removed in favor of `.mp4` Star Trek badge. Provider presets kept `kimi-k2.7-code` entries.

## Session References

- **`references/pre-update-system-prep.md`** — Stop gateway and WebUI before performing Hermes core or WebUI updates. Covers the Telegram token conflict that happens when a stale gateway process holds the token while a new one attempts to connect. Includes cron-watchdog pause instructions.
- **`references/upstream-merge-v0.6.7.md`** — Notes from merging upstream v0.6.7. The "stash pop fails" pattern: when upstream does NOT reintroduce `RouteLinkItem` or `is="a"`, the working tree already contains the Spock customizations and the stash is redundant — just drop it. No manual conflict resolution needed for this 5-commit release.
- **`references/hermes-core-update-with-webui.md`** — How to update the Hermes CLI core (`hermes update --backup --yes`) without touching the WebUI. Covers profile export, gateway kill, auto-stash rollback, venv path verification, and WebUI server restart to pick up the new version string.
- **`references/upstream-merge-0.6.3.md`** — Notes from merging upstream 0.6.3 while preserving Spock branding and auth enforcement. Includes commit-by-commit breakdown, conflict resolution for `AppSidebar.vue`, and post-merge verification checklist.
- **`references/upstream-merge-0.6.4.md`** — Notes from merging upstream 0.6.4. Same conflict pattern in `AppSidebar.vue`, same `.gif` → `.mp4` asset corruption in `MessageList.vue`. Build time ~4 minutes. Server env requirements unchanged.
- **`references/webui-model-switch-workflow.md`** — End-to-end workflow for switching the default LLM model (e.g., `kimi-k2.6:cloud` → `kimi-k2.7-code:cloud`). Covers profile config, provider presets (`packages/server/src/shared/providers.ts`), WebUI session DB updates, and agent core context metadata (`agent/model_metadata.py`). Includes format mismatch pitfalls (`:cloud` suffix, `moonshotai/` prefix) and verification commands.
- **`references/upstream-merge-v0.6.11.md`** — Notes from merging upstream v0.6.4 → v0.6.11. Clean 2-conflict merge (both branding files). New finding: `ChatView.vue` introduced dynamic `productTitle = 'Hermes Studio'` baked into JS bundle by Vite — requires source patch + rebuild. Service `WorkingDirectory` corrected from stale Windows path to active WSL repo. All 66 customization files survived.
- **`references/webui-db-migration-data-loss-prevention.md`** — Complete guide to detecting and recovering from WebUI database directory migrations that cause chat history to appear lost. Covers the `~/.hermes-web-ui/` → `~/.hermes/webui/` transition, session comparison scripts, message ID renumbering during merge, and prevention steps (DB snapshots before updates, launcher script sync, post-update verification).
- **`references/webui-server-diagnostics.md`** — Quick commands to verify the WebUI server is actually healthy (not just `active (running)`). Covers `curl -v` health checks, `lsof` DB detection, `journalctl` for internal crashes, and log file descriptor mapping under systemd.
- **`references/webui-reasoning-config-system.md`** — Full end-to-end architecture for adding a per-chat reasoning depth slider. Traces the path from `ChatInput.vue` → `chat.ts` store → Socket.IO → `handle-bridge-run.ts` → agent bridge → `run_agent.py` → provider transport. Includes provider-specific mappings (OpenAI, Anthropic, Gemini, Codex) and the current limitation that reasoning config is read once from `config.yaml` at bridge startup.