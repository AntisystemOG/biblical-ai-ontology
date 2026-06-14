# WebUI Update and Restore — Full Session Reference

## Context
May 2026 session: Hermes WebUI at `/home/thadd/hermes-web-ui` updated from v0.6.0 base, pulling 55 new commits from `origin/main`.

## What Was Done

1. **Profile backup**: `hermes profile export plc-coder` → `/home/thadd/plc-coder.tar.gz`
2. **Hermes core update**: `hermes update` (150 commits, venv recreated)
3. **WebUI source update**: `git fetch origin`, `git merge origin/main` (55 commits)
4. **Dependencies**: `npm install` — completed in 1 minute
5. **Build**: `npm run build` — client 18.85s + server 824ms
6. **Customizations verified**: `logo.png`, `favicon.ico`, `thinking-*.mp4`, `spock-avatar.png` all present in `dist/`
7. **Server restart**: Background process at `0.0.0.0:8648`

## Key Learning: Upstream Already Includes Spock Branding

This session revealed that the upstream fork (`AntisystemOG/hermes-web-ui`) already includes Spock branding assets. The restore script must **check first** before attempting to copy from local image directories.

**Check command** (run before any restore):
```bash
ls -la /home/thadd/hermes-web-ui-ekko/packages/client/public/ | grep -E "spock|logo|favicon"
ls -la /home/thadd/hermes-web-ui-ekko/packages/client/src/assets/ | grep thinking
```

If present with recent timestamps, only verify `dist/` after build.

## Pitfall: `git reset --hard` Blocked

The user explicitly blocked `git reset --hard origin/main` in this session. Always use `git merge origin/main` for WebUI updates.

## Server Start Command

```bash
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=8648 BIND_HOST=0.0.0.0 WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace
/home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js
```

Use `terminal(background=true)` in Hermes to start, then `process(action='poll')` to check health.
