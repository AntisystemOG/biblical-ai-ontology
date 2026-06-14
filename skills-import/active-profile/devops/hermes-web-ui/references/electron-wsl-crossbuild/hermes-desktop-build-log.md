# Hermes Desktop Build Session Log

**Date**: 2026-05-19
**Repo**: https://github.com/fathah/hermes-desktop
**Version cloned**: 0.4.3

## Environment
- WSL2 (6.6.114.1-microsoft-standard-WSL2)
- Node.js v22.22.3 / npm 10.9.8
- `DISPLAY=:0` set

## Commands Run

```bash
cd /mnt/c/Users/thadd/.openclaw/workspace
git clone https://github.com/fathah/hermes-desktop.git
cd hermes-desktop
npm install          # ~5 minutes, completed successfully
npm run dev          # started Vite dev server on 127.0.0.1:5173
npm run build        # completed successfully (main + preload + renderer)
npm run build:win    # timed out (300s) during electron-builder packaging
```

## Build Artifacts Produced

- `out/main/index.js` (430KB) - main process bundle
- `out/preload/index.js` (15.8KB) + `askpass.js` (0.83KB) - preload scripts
- `out/renderer/assets/` - Vite client bundle (~4MB of assets incl fonts)
- `dist/win-unpacked/` - partial Windows package (missing NSIS installer step)

## Error Encountered by User

```
Cannot read properties of undefined (reading 'onInstallProgress')
```

**Location**: `src/renderer/src/screens/Install/Install.tsx:36`
**Code**: `window.hermesAPI.onInstallProgress(...)`

**Root cause**: User was opening `http://127.0.0.1:5173` in a regular browser. The `hermesAPI` object is injected by `src/preload/index.ts` via `contextBridge.exposeInMainWorld("hermesAPI", hermesAPI)`, which only works inside the Electron runtime. A browser has no preload script, so `window.hermesAPI` is `undefined`.

## Key Files for Debugging Preload Issues

| File | Purpose |
|------|---------|
| `src/preload/index.ts` | Defines `hermesAPI` object, exposes via `contextBridge` |
| `src/main/index.ts` | Sets up IPC handlers (e.g. `"check-install"`, `"start-install"`) |
| `src/renderer/src/App.tsx` | Entry point that calls `window.hermesAPI.checkInstall()` |
| `src/renderer/src/screens/Install/Install.tsx` | Uses `window.hermesAPI.onInstallProgress` |
| `out/preload/index.js` | Compiled preload (verify this exists after build) |

## First-Run Flow (Hermes Desktop)

App checks on startup (`App.tsx:runInstallCheck`):
1. Get connection config (`getConnectionConfig()`) - mode: local | remote | ssh
2. If SSH: start tunnel, go to main
3. If remote: test connection, go to main on success
4. If local: `checkInstall()` status:
   - Not installed -> Welcome screen
   - No API key -> Setup screen  
   - Everything OK -> Main screen
5. After UI mounts: lazy `verifyInstall()` in background

## Packaging Notes

- `electron-builder` config in `electron-builder.yml`
- Windows target: NSIS installer (`artifactName: ${name}-${version}-setup.exe`)
- `npmRebuild: false` set in config (skips native rebuilds)
- WSL cannot build Windows `.exe` installer because `makensis` is missing
- `win-unpacked/` directory is usable as a portable app but has no `resources/` folder (electron-builder timed out before completing)
