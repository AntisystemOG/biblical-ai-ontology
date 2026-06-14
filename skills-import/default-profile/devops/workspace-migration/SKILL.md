---
name: workspace-migration
description: Migrate an agent workspace from one system to another — locating agent configs, reading persona and memory files, mapping schedules to cron jobs, and preserving context across platforms. Covers imports from OpenClaw, Claude Code, and other agent ecosystems into Hermes.
triggers:
  - User asks to "import my agent" or "import my workspace"
  - User references `.openclaw`, `.claude`, or another agent platform directory
  - User wants to move agent data, cron schedules, or memory from one system to another
  - User says "sync my workspace" across machines or platforms
---

# Workspace Migration

Migrate agent workspaces, configurations, and scheduled tasks from one platform to another while preserving context.

## When to Use

- Importing an existing agent workspace (OpenClaw, Claude Code, etc.) into Hermes
- Migrating cron schedules and agent configs between systems
- Syncing workspace data across machines (work PC → home PC, Windows → WSL)
- Setting up parallel cron jobs to mirror an existing automation setup
- Preserving user persona, memory, and agent behavior when switching platforms

## UI Target: Browser-Based vs Electron

For WSL + Windows setups, **prefer browser-based web UIs run inside WSL** over Electron desktop apps or Windows-native Node processes. Electron requires Node module platform alignment, a display server, and is prone to accidental first-run onboarding. Running the web UI dev server in WSL and accessing it from Windows browser (`http://localhost:8648`) avoids cross-platform spawn issues (e.g., `Error: spawn hermes ENOENT`). See `references/web-ui-cross-platform-integration.md` for the wrapper workaround if running on Windows is required.

## Prerequisites

- Identify the source workspace path (often hidden: `~/.openclaw/workspace/`, `~/.claude/`, etc.)
- Map Windows ↔ WSL paths (e.g. `C:\Users\<name>` → `/mnt/c/Users/<name>`)
- Know the target machine's timezone for cron scheduling

## Migration Steps

### Preferred Path: Built-in Hermes Migration (`hermes claw migrate`)

Hermes has a built-in OpenClaw importer. Use this first — it handles skills, memory, user profile, config, and secrets automatically.

**1. Stop both services before migrating**

Bot tokens (Telegram, Discord, Slack) only allow one active session per token. If both OpenClaw and Hermes gateway are running, the migration will warn and may cause disconnects:

```bash
# Stop Hermes gateway
hermes gateway stop

# Stop OpenClaw (method varies by install)
pkill -f openclaw          # or the OpenClaw stop command
```

**2. Preview with dry-run**

Always preview first to see conflicts:

```bash
hermes claw migrate --source /mnt/c/Users/thadd/.openclaw --dry-run
```

Common conflicts:
- `soul` — Hermes SOUL.md already exists
- `secret-settings` — .env already has different values
- `model-config` — model already configured in Hermes

**3. Run the migration**

```bash
hermes claw migrate \
  --source /mnt/c/Users/thadd/.openclaw \
  --preset full \
  --migrate-secrets \
  --overwrite \
  --yes
```

Flags:
- `--source PATH` — OpenClaw directory (default `~/.openclaw`)
- `--preset full` — migrates skills, memory, config, and env vars
- `--migrate-secrets` — includes allowlisted secrets (API keys, bot tokens)
- `--overwrite` — replaces conflicting targets (backs up originals first)
- `--yes` — skips confirmation prompts
- `--workspace-target PATH` — copies workspace files to a specific directory

**4. Verify results**

```bash
hermes skills list
hermes config check
```

**What gets migrated:** SOUL.md, MEMORY.md, USER.md, .env secrets, config.yaml, skills, daily memory.

**What does NOT get migrated:** cron jobs, MCP servers, workspace files (unless `--workspace-target` is set), Discord/Slack/Signal settings if none exist in OpenClaw.

**WARNING:** OpenClaw may respawn during migration (Windows services, scheduled tasks, etc.). If `hermes claw migrate` warns "OpenClaw appears to be running" mid-process, `pkill -f openclaw` and re-run the migration. The importer does NOT block or restart itself when the source platform is still active.

### Manual Fallback Migration

Use the manual steps below only if the built-in importer fails or the source platform is not OpenClaw.

#### 1. Locate and Explore Source Workspace

Search for known agent platform directories:

```bash
find /mnt/c/Users/ -maxdepth 3 -type d -iname '*openclaw*' 2>/dev/null
find /mnt/c/Users/ -maxdepth 3 -type d -iname '*claude*' 2>/dev/null
```

**WSL note:** Windows OpenClaw installs often live under `/mnt/c/Users/<name>/` rather than `~/.openclaw`. Check both.

Key directories to inspect:
- `agents/` — agent config files (`.md`)
- `memory/` — daily logs (`.md` / `.sqlite`)
- `cron/` — scheduled job state (`.json`)
- `workspace/` — working files, scripts, reports, skills
- `flows/` — flow registry (`.sqlite`)

#### 2. Read Core Persona Files

In priority order — these define identity and behavior:
1. `SOUL.md` — agent persona, values, vibe, truth principle
2. `USER.md` — user profile, family, preferences, timezone
3. `AGENTS.md` — session startup rules, naming conventions, autonomy rules
4. `HEARTBEAT.md` — proactive check rules, health checks
5. `TOOLS.md` — local system specifics (installed binaries, env vars)
6. `MEMORY.md` — curated long-term memory

#### 3. Read Agent Configs

For each `.md` file in the agents directory, extract:
- **Role / purpose** (what this agent does)
- **Schedule** (when it runs — map to cron expressions)
- **Task steps** (what the agent does each run)
- **Output location** (where reports go)
- **Universal rules** (e.g. "signal completion", naming conventions)
- **Important notes** (gotchas, hard-coded paths, Windows vs WSL paths)

Common agent patterns from OpenClaw:
| Agent | Schedule | Mirrors |
|-------|----------|---------|
| whale-watch | Daily 6:00 AM | Hedge fund 13F overlap tracker |
| history-rhymes | Daily 7:00 AM | Market history pattern analyzer |
| daily-brief | Daily 8:00 AM | Ground News cross-spectrum summary |
| financial-advisor | Monday 9:00 AM | Value investing screener |
| memory-dreaming | Daily 3:00 AM | Memory synthesis / dream diary |
| trading-arena | M-F 8:30-15:00 every 30min | Trading simulation dashboard |
| top-100-strategists | Daily 9:00 AM | Hedge fund conviction analysis |
| long-term-holds | Monday 10:00 AM | Inflation-beating asset allocator |

#### 4. Create Hermes Cron Jobs

Use `cronjob` tool with `action='create'` for each agent. Include in the prompt:
- The agent's exact task steps (from the source config)
- Timezone awareness (America/Chicago = CDT/UTC-5 or CST/UTC-6)
- WSL path mapping rules for any Windows paths in the source
- The source's universal rules (e.g. "end with Done/Complete/Failed")
- Toolsets needed (usually `["web", "terminal", "file"]`)

**WSL Path Conventions:**
- Space-containing paths: `C:\Users\thadd\Desktop\Portfolio Positions` → `/mnt/c/Users/thadd/Desktop/Portfolio Positions` (with quotes in terminal, escaped in cron prompts)
- Underscore aliases: Some systems use `Spocks_Reports` to avoid spaces — check which path actually exists
- Git workspace: If the source is git-backed, set `--workdir` on the cron job (absolute path) so file tools default to the right directory for reports

Set schedules using cron expressions that match the source times.

#### 5. Read Recent Memory for Context

Read the latest 5-7 daily memory files to catch up on what's happening:
- `memory/YYYY-MM-DD.md` files
- Note events, decisions, open tasks, system status, and errors

#### 6. Save Key Facts to Hermes Persistent Memory

Use `memory` tool with `target='memory'` and `target='user'` to store:
- User profile (name, timezone, values, family)
- Portfolio / financial data (if present and user approves)
- Active predictions / investment thesis
- Current projects and their status
- Security rules (never share without permission)
- Workspace path and git workflow rules

#### 7. Report Back

Summarize:
- What was read
- What cron jobs were created (with job IDs)
- What remains un-migrated
- Any gotchas or path issues encountered

## Common Gotchas

- **Path mismatches:** Source configs reference `C:\Users\thadd\...` but Hermes runs in WSL. Map to `/mnt/c/Users/thadd/...`. Also, OpenClaw on Windows may live at `/mnt/c/Users/<name>/.openclaw` rather than `~/.openclaw`.
- **Service conflicts:** Never migrate while OpenClaw or Hermes gateway are running. Both will fight over the same Telegram/Discord bot token and cause disconnects. Stop both first.
- **Migration conflicts:** If `hermes claw migrate` reports conflicts (soul, secret-settings, model-config), use `--dry-run` to preview, then `--overwrite` to apply. Hermes automatically creates a pre-migration backup at `~/.hermes/backups/pre-migration-*.zip`.
- **Model allowlists:** The source may target models not available in Hermes (e.g. `kimi-k2.6:cloud` blocked). Note this but don't attempt to fix.
- **Skills vs cron configs:** OpenClaw has a `skills/` directory with SKILL.md files. These are platform-agnostic knowledge that can be reused. Just read them — don't migrate them as cron jobs.
- **SQLite databases:** Source memory may be in `.sqlite` files — read them with SQLite tools if needed, but don't overwrite Hermes memory directly.
- **Git sync:** The source workspace may be git-backed. A separate cron job for `git pull` keeps it in sync.
- **`hermes` CLI not found after migration:** If `hermes: command not found` occurs when restarting the gateway, the CLI may live in `~/.local/bin/hermes` or a venv. Find it with `find /home/$USER -maxdepth 5 -name 'hermes' -type f` and use the full path, or source `~/.profile` if installed via pip.

## Post-Migration Cleanup

After `hermes claw migrate` completes, there are usually a few manual cleanup items:

### 1. Remove deprecated `.env` keys

OpenClaw stored `MESSAGING_CWD` in `.env`, which is deprecated in Hermes. If present, the gateway will log a warning on every start:

```
⚠ MESSAGING_CWD=C:\Users\thadd\.openclaw\workspace found in .env — this is deprecated.
  Move to config.yaml instead:  terminal:\n    cwd: /your/project/path
```

**Fix:**
```bash
hermes config set terminal.cwd /mnt/c/Users/thadd/.openclaw/workspace
sed -i '/^MESSAGING_CWD=/d' ~/.hermes/.env
```

Replace the path with the actual workspace directory.

### 2. `--migrate-secrets` quirk: partial migration

The tool may report *"API keys were NOT migrated"* even when some secrets (e.g. `OLLAMA_API_KEY`, `TELEGRAM_BOT_TOKEN`, `HERMES_GATEWAY_TOKEN`) **did** transfer. Always verify the actual `.env` contents after migration rather than trusting the summary message.

```bash
cat ~/.hermes/.env | grep -E 'API_KEY|TOKEN'
```

Provider API keys like `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY` may still need manual addition if they were stored as Windows env vars rather than in OpenClaw's config files.

### 3. Restart the gateway

New `.env` values and config changes only take effect after a gateway restart:

```bash
hermes gateway restart
```

### 4. Verify Telegram pairing

If the Telegram bot token was migrated, confirm the pairing still works:

```bash
hermes pairing list
hermes pairing approve telegram <chat_id>   # if needed
```

## Support Files

- `references/hermes-claw-migrate.md` — CLI reference for the built-in `hermes claw migrate` importer (options, flags, what migrates, WSL notes)
- `references/openclaw-structure.md` — Directory layout, file types, and mapping of OpenClaw → Hermes concepts
- `references/post-migration-cleanup.md` — Step-by-step checklist after migration (deprecated keys, secret verification, gateway restart, pairing)

- `hermes-agent` — Hermes configuration and setup
- `cronjob` — Hermes scheduling tool reference
- `memory` — Hermes persistent memory usage
