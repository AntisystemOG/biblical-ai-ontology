# WSL Batch File Escaping Pitfall

## Symptom
Double-clicking the Windows `.bat` shortcut opens the browser to `http://172.24.60.180:8648/` but the page shows "This site can't be reached." The server never actually started — port 8648 is silent.

## Root Cause

CMD-style `^` escape characters inside a `wsl` command are passed **literally** to bash, which does not recognize `^` as an escape character. The server command crashes silently because `^` becomes literal.

**Broken pattern (CMD-only escaping):**
```batch
wsl env HERMES_WEB_UI_HOME=... PORT=8648 ... /home/thadd/node26/bin/node ... ^> /dev/null 2^>^&1 ^&
```

Bash receives the command with literal `^` characters:
```bash
env ... node ... ^> /dev/null 2^>^&1 ^&
```
Since `^` is not a bash escape, bash treats `^>` as a literal token, `^&` as a literal `&`, and the redirections fail. The server never starts and the `.bat` window flashes away before the error is visible.

## Correct Pattern

Use `wsl bash -c` with a proper bash double-quoted string containing standard bash redirections:

```batch
@echo off
set WSL_IP=172.24.60.180
set PORT=8648

echo Checking if Web UI is running...
wsl bash -c "curl -s http://127.0.0.1:%PORT%/health | grep -q ok"
if %errorlevel% == 0 (
    echo Already running. Opening browser...
    start http://%WSL_IP%:%PORT%/
    exit /b 0
)

echo Starting Web UI server in WSL...
wsl bash -c "export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui PORT=%PORT% BIND_HOST=0.0.0.0 WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace AUTH_DISABLED=1; nohup /home/thadd/node26/bin/node /home/thadd/hermes-web-ui-ekko/dist/server/index.js > /dev/null 2>&1 &"

timeout /t 5 /nobreak >nul
start http://%WSL_IP%:%PORT%/
timeout /t 2 /nobreak >nul
exit /b 0
```

Inside the `bash -c` string:
- `> /dev/null` redirects stdout
- `2>&1` redirects stderr to stdout (which is `/dev/null`)
- `nohup ... &` runs the server detached from the terminal session

## Key Rule

| Where escaping happens | Use this style |
|---|---|
| Inside `.bat` for CMD itself | `^>`, `^|`, `^&` |
| Inside `.bat` passed to `wsl bash -c` | Standard bash: `>`, `>>`, `2>&1`, `&` |
| Inside `.bat` passed to `wsl` directly (no `bash -c`) | DO NOT — `wsl` passes raw args to bash |

## Verification

After running the fixed `.bat`:
```bash
# In WSL:
ss -tlnp | grep 8648
# Should show node listening

curl -s http://127.0.0.1:8648/health
# Should return JSON with status: ok
```

## Shortcut Icon (.lnk) Notes

For a proper `.lnk` shortcut with custom icon (not `.url`):
1. Set `TargetPath` to the `.bat` file — NOT Chrome directly
2. Set `IconLocation` to the `.ico` file
3. `WindowStyle = 7` (minimized) prevents CMD window flash

**Pitfall:** Setting `TargetPath` to `chrome.exe` with arguments creates a shortcut that only opens Chrome — it never runs the batch file that starts the server.
