# Restore-Spock Backup Order Fix — Session Reference (2026-05-22)

## What Changed

The `restore-spock` skill previously instructed users to restore from git history first (`git checkout f636b1b` and `d37f88e`), then patch dist/ manually. This was flawed because:

1. `f636b1b` is an old commit that predates the ProfileAvatar.vue universal fix
2. `d37f88e` may also be stale for some files
3. The `spock-protector` backup directory contains post-fix versions that are authoritative
4. Running `git checkout` after `cp` overwrote correct code with old code

## New Authoritative Method

**Always use `bash ~/.hermes/spock-protector/restore-spock.sh --force-build` first.**

This script:
1. Checks each file in the `FILES` array
2. If a backup exists in `~/.hermes/spock-protector/`, copies it (authoritative)
3. If no backup exists, falls back to `git checkout f636b1b -- <file>`
4. Optionally rebuilds `dist/` and restarts the server

The file backup order guarantees post-fix versions survive.

## Git History as Fallback Only

Git commits `f636b1b`, `d37f88e`, and `9caac49` are historical references. They contain the original customizations but may not have the latest fixes. Use them only when:
- The file has no backup in `~/.hermes/spock-protector/`
- You are setting up the backup directory for the first time
- You need to verify what the original customization looked like

## Files That Must Have Backups

These files MUST exist in `~/.hermes/spock-protector/` because they contain post-fix code not present in any git commit:
- `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` (universal Spock fix)
- `packages/client/public/favicon.ico` (multi-resolution Spock ICO)
- `packages/client/src/components/hermes/chat/SessionListItem.vue` (object-shape avatar)

If any of these are missing from the backup directory, copy them immediately:
```bash
cp /mnt/c/Users/thadd/hermes-web-ui/packages/client/src/components/hermes/profiles/ProfileAvatar.vue ~/.hermes/spock-protector/packages/client/src/components/hermes/profiles/
cp /mnt/c/Users/thadd/hermes-web-ui/packages/client/public/favicon.ico ~/.hermes/spock-protector/packages/client/public/
cp /mnt/c/Users/thadd/hermes-web-ui/packages/client/src/components/hermes/chat/SessionListItem.vue ~/.hermes/spock-protector/packages/client/src/components/hermes/chat/
```

## Verification After Any Restore

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
grep -q "spock-avatar.png" packages/client/src/components/hermes/profiles/ProfileAvatar.vue && echo "✓ ProfileAvatar.vue" || echo "✗ FAIL"
grep -q "spock-avatar.png" packages/client/src/components/hermes/chat/SessionListItem.vue && echo "✓ SessionListItem.vue" || echo "✗ FAIL"
grep -q "spock" packages/client/src/components/layout/AppSidebar.vue && echo "✓ AppSidebar.vue" || echo "✗ FAIL"
grep -q "Spock" packages/client/index.html && echo "✓ index.html" || echo "✗ FAIL"
ls packages/client/public/spock-avatar.png && echo "✓ spock-avatar.png" || echo "✗ FAIL"
ls packages/client/public/favicon.ico && echo "✓ favicon.ico" || echo "✗ FAIL"
```

If any check fails, the restore script or hooks ran in the wrong order.
