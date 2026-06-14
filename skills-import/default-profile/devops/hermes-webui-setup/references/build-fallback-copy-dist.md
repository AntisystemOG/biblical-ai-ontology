# WebUI Build Failure: Copy Pre-built dist from Fork

## Problem
`npm run build` (or `npx vite build`) fails in the EKKOLearnAI repo due to:
- Missing native binding (`rolldown` → `Error: Cannot find native binding`)
- Wrong Node version (<23 required, older Node installed)
- Corrupted `node_modules` / `package-lock.json`

## Solution: Pre-built `dist/client/` Copy

If the user has a second repo (e.g., `~/hermes-web-ui-ekko`) with a **pre-built, customized `dist/`**, copy it over the correct repo's `dist/client/`:

```bash
# 1. Kill running server
pkill -f "dist/server/index.js"
sleep 2

# 2. Back up current dist (optional preservation)
cp -r /mnt/c/Users/thadd/hermes-web-ui/dist/client \
      /mnt/c/Users/thadd/hermes-web-ui/dist/client.bak.$(date +%s) 2>/dev/null

# 3. Copy custom pre-built dist from the fork's built output
cp -r /home/thadd/hermes-web-ui-ekko/dist/client/* \
      /mnt/c/Users/thadd/hermes-web-ui/dist/client/

# 4. Verify the custom assets landed
grep "Spock" /mnt/c/Users/thadd/hermes-web-ui/dist/client/index.html
ls -la /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/mp4/

# 5. Restart server with auth disabled
export AUTH_DISABLED=1
cd /mnt/c/Users/thadd/hermes-web-ui
nohup node bin/hermes-web-ui.mjs start > ~/.hermes-web-ui/server.log 2>&1 &
sleep 3
curl -s http://127.0.0.1:8648/ | head -3
```

## When This Works vs. When It Doesn't

**Works when:**
- The pre-built `dist/` is from the SAME upstream base (or close enough)
- The server (`dist/server/index.js`) is built separately and still valid
- Only client-side assets (HTML, CSS, JS, images, videos) need updating

**Does NOT work when:**
- The server code itself needs changes (API routes, bridge logic, config)
- The `dist/server/index.js` is missing, broken, or from a different branch
- The client dist is from a radically different upstream version with incompatible API contracts

## How Customizations Get Into the Pre-built dist

Typical customization commit (from user's fork):
```
commit f636b1b — feat: rebrand to Spock - icon, sidebar text, browser title
 files changed:
   packages/client/index.html          (title: "Spock")
   packages/client/public/logo.png     (new Spock logo)
   packages/client/src/assets/logo.png (new Spock logo)
   packages/client/src/assets/thinking-dark.mp4   (Star Trek badge ~49KB)
   packages/client/src/assets/thinking-light.mp4  (Star Trek badge ~49KB)
   packages/client/src/components/layout/AppSidebar.vue (logo alt="Spock", text="Spock")
   vite.config.website.ts              (chunk size adjustment)
```

These source changes get compiled by `vite build` into `dist/client/`:
- `index.html` → `<title>Spock</title>`
- `logo.png` → served at root
- MP4 videos → hashed into `assets/mp4/thinking-light-*.mp4`
- Vue component templates → inlined into compiled JS bundles

## Bringing Customizations into Source (Long-term Fix)

To make the customizations reproducible on the correct repo:

```bash
cd /mnt/c/Users/thadd/hermes-web-ui

# Add user's fork as a remote
git remote add spock https://github.com/AntisystemOG/hermes-web-ui.git
git fetch spock main --depth=20

# Restore specific customization files from fork's commit
git restore --source=spock/main \
  packages/client/index.html \
  packages/client/public/logo.png \
  packages/client/src/assets/logo.png \
  packages/client/src/assets/thinking-dark.mp4 \
  packages/client/src/assets/thinking-light.mp4 \
  packages/client/src/components/layout/AppSidebar.vue \
  vite.config.website.ts

# Now these source files are customized. Rebuild when environment is fixed:
# npm run build   →  produces custom dist/client/
```

## Verification Checklist

After copying pre-built dist and restarting:
- [ ] `curl -s http://127.0.0.1:8648/ | head -2` shows custom `<title>`
- [ ] `ls dist/client/assets/mp4/` shows custom video (not 8MB default girl)
- [ ] `grep "Spock" dist/client/assets/js/*.js` finds sidebar text in compiled JS
- [ ] Browser opens without login prompt (if `AUTH_DISABLED=1` + `?token=fake-token`)
- [ ] Server PID shows `node bin/hermes-web-ui.mjs` (not `python3 server.py`)

## Remember: Always Kill Stale Servers First

If `ss -tlnp | grep :8648` shows ANY process, kill it before copying dist or restarting:
```bash
# Kill all known occupants
pkill -f "hermes-web-ui.mjs"
pkill -f "server\.py"
rm -f ~/.hermes-web-ui/server.pid
# Also disable systemd auto-respawn
systemctl --user stop hermes-webui.service 2>/dev/null
systemctl --user disable hermes-webui.service 2>/dev/null
```
