# Source-Level Re-branding (Pre-Build)

The cleanest way to re-brand Hermes WebUI: edit Vue source files, then rebuild.
This is more maintainable than post-build `sed` surgery on compiled JS.

## Files to Edit

### 1. Browser Tab Title
`packages/client/index.html`
```html
<title>Spock</title>
```

### 2. Sidebar Logo + Text
`packages/client/src/components/layout/AppSidebar.vue`
```vue
<img :src="logoPath" alt="Spock" class="logo-img" />
<span class="logo-text">Spock</span>
```

The logo image itself is referenced as `/logo.png` — copy your replacement to:
- `packages/client/public/logo.png` (served at runtime)
- `packages/client/src/assets/logo.png` (fallback for bundler)

### 3. Login Screen Logo
`packages/client/src/views/LoginView.vue`
```vue
<img src="/logo.png" alt="Spock" width="80" height="80" />
```

### 4. Chat Empty State
`packages/client/src/components/hermes/chat/MessageList.vue`
```vue
<img src="/logo.png" alt="Spock" class="empty-logo" />
```

### 5. Message Avatar & Group Chat
`packages/client/src/components/hermes/chat/MessageItem.vue`
`packages/client/src/components/hermes/group-chat/GroupMessageList.vue`

Both reference `/logo.png` — already covered by the public/logo.png swap.

## Build & Restart

If you're also tweaking `vite.config.website.ts` (e.g., raising `chunkSizeWarningLimit` to suppress large-chunk warnings during build), commit that change before building.

```bash
cd ~/hermes-web-ui-ekko

# Optional: edit vite.config.website.ts to suppress chunk warnings (user preference)
#   build: { ... chunkSizeWarningLimit: 1000, ... }

npm run build

# Kill old server
pkill -f "dist/server/index.js"
sleep 1

# Start fresh (match your existing launch method — .bat, systemd, etc.)
```

## Windows Desktop Icon Launch Pattern

This user's setup uses a WSL `.bat` file on the Windows desktop:

**`Start Hermes WebUI.bat`:**
```batch
@echo off
set WSL_IP=172.24.60.180
set PORT=8648

wsl curl -s http://127.0.0.1:%PORT%/health ^| findstr "ok" ^>nul
if %errorlevel% == 0 (
    start http://%WSL_IP%:%PORT%/
    exit /b 0
)

wsl env HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=%PORT% \
  BIND_HOST=0.0.0.0 WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace \
  AUTH_DISABLED=1 /home/thadd/node26/bin/node \
  /home/thadd/hermes-web-ui-ekko/dist/server/index.js ^&

timeout /t 6 /nobreak ^>nul
start http://%WSL_IP%:%PORT%/
```

After rebuilding, the user double-clicks the desktop icon to relaunch.

## Verification Checklist

- [ ] Tab title shows "Spock"
- [ ] Sidebar shows Spock icon + "Spock" text  
- [ ] Login screen shows Spock icon
- [ ] Empty chat state shows Spock icon
- [ ] Hard-refresh browser (`Ctrl+F5`) to bust cache
