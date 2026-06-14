# fathah/hermes-desktop Client Setup

A community Electron desktop app that connects to a local Hermes backend via the
`api_server` platform adapter.

## Architecture

- **Frontend**: React + Electron + Vite + Tailwind CSS v4
- **Backend**: Hermes `api_server` platform (OpenAI-compatible HTTP API on port 8642)
- **Communication**: Electron preload script injects `window.hermesAPI` (ipcRenderer)

## Prerequisites

1. **Hermes agent with `api_server` enabled**
2. **Node.js 20+ and npm**
3. **Windows PowerShell/CMD** (Electron needs a real GUI; cannot run in WSL text mode)

## Enabling `api_server` Platform

Add to `~/.hermes/config.yaml`:

```yaml
platforms:
    api_server:
        enabled: true
        extra:
            host: 127.0.0.1
            port: 8642
```

Restart the gateway:

```bash
hermes gateway run --replace
```

Verify it is listening:

```bash
curl http://127.0.0.1:8642/health
# → {"status": "ok", "platform": "hermes-agent"}
```

## Running Dev Mode (Windows)

```powershell
git clone https://github.com/fathah/hermes-desktop.git
cd hermes-desktop
npm install           # installs electron-vite + dependencies
npm run dev           # starts Vite dev server + Electron window
```

The Vite dev server runs on `http://127.0.0.1:5173`. **Do not open this in a
browser** — the app requires Electron's preload APIs (e.g.
`window.hermesAPI.onInstallProgress`). Opening in Chrome will fail with
`Cannot read properties of undefined (reading 'onInstallProgress')`.

## First-Run Configuration

When the Electron window opens, click "Connect to Remote Hermes" and enter:

- **URL**: `http://127.0.0.1:8642`
- **API Key**: leave empty for unauthenticated local mode (default when no
  `API_SERVER_KEY` or `platforms.api_server.key` is configured)

For authenticated mode, set an API key:

```bash
hermes config set platforms.api_server.key YOUR_SECRET_KEY
```

Then use `Bearer YOUR_SECRET_KEY` in the desktop app's API key field.

## Building Installer

```powershell
npm run build:win
# Output: dist/hermes-desktop Setup 0.4.3.exe
```

**WSL limitation**: `npm run build:win` from WSL fails because NSIS
(`makensis`) is a Windows-only installer tool. From WSL you can only get
`dist/win-unpacked/` (raw binaries, no .exe installer). Build from Windows
PowerShell instead.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Cannot read properties of undefined (reading 'onInstallProgress')" | Opened dev URL in a browser instead of Electron | Use Electron window, not Chrome |
| "Connection refused" on port 8642 | `api_server` platform not enabled | Add `platforms.api_server.enabled: true` to config.yaml and restart gateway |
| `electron-vite` not found | `npm install` incomplete | Run `npm install` from Windows PowerShell |
| Build fails with "makensis not found" | Building Windows installer from WSL | Build from Windows PowerShell instead |
