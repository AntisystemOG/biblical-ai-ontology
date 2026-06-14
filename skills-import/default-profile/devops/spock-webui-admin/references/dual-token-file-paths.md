---
source: session 2026-05-22
context: Windows batch launcher reading wrong token file path
---

# Dual Token File Paths in Hermes WebUI

## The Problem

The Hermes WebUI ecosystem has **two token file locations** that can diverge over time:

| Path | Purpose | Used By |
|------|---------|---------|
| `~/.hermes-web-ui/.token` | **Canonical** — server reads this on startup | Node.js server, systemd service |
| `~/.hermes/webui/.token` | **Legacy** — old path from earlier installs | Some launchers, backup scripts |

When these files have different tokens:
- The server accepts one token
- The launcher passes a different (stale) token in the URL
- User gets auth errors or "wrong token" behavior
- May lead to accidentally bypassing auth if the launcher passes `fake-token` or a stale value

## Detection

```bash
# Check both files exist and compare
diff ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null && echo "Same" || echo "DIFFERENT"

# Check file ages
ls -la ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null

# Check server log for which token it loaded
grep -i "token\|auth" /home/thadd/.hermes-web-ui/logs/server.log 2>/dev/null | tail -5
```

## Fix Options

### Option 1: Update launcher to read canonical path (recommended)

Edit the Windows batch launcher:
```batch
# In Launch Hermes WebUI.bat, change:
FOR /F "delims=" %%i IN ('wsl cat /home/thadd/.hermes/webui/.token') DO set WSLTOKEN=%%i

# To:
FOR /F "delims=" %%i IN ('wsl cat /home/thadd/.hermes-web-ui/.token') DO set WSLTOKEN=%%i
```

### Option 2: Symlink legacy to canonical

```bash
# Remove stale legacy file and symlink to canonical
rm ~/.hermes/webui/.token
ln -sf ~/.hermes-web-ui/.token ~/.hermes/webui/.token
```

### Option 3: Keep both in sync

Add a cron job or startup script that copies the canonical token to the legacy path whenever it changes.

## Verification After Fix

```bash
# Both files should now match
diff ~/.hermes-web-ui/.token ~/.hermes/webui/.token && echo "✓ Both match"

# Launcher should now pass the correct token
# Open WebUI in browser and verify auth works
```

## Historical Context

In session 2026-05-22, the launcher `Launch Hermes WebUI.bat` was reading from `~/.hermes/webui/.token` while the server (started via systemd) was reading from `~/.hermes-web-ui/.token`. The tokens had diverged. The launcher passed a stale token, causing auth confusion. Fix: updated the batch file to read from the canonical path.
