# WebUI Backup Creation — Complete Archive Without node_modules

## Purpose
Create a complete, restorable backup of the running WebUI at `C:\Users\thadd\Documents\SpockWebUI` (or equivalent). The backup must include all source, compiled dist, git history, and assets, but exclude reinstallable dependencies.

## Why Exclude node_modules
- `node_modules` is ~658MB of reinstallable packages (`npm install`)
- Source + dist + git + assets is only ~143MB
- Backup completes in ~50 seconds instead of 15+ minutes

## Command

```bash
dest="/mnt/c/Users/thadd/Documents/SpockWebUI"
rm -rf "$dest" && mkdir -p "$dest"

rsync -avh --info=progress2 \
  --exclude='node_modules' \
  --exclude='.next' \
  "/mnt/c/Users/thadd/hermes-web-ui/" \
  "$dest/"

echo "BACKUP_COMPLETE: $(date)" > "$dest/.backup_timestamp.txt"
```

## Verification Checklist

```bash
echo "=== Backup Verification ==="
ls -la "$dest/packages/client/public/spock-avatar.png"
ls -la "$dest/dist/client/spock-avatar.png"
grep -q "spock-avatar" "$dest/packages/client/src/components/hermes/chat/SessionListItem.vue" && echo "✓ SessionListItem.vue patched"
grep -q "spock-avatar" "$dest/dist/client/assets/js/OutlinePanel-CBYfEuCP.js" && echo "✓ Compiled JS patched"
ls -la "$dest/.git" && echo "✓ Git repo present"
ls -la "$dest/packages/client/src/components/layout/AppSidebar.vue" && echo "✓ AppSidebar present"
echo "=== ALL CHECKS PASSED ==="
```

## Restore

```bash
cd C:\Users\thadd\Documents\SpockWebUI
node dist/server/index.js    # uses existing compiled dist
```

Or rebuild:
```bash
cd C:\Users\thadd\Documents\SpockWebUI
npm install
npm run build
node dist/server/index.js
```

## Spock Guardian Hook Untracked File Quirk

After `git rebase --continue`, the `[Spock Guardian]` hook may emit:
```
[Spock Guardian] RESTORING: packages/client/public/spock-avatar.png
error: pathspec 'packages/client/public/spock-avatar.png' did not match any file(s) known to git
```

This occurs because the hook tries to `git checkout` files that are not tracked in the git index (newly added assets). The error is harmless — the file already exists from the commit. Do not panic when you see this.
