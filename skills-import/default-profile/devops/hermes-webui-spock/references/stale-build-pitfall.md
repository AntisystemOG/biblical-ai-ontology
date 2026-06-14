# Stale Build vs Fresh Source — Common Pitfall

## Symptom
User reports missing customizations, wrong avatar, or old branding even though
source files on disk appear correct and the server is running.

## Diagnosis

The server serves **compiled `dist/` files**, not `.vue` source files.
If the build is old, the running behavior reflects the old compiled code.

### Quick check: Is the server running stale dist?
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
echo "=== Server start time ==="
ss -tlnp | grep ":8648 " | awk '{print $6}'  # PID
ps -o lstart= -p $(ss -tlnp | grep ":8648 " | grep -oP 'pid=\K\d+') 2>/dev/null
echo "=== dist/client modification time ==="
ls -ld dist/client/
echo "=== Source modification time ==="
ls -ld packages/client/src/components/hermes/chat/SessionListItem.vue
```

If the server started BEFORE the last source change, it is serving stale code.

## Root Cause: ProfileAvatar `type` field mismatch

The `ProfileAvatar.vue` component only renders an `<img>` when BOTH conditions
true:
- `avatar?.type === 'image'`
- `avatar?.dataUrl` is truthy

If the compiled dist passes a plain string (e.g., `'/spock-avatar.png'`) instead
of `{ type: 'image', dataUrl: '/spock-avatar.png' }`, the component falls back
to multiavatar SVG generation, producing a generic anime character.

### Check what the compiled dist passes:
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
grep -o 'profileAvatar.*spock' dist/client/assets/js/*.js | head -5
# Should show: computed(()=>({type:"image",dataUrl:"/spock-avatar.png"}))
# If it shows: computed(()=>"/spock-avatar.png")  → WRONG, will fall back to multiavatar
```

## Fix: Rebuild and Restart

```bash
cd /mnt/c/Users/thadd/hermes-web-ui

# 1. Rebuild
npm run build 2>&1 | tail -5

# 2. Kill old server
pkill -f "node dist/server/index.js" || true
sleep 2
ss -tlnp | grep ":8648 " || echo "Port free"

# 3. Start new server
cd /mnt/c/Users/thadd/hermes-web-ui
node dist/server/index.js

# 4. Verify avatar is served correctly
curl -s http://localhost:8648/spock-avatar.png | md5sum
# Expected: 59ff0506bb8145188092b17b2b7c5e8e (Spock image)
```

## Prevention: Build on every Spock source change

After ANY modification to these source files, rebuild immediately:
- `SessionListItem.vue`
- `AppSidebar.vue`
- `index.html`
- Any `public/` asset (logo.png, favicon.png, spock-avatar.png)

If build is broken (rolldown), use the dist-patch technique documented in
`references/session-2026-05-22-avatar-dist-patching.md`.

## Spock Protector: Add dist rebuild check

The cron watchdog (`spock-guardian-watchdog`) should also check:
1. If `packages/client/` mtime > `dist/client/` mtime → rebuild needed
2. After rebuild, verify `spock-avatar.png` is in dist with correct checksum

```bash
# Add to guardian script
SRC_MTIME=$(stat -c %Y packages/client/src/components/hermes/chat/SessionListItem.vue)
DIST_MTIME=$(stat -c %Y dist/client/assets/js/*.js | sort -n | tail -1)
if [ "$SRC_MTIME" -gt "$DIST_MTIME" ]; then
  echo "[Guardian] Source newer than dist — rebuild required!"
  cd /mnt/c/Users/thadd/hermes-web-ui && npm run build
fi
```
