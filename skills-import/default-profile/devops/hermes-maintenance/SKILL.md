---
name: hermes-maintenance
description: "Maintain and update Hermes Agent installations on WSL — recover from failed updates, manage venv paths, reinstall dependencies, and keep extras in sync."
version: 1.0.0
author: Spock
platforms: [linux, wsl]
metadata:
  hermes:
    tags: [hermes, update, maintenance, wsl, uv, venv, dependencies, troubleshooting]
---

# Hermes Maintenance

Maintain and update Hermes Agent on WSL when the standard `hermes update` command fails or the environment has a non-standard venv layout.

## Trigger

- `hermes update` fails with `Python interpreter not found at <project-root>/venv/bin/python3`
- `hermes --version` still reports old version after `hermes update` claims success
- Need to reinstall optional extras after a manual update recovery
- Venv lives at `~/.hermes/hermes-agent/venv/` but source clone is elsewhere

## Recovery Pattern: Manual Reinstall After Failed Update

### 1. Verify the failure mode

```bash
cd /home/thadd/hermes-agent-ui  # or your clone dir
hermes --version
```

If git shows latest commit but `--version` reports the old version, the code was pulled but the Python package was NOT rebuilt.

### 2. Reinstall the base package with the correct venv

Do NOT rely on the updater's auto-detected venv path. Pin the correct Python explicitly:

```bash
cd /home/thadd/hermes-agent-ui
/home/thadd/.local/bin/uv pip install -e . --python /home/thadd/.hermes/hermes-agent/venv/bin/python
```

**Why this matters:** `hermes update` looks for `venv/bin/python3` inside the git clone directory. When your venv is at `~/.hermes/hermes-agent/venv/` (the standard Hermes install path), the updater cannot find it and aborts the dependency step. The git pull succeeds, but the package remains stale.

### 3. Verify the reinstall

```bash
hermes --version
```

Expected: `Up to date` instead of `N commits behind`.

### 4. Reinstall optional extras

The updater also skips extras during a failed dependency step. Reinstall any you need:

```bash
# Messaging (Telegram, Discord, Slack, WhatsApp, etc.)
/home/thadd/.local/bin/uv pip install -e ".[messaging]" --python /home/thadd/.hermes/hermes-agent/venv/bin/python

# Anthropic direct provider
/home/thadd/.local/bin/uv pip install -e ".[anthropic]" --python /home/thadd/.hermes/hermes-agent/venv/bin/python

# Dev tools (pytest, ruff, etc.)
/home/thadd/.local/bin/uv pip install -e ".[dev]" --python /home/thadd/.hermes/hermes-agent/venv/bin/python

# Edge TTS (default voice provider)
/home/thadd/.local/bin/uv pip install -e ".[edge-tts]" --python /home/thadd/.hermes/hermes-agent/venv/bin/python

# Modal / Daytona / Vercel backends
/home/thadd/.local/bin/uv pip install -e ".[modal]" --python /home/thadd/.hermes/hermes-agent/venv/bin/python
/home/thadd/.local/bin/uv pip install -e ".[daytona]" --python /home/thadd/.hermes/hermes-agent/venv/bin/python
/home/thadd/.local/bin/uv pip install -e ".[vercel]" --python /home/thadd/.hermes/hermes-agent/venv/bin/python
```

See `hermes-agent` skill or `pyproject.toml` for the full list of extras.

### 5. Restart the gateway if running

```bash
hermes gateway restart
```

Or `/restart` from the gateway chat.

## Key Paths for This Environment

| Path | Purpose |
|------|---------|
| `/home/thadd/hermes-agent-ui` | Git clone of NousResearch/hermes-agent (source of truth) |
| `/home/thadd/.hermes/hermes-agent/venv/` | Active Hermes Python venv (managed by uv) |
| `/home/thadd/.local/bin/uv` | uv binary for package management |
| `~/.hermes/config.yaml` | Main configuration |
| `~/.hermes/.env` | API keys and secrets |

## Pitfalls

1. **Do NOT create a new venv at the project root** just to make `hermes update` happy. That duplicates the environment and breaks profile-aware paths.
2. **Do NOT run `hermes update` again** after manual recovery unless the updater's venv detection has been fixed. It will stash your local changes and fail the same way.
3. **Always use `--python /home/thadd/.hermes/hermes-agent/venv/bin/python`** with `uv pip install`. Omitting it may target a system Python or a different venv.
4. **Local changes survive the update** because `hermes update` stashes before pulling and restores after. Review `git status`/`git diff` after recovery if anything behaves unexpectedly.
5. **Clear `__pycache__` after major updates** — the updater already does this (`69 stale __pycache__ directories cleared`), but verify if you did a purely manual reinstall.

## Related Skills

- `hermes-agent` — general Hermes setup, config, and CLI reference
- `spock-infrastructure-health` — Spock WebUI and gateway health checks
- `hermes-webui-upgrade-preservation` — preserving Spock branding across upgrades
