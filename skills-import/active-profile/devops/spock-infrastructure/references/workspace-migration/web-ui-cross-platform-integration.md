# Web UI Cross-Platform Integration (WSL + Windows)

When Hermes runs in WSL but the web UI runs natively on Windows, the UI's server cannot spawn `hermes` directly because there's no `hermes` binary in the Windows PATH.

## Error Signature

```
Error: spawn hermes ENOENT
    at Process.ChildProcess._handle.onexit (node:internal/child_process:287:19)
```

This happens when the web UI server tries to call `hermes gateway run --replace` but `hermes` is only installed in WSL (`/home/thadd/.local/bin/hermes`).

## Root Cause

The web UI (Node.js on Windows) spawns child processes using the Windows `CreateProcess` API. It looks for `hermes` in the Windows PATH, finds nothing (since Hermes is inside WSL), and fails with ENOENT.

## Solutions

### Option A: WSL Wrapper (Recommended for Dev Mode)

Create a Windows `.cmd` wrapper that forwards to WSL:

```powershell
# Create a bin directory
mkdir "C:\Users\<username>\bin"

# Create the wrapper
$wrapper = @'echo off
set WSLENV=HERMES_HOME/u
wsl.exe /home/<linux-user>/.local/bin/hermes %*
'@
$wrapper | Out-File -FilePath "C:\Users\<username>\bin\hermes.cmd" -Encoding ASCII

# Add to PATH
$env:Path += ";C:\Users\<username>\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "User")
```

Also set `HERMES_HOME` so the wrapper knows where the WSL home is:
```powershell
$env:HERMES_HOME = "C:\Users\thadd"
[Environment]::SetEnvironmentVariable("HERMES_HOME", "C:\Users\thadd", "User")
```

**Verify:** From PowerShell, `hermes gateway status` should work.

### Option B: Run Web UI Inside WSL Instead

Instead of fighting the cross-platform spawn, install Node.js inside WSL and run the web UI there:

```bash
# Install Node via nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 22
nvm use 22

cd /mnt/c/Users/thadd/hermes-web-ui
npm run dev
```

This avoids all spawn/path issues because everything lives in the same Linux environment.

### Option C: Build and Serve from Node-pty

The `npm run prepare` / `npm run build` build step produces a `dist/` folder that the `bin/hermes-web-ui.mjs` script can serve. The packaged version handles Hermes home detection differently than dev mode.

```powershell
cd C:\Users\thadd\hermes-web-ui
npm run prepare
node bin/hermes-web-ui.mjs start --port 8648
```

## Authentication Token

Once the server starts successfully, it prints:

```
Access token: <64-char-hex>
```

Or writes it to:
- `%USERPROFILE%\.hermes-web-ui\.token` (Windows)
- `~/.hermes-web-ui/.token` (WSL)

Copy that token into the web UI login prompt.

## Key Decision: Where to Run the Server

| Where | Pros | Cons |
|-------|------|------|
| Windows (PowerShell) | Browser-native URL, easier file dialogs | Spawn hermes ENOENT, needs wrapper |
| WSL (Bash) | No spawn issues, native hermes path | Browser needs `http://localhost:8648` from Windows side |

For most users, **run the dev server in WSL** and access it from Windows browser. No wrapper needed, no cross-platform pain.
