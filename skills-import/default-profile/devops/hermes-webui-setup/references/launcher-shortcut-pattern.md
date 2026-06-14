# Windows Desktop Shortcut Pattern for WSL-Bound Hermes WebUI

## Goal
A double-clickable Windows Desktop `.lnk` that launches the EKKOLearnAI Hermes WebUI (Node.js stack) running from `/mnt/c/Users/thadd/hermes-web-ui` inside WSL.

## What NOT to do
- Do NOT build a shortcut pointing to `wsl.exe` with complex nested bash arguments — Windows `.lnk` argument parsing is brittle and fails silently.
- Do NOT use `xdg-open` from WSL — WSL does not have a browser opener.
- Do NOT auto-bash-execute without first checking what server is already running on port 8648.

### CRITICAL: Windows `start` command syntax for `.bat` files

Windows `cmd /c start` interprets the **first quoted argument as the window title**, not the URL.

**Correct (opens browser):**
```bat
start "" "http://localhost:8648"
:: or
start "" "http://localhost:8648/?token=fake-token"
```

**Wrong (silently opens nothing, window flashes closed):**
```bat
start "http://localhost:8648"        :: URL treated as window title
cmd /c start "http://localhost:8648" :: same bug
```

This is a silent-failure mode: the `.bat` appears to run and close immediately with no visible error because `start` creates an empty window titled `"http://localhost:8648"` and then exits. The browser never opens. The fix is always `start "" "url"`.

**Related:** In VBS wrappers, the escaping is `WshShell.Run "cmd /c start "" """"http://localhost:8648""""",`. The `""` pair produces the empty title; `""http://...""""` encodes the double-quoted URL.

## Correct approach: PowerShell VBS wrapper

### Step 1 — Verify nothing wrong is squatting on port 8648

Before creating the shortcut, check what's actually running on port 8648 RIGHT NOW:

```bash
ss -tlnp | grep :8648
lsof -iTCP:8648 -sTCP:LISTEN
curl -s http://127.0.0.1:8648/ | head -2   # EKKOLearnAI: <!doctype html> + <html lang="zh-CN">
```

### Critical: Check for systemd user service auto-respawning wrong server

If `lsof` shows Python (`server.py`) on port 8648, and killing it results in a new PID seconds later:

```bash
systemctl --user status hermes-webui.service 2>/dev/null
cat ~/.config/systemd/user/hermes-webui.service 2>/dev/null
```

If a systemd service with `Restart=on-failure` is present and points to the wrong repo:
```bash
systemctl --user stop hermes-webui.service
systemctl --user disable hermes-webui.service
```

Then kill the wrong process and clear its PID file:
```bash
pkill -f "server\.py"
rm -f ~/.hermes-web-ui/server.pid
```

### Distinguish which server is running by HTTP response

| Server | Response fingerprint |
|--------|---------------------|
| EKKOLearnAI (correct) | `HTML lang="zh-CN"` |
| Old Spock Python (wrong) | `<title>Spock</title>`, git conflict markers `<<<<<<<` |

Use `curl -s http://127.0.0.1:8648/ | head -5` to identify before declaring the server correct.

## Step 2 — Create the launcher script (inside WSL repo)

Write `launch.vbs` at the repo root (`C:\Users\thadd\hermes-web-ui\launch.vbs`):

```vbs
Set WshShell = CreateObject("WScript.Shell")

' Start Hermes WebUI from WSL — runs hidden
WshShell.Run "wsl bash -c """" " & _
    "cd /mnt/c/Users/thadd/hermes-web-ui \" & _
    "&& node bin/hermes-web-ui.mjs start""""", 0, False

' Poll health endpoint (max 30s)
Dim waited : waited = 0
Do While waited < 30
    WScript.Sleep 1000
    If WshShell.Run("wsl bash -c """"curl -sf http://127.0.0.1:8648/health > /dev/null 2>&1""""", 0, True) = 0 Then Exit Do
    waited = waited + 1
Loop

If waited >= 30 Then
    MsgBox "Hermes WebUI did not start within 30 seconds.", vbCritical, "Launch Failed"
    WScript.Quit 1
End If

' Open browser on Windows side
WshShell.Run "cmd /c start "" """"http://localhost:8648""""", 0, False
```

#### Step 2 — Verify auth is disabled (recommended)

If auth is **not** disabled, the browser will show a login screen. The cleanest fix is to disable auth server-side so no token is ever needed:

```bash
# WSL: add to ~/.hermes/.env if not already present
grep "^AUTH_DISABLED=1" ~/.hermes/.env || echo "AUTH_DISABLED=1" >> ~/.hermes/.env

# Restart the server so the env var is picked up
# (the VBS wrapper below does this automatically via bash -lc which sources .bashrc -> .env)
```

If auth **must** remain enabled, modify the VBS to inject the token from `~/.hermes-web-ui/.token` into the URL:

```vbs
' ... after health check passes ...
Dim tokenCmd, tokenStream, tokenLine, token
Set tokenCmd = WshShell.Exec("wsl cat ~/.hermes-web-ui/.token")
Set tokenStream = tokenCmd.StdOut
tokenLine = tokenStream.ReadLine()
token = Trim(tokenLine)
WshShell.Run "cmd /c start "" """"http://localhost:8648/?token=" & token & """""", 0, False
```

Or, simpler: use a `.bat` (visible, debuggable) that reads the token with `for /f ... in ('wsl cat ...')`. See `references/auth-debugging.md` for the token-injection `.bat` pattern. The VBS above is a clean silent `.lnk` target — use `.bat` for first-run debugging.

## Step 3 — Create the `.lnk` via PowerShell

On Windows side, run the following PowerShell **as a single command** (via `powershell.exe -Command` or a `.ps1` file):

```powershell
$Wsh = New-Object -ComObject WScript.Shell
$Lnk = $Wsh.CreateShortcut('C:\Users\thadd\Desktop\Hermes WebUI.lnk')
$Lnk.TargetPath   = 'C:\Windows\System32\wscript.exe'
$Lnk.Arguments    = '//B "C:\Users\thadd\hermes-web-ui\launch.vbs"'
$Lnk.IconLocation = 'C:\Users\thadd\hermes-web-ui\packages\client\public\favicon.ico,0'
$Lnk.WorkingDirectory = 'C:\Users\thadd\hermes-web-ui'
$Lnk.Description  = 'Launch Hermes WebUI (EKKOLearnAI repo)'
$Lnk.WindowStyle = 7  ' hidden
$Lnk.Save()
```

### Step 3 — Verify before declaring success

```powershell
# Check PID matches expected repo
ps -ef | grep -E "hermes_web_ui|node.*index"
# Should show: node bin/hermes-web-ui.mjs start
# NOT: python3 /home/thadd/hermes-webui-new/server.py
```

### Step 4 — Cleanup old/conflicting launchers

Before creating the new shortcut, remove any stale `.lnk`, `.bat`, `.vbs`, or `.ps1` files that may point to the wrong repo:

```powershell
Remove-Item 'C:\Users\thadd\Desktop\Hermes WebUI.lnk' -ErrorAction SilentlyContinue
Remove-Item 'C:\Users\thadd\hermes-web-ui\launch-webui.*' -ErrorAction SilentlyContinue
```

## Pitfall: stale Python process occupying port 8648

If `ss -tlnp | grep :8648` shows a Python process (`server.py`) from `~/hermes-webui-new/` or a prior Node process with stale PID file, the EKKOLearnAI `hermes-web-ui.mjs start` will fail with "already running" or "port in use."

**Check first:**
```bash
curl -s http://127.0.0.1:8648/health | grep uptime_seconds
lsof -iTCP:8648 -sTCP:LISTEN
```

**Kill the wrong occupant:**
```bash
pkill -f "hermes-web-ui.mjs"
pkill -f "server\.py"
rm -f ~/.hermes-web-ui/server.pid
```

Then relaunch the correct EKKOLearnAI server.

## Pitfall: VBS execution disabled by policy

Some Windows environments disable `wscript.exe` via Group Policy. If double-clicking the `.lnk` does nothing:

1. Enable WScript temporarily via `cscript //B launch.vbs` or by allowing `.vbs` in Windows Security settings.
2. Alternatively, replace VBS with a PowerShell `.ps1` that runs `-WindowStyle Hidden`.

## Pitfall: user has multiple WebUI repos; default is EKKOLearnAI

Thad explicitly established: "when I say web ui or webui I am referring to the EKKOLearnAI repo." Do not pivot to other repos (`hermes-webui-new`, etc.) even if they appear to be running. If another repo is running, stop it and start the EKKOLearnAI one.
