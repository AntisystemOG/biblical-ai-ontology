# Token & Credential Hygiene — Quick Reference

## The `.hermes/.env` Vault

`~/.hermes/.env` stores ALL tokens (Ollama, Telegram, ElevenLabs, GitHub PAT, Brave API key, etc.). It is the single source of truth. Corrupting it means recovering tokens from provider dashboards.

## Rules

### 1. Append, Never Overwrite
```bash
# WRONG — wipes all existing tokens
echo "X=Y" > ~/.hermes/.env

# RIGHT — safe append
echo "X=Y" >> ~/.hermes/.env

# Best — open in editor
nano ~/.hermes/.env
```

### 2. Never Reconstruct from Chat
Chat transcripts show credentials as **redacted** (`***`). Pasting what you see in chat will write literal `***` into `.env`.

**Recovery steps if .env is corrupted:**
- If `~/.hermes/.env.bak*` exists: restore from that
- If no backup: re-enter each token manually from provider dashboards
- Never try to reconstruct from redacted chat output

### 3. Inline Token for One-Shot Operations
When a token must be passed to a command (git push, curl with auth):
```bash
source ~/.hermes/.env && \
  git remote set-url origin "https://${GITHUB_PAT}@github.com/USER/REPO.git" && \
  git push && \
  git remote set-url origin "https://github.com/USER/REPO.git"
```

Afterwards verify remote is clean:
```bash
git remote -v
# Must NOT contain token string
```

### 4. Revoke Exposed Tokens Immediately
- Go to provider settings (GitHub: https://github.com/settings/tokens)
- Revoke the token
- Generate new token
- Replace in `~/.hermes/.env` via `nano`

## Hermes Venv Path
When a Hermes skill script needs a Python package (e.g., `ddgs` for web search), install into Hermes' own venv — NOT system pip:
```bash
/home/thadd/.hermes/hermes-agent/venv/bin/pip install ddgs
```
System `pip` is frequently missing in WSL. The venv path is reliable.
