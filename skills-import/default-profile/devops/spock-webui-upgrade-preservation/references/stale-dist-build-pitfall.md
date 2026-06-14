# Stale dist/ Build After Avatar Fix — Session Reference (2026-05-22)

## What Happened

After fixing `SessionListItem.vue` to pass `{type:'image',dataUrl:'/spock-avatar.png'}` to the `ProfileAvatar` component, the browser still displayed a generic anime multiavatar character in both:
- The sidebar session list (small green-circle avatar next to profile name)
- The message bubble header (larger avatar next to "Thinking - N characters")

## Root Cause

The WebUI server serves **compiled** `dist/client/` assets — not the source `.vue` files. The `dist/` was built at 04:14, **before** the avatar fix commit `6146e90` (05:56). In that stale build:

- `SessionListItem.vue` compiled to code that still fetched `profilesStore.profiles.find(...)?.avatar`
- The backend's `default` profile had no custom avatar set
- `ProfileAvatar` fell back to `multiavatar('default')` → generated a generic anime character with spiky blonde hair on green background

The `spock-avatar.png` file was correct on disk (verified via vision analysis), and the source code at HEAD was correct. But the server delivered old compiled JS.

## Detection

```bash
# Check dist/ build timestamp vs latest Spock commit
ls -la /mnt/c/Users/thadd/hermes-web-ui/dist/client/index.html
git log --oneline -3
# If dist is older than the avatar fix commit, it's stale

# Verify the compiled JS still references multiavatar fallback
grep -o "multiavatar\|profileAvatar.*computed.*'/spock'" \
  /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/js/OutlinePanel-*.js
# Empty result = old build has been replaced; match found = still stale
```

## Fix

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
npm run build
```

If build succeeds, verify:
```bash
# dist/server/index.js must exist and be non-empty
ls -la dist/server/index.js
# favicon.ico must be Spock (not old default)
file dist/client/favicon.ico
# spock-avatar.png must exist in dist/client/
ls dist/client/spock-avatar.png
```

Then restart:
```bash
systemctl --user restart hermes-webui
```

## Build Timeout Pitfall

When `npm run build` timed out (120s), `dist/server/` was cleaned at build start but never repopulated. The server failed to start with:
```
Error: Cannot find module '/mnt/c/Users/thadd/hermes-web-ui/dist/server/index.js'
```

**Recovery:** Restore server from backup:
```bash
rsync -avh /mnt/c/Users/thadd/Documents/SpockWebUI/dist/server/ \
  /mnt/c/Users/thadd/hermes-web-ui/dist/server/
```

The `Documents/SpockWebUI` backup always contains the last working `dist/server/`.

## ProfileAvatar Component — Universal Spock Fix

The upstream `ProfileAvatar.vue` renders `<img>` only when the `:avatar` prop is an **object** with `type === 'image'` and a truthy `dataUrl`. If no avatar is passed or it's null/undefined, it falls back to `multiavatar(seed)` generating a generic anime character.

**Old approach (SessionListItem.vue only):**
```js
const profileAvatar = computed(() => ({ type: 'image' as const, dataUrl: '/spock-avatar.png' }))
// Only fixes the session list; MessageItem, GroupChat, Kanban, ProfileSelector still show anime
```

**New approach (ProfileAvatar.vue — fixes ALL avatars everywhere):**
Edit `packages/client/src/components/hermes/profiles/ProfileAvatar.vue`:
```vue
<script setup lang="ts">
import { computed } from 'vue'
import type { ProfileAvatar } from '@/api/hermes/profiles'

const props = withDefaults(defineProps<{
  name: string
  avatar?: ProfileAvatar | null
  size?: number
}>(), {
  size: 24,
})

const style = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  flexBasis: `${props.size}px`,
}))
</script>

<template>
  <span class="profile-avatar-view" :style="style">
    <img
      v-if="avatar?.type === 'image' && avatar.dataUrl"
      class="profile-avatar-image"
      :src="avatar.dataUrl"
      alt=""
      draggable="false"
    >
    <img
      v-else
      class="profile-avatar-image"
      src="/spock-avatar.png"
      alt=""
      draggable="false"
    >
  </span>
</template>
```

**What this fixes:**
- Session list avatars (sidebar) ✓
- Message bubble avatars (chat) ✓
- Group chat avatars ✓
- Profile selector avatars ✓
- Kanban task card assignee avatars ✓
- Profile modal avatars ✓
- Any future component using ProfileAvatar ✓

**Remove multiavatar import** — the `@multiavatar/multiavatar` dependency import and `generatedSvg` computed are no longer needed.

## ProfileAvatar Component Contract

The upstream `ProfileAvatar.vue` ONLY renders `<img>` when the `:avatar` prop is an **object** with `type === 'image'` and a truthy `dataUrl`. A plain string causes multiavatar SVG fallback.

**Correct:**
```js
const profileAvatar = computed(() => ({ type: 'image' as const, dataUrl: '/spock-avatar.png' }))
```

**Wrong (fallback to anime):**
```js
const profileAvatar = computed(() => '/spock-avatar.png')
```

## favicon.ico Specifics

`index.html` references `/favicon.ico`, not `/favicon.png`. The old `.ico` file (May 19, 16KB, 64x64 default icon) was still being served despite `favicon.png` being present.

**Fix:** Convert `spock-avatar.png` to multi-resolution `.ico` (16/32/64/128px) using Pillow, replace both `packages/client/public/favicon.ico` and `dist/client/favicon.ico`, and add to Spock Protector registry.

## Key Lesson

**Always verify the dist/ build timestamp after any source code change.** Source correctness does not guarantee the running server is serving it. The `npm run build` step is mandatory for client-side changes to take effect.

## Spock Guardian Audit — 2026-05-22

**Critical flaws found and fixed in the protection mechanisms:**

### ❌ OLD: Stale SPOCK_COMMIT
- **Was:** `6146e90` (avatar fix only, did not contain ProfileAvatar.vue or favicon.ico changes)
- **Should be:** `f636b1b` (original rebrand commit, contains title/logo/sidebar, still has all files in history)
- **Problem:** If upstream changed `ProfileAvatar.vue` after `6146e90`, the hooks would restore an even older version that still had multiavatar. The hooks would silently "succeed" but produce the wrong code.
- **Fix:** Changed hooks and `restore-spock.sh` to use `f636b1b`. This commit contains all Spock customizations in its tree, so `git checkout f636b1b -- <file>` always gets the Spock-branded version.

### ❌ OLD: Missing `favicon.ico` from protection
- **Was:** Only `favicon.png` listed, but `index.html` references `/favicon.ico`
- **Problem:** Browser tab showed old default icon despite Spock PNG being present
- **Fix:** Added `packages/client/public/favicon.ico` to hooks, PROTECTED_FILES.txt, and restore-spock.sh

### ❌ OLD: Missing `ProfileAvatar.vue` from hooks
- **Was:** Hooks only restored `SessionListItem.vue`, not the universal avatar component
- **Problem:** MessageItem, GroupChat, Kanban, ProfileSelector still showed anime after upgrade
- **Fix:** Added `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` to all three mechanisms

### ❌ OLD: Missing `spock-avatar.png` from restore-spock.sh
- **Was:** restore-spock.sh only restored compiled/structural files, not the image asset itself
- **Problem:** If asset was deleted, rebuild would fail to include the Spock image
- **Fix:** Added `packages/client/public/spock-avatar.png`, `favicon.ico`, `favicon.png` to restore-spock.sh FILES array

### ❌ OLD: Missing `SessionListItem.vue` from restore-spock.sh
- **Was:** restore-spock.sh had ProfileAvatar.vue but not SessionListItem.vue
- **Problem:** Session list avatar object format could revert to string
- **Fix:** Added `packages/client/src/components/hermes/chat/SessionListItem.vue` to restore-spock.sh

### ❌ OLD: No file backup in hooks
- **Was:** Hooks used `git diff --quiet` + `git checkout` only
- **Problem:** If Spock commit hash changed or the commit was garbage-collected, hooks would fail silently
- **Fix:** Hooks now restore from `~/.hermes/spock-protector/` file backups FIRST (authoritative), then do `git checkout` for clean git state

### ❌ OLD: Broken hook logic (`git diff --quiet`)
- **Was:** `if ! git diff --quiet "$SPOCK_COMMIT" -- "$file"` — only restores if file DIFFERS from the commit
- **Problem:** If upstream made the SAME change (e.g., both upstream and Spock changed a line), `git diff` returns clean and the hook skips restoration, leaving upstream changes intact
- **Fix:** Removed the conditional check. Now always copies from backup + always runs `git checkout` (idempotent, no harm if already correct)

### ❌ OLD: Duplicate `favicon.png` in hooks
- **Was:** `favicon.png` appeared TWICE in the PROTECTED_FILES array
- **Problem:** Wasted iteration, confusing to read
- **Fix:** Replaced duplicate with `favicon.ico`

### Current State (verified 2026-05-22)
All mechanisms now correctly protect 16 files with **file backup as authoritative source**:
- `packages/client/public/spock-avatar.png` (image asset)
- `packages/client/public/favicon.ico` (tab icon)
- `packages/client/public/favicon.png` (PNG backup)
- `packages/client/index.html` (title + favicon ref)
- `packages/client/public/logo.png` (main logo)
- `packages/client/src/assets/logo.png` (sidebar logo)
- `packages/client/src/assets/thinking-dark.mp4` (thinking video)
- `packages/client/src/assets/thinking-light.mp4` (thinking video)
- `packages/client/src/components/layout/AppSidebar.vue` (sidebar text)
- `packages/client/src/components/hermes/chat/SessionListItem.vue` (avatar object)
- `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` (universal avatar)
- `vite.config.website.ts` (build config)

**CRITICAL FIX APPLIED 2026-05-22:** All three mechanisms (restore-spock.sh, post-checkout, post-merge) now use file backup as authoritative and git checkout as fallback only. Previously, git checkout overwrote post-fix versions with pre-fix versions from the stale `f636b1b` commit, silently reintroducing the multiavatar bug every time the hooks ran.

See `references/guardian-hook-backup-order-bug.md` for the full forensic analysis.

### Post-Upgrade Verification Checklist
After ANY future upgrade (`git pull`, `hermes-webui update`, etc.), run:
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
echo "=== HOOK VERIFICATION ==="
bash .git/hooks/post-checkout  # manually trigger restoration
echo "=== FILE CHECKS ==="
grep -q "spock-avatar.png" packages/client/src/components/hermes/profiles/ProfileAvatar.vue && echo "✓ ProfileAvatar.vue" || echo "✗ ProfileAvatar.vue MISSING SPOCK"
grep -q "spock-avatar.png" packages/client/src/components/hermes/chat/SessionListItem.vue && echo "✓ SessionListItem.vue" || echo "✗ SessionListItem.vue MISSING SPOCK"
grep -q "spock" packages/client/src/components/layout/AppSidebar.vue && echo "✓ AppSidebar.vue" || echo "✗ AppSidebar.vue MISSING SPOCK"
grep -q "Spock" packages/client/index.html && echo "✓ index.html" || echo "✗ index.html MISSING SPOCK"
ls packages/client/public/spock-avatar.png && echo "✓ spock-avatar.png" || echo "✗ spock-avatar.png MISSING"
ls packages/client/public/favicon.ico && echo "✓ favicon.ico" || echo "✗ favicon.ico MISSING"
echo "=== DIST CHECKS ==="
[ -f dist/client/spock-avatar.png ] && echo "✓ dist/spock-avatar.png" || echo "✗ dist/spock-avatar.png MISSING"
[ -f dist/client/favicon.ico ] && echo "✓ dist/favicon.ico" || echo "✗ dist/favicon.ico MISSING"
[ -f dist/server/index.js ] && echo "✓ dist/server/index.js" || echo "✗ dist/server/index.js MISSING"
echo "=== REBUILD ==="
npm run build 2>&1 | tail -3
systemctl --user restart hermes-webui
```

### If Something Still Breaks After Upgrade
1. Run `bash ~/.hermes/spock-protector/restore-spock.sh --force-build`
2. Hard-refresh browser (`Ctrl+Shift+R`)
3. Check `dist/` timestamp: `ls -la dist/client/index.html`
4. If avatar is still anime, the dist/ is stale — rebuild again
5. If all else fails, restore from `C:\Users\thadd\Documents\SpockWebUI` backup
