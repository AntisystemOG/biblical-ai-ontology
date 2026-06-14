---
name: backup-agent-state
description: "Backup an agent's runtime state (skills, config, SOUL) to a private GitHub repository without leaking secrets"
triggers:
  - "backup to github"
  - "git backup"
  - "push .hermes"
  - "backup my skills"
  - "save agent state"
toolsets: ["terminal", "file"]
---

# Backup Agent State to GitHub

Push `.hermes/` contents to a private GitHub repo for disaster recovery, keeping secrets (API keys, tokens, auth files) out of the remote.

---

## 1. Prerequisites

- Git installed
- A GitHub Personal Access Token (PAT) with `repo` scope
- A private GitHub repo (e.g. `AntisystemOG/Hermes`)

---

## 2. Write `.gitignore` (BEFORE first commit)

Create `/home/thadd/.hermes/.gitignore` before `git init` so nothing accidentally leaks:

```gitignore
# === SECRETS / CREDENTIALS ===
.env
.env.*
auth.json
auth.lock
*.key
*.pem

# === DATA / SESSIONS ===
*.db
*.sqlite
*.sqlite3
sessions/
backups/
state-snapshots/
audio_cache/
channel_directory.json

# === LOGS / CACHE ===
*.log
*.log.*
cache/
cache-web/
webui/logs/

# === OS ===
.DS_Store
Thumbs.db
temp_*.*

# === TEMP / BACKUP ===
*.tmp
*.temp
*.bak*
```

---

## 3. Sanitize `config.yaml`

`config.yaml` contains provider API keys and tokens. BEFORE committing, remove all values:

```bash
cd ~/.hermes
python3 -c "
import re
with open('config.yaml', 'r') as f:
    text = f.read()
# Blank out all api_key / session_key / token values
text = re.sub(r'(api_key|session_key|brave_api_key|token|password|secret_key):\s*\"[^\"]*\"', r'\1: \"\"', text)
with open('config.yaml', 'w') as f:
    f.write(text)
"
```

**Verify nothing remains:**
```bash
grep -rn "api_key.*=\|api_key:.*\"[^\"]\+\"" config.yaml | grep -v ': ""'
# Should return NOTHING
```

---

## 4. Commit contents

```bash
cd ~/.hermes
git init
git config user.email "agent@backup.local"
git config user.name "Spock-Agent"

git add SOUL.md skills/ .gitignore config.yaml config.yaml.bak*
git add webui/*.sh webui/*.md webui/*.json 2>/dev/null || true
git add bin/ 2>/dev/null || true
git commit -m "Initial backup: SOUL, skills, sanitized config"
```

---

## 5. Push securely (one-shot credential helper)

**Do NOT hardcode the PAT in the remote URL** — it leaks into `.git/config` and shell history.

Instead, use a temporary credential helper script:

```bash
# 1. Write helper
cat > /tmp/git-cred-helper.sh <<'EOF'
#!/bin/bash
case "$1" in
  get)
    echo "protocol=https"
    echo "host=github.com"
    echo "username=<GITHUB_USERNAME>"
    echo "password=<YOUR_PAT>"
    ;;
  store|erase) : ;;
esac
EOF
chmod 700 /tmp/git-cred-helper.sh

# 2. Push with helper
cd ~/.hermes
git remote add origin https://github.com/<OWNER>/<REPO>.git 2>/dev/null || true
git push -u origin main --force

# 3. IMMEDIATELY delete helper
rm -f /tmp/git-cred-helper.sh
```

**After push, verify remote has no leaked tokens:**
```bash
cd ~/.hermes
cat .git/config | grep -i "token\|password\|ghp_"
# Should return NOTHING
```

---

## 6. Restore from backup

```bash
cd ~
git clone https://github.com/<OWNER>/<REPO>.git hermes-recovery
# Then copy in live secrets from a local file or password manager
cp ~/.hermes/.env hermes-recovery/
cp ~/.hermes/auth.json hermes-recovery/
# Then replace ~/.hermes with hermes-recovery
```

---

## Pitfalls

- **Forgetting `.gitignore`** causes `auth.json` and `.env` to be committed. If this happens, rotate ALL exposed secrets immediately (API keys, tokens, passwords) — GitHub keeps history even after deletion.
- **Sanitizing `config.yaml` after committing** is too late — the secret is in git history forever. Always sanitize BEFORE first commit.
- **Don't reconstruct `.env` from redacted chat output** — `***` placeholders may end up written literally. Restore from a clean local backup (e.g. `.env.bak.pre-brave`).
- **Force push on main** rewrites remote history. Only use `--force` when the remote repo is brand new and empty.

---

## Verification checklist before every push

```bash
cd ~/.hermes
# 1. No secrets in staged files
git diff --cached | grep -E "api_key|token|password|secret" | grep -v ': ""'
# 2. .gitignore exists and covers .env / auth.json
ls .gitignore
# 3. config.yaml has blanked API keys
grep -c 'api_key: ""' config.yaml  # should be > 0
# 4. No log files or DBs staged
git diff --cached --name-only | grep -E '\.(db|log|sqlite3?)$'
# Should return NOTHING
```