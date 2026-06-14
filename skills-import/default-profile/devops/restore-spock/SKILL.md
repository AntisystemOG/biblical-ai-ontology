---
title: Restore Spock WebUI Customizations
name: restore-spock
trigger: |
  When Spock customizations in the hermes-web-ui have been lost, overwritten,
  corrupted, or need to be re-applied after an upgrade, sync, or clean build.
  Also triggers on "restore spock", "fix spock", "re-apply spock", or any
  request to restore branding/avatar/sidebar/title customizations.
description: |
  Restores all Spock customizations to the hermes-web-ui at
  /mnt/c/Users/thadd/hermes-web-ui. This is a surgical restoration that
  re-applies only the known Spock changes without touching upstream code.
  Can be run after any upgrade, rebase, or build to ensure customizations
  survive.
---

# Restore Spock WebUI Customizations

## When to Run

- After an upgrade/rebase that may have overwritten customizations
- After `git reset --hard` or `git clean -fd`
- After a fresh `npm install` + `npm run build` that lost compiled patches
- When the Spock avatar, logo, sidebar text, or browser title is missing
- After the Spock Guardian hook fails to restore everything
- **Before any upgrade/rebase** — verify `f636b1b` and `9caac49` exist first

## Spock Customization Inventory

| # | File | What It Does | Restore Source |
|---|------|-------------|---------------|
| 1 | `packages/client/public/spock-avatar.png` | Spock avatar image for session list | `git show d37f88e` or backup |
| 2 | `packages/client/public/favicon.ico` | Browser tab icon (multi-res Spock ICO) | Convert from spock-avatar.png |
| 3 | `packages/client/public/favicon.png` | Browser tab icon (PNG backup) | `git show 5c0bd0b` or backup |
| 4 | `packages/client/src/components/hermes/chat/SessionListItem.vue` | Renders Spock avatar instead of multiavatar | `git show d37f88e` |
| 5 | `packages/client/index.html` | Browser tab title = "Spock" | `git show f636b1b` |
| 6 | `packages/client/public/logo.png` | Spock logo (public asset) | `git show f636b1b` |
| 7 | `packages/client/src/assets/logo.png` | Spock logo (bundled asset) | `git show f636b1b` |
| 8 | `packages/client/src/assets/thinking-dark.mp4` | Spock thinking animation | `git show f636b1b` |
| 9 | `packages/client/src/assets/thinking-light.mp4` | Spock thinking animation | `git show f636b1b` |
| 10 | `packages/client/src/components/layout/AppSidebar.vue` | Sidebar shows "Spock" text + logo | `git show f636b1b` |
| 11 | `vite.config.website.ts` | Website build customization | `git show f636b1b` |
| 12 | `dist/client/spock-avatar.png` | Compiled asset | Copy from `packages/client/public/` |
| 13 | `dist/client/favicon.ico` | Compiled tab icon | Copy from `packages/client/public/` |
| 14 | `dist/client/assets/js/OutlinePanel-CBYfEuCP.js` | Compiled JS with Spock img | Patch manually |
| 15 | `dist/client/assets/js/OutlinePanel-P0pfhZX2.js` | Compiled JS with Spock img | Patch manually |

## Restoration Procedure

### Step 0: Use the Spock Protector (Recommended)

The authoritative restoration method is the Spock Protector backup system:

```bash
bash ~/.hermes/spock-protector/restore-spock.sh --force-build
```

This script restores from **file backups** (authoritative, contains post-fix versions) and only falls back to git checkout for files without backups. It also rebuilds `dist/` and restarts the server.

**Why file backups over git checkout:** The git commit `f636b1b` predates some fixes (ProfileAvatar.vue universal fix, favicon.ico multi-res ICO). If `git checkout` runs after a file copy, it silently overwrites correct post-fix code with old pre-fix code, reintroducing the multiavatar bug. The file backup directory at `~/.hermes/spock-protector/` always has the latest corrected versions.

### Step 1: Verify Base Commits Exist (ABORT if missing, but use backup)

The commits `f636b1b` and `9caac49` contain historical Spock customizations but may be stale for some files. Always prefer the file backup path. Only use git checkout as fallback for files that don't exist in the backup directory.

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
for commit in f636b1b 9caac49; do
  git cat-file -t "$commit" >/dev/null 2>&1 && echo "✓ $commit exists" || echo "✗ $commit MISSING (use backup path)"
done
```

### Step 3: Restore Compiled dist/ Files

The build system (`rolldown`) is broken, so we must patch `dist/` manually:

```bash
cd /mnt/c/Users/thadd/hermes-web-ui

# Copy spock-avatar.png to dist
cp packages/client/public/spock-avatar.png dist/client/spock-avatar.png

# Patch the compiled JS files for Spock avatar in session list
for fname in dist/client/assets/js/OutlinePanel-CBYfEuCP.js dist/client/assets/js/OutlinePanel-P0pfhZX2.js; do
  if [ -f "$fname" ]; then
    # Replace multiavatar span with Spock img
    python3 -c "
import re
with open('$fname', 'r') as f:
  content = f.read()
# Old pattern: n(\"span\",{class:\"session-item-profile-avatar\",innerHTML:e.value},null,8,z)
# New pattern: n(\"img\",{class:\"session-item-profile-avatar\",src:\"/spock-avatar.png\",alt:\"Spock\"},null,8,z)
content = content.replace(
  'n(\"span\",{class:\"session-item-profile-avatar\",innerHTML:e.value},null,8,z)',
  'n(\"img\",{class:\"session-item-profile-avatar\",src:\"/spock-avatar.png\",alt:\"Spock\"},null,8,z)'
)
# Fix the dynamic props array from ['innerHTML'] to ['src']
content = content.replace('z=[\"innerHTML\"]', 'z=[\"src\"]')
with open('$fname', 'w') as f:
  f.write(content)
"
    echo "Patched: $fname"
  fi
done
```

### Step 4: Verify Everything
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
echo "=== Verification ==="
grep -q 'type:.*image.*dataUrl.*spock-avatar' packages/client/src/components/hermes/chat/SessionListItem.vue && echo "✓ SessionListItem.vue (object shape)" || echo "✗ FAIL — wrong avatar type"
grep -q "Spock" packages/client/src/components/layout/AppSidebar.vue && echo "✓ AppSidebar.vue" || echo "✗ FAIL"
grep -q "Spock" packages/client/index.html && echo "✓ index.html" || echo "✗ FAIL"
ls packages/client/public/spock-avatar.png && echo "✓ spock-avatar.png" || echo "✗ FAIL"
ls dist/client/spock-avatar.png && echo "✓ dist spock-avatar.png" || echo "✗ FAIL"
grep -q "spock-avatar" dist/client/assets/js/OutlinePanel-CBYfEuCP.js && echo "✓ OutlinePanel JS" || echo "✗ FAIL"
```

### Step 5: Restart Server
```bash
# Kill existing
pkill -f "node dist/server/index.js" || true
# Restart
cd /mnt/c/Users/thadd/hermes-web-ui && node dist/server/index.js &
```

## Alternative: Restore from Backup

If git history is lost, restore from the backup at:
`C:\Users\thadd\Documents\SpockWebUI`

```bash
# Full restore from backup
cp -r "/mnt/c/Users/thadd/Documents/SpockWebUI/"* "/mnt/c/Users/thadd/hermes-web-ui/"
# Then reinstall node_modules
cd /mnt/c/Users/thadd/hermes-web-ui && npm install
```

## If Customizations Are Still Missing

1. Check git reflog: `git reflog --all | head -20`
2. Check if commits `f636b1b` and `9caac49` exist: `git log --oneline | grep -i spock`
3. If commits are gone, restore from backup: `cp -r /mnt/c/Users/thadd/Documents/SpockWebUI /mnt/c/Users/thadd/hermes-web-ui/`
4. Re-apply changes manually using the commit diffs as reference

## references/
- `references/customization-commits.md` — Full diffs of f636b1b and 9caac49.
- `references/restore-from-backup.md` — Step-by-step backup restoration.
