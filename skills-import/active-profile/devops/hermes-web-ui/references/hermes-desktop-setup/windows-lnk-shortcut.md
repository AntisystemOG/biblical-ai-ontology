# Windows `.lnk` Shortcut for WSL-Based Web UI

Native Windows shortcuts (`.lnk`) are cleaner than `.bat` files: no flashing console window, no cmd escape headaches, and they support custom icons natively.

## Creating via PowerShell

Use `WScript.Shell` COM object:

```powershell
$Wsh = New-Object -ComObject WScript.Shell
$Lnk   = $Wsh.CreateShortcut('C:\Users\<user>\Desktop\Hermes WebUI.lnk')
$Lnk.TargetPath       = 'C:\Windows\System32\wsl.exe'
$Lnk.Arguments        = 'bash -c '"'"'cd /mnt/c/Users/<user>/hermes-web-ui \&\& node bin/hermes-web-ui.mjs start'"'"''
$Lnk.IconLocation     = 'C:\Users\<user>\hermes-web-ui\packages\client\public\favicon.ico,0'
$Lnk.WorkingDirectory = 'C:\Users\<user>\hermes-web-ui'
$Lnk.Description      = 'Launch Hermes Web UI (port 8648)'
$Lnk.Save()
```

## Key Points

- **TargetPath must be `wsl.exe`** — not `node.exe` or a `.bat`. The server runs inside WSL because it spawns Python venv processes and needs the Linux PATH and env.
- **Arguments use `bash -c`** with standard bash `&&` chaining. No `^` escaping needed because PowerShell passes the string literal to `wsl.exe`.
- **`bin/hermes-web-ui.mjs start`** works when `dist/` exists (built via `npm run build` or the `prepare` hook). The CLI polls `/health` and auto-opens the browser via `start http://...`.
- **IconLocation** can point to any `.ico`. The stock `packages/client/public/favicon.ico` is a sensible default. If the repo has custom branding (e.g. a Star Trek avatar), point to that `.ico` instead.
- **Naming convention:** The user's Desktop accumulates multiple launchers over sessions. When creating a new `.lnk`, first remove old/conflicting ones (`Spock WebUI.lnk`, `Hermes WebUI.lnk`, `launch.vbs`, `create-shortcut.ps1`) so there is exactly one canonical launcher.

## Pitfall: Stale `dist/` after git pull or local changes

The `bin/hermes-web-ui.mjs` entrypoint expects `dist/server/index.js`. After pulling updates or stashing/restoring local changes, rebuild before the shortcut will work:

```bash
cd /mnt/c/Users/<user>/hermes-web-ui
npm run build
```

If `dist/server/` is missing, the shortcut WSL window flashes and closes. Verify:

```bash
ls dist/server/
# expected: agent-bridge  index.js  index.js.map
```

## Alternative: Direct Node (no CLI wrapper)

For explicit env control, bypass the `hermes-web-ui.mjs` wrapper:

```powershell
$Lnk.Arguments = 'bash -c '"'"'export HERMES_WEB_UI_HOME=/home/<user>/.hermes/webui PORT=8648; cd /mnt/c/Users/<user>/hermes-web-ui && node dist/server/index.js'"'"''
```

This loses the built-in health-poll + auto-browser-open; add your own `start http://...` in a `.bat` or use a `.url` file for the browser part.

## Alternative: `.bat` Launcher with Health Check (Visible Console)

When a `.lnk` shortcut silently fails (VBS disabled by policy, `wsl.exe` argument parsing issues, or user just wants to see status), a visible `.bat` file is the right fallback:

```batch
@echo off
REM Start Hermes WebUI and open browser
REM Uses wsl bash -c with nohup to avoid ^ escape issues

echo Checking if server is already running...
wsl ss -tlnp | findstr ":8648" >nul
if %errorlevel% == 0 (
    echo WebUI already running.
    start http://localhost:8648
    timeout /t 3 /nobreak >nul
    exit /b 0
)

echo Starting Hermes WebUI in background...
wsl bash -c "cd /mnt/c/Users/thadd/hermes-web-ui && nohup node bin/hermes-web-ui.mjs start > /dev/null 2>&1 &"

echo Waiting for server (up to 30s)...
set /a waited=0
:wait_loop
wsl curl -sf http://127.0.0.1:8648/health >nul 2>&1
if %errorlevel% == 0 goto server_ready
set /a waited+=1
if %waited% geq 30 goto timeout_failed
timeout /t 1 /nobreak >nul
goto wait_loop

:server_ready
echo Server ready. Opening browser...
start http://localhost:8648
exit /b 0

:timeout_failed
echo ERROR: Server did not start within 30 seconds.
pause
exit /b 1
```

**Why `.bat` is the right fallback when `.lnk` fails:**
- Visible console shows status messages and errors
- `wsl bash -c "... nohup ... &"` works reliably — no `^` escape issues
- Health poll loop confirms the server is actually serving before opening browser
- If a systemd service or stale process is squatting port 8648, the `wsl ss` + `wsl curl` checks surface the problem

**Recommended approach:** Create the `.bat` on the Desktop for the user to try first. If it works and they prefer a cleaner `.lnk`, use the PowerShell `.lnk` builder shown above. If the `.lnk` is silently broken, keep the `.bat` as the canonical launcher.

## `.url` Internet Shortcut (No Server Start)

If the server is already running (e.g. via cron or systemd), create a lightweight `.url` file:

Create `C:\Users\<user>\Desktop\Spocks WebUI.url`:
```ini
[InternetShortcut]
URL=http://172.24.60.180:8648/
IconFile=C:\Users\<user>\Desktop\spock-icon.ico
IconIndex=0
```

WSL IP is dynamic — run `hostname -I | awk '{print $1}'` inside WSL and update the URL after restarts.
