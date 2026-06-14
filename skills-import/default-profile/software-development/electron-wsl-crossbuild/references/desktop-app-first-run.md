# Hermes Desktop — First-Run Recovery (Session 2026-05-19)

## What Happened
User clicked **"Get Started"** on the welcome screen instead of **"Connect to Remote Hermes"**. This triggered a ~2GB Hermes installation inside Windows, which the user already had running in WSL. The app then saved `connectionMode: "local"` in `desktop.json`, hiding the welcome screen permanently.

## Recovery Steps

### 1. Reset the Desktop Config (to get welcome screen back)
**Windows PowerShell:**
```powershell
Remove-Item -Force "$env:USERPROFILE\.hermes\desktop.json"
```

**WSL/Linux/macOS:**
```bash
rm ~/.hermes/desktop.json
```

### 2. Fix `node_modules` Platform Mismatch
The repo was cloned into WSL and `npm install` ran there first. This produced Unix-only `.bin/` scripts with no `.cmd` wrappers, so Windows PowerShell could not find `electron-vite`.

**Fix:** Delete `node_modules` from the target platform and reinstall.

**Windows PowerShell:**
```powershell
cd C:\Users\thadd\.openclaw\workspace\hermes-desktop
Remove-Item -Recurse -Force node_modules
npm install
npm run dev
```

### 3. Correct Welcome Screen Choice
Relaunch the app → click **"Connect to Remote Hermes"** (NOT "Get Started").

- **Server URL:** `http://127.0.0.1:8642`
- **API Key:** leave blank (no auth for local)

## Backend Prerequisite
Ensure the `api_server` gateway platform is enabled in `~/.hermes/config.yaml`:
```yaml
platforms:
    api_server:
        enabled: true
        extra:
            host: 127.0.0.1
            port: 8642
```

Restart gateway: `hermes gateway run --replace`

Verify: `curl http://127.0.0.1:8642/health` → `{"status": "ok"}`

## Key Lesson
"Get Started" is for **new users** who don't have Hermes installed. Existing users with a WSL or remote gateway must always choose **"Connect to Remote Hermes"**.