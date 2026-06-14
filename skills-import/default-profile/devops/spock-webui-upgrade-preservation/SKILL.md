---
title: Spock WebUI Upgrade with Customization Preservation
name: spock-webui-upgrade-preservation
trigger: |
  Any task involving upgrading, updating, pulling upstream changes, or syncing
  the EKKOLearnAI / hermes-web-ui repository when Spock customizations (branding,
  avatar, sidebar, title, logo) are present. Also applies to rebasing, merging
  origin/main, or running `git pull` in the hermes-web-ui repo.
description: |
  The Spock WebUI at /mnt/c/Users/thadd/hermes-web-ui carries persistent
  customizations (Spock rebrand, avatar image, sidebar text, browser title).
  Upgrades must NEVER overwrite, drop, or conflict these customizations.
  This skill documents the safe upgrade workflow, the guardian hook, and
  forbidden actions.
---

# Spock WebUI Upgrade — Customization Preservation Rule

## Core Rule

**NEVER upgrade in a way that changes or discards Spock customizations.**

Customizations are authoritative. The upstream EKKOLearnAI repo is secondary.
When upgrading, merge or rebase **in favor of the local Spock customizations**,
not the upstream defaults.

### Emergency Recovery

If customizations are lost during an upgrade:
1. **Restore from local backup:** `C:\Users\thadd\Documents\SpockWebUI` contains a complete backup of the working WebUI with all customizations
2. **Re-apply from git reflog:** `git reset --hard HEAD@{1}` (if caught immediately)
3. **Re-apply from upstream merge:** See `hermes-webui-spock` skill for the 3-layer Spock Protector system

Always verify the backup exists before attempting risky upgrade operations.

## What Constitutes Spock Customizations

| File | Customization |
|------|--------------|
| `packages/client/public/spock-avatar.png` | Spock avatar image (replaces multiavatar) |
| `packages/client/public/favicon.ico` | Browser tab icon (multi-res Spock ICO) |
| `packages/client/public/favicon.png` | Browser tab icon (PNG backup) |
| `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` | **UNIVERSAL AVATAR** — ALL profile avatars render as Spock image instead of multiavatar SVG |
| `packages/client/src/components/hermes/chat/SessionListItem.vue` | Session list passes Spock image object to ProfileAvatar |
| `packages/client/src/components/layout/AppSidebar.vue` | Spock sidebar branding / title |
| `packages/client/public/logo.png` | Spock/EKKOLearnAI logo |
| `packages/client/index.html` | Browser title / favicon |
| `packages/client/src/assets/logo.png` | Logo asset |
| `packages/client/src/assets/thinking-dark.mp4` | Spock thinking animation |
| `packages/client/src/assets/thinking-light.mp4` | Spock thinking animation |
| `vite.config.website.ts` | Website build customization |
| `dist/client/spock-avatar.png` | Compiled avatar asset |
| `dist/client/favicon.ico` | Compiled tab icon |
| `dist/client/assets/js/OutlinePanel-*.js` | Compiled JS with Spock avatar patches |
| `dist/client/assets/js/index-*.js` | Compiled JS with ProfileAvatar universal Spock |
| Any `.git/hooks/post-checkout` or `post-merge` guardian hook | Spock Guardian restoration hook |

## Safe Upgrade Workflow

### 1. Check Current State
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
git status --short
git log --oneline -5
```

If there are unstaged changes, **do NOT proceed** until they are resolved.

### 2. Verify Spock Base Commits Exist

The two commits that contain all Spock customizations must exist in git history
before starting:
- `f636b1b` — Original rebrand (logo, title, sidebar, thinking videos)
- `9caac49` — Spock avatar for session list (or latest avatar commit)

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
for commit in f636b1b 9caac49; do
  git cat-file -t "$commit" >/dev/null 2>&1 && echo "✓ $commit exists" || echo "✗ $commit MISSING"
done
```

If either is missing, abort the upgrade and restore from backup first.

### 3. Stash or Commit Pre-existing Changes
If the working tree has local modifications unrelated to the upgrade:
```bash
git stash push -m "pre-upgrade local changes" --include-untracked
```

### 3. Fetch Upstream (Never Pull Directly)
```bash
git fetch origin
```

### 4. Temporarily Disable Guardian Hook
The Spock Guardian `post-checkout` / `post-merge` hooks auto-restore files from
commit `f636b1b` after any checkout. During a rebase, the hook fires on every
rewritten commit, creating unstaged modifications that abort the rebase with:
```
error: cannot rebase: You have unstaged changes.
```

**Disable before rebase, re-enable after:**
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
mv .git/hooks/post-checkout .git/hooks/post-checkout.bak 2>/dev/null || true
mv .git/hooks/post-merge   .git/hooks/post-merge.bak   2>/dev/null || true
```

### 5. Rebase onto Upstream (Preserve Spock)
```bash
git config pull.rebase true
git pull origin main
```

If conflicts occur in Spock-customized files:
- **ALWAYS resolve in favor of the local (Spock) version**
- Mark resolved: `git add <file>`
- Continue: `git rebase --continue`

### 5a. Re-enable Guardian Hook
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
mv .git/hooks/post-checkout.bak .git/hooks/post-checkout 2>/dev/null || true
mv .git/hooks/post-merge.bak   .git/hooks/post-merge   2>/dev/null || true
```

### 5b. Post-Rebase Staging Cleanup (if needed)
If the Guardian hook fired during rebase before you could disable it, or if
upstream changed a Spock-customized file's CSS/layout (e.g., `AppSidebar.vue`
gap/flex properties), the file may have staged upstream changes mixed with
Spock text.

**Reset the file to the rebased Spock version and re-stage cleanly:**
```bash
git checkout HEAD -- packages/client/src/components/layout/AppSidebar.vue
git add packages/client/src/components/layout/AppSidebar.vue
```

Then verify with `git status --short` that only real Spock changes are staged.

### 6. Verify Customizations Intact
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
echo "=== Checking Spock customizations ==="
grep -q "spock-avatar.png" packages/client/src/components/hermes/profiles/ProfileAvatar.vue && echo "✓ Universal avatar OK"
grep -q "spock-avatar.png" packages/client/src/components/hermes/chat/SessionListItem.vue && echo "✓ SessionListItem avatar OK"
grep -q "spock" packages/client/src/components/layout/AppSidebar.vue && echo "✓ Sidebar OK"
grep -q "Spock" packages/client/index.html && echo "✓ Title OK"
ls packages/client/public/spock-avatar.png && echo "✓ Avatar asset OK"
ls packages/client/public/favicon.ico && echo "✓ favicon.ico asset OK"
ls dist/client/spock-avatar.png && echo "✓ Dist avatar OK"
ls dist/client/favicon.ico && echo "✓ Dist favicon OK"
grep -q "spock-avatar" dist/client/assets/js/OutlinePanel-*.js 2>/dev/null && echo "✓ Dist JS OK"
```

### 7. Push to Spock Fork

After a successful rebase, the local commit hashes change. Push to the fork
with force to overwrite the old branch:

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
git push spock main --force-with-lease
```

If `--force-with-lease` rejects (remote has new commits), inspect first:
```bash
git fetch spock
git log spock/main..HEAD --oneline   # what would be overwritten
git push spock main --force           # only if confirmed safe
### 8. Rebuild Dist (if build system works)
```bash
# Only if build is functional; if rolldown is broken, skip and patch dist manually
cd /mnt/c/Users/thadd/hermes-web-ui && npm run build 2>/dev/null || echo "Build broken — patch dist/ manually"
```

If build is broken, manually propagate source changes to `dist/client/` compiled JS.
See `references/session-2026-05-22-avatar-dist-patching.md` in the
`hermes-webui-spock` skill for the exact dist-JS patch technique.

### 9. Restart Server
```bash
# Kill existing
cd /mnt/c/Users/thadd/hermes-web-ui && pkill -f "node dist/server/index.js" || true
# Restart via launcher or manually
bash -lic "cd /mnt/c/Users/thadd/hermes-web-ui && node dist/server/index.js" &
```

## Forbidden Actions (Never Do These)

| Action | Why Forbidden |
|--------|--------------|
| `git reset --hard origin/main` | Wipes all Spock customizations instantly |
| `git checkout origin/main -- .` | Overwrites all local files with upstream defaults |
| `git merge origin/main` without reviewing | May silently prefer upstream over Spock customizations |
| `git pull` without rebasing strategy | Creates merge commits that can override customizations |
| Deleting `dist/` and rebuilding from clean upstream | Loses compiled-in Spock patches |
| Running `git clean -fd` | Deletes untracked assets like `spock-avatar.png` |

## The Spock Guardian Hook

There is a git hook (`post-checkout` / `post-merge`) that auto-restores some
Spock files after checkout. **Do not rely solely on it** — it may fail or
restore incomplete state. Always verify manually after any upgrade operation.

### Hook Implementation (Correct Order)

The hooks MUST use this exact restoration order to avoid re-introducing old multiavatar code:

```bash
for file in "${PROTECTED_FILES[@]}"; do
  SRC="$BACKUP/$file"
  DST="$REPO_ROOT/$file"
  if [ -f "$SRC" ]; then
    # File backup exists — use it (authoritative, contains post-fix versions)
    cp -f "$SRC" "$DST"
  else
    # No backup — try git checkout as fallback
    git checkout "$SPOCK_COMMIT" -- "$file" 2>/dev/null || true
  fi
done
```

**CRITICAL: File backup is authoritative. Git checkout is fallback ONLY.**

### Why This Order Matters

The `SPOCK_COMMIT` (e.g., `f636b1b`) is an **old commit** that predates some fixes. If `git checkout` runs AFTER the file copy, it overwrites the post-fix version with the pre-fix version from the commit. This silently reintroduces bugs that were already fixed.

**Wrong (reintroduces old code):**
```bash
cp backup/ProfileAvatar.vue repo/ProfileAvatar.vue      # puts correct code
git checkout f636b1b -- packages/client/src/.../ProfileAvatar.vue  # OVERWRITES with old code
```

**Right (backup wins):**
```bash
git checkout f636b1b -- packages/client/src/.../ProfileAvatar.vue  # baseline (may be old)
cp backup/ProfileAvatar.vue repo/ProfileAvatar.vue      # OVERWRITES with correct code
```

Or even better: skip git checkout entirely for files that have backups.

## If Customizations Are Lost

1. Abort immediately: `git reset --hard HEAD@{1}` (if recent)
2. Check reflog: `git reflog --all | head -20`
3. Restore from backup if available (old build at `~/hermes-web-ui-ekko/`)
4. Re-apply customizations from memory / this skill

## Pitfall: Stale dist/ Build After Source Fix

**Symptom:** Source files (`SessionListItem.vue`) are correct and show the Spock avatar code, but the browser still shows the old anime multiavatar character.

**Root cause:** The running Node server serves `dist/client/` — the *compiled* JS — not the source `.vue` files. If the `dist/` was built before the avatar fix commit, the server delivers stale compiled code that still pulls `profile.avatar` from the backend (multiavatar-generated anime character).

**Detection:**
```bash
# Check when dist/ was last modified
ls -la dist/client/index.html   # timestamp reveals build age
# Compare to git log
git log --oneline -3
```
If the dist timestamp predates the avatar fix commit, it's stale.

**Fix:** Rebuild with `npm run build` (if build works) or restore server from backup:
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
npm run build
# If build times out and wipes dist/server/ (see below), restore server from backup:
rsync -avh /mnt/c/Users/thadd/Documents/SpockWebUI/dist/server/ dist/server/
```
Then restart the systemd service.

## Pitfall: Build Timeout Wipes dist/server/

**Symptom:** After `npm run build` times out, the server fails to start with:
```
Error: Cannot find module '/mnt/c/Users/thadd/hermes-web-ui/dist/server/index.js'
```

**Root cause:** The build process cleans `dist/` at the start. If it times out during the server compilation phase, `dist/server/` remains empty while `dist/client/` may be partially or fully intact.

**Fix — restore server from backup:**
```bash
rsync -avh /mnt/c/Users/thadd/Documents/SpockWebUI/dist/server/ /mnt/c/Users/thadd/hermes-web-ui/dist/server/
```
The `Documents/SpockWebUI` backup always contains a working `dist/server/` from the last successful build.

## Pitfall: favicon.ico vs favicon.png Mismatch

**Symptom:** Browser tab shows old default icon instead of Spock.

**Root cause:** `packages/client/index.html` references `/favicon.ico`, but `packages/client/public/favicon.ico` is the old default icon (dated before the rebrand). The Spock image was added as `favicon.png` but the HTML still points to `.ico`.

**Fix:** Convert `spock-avatar.png` to a multi-resolution `.ico` file and replace `packages/client/public/favicon.ico`:
```python
from PIL import Image
src = '/mnt/c/Users/thadd/hermes-web-ui/packages/client/public/spock-avatar.png'
dst = '/mnt/c/Users/thadd/hermes-web-ui/packages/client/public/favicon.ico'
img = Image.open(src)
if img.mode != 'RGBA': img = img.convert('RGBA')
sizes = [(16,16),(32,32),(64,64),(128,128)]
frames = [img.resize(s, Image.LANCZOS) for s in sizes]
frames[0].save(dst, format='ICO', sizes=sizes, append_images=frames[1:])
```
Then copy to `dist/client/favicon.ico` and backup `~/.hermes/spock-protector/packages/client/public/favicon.ico`.

**Protection:** Add `favicon.ico` to the Spock Protector registry (`PROTECTED_FILES.txt` and `restore-spock.sh`) so upgrades do not overwrite it.

## Verification Checklist Post-Upgrade

- [ ] `spock-avatar.png` exists in `packages/client/public/`
- [ ] `spock-avatar.png` exists in `dist/client/`
- [ ] `favicon.ico` exists in `packages/client/public/` and `dist/client/` (Spock multi-res ICO, not old default)
- [ ] `SessionListItem.vue` references `/spock-avatar.png` as `{type:'image',dataUrl:'/spock-avatar.png'}` (NOT a plain string)
- [ ] `AppSidebar.vue` retains Spock branding
- [ ] `logo.png` and `index.html` are correct
- [ ] `dist/client/assets/js/OutlinePanel-*.js` contain Spock patches (if build broken)
- [ ] dist/ build timestamp is newer than the latest Spock commit (not stale)
- [ ] `dist/server/index.js` exists and is non-empty
- [ ] WebUI loads and shows Spock avatar in session list
- [ ] Browser tab title shows Spock branding
- [ ] Browser tab icon shows Spock (not old default)
- [ ] Local backup `C:\Users\thadd\Documents\SpockWebUI` is up to date (run backup after successful upgrade)
- [ ] Spock Guardian hooks (`post-checkout`, `post-merge`) are enabled in `.git/hooks/`
- [ ] Fork (`spock` remote) pushed with rebased commits

## references/
- `references/spock-customization-inventory.md` — Full list of every customized file and what it does.
- `references/backup-creation.md` — How to create a complete restorable backup of the WebUI without node_modules, including verification checklist and Spock Guardian hook quirks.
- `references/stale-dist-build-pitfall.md` — Root cause analysis of anime avatar bug, ProfileAvatar universal fix, dist/ build verification, favicon.ico conversion, and post-upgrade checklist.
- `references/audit-2026-05-22.md` — Forensic audit of 7 critical protection flaws found and fixed, with the one-command recovery procedure.