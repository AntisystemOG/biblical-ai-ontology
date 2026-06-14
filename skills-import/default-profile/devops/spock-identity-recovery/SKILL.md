---
name: spock-identity-recovery
description: Create a dedicated GitHub repository containing the essential identity and memory files needed to reconstruct Spock (Hermes Agent persona) from scratch. Covers recovery repo structure, `README.md` with restoration instructions, and what files to include/exclude.
trigger:
  - backup spock identity
  - create recovery repo
  - spock identity backup
  - recover hermes agent
  - restore spock from scratch
---

# Spock Identity Recovery Repository

## Purpose

Create a lean GitHub repo that contains everything needed to reconstruct the Spock persona if the Hermes Agent instance is lost (WSL crash, PC failure, reinstall).

## What to Include

**Core identity files** (all from `/mnt/c/Users/thadd/.openclaw/workspace/`):
- `SOUL.md` — Core personality, values, boundaries
- `MEMORY.md` — Long-term memory (portfolio, predictions, preferences)
- `USER.md` — Who Thad is (family, values, preferences)
- `IDENTITY.md` — Spock/Vulcan identity specification
- `AGENTS.md` — Agent conventions, autonomy rules, heartbeat/cron docs
- `TOOLS.md` — Tool configurations and local notes
- `SECURITY.md` — Security rules and privacy boundaries
- `REGISTRY.md` — Agent/cron registry
- `DREAMS.md` — Memory-dreaming agent documentation
- `HEARTBEAT.md` — Heartbeat task checklist
- `HOME_PC_SETUP.md` — Home PC configuration
- `PLC_SPAWN.md` — PLCTools subagent spawning guide

**Plus:**
- `README.md` — Step-by-step recovery instructions
- `~/.hermes/config.yaml` — Hermes gateway configuration (tokens redacted)

## What to Exclude

**Do NOT include:**
- Daily briefs, whale watch reports, trading arena outputs (these are ephemeral)
- Large binary files (videos, audio, compiled EXEs)
- Active tokens or credentials (store `.env` separately, or use `~/.hermes/.env`)
- Session logs and raw chat transcripts
- Any file > 1MB (GitHub soft limit for web UI)

## Recovery Instructions (template for README.md)

```markdown
# Spock Recovery

## How to Recover Spock

### Step 1: Clone This Repo
git clone https://github.com/AntisystemOG/HermestoSpock.git
cd HermestoSpock

### Step 2: Set Up Workspace
mkdir -p /mnt/c/Users/thadd/.openclaw/workspace
cp *.md /mnt/c/Users/thadd/.openclaw/workspace/

### Step 3: Configure Hermes
cp config.yaml ~/.hermes/config.yaml
hermes gateway restart

### Step 4: Initial Session
Tell the agent: "Become Spock. Read SOUL.md, MEMORY.md, DREAMS.md, AGENTS.md, USER.md, IDENTITY.md."
```

## Workflow

1. **User requests recovery repo** → gather identity files → commit → push
2. **After each significant identity update** → commit changes to recovery repo
3. **Full workspace** stays in separate repo (`spock-workspace`) for complete backup

## Pitfalls

- **Token exposure**: Never commit `~/.hermes/.env` or any file containing real API keys. Redact or exclude.
- **Token in git remote**: After push, ALWAYS strip the token from the remote URL:
  ```bash
  git remote set-url origin https://github.com/USER/REPO.git
  ```
- **Outdated identity**: Recovery repo drifts from actual `MEMORY.md` over time. Review and update monthly.
- **Skill library not included**: Skills in `~/.hermes/skills/` are separate from the workspace. Back those up separately if customized.
