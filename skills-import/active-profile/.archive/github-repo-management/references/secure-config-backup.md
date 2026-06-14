# Secure Config Backup for Agent Directories

This reference covers backing up sensitive configuration directories (e.g. `~/.hermes/`) to a GitHub repo **without leaking secrets**.

## The Problem

Agent directories contain:
- `SOUL.md`, `USER.md` — memory/personality
- `config.yaml` — model configuration **with API keys inline**
- `.env` — credentials (OLLAMA_API_KEY, TELEGRAM_BOT_TOKEN, etc.)
- `skills/` — extensive skill library
- `.db`, `.sqlite` files — session/state databases
- `gateway.*`, `auth.json` — runtime tokens

A naïve `git add .` will expose secrets and bloat the repo with files 100+ MB.

## The Safe Workflow

### 1. Add a `.gitignore` BEFORE first commit

```gitignore
# === SECRETS / CREDENTIALS ===
.env
.env.*
auth.json
auth.lock
*.key
*.pem

# === DATA / DB ===
*.db
*.db-*
*.sqlite
*.sqlite3
sessions/
backups/
state-snapshots/
audio_cache/

# === RUNTIME / TEMP ===
.update_check
context_length_cache.yaml
gateway.lock
gateway.pid
gateway_state.json
processes.json
*.log
*.log.*
cache/
cache-web/
webui/logs/

# === OS ===
.DS_Store
Thumbs.db
```

### 2. Sanitize `config.yaml` before staging

`config.yaml` usually embeds `api_key` / `session_key` values. Strip them for GitHub, restore after push.

```python3
import re

with open('/home/thadd/.hermes/config.yaml', 'r') as f:
    cfg = f.read()

# Replace all non-empty api_key / session_key values
sanitized = re.sub(
    r'(brave_api_key|api_key|session_key):\s*"[^"]*"',
    r'\1: ""',
    cfg
)

with open('/home/thadd/.hermes/config.yaml', 'w') as f:
    f.write(sanitized)
```

After push, restore from `config.yaml.bak`.

### 3. Read PAT from `.env`, never from user prompt

If the directory already has a `.env`, extract the token there rather than asking the user to paste it again.

```python3
env_path = '/home/thadd/.hermes/.env'
with open(env_path, 'r') as f:
    for line in f:
        if line.startswith('GITHUB_PAT='):
            token = line.split('=', 1)[1].strip()
            break
```

### 4. Use a credential helper script, never embed token in remote URL

Embedding the token in the remote URL (`https://TOKEN@github.com/...`) exposes it via `ps` output.

Instead, write a shell credential helper and delete it after push:

```bash
#!/bin/bash
case "$1" in
  get)
    echo "protocol=https"
    echo "host=github.com"
    echo "username=AntisystemOG"
    echo "password=<TOKEN_HERE>"
    ;;
  store|erase)
    : ;;
esac
```

Then:
```bash
chmod 700 /tmp/git-cred-helper.sh
GIT_ASKPASS=/tmp/git-cred-helper.sh git push -u origin main
rm -f /tmp/git-cred-helper.sh
```

### 5. Commit and push

```bash
cd /home/thadd/.hermes
git add .gitignore SOUL.md skills/ webui/ config.yaml
git commit -m "Backup: skills, config, .gitignore"
git remote add origin https://github.com/OWNER/REPO.git 2>/dev/null || true
git branch -M main
GIT_ASKPASS=/tmp/git-cred-helper.sh git push -u origin main
```

### 6. Restore config after push

```python3
with open('config.yaml.bak', 'r') as f:
    backup = f.read()
with open('config.yaml', 'w') as f:
    f.write(backup)
```

## Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Token in commit history | Never `git commit` before sanitizing `config.yaml` |
| Token in `ps` output | Never use `git remote add origin https://TOKEN@github.com/...` |
| `.env` committed | Add `.env` to `.gitignore` _before_ first commit |
| Credential helper left in `/tmp` | `rm -f` immediately after `git push` |
| `config.yaml` left sanitized after push | Restore from backup or the ollama bridge/APIs will break |
| User uploads partial `.env` | Always validate `.env` completeness before relying on it |
| Stale `/tmp/git-cred-helper.sh` with old token | Overwrite with new token, never reuse the file unchanged |
