# Hermes Core Update alongside WebUI

## Context  

- **Hermes CLI:** `v0.14.0` → `v0.15.1` (290 commits)
- **WebUI:** already on `v0.6.6` (separate repo, WSL path `/mnt/c/Users/thadd/hermes-web-ui`)
- **Active profiles:** `plc-coder` with lots of skills and memories
- **Hermes repo:** `/home/thadd/hermes-agent-ui`

## Independence of WebUI and Hermes Core

| Component | Repo path | Update command | What it affects |
|---|---|---|---|
| WebUI | `/mnt/c/Users/thadd/hermes-web-ui` | `git merge origin/main`, then `npm run build` | Web server, client UI, bridge spawn logic |
| Hermes CLI | `/home/thadd/hermes-agent-ui` | `hermes update --backup --yes` | Core agent loop, CLI commands, gateway, bridge worker spawn |

**Key rule:** They can be updated independently. But the WebUI server must know where the Hermes venv Python is (`HERMES_AGENT_BRIDGE_PYTHON`). If a Hermes update moves or recreates the venv, the WebUI needs the new path.

## Pre-Update Checklist

1. **Export active profile(s):**
   ```bash
   hermes profile export plc-coder --output plc-coder-pre-update.tar.gz
   ```
   This is the fastest rollback if configs get corrupted.

2. **Check venv integrity:**
   ```bash
   /home/thadd/hermes-agent-ui/venv/bin/python3 -c "import openai, websockets; print(openai.__version__)"
   ```
   If this fails, fix the venv BEFORE updating.

3. **Kill gateways (prevents file locks during pip reinstall):**
   ```bash
   pkill -f "hermes_cli.*gateway run" || true
   ```

## Update Command

```bash
cd /home/thadd/hermes-agent-ui
hermes update --backup --yes
```

Flags:
- `--backup`: Forces a pre-update backup (stash) even if the config says not to
- `--yes`: Auto-answers config migration prompts (API key entry is skipped, run `hermes config migrate` separately if needed)

## What the update does

Observed output:
```
Saved working directory and index state On main: hermes-update-autostash-20260530-120701
Using Python 3.14.4 environment at: venv
Resolved 101 packages in 844ms
...
 - hermes-agent==0.14.0
 + hermes-agent==0.15.1
 + setuptools==82.0.1
 - starlette==1.1.0
 + starlette==1.0.1
```

The stash is auto-created with tag `hermes-update-autostash-<timestamp>`. It can be popped if needed.

## Post-Update Verification

1. **Hermes CLI version:**
   ```bash
   hermes version
   # Hermes Agent v0.15.1 (2026.5.29)
   # Up to date ← confirms no more commits behind
   ```

2. **Profile still exists:**
   ```bash
   hermes profile list | grep plc-coder
   # ◆plc-coder       kimi-k2.6                    stopped      —            —
   ```

3. **Config survived:**
   ```bash
   ls -la ~/.hermes/profiles/plc-coder/config.yaml
   # Should be non-empty and have your model settings
   ```

4. **Skills survived:**
   ```bash
   ls ~/.hermes/profiles/plc-coder/skills/
   ```

5. **Gateway auto-restarted (observed):**
   ```bash
   ps aux | grep "hermes_cli.*gateway run" | grep -v grep
   # Two processes: one with --profile ai-advocate, one generic
   # They auto-restart after the update finishes
   ```

6. **WebUI Hermes version string:**
   ```bash
   curl -sf http://127.0.0.1:8648/health | grep '"version"'
   # Shows v0.15.1 if server is restarted after update
   ```

## Risk: Bridge Python path

The WebUI server sets `HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3`. After a Hermes update:

- If the update rebuilt the venv in-place → path unchanged → bridge works
- If the update moved the venv → the env var is stale → bridge workers fail with `No module named 'openai'`

**Detection after Hermes update:**
```bash
# Verify the path still resolves
ls -la /home/thadd/hermes-agent-ui/venv/bin/python3

# Verify it has the packages
/home/thadd/hermes-agent-ui/venv/bin/python3 -c "import openai, websockets; print('OK')"
```

## Pitfall: Venv points to a missing Python interpreter

The `hermes update` command tries to reinstall the editable package inside the active venv. If the venv's Python interpreter has been removed or upgraded (e.g., system Python moved from 3.13 to 3.14, or a custom build was deleted), `hermes update` fails mid-install with:

```
error: Failed to inspect Python interpreter from active virtual environment at `venv/bin/python3`
  Caused by: Python interpreter not found at `.../venv/bin/python3`
```

**Detection:**
```bash
# Check if the venv's interpreter exists
ls -la /home/thadd/hermes-agent-ui/venv/bin/python3

# Check what Python versions are available
which python3.11 python3.12 python3.13 2>/dev/null || ls /usr/bin/python3.*
```

**Fix:**
```bash
cd /home/thadd/hermes-agent-ui

# 1. Rename the broken venv so you can inspect it later
mv venv venv.bak

# 2. Find a compatible Python (Hermes requires >=3.11, <3.14)
#    Check available versions with: ls /usr/bin/python3.*

# 3. Create a fresh venv with a working interpreter
/home/thadd/.local/bin/python3.11 -m venv venv

# 4. Reinstall in editable mode
source venv/bin/activate
pip install -e .
```

**Post-fix verification:**
```bash
source venv/bin/activate
hermes --version  # Should show the updated version string
/home/thadd/hermes-agent-ui/venv/bin/python3 -c "import openai, websockets; print('OK')"
```

**When to clean up the old venv:**
After confirming the new venv works and has no extra packages (compare `pip freeze` output if needed), remove `venv.bak` to reclaim disk space. If you want to be extra safe, keep it for a few days.

## WebUI Restart After Hermes Core Update

The WebUI server does NOT need to be rebuilt when Hermes core updates. Only restart it to pick up the new health check version string and to refresh the bridge Python path if the venv moved.

```bash
pkill -f "node.*dist/server/index.js" || true; sleep 2

unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export PORT=8648
export BIND_HOST=0.0.0.0
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export HERMES_WEB_UI_DISABLE_UPDATE_CHECK=true

cd /mnt/c/Users/thadd/hermes-web-ui
node dist/server/index.js
```

## What Does NOT Get Updated

- WebUI repo contents (separate repo)
- WebUI `dist/` build output
- WebUI database (`~/.hermes/webui/hermes-web-ui.db`)
- Profile data in `~/.hermes/profiles/<name>/`
- Memory files, skills directory
- Gateway platform configs

## Rolling Back a Bad Hermes Update

If the update breaks something:

```bash
# Option 1: Pop the auto-stash
cd /home/thadd/hermes-agent-ui
git stash pop
# Then reinstall previous version if needed

# Option 2: Restore profile from tarball
hermes profile import --input plc-coder-pre-update.tar.gz

# Option 3: Full reinstall of previous version
cd /home/thadd/hermes-agent-ui
git checkout v0.14.0
./scripts/install.sh  # or whatever install path you used
```
