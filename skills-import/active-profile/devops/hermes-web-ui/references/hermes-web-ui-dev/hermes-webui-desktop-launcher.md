# Hermes WebUI Desktop Launcher Pattern

## Context

On WSL + Windows setups, users often double-click a `.bat` shortcut on the Desktop to start the WebUI. This bypasses `npm run dev` and runs the **pre-built** server directly from `dist/`.

## How to Spot It

```
Desktop
└── Start Hermes WebUI.bat
```

Inside the `.bat`:
```batch
wsl env HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui \
  PORT=8648 BIND_HOST=0.0.0.0 \
  /home/thadd/node26/bin/node \
  /home/thadd/hermes-web-ui-ekko/dist/server/index.js
```

**Key tell:** the path is `dist/server/index.js`, not `npm run dev` or a live dev server.

## What This Means for Changes

- **Logo/css changes to `packages/client/public/` → NOT reflected live**
- **Must copy asset to `dist/client/` OR rebuild** to see changes
- **Rebuild command** (when ready to make it permanent):
  ```bash
  cd /home/thadd/hermes-web-ui-ekko
  npm run build
  ```

## Quick-Test vs Permanent Change

| Goal | Action | Persistence |
|------|--------|-------------|
| Preview a logo swap | `cp new-logo.png dist/client/logo.png` + restart server | Lost on next `npm run build` |
| Make it stick | `cp new-logo.png packages/client/public/logo.png` + `cp new-logo.png packages/client/src/assets/logo.png` + `npm run build` | Survives rebuilds |

## Restart Procedure

If server is running from `dist/`:
```bash
# Find and kill the running node process
kill $(pgrep -f "dist/server/index.js")

# Re-launch (or tell user to double-click the .bat again)
env HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=8648 BIND_HOST=0.0.0.0 \
  /home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js &
```

## Cache-Busting

After any logo/asset change, tell the user to **hard-refresh** the browser:
- Windows: `Ctrl + F5` or `Ctrl + Shift + R`
- macOS: `Cmd + Shift + R`
