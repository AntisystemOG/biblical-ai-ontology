# Spock Guardian Hook — File Backup vs Git Checkout Order Bug

## Session: 2026-05-22

### What Happened

After fixing `ProfileAvatar.vue` and `SessionListItem.vue` to use `/spock-avatar.png` instead of `multiavatar`, the anime avatar bug kept coming back every time `restore-spock.sh` or the git hooks ran. The source files would be correct one moment, then wrong the next.

### Root Cause

The restore script and hooks used this order:

```bash
# WRONG ORDER — reintroduces old code
cp backup/ProfileAvatar.vue repo/ProfileAvatar.vue      # puts correct (post-fix) code
git checkout f636b1b -- packages/client/src/.../ProfileAvatar.vue  # OVERWRITES with old (pre-fix) code
```

The `SPOCK_COMMIT="f636b1b"` is an **old commit** from before the avatar fix. It contains the original multiavatar code. When `git checkout` runs after the file copy, it silently overwrites the correct post-fix version with the old pre-fix version.

### Why `f636b1b` Is Stale

`f636b1b` was the original rebrand commit (logo, title, sidebar, thinking videos). It does NOT contain:
- The `ProfileAvatar.vue` universal Spock fix (removes multiavatar import)
- The `SessionListItem.vue` object-shape avatar fix (`{type:'image',dataUrl:'/spock-avatar.png'}`)
- The `favicon.ico` multi-resolution Spock ICO

These fixes were applied AFTER `f636b1b` and saved to the file backup directory, but never committed to a new hash. So `git checkout f636b1b` always restores the old broken version.

### Detection

If you see this pattern, the order is wrong:
```bash
cp -f "$SRC" "$DST"      # file backup
git checkout "$SPOCK_COMMIT" -- "$FILE"  # git OVERWRITES the backup
```

After running the restore script, check:
```bash
grep "multiavatar" packages/client/src/components/hermes/profiles/ProfileAvatar.vue
# If this matches, git checkout overwrote the fix
```

### Fix

**Option A: File backup authoritative, git fallback only**
```bash
for FILE in "${FILES[@]}"; do
  SRC="$BACKUP/$FILE"
  DST="$REPO/$FILE"
  if [ -f "$SRC" ]; then
    cp -f "$SRC" "$DST"   # backup wins
  else
    git checkout "$SPOCK_COMMIT" -- "$FILE" 2>/dev/null || true  # fallback only
  fi
done
```

**Option B: Git first, then backup overwrite**
```bash
for FILE in "${FILES[@]}"; do
  git checkout "$SPOCK_COMMIT" -- "$FILE" 2>/dev/null || true  # baseline (may be old)
  cp -f "$BACKUP/$FILE" "$REPO/$FILE" 2>/dev/null || true  # OVERWRITES with correct code
done
```

Both work. Option A is cleaner — fewer disk writes, no unnecessary git operations.

### Files Affected

This bug affected all three protection mechanisms:
- `~/.hermes/spock-protector/restore-spock.sh`
- `/mnt/c/Users/thadd/hermes-web-ui/.git/hooks/post-checkout`
- `/mnt/c/Users/thadd/hermes-web-ui/.git/hooks/post-merge`

### Lesson

**The backup directory is the authoritative source of truth, not the git commit.** Git commits are snapshots in time. File backups evolve as fixes are applied. When they diverge, the backup must win.

If you update a protected file (fix a bug, add a feature), always update the backup copy AND the restore script. Never assume the git commit will pick up the change automatically.

### Prevention Checklist

- [ ] After fixing any protected file, copy it to `~/.hermes/spock-protector/`
- [ ] Verify the backup copy has the fix: `diff <repo-file> <backup-file>`
- [ ] Test the restore script: `bash restore-spock.sh` then verify the repo file
- [ ] Never run `git checkout` after `cp` for the same file
- [ ] Consider creating a new commit with all fixes and updating `SPOCK_COMMIT`
