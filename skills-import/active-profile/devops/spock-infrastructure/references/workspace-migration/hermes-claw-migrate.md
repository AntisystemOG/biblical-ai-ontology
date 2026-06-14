# `hermes claw migrate` CLI Reference

Built-in command for importing OpenClaw workspaces into Hermes. Handles skills, memory, config, env vars, and secrets.

## Usage

```bash
hermes claw migrate [options]
```

## Options

| Flag | Description |
|------|-------------|
| `--source PATH` | OpenClaw directory (default: `~/.openclaw`) |
| `--dry-run` | Preview only — no changes |
| `--preset {user-data,full}` | Scope of migration (default: `full`) |
| `--overwrite` | Replace conflicting targets (backs up originals) |
| `--migrate-secrets` | Include allowlisted secrets (API keys, bot tokens) |
| `--no-backup` | Skip pre-migration zip snapshot |
| `--workspace-target PATH` | Copy workspace files to a directory |
| `--skill-conflict {skip,overwrite,rename}` | How to handle skill name clashes |
| `--yes, -y` | Skip confirmation prompts |

## What Migrates (with `--preset full`)

- `SOUL.md` → `~/.hermes/SOUL.md`
- `MEMORY.md` / daily memory → `~/.hermes/memories/MEMORY.md`
- `USER.md` → `~/.hermes/memories/USER.md`
- `.env` (messaging settings, secrets with `--migrate-secrets`) → `~/.hermes/.env`
- `config.yaml` (model config, custom providers) → `~/.hermes/config.yaml`
- `skills/` (SKILL.md files) → `~/.hermes/skills/openclaw-imports/...`

## What Does NOT Migrate

- Cron jobs (must be recreated manually via `cronjob` tool)
- MCP servers
- Workspace files (unless `--workspace-target` is set)
- Discord/Slack/Signal/Signal settings if absent in source
- Browser config, approvals config, TTS config

## WSL-Specific Notes

- Windows OpenClaw often lives at `/mnt/c/Users/<name>/.openclaw/`, not `~/.openclaw`.
- Always pass `--source` explicitly on WSL.
- Gateway tokens may be at `C:\Users\<name>\.openclaw\credentials\telegram-pairing.json`.

## Pre-Migration Safety

1. **Stop OpenClaw** — `pkill -f openclaw` (varies by install)
2. **Stop Hermes gateway** — `hermes gateway stop`
   *Bot tokens only allow one active session. Running both causes disconnects.*
3. **Preview** — `hermes claw migrate --source PATH --dry-run`
4. **Check conflicts** — If `soul`, `secret-settings`, or `model-config` conflict, decide whether to `--overwrite`.
5. **Backup** — Hermes auto-creates `~/.hermes/backups/pre-migration-*.zip` before applying. Keep it.

## Post-Migration Verification

```bash
hermes skills list              # Check imported skills
hermes config check             # Validate config
hermes memory status            # Confirm memory
hermes cron list                # Note: no cron jobs migrated — recreate manually
```
