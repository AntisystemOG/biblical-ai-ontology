# Spock Guardian Protection Mechanism Audit — 2026-05-22

## Trigger
After `hermes-webui update` to `0.5.34`, anime multiavatar characters appeared in place of Spock avatars in the sidebar session list and message bubble headers. The user requested a full root-cause audit of every protection mechanism to prevent recurrence.

## Audit Methodology
Do not read files and assume they work — **test every mechanism end-to-end**. Simulated upstream overwrite of protected files, then ran `restore-spock.sh`, then verified restoration.

## Critical Flaws Found and Fixed

### 1. Stale SPOCK_COMMIT in hooks
- **Was:** `6146e90` (avatar fix only, missing `ProfileAvatar.vue` and `favicon.ico` changes)
- **Problem:** If upstream changed `ProfileAvatar.vue` after `6146e90`, hooks would restore an older version still containing multiavatar fallback
- **Fix:** Changed to `f636b1b` (original rebrand commit, contains all Spock customizations in its tree)
- **Testing:** Confirmed `git show f636b1b:packages/client/src/components/hermes/profiles/ProfileAvatar.vue` returns the Spock-branded version

### 2. Missing `favicon.ico` from all protection layers
- **Was:** Only `favicon.png` listed (appeared TWICE in hooks as a duplicate)
- **Problem:** `index.html` references `/favicon.ico`, so browser showed old default icon despite Spock PNG existing
- **Fix:** Added `packages/client/public/favicon.ico` to hooks, `PROTECTED_FILES.txt`, and `restore-spock.sh`

### 3. Missing `ProfileAvatar.vue` from hooks
- **Was:** Hooks only restored `SessionListItem.vue`, not the component that actually renders avatars
- **Problem:** MessageItem, GroupChat, Kanban, ProfileSelector still showed anime after upgrade
- **Fix:** Added `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` to all three mechanisms

### 4. Missing assets from `restore-spock.sh`
- **Was:** Script only restored structural files, not `spock-avatar.png` or `favicon.ico`
- **Problem:** If image assets were deleted, rebuild would fail to include the Spock image
- **Fix:** Added `spock-avatar.png`, `favicon.ico`, `favicon.png` to `restore-spock.sh` FILES array

### 5. Missing `SessionListItem.vue` from `restore-spock.sh`
- **Was:** Script had `ProfileAvatar.vue` but not `SessionListItem.vue`
- **Problem:** Session list avatar object format (`{type:'image',dataUrl:'/spock-avatar.png'}`) could revert to plain string
- **Fix:** Added `packages/client/src/components/hermes/chat/SessionListItem.vue`

### 6. No file backups in hooks (git-only dependency)
- **Was:** Hooks used `git diff --quiet` + `git checkout` only
- **Problem:** If the Spock commit was garbage-collected or rebased away, hooks would silently fail
- **Fix:** Hooks now restore from `~/.hermes/spock-protector/` file backups FIRST (authoritative), then do `git checkout` for clean git state

### 7. Broken hook logic (`git diff --quiet`)
- **Was:** `if ! git diff --quiet "$SPOCK_COMMIT" -- "$file"` — only restores if file DIFFERS from commit
- **Problem:** If upstream made the SAME structural change (e.g., both added a prop), `git diff` returns clean and hook skips
- **Fix:** Removed conditional. Now always copies from backup + always runs `git checkout` (idempotent)

## Universal Avatar Fix
The root cause was that `ProfileAvatar.vue` fell back to `multiavatar(seed)` when no avatar prop was passed. Fixing `SessionListItem.vue` to pass `{type:'image',dataUrl:'/spock-avatar.png'}` only fixed ONE location. Every other component using `ProfileAvatar` (MessageItem, GroupChatPanel, GroupMessageItem, KanbanTaskCard, ProfileSelector, ProfileCard) still showed anime.

**Fix:** Modified `ProfileAvatar.vue` to fall back to `/spock-avatar.png` instead of `multiavatar`. This single change fixes ALL avatars everywhere.

```vue
<!-- ProfileAvatar.vue -->
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
```

Removed `@multiavatar/multiavatar` import and `generatedSvg` computed entirely.

## Verified Protection State (2026-05-22)
All 16 protected artifacts confirmed:
1. `packages/client/public/spock-avatar.png`
2. `packages/client/public/favicon.ico`
3. `packages/client/public/favicon.png`
4. `packages/client/index.html`
5. `packages/client/public/logo.png`
6. `packages/client/src/assets/logo.png`
7. `packages/client/src/assets/thinking-dark.mp4`
8. `packages/client/src/assets/thinking-light.mp4`
9. `packages/client/src/components/layout/AppSidebar.vue`
10. `packages/client/src/components/hermes/chat/SessionListItem.vue`
11. `packages/client/src/components/hermes/profiles/ProfileAvatar.vue`
12. `vite.config.website.ts`
13. `~/.config/systemd/user/hermes-webui.service`
14. `~/.hermes/webui/.token`
15. `~/.hermes/webui/config.json`
16. `/mnt/c/Users/thadd/Desktop/Launch Hermes WebUI.bat`

## Post-Upgrade Verification Checklist
Run after ANY upgrade:
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
bash .git/hooks/post-checkout  # trigger manual restoration
grep -q "spock-avatar.png" packages/client/src/components/hermes/profiles/ProfileAvatar.vue && echo "✓ ProfileAvatar.vue"
grep -q "spock-avatar.png" packages/client/src/components/hermes/chat/SessionListItem.vue && echo "✓ SessionListItem.vue"
grep -q "spock" packages/client/src/components/layout/AppSidebar.vue && echo "✓ AppSidebar.vue"
grep -q "Spock" packages/client/index.html && echo "✓ index.html"
ls packages/client/public/spock-avatar.png && echo "✓ spock-avatar.png"
ls packages/client/public/favicon.ico && echo "✓ favicon.ico"
[ -f dist/client/spock-avatar.png ] && echo "✓ dist/spock-avatar.png"
[ -f dist/client/favicon.ico ] && echo "✓ dist/favicon.ico"
[ -f dist/server/index.js ] && echo "✓ dist/server/index.js"
npm run build 2>&1 | tail -3
systemctl --user restart hermes-webui
```

## Emergency Recovery
If avatars break after upgrade:
1. `bash ~/.hermes/spock-protector/restore-spock.sh --force-build`
2. Hard-refresh browser (`Ctrl+Shift+R`)
3. Check `dist/` timestamp: `ls -la dist/client/index.html`
4. If still anime, `dist/` is stale — rebuild again
5. If all else fails, restore from `C:\Users\thadd\Documents\SpockWebUI` backup
