---
name: hermes-webui-spock
title: Hermes WebUI (EKKOLearnAI) - Setup, Customization & Troubleshooting
description: |
  Complete workflow for managing Thad's customized Hermes WebUI pulled from EKKOLearnAI/hermes-web-ui.
  Covers: correct repo identification, auth bypass, Spock branding, server start/stop, launcher creation,
  and the broken npm build workaround.
trigger: |
  - User mentions "webui", "web ui", "hermes webui", "spock webui"
  - Need to start/stop/restart the WebUI server
  - Customizations missing or need re-applying
  - Token/login issues with WebUI
  - Need to rebuild or update WebUI
  - Desktop launcher needs fixing
---

## 1. Correct Repository

**THE ONLY CORRECT REPO:**
- **Path:** `/mnt/c/Users/thadd/hermes-web-ui` (Windows mount, accessible in WSL)
- **Git remote:** `https://github.com/EKKOLearnAI/hermes-web-ui.git`
- **Fork (with customizations):** `https://github.com/AntisystemOG/hermes-web-ui.git`

**OLD/WRONG REPOS — DO NOT USE:**
- `~/hermes-webui-new/` — Wrong Spock WebUI, has a systemd service that auto-restarts
- `~/hermes-web-ui-ekko/` — Old EKKO build, contains pre-built dist with customizations

> ⚠️ **CRITICAL:** Always verify which repo the server is running from. The old `hermes-webui-new` had a systemd service `hermes-webui.service` that auto-restarts the wrong server.

### User Terminology Preference

When Thad says **"web ui"** or **"webui"** without further qualification, he ALWAYS refers exclusively to the EKKOLearnAI/hermes-web-ui repository at `/mnt/c/Users/thadd/hermes-web-ui`. Do NOT disambiguate to other web interfaces, dashboards, or tools. Default all "webui" / "web ui" queries directly to this repo and its Spock customizations.

## 2. Customizations

Thad's fork has commit `f636b1b` — "feat: rebrand to Spock":
- **Browser title:** `Spock` (instead of `Hermes`)
- **Sidebar logo/text:** Spock branding
- **Thinking avatar:** Star Trek badge video (49KB, replaces the 8MB default girl animation)
- **Logo:** Custom Spock logo

### Source files modified:
- `packages/client/index.html` — `<title>Spock</title>`
- `packages/client/src/assets/logo.png`
- `packages/client/src/assets/thinking-dark.mp4`
- `packages/client/src/assets/thinking-light.mp4`
- `packages/client/src/components/layout/AppSidebar.vue` — sidebar text/logo
- `vite.config.website.ts` — (verify if changed)

### Customization script:
- **Location:** `/mnt/c/Users/thadd/.openclaw/workspace/scripts/apply-webui-customizations.sh`
- **Updated:** Points to correct repo (`/mnt/c/Users/thadd/hermes-web-ui`)
- **Media source:** `/mnt/c/Users/thadd/.hermes/images/startrek badge.mp4`

## 3. Authentication — Token-Based (Production Default)

**User preference: AUTH_ENABLED with real token.** Thad has explicitly requested the token be restored; do NOT default to auth bypass.

### How it works:

The server generates a random 64-char token on first start and stores it in:
- **File:** `~/.hermes/webui/.token` (mode `0600`)
- **Read via WSL:** `cat /home/thadd/.hermes/webui/.token`

The token is passed in the URL `?token=<...>` which the SPA auto-submits.

### Start server (auth enabled — DO NOT set AUTH_DISABLED):
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
node bin/hermes-web-ui.mjs start
# Or background:
nohup node bin/hermes-web-ui.mjs start > ~/.hermes-web-ui/server.log 2>&1 &
```

### Desktop Launcher (reads real token from WSL):
The `.bat` fetches the token via `wsl cat /home/thadd/.hermes/webui/.token` and appends it:
```
start "" "http://localhost:8648/?token=%WSLTOKEN%"
```

### Token location summary:
| Where | Path |
|-------|------|
| Token file | `/home/thadd/.hermes/webui/.token` |
| WSL launcher reads via | `wsl bash -lc "cat /home/thadd/.hermes/webui/.token"` |
| Desktop shortcut | `C:\Users\thadd\Desktop\Launch Hermes WebUI.bat` |

### Auth-disabled bypass (emergency only, NOT default):
If auth ever needs disabling for local debugging:
```bash
export AUTH_DISABLED=1
node bin/hermes-web-ui.mjs start
```
**Do this only temporarily — revert as soon as possible.**

## 4. The Auto-Update Pitfall (CRITICAL — May 2026)

**What happens:** The WebUI auto-updates via npm, installing a fresh vanilla copy at
`~/.hermes/node/lib/node_modules/hermes-web-ui/`. This overwrites your Spock
customizations (logo, title, thinking avatar) and may start running instead of your
local repo build.

**How to detect:**
```bash
# Check WHICH server is actually running
ps aux | grep "index.js" | grep -v grep | awk '{for(i=11;i<=NF;i++) print $i}'
# If path contains "node_modules/hermes-web-ui" — it's the VANILLA npm copy
# If path contains "hermes-web-ui/dist/server/index" — it's your local SPOCK build

# Also check file sizes
ls -la /mnt/c/Users/thadd/hermes-web-ui/dist/client/logo.png
# Should be ~726KB (Spock logo), not ~1.8MB (generic Hermes)

curl -s "http://127.0.0.1:8648/?token=$(cat ~/.hermes/webui/.token)" | grep "<title>"
# Should say "Spock", not "Hermes"
```

**How to fix (when vanilla is running):**
```bash
# 1. Kill the vanilla server
kill $(ps aux | grep "node_modules/hermes-web-ui" | grep -v grep | awk '{print $2}')

# 2. Verify port is free
ss -tlnp | grep ":8648 " || echo "Port free"

# 3. Start your LOCAL Spock build
cd /mnt/c/Users/thadd/hermes-web-ui
nohup node dist/server/index.js > ~/.hermes-web-ui/server.log 2>&1 &

# 4. Verify auth + customizations
curl -sf "http://127.0.0.1:8648/health?token=$(cat ~/.hermes/webui/.token)"
curl -s "http://127.0.0.1:8648/?token=$(cat ~/.hermes/webui/.token)" | grep "<title>"
```

## Prevention — Spock Protector 5-Layer Defense (May 2026)

| Layer | Mechanism | When it triggers |
|-------|-----------|-----------------|
| L1 — Pre-update Check | `pre-update-check.sh` | Before ANY update attempt — blocks if unsafe |
| L2 — Update Wrapper | `spock-update.sh` | Runs check → update → auto-restore in sequence |
| L3 — Git Hooks | `post-merge`, `post-checkout`, `post-rewrite` | Immediately after git pull/branch switch/rebase |
| L4 — Cron Watchdog | Every 5 min via `spock-guardian-watchdog` cron job | Persistent background monitoring |
| L5 — Hard Restore | `/home/thadd/.hermes/spock-protector/restore-spock.sh` | Emergency manual or scripted restore |

**All scripts reference a single `SPOCK_COMMIT` baseline.** When you commit new Spock changes, update this commit hash in:
- `~/.hermes/scripts/spock-protector/guard.sh`
- `~/.hermes/scripts/spock-protector/pre-update-check.sh`
- `~/.hermes/scripts/spock-protector/spock-update.sh`
- `~/.hermes/hermes-web-ui/.git/hooks/post-merge`
- `~/.hermes/hermes-web-ui/.git/hooks/post-checkout`
- `~/.hermes/hermes-web-ui/.git/hooks/post-rewrite`

**Current baseline:** `5c0bd0b` (includes favicon.png + sidebar CSS + all prior Spock branding)

> **PATH Pitfall:** systemd services do NOT inherit the user's PATH. If the WebUI fails with `Error: spawn hermes ENOENT`, the service file must explicitly set:
> ```
> Environment="PATH=/home/thadd/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
> ```
> The `hermes` binary lives at `/home/thadd/.local/bin/hermes` and is needed for the gateway bridge subprocess.

**Protected files (11 total from commit `5c0bd0b` + favicon fix):**
1. `packages/client/index.html` — `<title>Spock</title>`, favicon ref
2. `packages/client/public/favicon.ico` — Browser tab icon (multi-res Spock ICO)
3. `packages/client/public/favicon.png` — Browser tab icon (PNG backup)
4. `packages/client/public/logo.png` — Main Spock logo
5. `packages/client/public/spock-avatar.png` — Session profile avatar
6. `packages/client/src/assets/logo.png` — Sidebar logo
7. `packages/client/src/assets/thinking-dark.mp4` — Star Trek badge
8. `packages/client/src/assets/thinking-light.mp4` — Star Trek badge
9. `packages/client/src/components/layout/AppSidebar.vue` — "Spock" sidebar text
10. `packages/client/src/components/hermes/chat/SessionListItem.vue` — Avatar image source
11. `vite.config.website.ts` — chunk size config

> **Commit baseline drift pitfall:** If you make additional Spock changes (like adding favicon.png or CSS tweaks) without committing them, the git-diff baseline check will flag files as "DIRTY" and block updates. **Always commit Spock changes** so the baseline stays clean:
> ```bash
> git add <changed-files>
> git commit -m "feat(spock): <description>"
> # Then update SPOCK_COMMIT in all protector scripts
> ```

> **Commit baseline drift pitfall:** If you make additional Spock changes (like adding favicon.png or CSS tweaks) without committing them, the git-diff baseline check will flag files as "DIRTY" and block updates. **Always commit Spock changes** so the baseline stays clean:
> ```bash
> git add <changed-files>
> git commit -m "feat(spock): <description>"
> # Then update SPOCK_COMMIT in all protector scripts
> ```

## Avatar Implementation (Updated May 2026 — UNIVERSAL FIX)

**Previous approach (SessionListItem.vue only):**
`SessionListItem.vue` hardcoded `{type:'image',dataUrl:'/spock-avatar.png'}` as the `:avatar` prop. This only fixed the sidebar session list. Message bubbles, profile selector, group chat, and kanban still showed multiavatar anime characters.

**New approach (ProfileAvatar.vue — fixes ALL avatars everywhere):**
Edit `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` to remove the `multiavatar` fallback entirely:

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
- Group chat agent avatars ✓
- Profile selector avatars ✓
- Kanban task card assignee avatars ✓
- Profile modal avatars ✓
- Any future component using `ProfileAvatar` ✓

**Key change:** Remove the `import multiavatar from '@multiavatar/multiavatar'` line and the `generatedSvg` computed property. The `v-else` branch now renders `<img src="/spock-avatar.png">` instead of `<span v-html="generatedSvg">`.

**CRITICAL detail:** `ProfileAvatar.vue` ONLY renders `<img>` when the `:avatar` prop is an object with `type === 'image'` and a truthy `dataUrl`. A plain string causes multiavatar SVG fallback. If upstream code passes a string instead of an object, the universal fix in `ProfileAvatar.vue` still catches it (the `v-else` branch renders Spock regardless).

**Avatar sizing note:** The CSS renders avatars at various sizes (16px sidebar, 24px selector, 28px group chat, 34px runtime, 36px messages, 40px message bubbles, 72px profile modal). The transparent Spock PNG at 860x721 works fine — the browser downscales it on-the-fly via CSS `width/height` and `object-fit: cover` with `border-radius: 50%` (circular crop). No pre-resizing needed.

**If ProfileAvatar component is missing in future upstream versions:**
- Component path: `packages/client/src/components/hermes/profiles/ProfileAvatar.vue`
- If upstream removes it, search for `multiavatar` in the codebase and replace all inline SVG avatar rendering with `<img src="/spock-avatar.png">`

## Dist JS Verification (When Build Is Broken)

If `npm run build` is unavailable, the compiled `dist/client/assets/js/*.js` must be patched manually. After the universal `ProfileAvatar.vue` fix, the compiled JS will contain `spock-avatar` references in multiple chunk files.

Verify the dist contains Spock:
```bash
grep -c "spock-avatar" /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/js/*.js
grep -c "multiavatar\|profile-avatar-svg" /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/js/*.js
# First should be >0, second should be 0
```

If the dist still references `multiavatar` or `profile-avatar-svg`, the build is stale and needs rebuilding (or manual JS patching if build is broken).

## Stale dist/ Build Detection & Fix

**Symptom:** Source `ProfileAvatar.vue` is correct but browser still shows old anime avatar.
**Root cause:** The running server delivers compiled `dist/client/` JS. If `dist/` predates the latest Spock commit, the compiled code still falls back to multiavatar.

**Detection:**
```bash
ls -la /mnt/c/Users/thadd/hermes-web-ui/dist/client/index.html
git log --oneline -3
# If dist timestamp predates the latest commit, it's stale
```

**Fix:**
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
npm run build
# If build times out and wipes dist/server/, restore from backup:
rsync -avh /mnt/c/Users/thadd/Documents/SpockWebUI/dist/server/ dist/server/
systemctl --user restart hermes-webui
```

**Build timeout pitfall:** `npm run build` cleans `dist/` at the start. If it times out during server compilation, `dist/server/` is wiped (empty) while `dist/client/` may be intact. The server then fails to start with `Cannot find module 'dist/server/index.js'`. Always restore `dist/server/` from `Documents/SpockWebUI/dist/server/` backup.

## favicon.ico Fix (Multi-Resolution ICO)

**Symptom:** Browser tab shows old default icon.
**Root cause:** `index.html` references `/favicon.ico`. The old `.ico` (May 19) was still being served.

**Fix — Convert Spock PNG to multi-res ICO via Python/Pillow:**
```python
from PIL import Image
src = '/mnt/c/Users/thadd/hermes-web-ui/packages/client/public/spock-avatar.png'
dst = '/mnt/c/Users/thadd/hermes-web-ui/packages/client/public/favicon.ico'
img = Image.open(src)
if img.mode != 'RGBA':
    img = img.convert('RGBA')
sizes = [(16,16), (32,32), (64,64), (128,128)]
frames = [img.resize(s, Image.LANCZOS) for s in sizes]
frames[0].save(dst, format='ICO', sizes=sizes, append_images=frames[1:])
```
Then copy to `dist/client/favicon.ico` and backup to `~/.hermes/spock-protector/packages/client/public/favicon.ico`.

**System ImageMagick alternative (if available):**
```bash
convert /mnt/c/Users/thadd/hermes-web-ui/packages/client/public/spock-avatar.png \
  -resize 16x16 /tmp/favicon-16.png \
  -resize 32x32 /tmp/favicon-32.png \
  -resize 64x64 /tmp/favicon-64.png \
  -resize 128x128 /tmp/favicon-128.png
convert /tmp/favicon-16.png /tmp/favicon-32.png /tmp/favicon-64.png /tmp/favicon-128.png \
  /mnt/c/Users/thadd/hermes-web-ui/packages/client/public/favicon.ico
```

> **Pillow over system tools:** When system `pip` and `ImageMagick` are unavailable, use the Python venv at `~/.hermes/hermes-agent/venv/bin/python3` which has Pillow installed.

## Protected Files (12 total)

| # | File | Customization |
|---|------|--------------|
| 1 | `packages/client/index.html` | `<title>Spock</title>`, favicon ref |
| 2 | `packages/client/public/favicon.ico` | Browser tab icon (multi-res Spock ICO) |
| 3 | `packages/client/public/favicon.png` | Browser tab icon (PNG backup) |
| 4 | `packages/client/public/logo.png` | Main Spock logo |
| 5 | `packages/client/public/spock-avatar.png` | Session profile avatar |
| 6 | `packages/client/src/assets/logo.png` | Sidebar logo |
| 7 | `packages/client/src/assets/thinking-dark.mp4` | Star Trek badge thinking animation |
| 8 | `packages/client/src/assets/thinking-light.mp4` | Star Trek badge thinking animation |
| 9 | `packages/client/src/components/layout/AppSidebar.vue` | "Spock" sidebar text |
| 10 | `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` | **Universal avatar** — all avatars render as Spock |
| 11 | `packages/client/src/components/hermes/chat/SessionListItem.vue` | Session list passes Spock image object |
| 12 | `vite.config.website.ts` | Chunk size config |

**Spock Protector registry:** `~/.hermes/spock-protector/PROTECTED_FILES.txt`
**Restore script:** `~/.hermes/spock-protector/restore-spock.sh` (accepts `--build`)
**Backup directory:** `~/.hermes/spock-protector/` mirrors repo paths for all protected files

> **Commit baseline:** Update `SPOCK_COMMIT` in all protector scripts whenever new Spock changes are committed. Current baseline includes all 12 protected files.

## Anti-Footgun Rules

- **ALWAYS** verify `pwd` and the repo path before making changes
- **ALWAYS** check `ps aux | grep hermes-web-ui` to see which server is actually running
- **NEVER** assume the server at `localhost:8648` is the correct one
- **NEVER** run builds on the old `~/hermes-webui-new` repo
- If the `.bat` launcher doesn't work, check if the **wrong** systemd service was re-enabled
- When starting the server, **do NOT** export `AUTH_DISABLED=1` — token auth is the default and preferred mode
- **Always clear stale bridge processes** after any WebUI restart to avoid orphaned `hermes_bridge.py` instances competing on the same IPC socket
- **Always verify dist/ build timestamp** after source code changes — source correctness does not guarantee the running server is serving it
- **Always restore dist/server/ from backup** if build times out (do not leave it empty)
- **Always use Python venv Pillow** when system ImageMagick is unavailable: `~/.hermes/hermes-agent/venv/bin/python3`

## 5. Server Management

### Start (with auth enabled, default — LOCAL build):
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
node dist/server/index.js
# Or in background:
nohup node dist/server/index.js > ~/.hermes-web-ui/server.log 2>&1 &
```

### Start with auth disabled (emergency only):
```bash
export AUTH_DISABLED=1
cd /mnt/c/Users/thadd/hermes-web-ui
node dist/server/index.js
```

### Health check:
```bash
curl http://127.0.0.1:8648/health
curl -sf "http://127.0.0.1:8648/health?token=$(cat ~/.hermes/webui/.token)"
```

### Check which server is running:
```bash
ps aux | grep "dist/server/index\|hermes-web-ui" | grep -v grep
ss -tlnp | grep ":8648 "
```

### Stop:
```bash
# Find PID of the LOCAL server
ps aux | grep "hermes-web-ui.*dist/server/index" | grep -v grep
kill <PID>
```

### Clean up orphaned bridge processes after restart:
```bash
# Check for duplicates
ps aux | grep "hermes_bridge\|agent-bridge" | grep -v grep
# Kill orphans (old PIDs from previous crashed server)
for pid in $(ps aux | grep "hermes_bridge" | grep -v grep | awk '{print $2}'); do
  kill $pid 2>/dev/null
done
```

## 5. The Broken Build Problem

**ENVIRONMENT ISSUE:** `npm run build` fails due to missing `rolldown` native binding (`@rolldown/binding-linux-x64-gnu`). This is an npm optional dependency bug.

### Workaround — Copy Pre-built Dist:
The old EKKO repo (`~/hermes-web-ui-ekko`) has a working pre-built dist with customizations:

```bash
# Kill current server
kill <PID>
sleep 2

# Copy pre-built custom dist from EKKO repo
cp -r ~/hermes-web-ui-ekko/dist/client/* /mnt/c/Users/thadd/hermes-web-ui/dist/client/

# Restart server
export AUTH_DISABLED=1
cd /mnt/c/Users/thadd/hermes-web-ui
node bin/hermes-web-ui.mjs start
```

### Future fix options:
1. Reinstall node_modules: `rm -rf node_modules package-lock.json && npm i`
2. Or fix the WSL node environment (switch to npm in WSL instead of Windows node)
3. Or build on Windows side where the binding exists

## 7. Complete Recovery Steps (If Everything Breaks)

### Recovery from Local Backup

The fastest recovery path is the local backup at `C:\Users\thadd\Documents\SpockWebUI`:

```bash
# 1. Stop current server
pkill -f "node dist/server/index.js" || true

# 2. Restore from backup (rsync back to live location)
rsync -avh --delete --exclude='node_modules' \
  "/mnt/c/Users/thadd/Documents/SpockWebUI/" \
  "/mnt/c/Users/thadd/hermes-web-ui/"

# 3. Reinstall dependencies if node_modules missing
# cd /mnt/c/Users/thadd/hermes-web-ui && npm install

# 4. Start server
node dist/server/index.js
```

**Backup contents:** ~139MB including `.git/`, `dist/`, source, assets, Spock customizations. Excludes `node_modules/` (reinstallable).

> See also: `references/security-auth-recovery-2026-05-21.md` for full audit+recovery detail.

If the server is wrong, auth is failing, and customizations are missing:

```bash
# 1. Kill wrong server + disable old auto-start (if pointing to old repo)
systemctl --user stop hermes-webui.service
# Edit service file to point to correct repo if needed:
#   WorkingDirectory=/mnt/c/Users/thadd/hermes-web-ui
#   ExecStart=/home/thadd/.hermes/node/bin/node dist/server/index.js
# Then:
systemctl --user daemon-reload
systemctl --user enable hermes-webui.service

# 2. Kill any remaining server processes
for pid in $(ps aux | grep "index.js" | grep -v grep | awk '{print $2}'); do kill $pid; done

# 3. Verify source files have Spock customizations
grep "Spock" /mnt/c/Users/thadd/hermes-web-ui/packages/client/index.html
ls -la /mnt/c/Users/thadd/hermes-web-ui/packages/client/src/assets/thinking-light.mp4
# Should be ~49KB (badge), not ~8MB (default girl)

# 4. Start correct server WITH auth enabled (default)
cd /mnt/c/Users/thadd/hermes-web-ui
nohup node dist/server/index.js > ~/.hermes-web-ui/server.log 2>&1 &

# 5. Clean up orphaned bridge processes
ps aux | grep "hermes_bridge" | grep -v grep
# Kill any PIDs that don't belong to the current server

# 6. Verify token file exists and .bat reads it
cat /home/thadd/.hermes/webui/.token
```

## 7. Anti-Footgun Rules

- **ALWAYS** verify `pwd` and the repo path before making changes
- **ALWAYS** check `ps aux | grep hermes-web-ui` to see which server is actually running
- **NEVER** assume the server at `localhost:8648` is the correct one
- **NEVER** run builds on the old `~/hermes-webui-new` repo
- If the `.bat` launcher doesn't work, check if the **wrong** systemd service was re-enabled
- When starting the server, **do NOT** export `AUTH_DISABLED=1` — token auth is the default and preferred mode
- **Always clear stale bridge processes** after any WebUI restart to avoid orphaned `hermes_bridge.py` instances competing on the same IPC socket

> See also: `references/spock-protector-3-layer-defense.md` for the complete branding lockdown system, and `references/spock-protector-session-2026-05-22.md` for the systemd PATH fix and exact service file.

## 8. File Locations Reference

| File | Path |
|------|------|
| Correct repo | `/mnt/c/Users/thadd/hermes-web-ui` |
| Old wrong repo | `/home/thadd/hermes-webui-new/` |
| Old EKKO repo (pre-built dist) | `/home/thadd/hermes-web-ui-ekko/` |
| Customize script | `/mnt/c/Users/thadd/.openclaw/workspace/scripts/apply-webui-customizations.sh` |
| Desktop launcher | `C:\Users\thadd\Desktop\Launch Hermes WebUI.bat` |
| Server log | `~/.hermes-web-ui/server.log` |
| Auth token file | `~/.hermes-web-ui/.token` |
| Dist output | `/mnt/c/Users/thadd/hermes-web-ui/dist/client/` |
| Thinking badge source | `/mnt/c/Users/thadd/.hermes/images/startrek badge.mp4` |
