---
name: spock-infrastructure
description: End-to-end operations for the Spock/Hermes persona and environment — agent identity recovery, workspace migration (especially from OpenClaw), infrastructure health checks, secure GitHub backups, and WSL-Windows interoperability.
trigger:
  - backup agent state
  - migrate workspace
  - import from openclaw
  - hermes claw migrate
  - spock identity
  - recover hermes agent
  - wsl windows file
  - windows shortcut from wsl
  - cross filesystem file
  - update hermes
  - upgrade hermes
  - hermes update failed
---

# Spock Infrastructure Operations

## Overview

This umbrella skill covers all operational tasks for maintaining, migrating, backing up, and recovering the Spock (Hermes Agent) persona and environment. It spans identity recovery, workspace migration, infrastructure health, and WSL-Windows file interop.

## 1. Workspace Migration

### Preferred Path: Built-in `hermes claw migrate`

Hermes has a built-in OpenClaw importer. Use this first.

**1. Stop both services**
```bash
hermes gateway stop
pkill -f openclaw
```

**2. Preview with dry-run**
```bash
hermes claw migrate --source /mnt/c/Users/thadd/.openclaw --dry-run
```

**3. Run migration**
```bash
hermes claw migrate \
  --source /mnt/c/Users/thadd/.openclaw \
  --preset full \
  --migrate-secrets \
  --overwrite \
  --yes
```

**4. Post-migration cleanup**
```bash
# Remove deprecated key
hermes config set terminal.cwd /mnt/c/Users/thadd/.openclaw/workspace
sed -i '/^MESSAGING_CWD=/d' ~/.hermes/.env

# Verify secrets transferred
cat ~/.hermes/.env | grep -E 'API_KEY|TOKEN'

# Restart gateway
hermes gateway restart
```

### Manual Fallback

When the built-in importer fails:

1. **Locate source**: `find /mnt/c/Users/ -maxdepth 3 -type d -iname '*openclaw*'`
2. **Read core persona files** in priority: `SOUL.md`, `USER.md`, `AGENTS.md`, `HEARTBEAT.md`, `TOOLS.md`, `MEMORY.md`
3. **Map agent configs to cron jobs** using the `cronjob` tool
4. **Read recent memory** (latest 5-7 daily files) for context catch-up
5. **Save key facts** to Hermes persistent memory

**WSL Path Conventions:**
- `C:\Users\thadd\Desktop\Portfolio Positions` → `/mnt/c/Users/thadd/Desktop/Portfolio Positions`
- Space-containing paths: use quotes in terminal, escaped in cron prompts
- Git workspace: set `--workdir` on cron jobs to project directory

**What migrates**: SOUL.md, MEMORY.md, USER.md, .env secrets, config.yaml, skills, daily memory.
**What does NOT migrate**: cron jobs, MCP servers, Discord/Slack/Signal settings.

## 2. Identity Recovery

Create a lean GitHub recovery repo containing everything to reconstruct Spock from scratch.

**Include** (from `/mnt/c/Users/thadd/.openclaw/workspace/`):
- `SOUL.md`, `MEMORY.md`, `USER.md`, `IDENTITY.md`, `AGENTS.md`, `TOOLS.md`, `SECURITY.md`, `REGISTRY.md`, `DREAMS.md`, `HEARTBEAT.md`, `HOME_PC_SETUP.md`, `PLC_SPAWN.md`
- `README.md` with step-by-step recovery instructions
- `~/.hermes/config.yaml` (tokens redacted)

**Exclude**: Daily briefs, whale watch reports, trading arena outputs, large binaries, active tokens, session logs.

**Recovery template (`README.md`)**:
```markdown
# Spock Recovery
1. git clone https://github.com/AntisystemOG/HermestoSpock.git
2. mkdir -p /mnt/c/Users/thadd/.openclaw/workspace
3. cp *.md /mnt/c/Users/thadd/.openclaw/workspace/
4. cp config.yaml ~/.hermes/config.yaml
5. hermes gateway restart
6. Tell agent: "Become Spock. Read SOUL.md, MEMORY.md, USER.md, IDENTITY.md."
```

## 3. Secure GitHub Backup

Backup `.hermes/` to a private GitHub repo without leaking secrets.

**1. Write `.gitignore` BEFORE first commit:**
```gitignore
.env
.env.*
auth.json
auth.lock
*.key
*.pem
*.db
*.sqlite
*.sqlite3
sessions/
backups/
state-snapshots/
audio_cache/
*.log
.DS_Store
temp_*.*
```

**2. Sanitize `config.yaml`:**
```bash
cd ~/.hermes
python3 -c "
import re
with open('config.yaml', 'r') as f:
    text = f.read()
text = re.sub(r'(api_key|session_key|brave_api_key|token|password|secret_key):\s*\"[^\"]*\"', r'\1: \"\"', text)
with open('config.yaml', 'w') as f:
    f.write(text)
"
grep -rn 'api_key.*=\|api_key:.*\"[^\"]\+\"' config.yaml | grep -v ': \"\"'  # should return NOTHING
```

**3. One-shot credential helper (no hardcoded PAT in remote URL):**:
```bash
cat > /tmp/git-cred-helper.sh <<'EOF'
#!/bin/bash
case "$1" in
  get)
    echo "protocol=https"; echo "host=github.com"
    echo "username=<GITHUB_USERNAME>"; echo "password=<YOUR_PAT>"
    ;;
  store|erase) : ;;
esac
EOF
chmod 700 /tmp/git-cred-helper.sh
cd ~/.hermes
git remote add origin https://github.com/<OWNER>/<REPO>.git 2>/dev/null || true
GIT_ASKPASS=/tmp/git-cred-helper.sh git push -u origin main --force
rm -f /tmp/git-cred-helper.sh
```

## 4. WSL-Windows File Interop

### Path Translation Rules

| Windows path | WSL equivalent |
|-------------|----------------|
| `C:\Users\thadd` | `/mnt/c/Users/thadd` |
| `C:\Users\thadd\Desktop` | `/mnt/c/Users/thadd/Desktop` |
| `C:\Users\thadd\.claude` | `/mnt/c/Users/thadd/.claude` |

**Critical distinction**: The Hermes agent runtime lives in `/home/thadd/.hermes/` (WSL home), but the WebUI and many project files live under `/mnt/c/Users/thadd/` (Windows home).

### Finding Folders Across Boundaries

When the user says "I just created a folder":
1. Search WSL home: `find /home/thadd -maxdepth ...`
2. Search Windows: `find /mnt/c/Users/thadd -maxdepth ... -iname "*folder*"`
3. Use `-iname` for case-insensitive search — Windows filesystem is case-insensitive but WSL is case-sensitive

### Creating Windows Shortcuts from WSL

**Method 1: PowerShell `-File` (Recommended)**
```bash
cat > "/mnt/c/Users/thadd/Desktop/create_shortcut_temp.ps1" << 'EOF'
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\thadd\Desktop\My Shortcut.lnk")
$Shortcut.TargetPath = "C:\Users\thadd\.claude\projects"
$Shortcut.IconLocation = "C:\Users\thadd\Desktop\spock-icon.ico,0"
$Shortcut.WorkingDirectory = "C:\Users\thadd\Desktop"
$Shortcut.Save()
EOF
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -ExecutionPolicy Bypass -File "C:\Users\thadd\Desktop\create_shortcut_temp.ps1"
rm "/mnt/c/Users/thadd/Desktop/create_shortcut_temp.ps1"
```

**Key WScript.Shell properties**:
| Property | Purpose |
|----------|---------|
| `TargetPath` | What the shortcut opens |
| `IconLocation` | `"path\\to\\icon.ico,0"` |
| `WorkingDirectory` | Start-in directory |

**Method 2: Quick `-Command` (escape `$` with `\$`)**
```bash
powershell.exe -Command "\$WshShell = New-Object -ComObject WScript.Shell; \$lnk = \$WshShell.CreateShortcut('C:\\Users\\thadd\\Desktop\\My Shortcut.lnk'); \$lnk.IconLocation = 'C:\\Users\\thadd\\Desktop\\spock-icon.ico,0'; \$lnk.Save()"
```

### Copying Projects for Dev Agents

Claude Code stores projects at `C:\Users\<user>\.claude\projects`. Use `rsync -av --exclude='node_modules' --exclude='.git' --exclude='build' --exclude='dist'` for transfers.

### Common Pitfalls

- **Case sensitivity**: `"CODE Projects"` and `"Code Projects"` are different in WSL. Always search with `-iname`.
- **`find` timeout**: `/mnt/c/` is very large. Use `-maxdepth` or `ls | grep`.
- **PowerShell not found**: Use absolute path `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`.
- **Script location for `-File`**: Must be on a Windows-accessible path (`/mnt/c/...`). `/tmp/` is invisible to `powershell.exe`.

## Session References

- **`references/infrastructure-health-checklist.md`** — Full structured health check.
- **`references/webui-chat-history-restoration.md`** — Complete script for merging lost WebUI chat histories when the data directory migrates or `NODE_ENV=production` is missing. Covers all 4 possible DB locations, detection, renumbering for overlapping auto-increment IDs, and prevention.
- **`references/hermes-update-missing-venv.md`** — Notes from the v0.15.1 → v0.16.0 update where Python `<3.14` constraint forced venv recreation.

Key checks:
- **Gateway**: `hermes gateway status` or `curl http://127.0.0.1:8000/health`
- **WebUI**: `curl http://127.0.0.1:8648/health`
- **Ollama token**: `curl -H "Authorization: Bearer $OLLAMA_API_KEY" https://ollama.com/v1/models`
- **Memory DB**: `hermes memory list`
- **Cron jobs**: `hermes cron list`
- **Orphaned processes**: `ps aux | grep "hermes_bridge\|agent-bridge"`

## 6. Cron Job Bulk Management

When the user says "suspend all cron jobs" or "they drained my tokens", pause every active job immediately. Use the `cronjob` tool directly — the `hermes cron pause` CLI may not catch all jobs.

**Procedure:**
1. `cronjob list` to get all job IDs and states
2. For every job with `enabled: true`, call `cronjob pause` with the job_id
3. Re-list to confirm all are `state: paused`

**Resume later:** Same pattern with `cronjob resume` per job_id.

Do NOT delete jobs unless the user explicitly asks — pausing preserves config and allows resume.

## 7. WebUI Chat History Restoration

**Trigger:** User says "my chat histories are gone" after a WebUI update or repo migration.

**Root cause:** The WebUI server stores conversations in a SQLite DB. When the server changes its data directory (e.g. `~/.hermes-web-ui/` → `~/.hermes/webui/`) or when `NODE_ENV=production` is missing (causing a dev DB at `packages/server/data/`), old sessions become invisible.

**Detection:**
```bash
# Check both possible DB locations
ls -la ~/.hermes-web-ui/hermes-web-ui.db 2>/dev/null
ls -la ~/.hermes/webui/hermes-web-ui.db 2>/dev/null
# Also check profile-specific copies
ls -la ~/.hermes/profiles/*/home/.hermes-web-ui/hermes-web-ui.db 2>/dev/null
```

If the old DB exists and has sessions that are NOT in the current DB, they need to be merged.

**Merge procedure (handles overlapping message IDs):**

The old and new DBs may both use auto-incrementing `id` columns for messages. Inserting old messages directly will collide. Renumber them instead.

```python
import sqlite3

old_db = "/home/thadd/.hermes-web-ui/hermes-web-ui.db"
curr_db = "/home/thadd/.hermes/webui/hermes-web-ui.db"

conn_old = sqlite3.connect(old_db)
conn_old.row_factory = sqlite3.Row
conn_curr = sqlite3.connect(curr_db)
conn_curr.row_factory = sqlite3.Row

c_old = conn_old.cursor()
c_curr = conn_curr.cursor()

# Get max message ID in current DB
c_curr.execute("SELECT MAX(id) FROM messages")
max_id = c_curr.fetchone()[0] or 0

# Find sessions in old DB that are missing from current
c_old.execute("SELECT id FROM sessions")
missing_sessions = []
for row in c_old.fetchall():
    sid = row[0]
    c_curr.execute("SELECT id FROM sessions WHERE id=?", (sid,))
    if not c_curr.fetchone():
        missing_sessions.append(sid)

# Copy each missing session and its messages with renumbered IDs
for sid in missing_sessions:
    # Copy session row
    c_old.execute("SELECT * FROM sessions WHERE id=?", (sid,))
    session = c_old.fetchone()
    cols = list(session.keys())
    placeholders = ','.join('?' for _ in cols)
    values = tuple(session[col] for col in cols)
    c_curr.execute(f"INSERT INTO sessions ({','.join(cols)}) VALUES ({placeholders})", values)
    
    # Copy messages with new IDs
    c_old.execute("SELECT * FROM messages WHERE session_id=?", (sid,))
    for msg in c_old.fetchall():
        max_id += 1
        msg_cols = list(msg.keys())
        new_values = {}
        for col in msg_cols:
            if col == 'id':
                new_values[col] = max_id
            elif col == 'session_id':
                new_values[col] = sid
            else:
                new_values[col] = msg[col]
        insert_cols = list(new_values.keys())
        placeholders = ','.join('?' for _ in insert_cols)
        values = tuple(new_values[col] for col in insert_cols)
        c_curr.execute(f"INSERT INTO messages ({','.join(insert_cols)}) VALUES ({placeholders})", values)
    
    # Update session message_count to actual count
    c_curr.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (sid,))
    actual_count = c_curr.fetchone()[0]
    c_curr.execute("UPDATE sessions SET message_count=? WHERE id=?", (actual_count, sid))

conn_curr.commit()
conn_old.close()
conn_curr.close()
```

**Post-restore verification:**
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM sessions')
print('Sessions:', c.fetchone()[0])
c.execute('SELECT COUNT(*) FROM messages')
print('Messages:', c.fetchone()[0])
conn.close()
"
```

**Service restart required** after DB merge for the WebUI to pick up new sessions.

## 8. WebUI Data Directory Migration Awareness

When updating the WebUI or migrating the repo, the server's data directory may shift:

| Era | Data Directory | Notes |
|---|---|---|
| Pre-v0.6.4 | `~/.hermes-web-ui/` | Legacy location |
| v0.6.4+ with `NODE_ENV=production` | `~/.hermes/webui/` | Production DB |
| Without `NODE_ENV=production` | `cwd/packages/server/data/` | Dev DB — empty users table |

**Check which DB is active:**
```bash
# Check server environment
systemctl --user cat hermes-webui.service | grep -i "HERMES_WEB_UI_HOME\|NODE_ENV"
# Or check running process
lsof -p $(pgrep -f "node.*dist/server/index.js") | grep -i "\.db"
```

If the server is using the dev DB (`packages/server/data/`), all user accounts and chat histories are invisible. Stop the server, set `NODE_ENV=production`, and restart.

**WebUI Health Check — go beyond `curl -sf`:**
`curl -sf` silently fails on non-2xx responses or timeouts. A process marked `active (running)` by systemd may still be unreachable if it crashed internally, is bound to the wrong port, or the DB is in dev mode. Always use verbose curl:

```bash
curl -v --max-time 10 http://127.0.0.1:8648/health
```

If the connection succeeds but returns no body, the server is alive but may be using the wrong DB. Check `lsof` for the actual SQLite file path.

If `ss -tlnp | grep 8648` shows nothing but `lsof -p <pid> | grep LISTEN` shows `127.0.0.1:8648`, the port IS listening — `ss` may need root for process names. Trust `lsof` over `ss` in this case.

**Log file descriptor mapping under systemd:**
```bash
ls -l /proc/$(pgrep -f "node.*dist/server/index.js")/fd/ | grep -E "log|server"
```
This reveals whether logs go to `~/.spock/webui.log` (systemd redirect) vs `~/.hermes/webui/logs/server.log` (internal Winston logger).

## 6. Safe Hermes Updates (Preserve Customizations)

`hermes update` pulls the latest commits and reinstalls dependencies, but it can fail if the venv is missing or stale. Always back up the active profile first.

**Pre-update checklist:**
1. **Export the active profile** — captures skills, memory, config, auth, cron jobs:
   ```bash
   hermes profile export <profile-name>
   # produces /home/thadd/<profile-name>.tar.gz
   ```
2. **Note the current version** — `hermes --version`
3. **Check gateway status** — `hermes gateway status` (update will restart it)

**Running the update:**
```bash
hermes update
```

**Common failure: missing venv**
- `hermes update` may fail with "Python interpreter not found at `venv/bin/python3`"
- This happens when the repo was cloned but the venv was never created or was deleted
- **Fix:** recreate venv and reinstall manually:
  ```bash
  cd ~/hermes-agent-ui   # or wherever the source lives
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  uv pip install -e ".[all]"   # base + all extras
  ```

**Post-update verification:**
```bash
hermes --version              # should say "Up to date"
hermes profile show <name>      # skills count, .env, SOUL.md should all be present
hermes skills list | wc -l      # skill count should match pre-update
hermes memory status            # built-in memory should be active
hermes gateway status           # confirm running after restart
```

**What survives the update:**
- `~/.hermes/profiles/<name>/` — entire profile directory (skills, memory, config, auth, cron)
- `~/.hermes/.env` — root-level secrets
- `~/.hermes/config.yaml` — root config

**What does NOT survive:**
- The source checkout at `~/hermes-agent-ui/` is overwritten by `git pull`
- Any uncommitted local changes are stashed and restored, but review `git status` after

**If the update fails mid-way:**
1. Restore from the exported tar.gz: `hermes profile import /home/thadd/<profile>.tar.gz`
2. Or manually recreate the venv and run `uv pip install -e ".[all]"` from the source dir

### Manual Safe Update (When `hermes update` Is Broken)

When `hermes update` fails due to a missing or incompatible venv, do the update manually while preserving all profile state.

**Pre-update checks:**
```bash
cd ~/hermes-agent-ui   # or wherever the source checkout lives
git status              # verify working tree is clean (or note stashes)
git log --oneline -1    # note current commit
hermes --version        # note current version
```

**Pull latest:**
```bash
git pull origin main    # or git fetch && git merge origin/main
```

**Python version constraint check (CRITICAL):**
The project pins `requires-python = ">=3.11,<3.14"` in `pyproject.toml`. If your existing venv uses Python 3.14, it is **incompatible** and must be recreated.

```bash
# Check venv Python version
cat venv/pyvenv.cfg | grep version
# If it says 3.14.x, recreate:
mv venv venv-backup-py314
python3.11 -m venv venv   # or use `uv venv --python python3.11`
```

**Reinstall editable package:**
```bash
uv pip install -e . --python venv/bin/python
```

**Also update the active runtime venv** (where `~/.local/bin/hermes` launcher points):
```bash
# The launcher usually points to ~/.hermes/hermes-agent/venv/bin/hermes
# That venv is ALSO an editable install pointing back to the source checkout.
# Reinstall there too:
uv pip install -e ~/hermes-agent-ui --python ~/.hermes/hermes-agent/venv/bin/python
```

**Verify:**
```bash
hermes --version   # should show new version + "Up to date"
python -c "import hermes_cli; print(hermes_cli.__version__)"   # should match
```

**Security dep changes to NOT skip:**
After pulling, check `pyproject.toml` for security-related bumps. Exact-pinned deps may have changed for CVE fixes. These are NOT customizations — they are supply-chain security updates. Always reinstall after pulling so the new pins take effect.

Known security bumps that have landed:
- `requests==2.33.0` (CVE-2026-25645)
- `PyJWT[crypto]==2.12.1` (CVE-2026-32597)
- `pydantic==2.13.4` (segfault fix in non-main-thread usage)

### User Preference: Protect Customizations Over Updates

When updating Hermes (via `hermes update` or manual `git pull` + reinstall), **never change user customizations unless they pose a security concern.**

**What counts as a customization (DO NOT TOUCH):**
- `~/.hermes/config.yaml` — user config
- `~/.hermes/.env` — secrets and API keys
- `~/.hermes/profiles/<name>/` — entire profile (skills, memory, cron, auth)
- `~/.hermes/skills/` — user-created or hub-installed skills
- Any uncommitted changes in the source checkout that are user modifications (check `git status`)

**What counts as a security concern (DO UPDATE):**
- Exact-pinned dependency bumps in `pyproject.toml` that fix CVEs (e.g. `requests`, `PyJWT`, `pydantic` security patches)
- Supply-chain attack mitigations (e.g. the May 2026 exact-pin policy)
- Config changes that are **required** for the new version to function (rare; usually announced in release notes)

**Procedure:**
1. Before updating, check `git status` for uncommitted changes — note them.
2. After `git pull`, inspect `pyproject.toml` for security-related dep changes.
3. Reinstall dependencies so security pins take effect.
4. If any customization file was modified by the pull (rare for files outside `~/.hermes/`), restore it unless the change is security-related.
5. Verify with `hermes --version` and `python -c "import hermes_cli; print(hermes_cli.__version__)"`.

### Safe Merge with Uncommitted Spock Customizations

**Trigger:** `git merge origin/main` aborts because `AppSidebar.vue` or `SessionListItem.vue` are dirty.

**Do not stash on a detached HEAD.** User had an old detached HEAD from a prior merge. The correct sequence:
1. `git checkout main` (moving from detached HEAD back to local branch)
2. `git stash -u -m "Spock customizations pre-merge"`
3. `git merge origin/main`
4. After merge, inspect working tree to confirm customizations survived
5. If the Spock Guardian hook claims it restored them, verify independently (don't trust the hook blindly)
6. Pop stash only if the merge obliterated the customizations; drop once confirmed redundant

**What this session proved:** Merging v0.6.4 → v0.6.6 (36 commits, 152 files, 17480 insertions, 1463 deletions) resulted in **zero merge conflicts**. The stash was unnecessary in retrospect — Spock customizations in `AppSidebar.vue` and `SessionListItem.vue` were uncommitted changes on `main` that did not conflict with upstream.

### Non-destructive WebUI git update workflow

The user prefers `git merge` over `git reset --hard` to avoid destroying local state. Follow this sequence when `git pull` shows divergent branches:

1. **Check divergence first** (don't assume fast-forward):
   ```bash
   git log --oneline HEAD..origin/main   # commits we would gain
   git log --oneline origin/main..HEAD   # commits we would lose
   ```
2. **If local is behind, merge:**
   ```bash
   git merge origin/main
   ```
3. **If merge conflicts occur**, resolve or abort — never force.
4. **If local has uncommitted changes**, stash first: `git stash && git merge origin/main && git stash pop`
5. **After merge**, rebuild and restart server.

**Never use `git reset --hard origin/main` without explicit user approval.** The user blocked this during the May 2026 WebUI update session.

---

## 7. Gateway Troubleshooting — Stale Python Module Imports

**Symptom:** `ImportError: cannot import name 'X' from 'hermes_constants'` even though the constant is present in the source file on disk.

**Root cause:** The `hermes-gateway.service` is a long-running Python daemon. Python caches imported modules in memory for the lifetime of the process. If `hermes_constants.py` (or any shared module) is updated on disk after the gateway started, new conversation worker sessions spawned by that gateway still inherit the **stale in-memory module**, not the updated disk version.

**Why clearing `__pycache__` is insufficient:**
1. The `.pyc` bytecode caches are only read on initial import.
2. Once loaded, the module object lives in `sys.modules` inside the gateway process.
3. Every new worker is forked or spawned from the gateway, inheriting its `sys.modules`.

**Diagnostic:**
```bash
# Check gateway age — if older than the file modification time, it's stale
systemctl --user status hermes-gateway.service
# Look at "Active since" vs when the code was last updated

# Verify the source IS correct in a fresh process
python3 -c "from hermes_constants import THE_MISSING_CONSTANT; print('OK')"
```

**Resolution:**
```bash
systemctl --user restart hermes-gateway.service
```

**After restart:**
```bash
systemctl --user status hermes-gateway.service
# Confirm new PID and recent "Active since" timestamp
```

**When `/reset` fails:** If a user runs `/reset` in Telegram and the same import error recurs, the problem is upstream in the gateway daemon, not the conversation worker. Restart the gateway — do not restart `__pycache__` deletion loops.

**Prevention:** After any update to shared modules (`hermes_constants.py`, protocol definitions, shared utilities), always restart the gateway service before testing via messaging platforms.

