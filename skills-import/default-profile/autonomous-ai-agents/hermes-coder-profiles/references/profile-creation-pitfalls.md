# Profile Creation Pitfalls

Common mistakes when creating specialized Hermes profiles for coding or other tasks, and how to avoid them.

## Pitfall 1: Wrong `toolsets` Syntax

**Problem:** Setting toolsets as a plain YAML list or space-separated string causes the config to be ignored.

**Wrong:**
```bash
hermes config set toolsets "[terminal, file, code_execution]"
hermes config set toolsets "terminal file web"
```

**Correct:**
```bash
hermes config set toolsets '["terminal", "file", "code_execution", "web", "search", "browser", "vision", "skills", "memory", "session_search", "delegation", "cronjob", "todo", "kanban", "debugging", "clarify"]'
```

The value must be a **valid JSON array string** because Hermes parses it as JSON at startup.

## Pitfall 2: Trying to Install Already-Bundled Skills

**Problem:** `hermes skills install claude-code` or `hermes skills install kanban-worker` fails with "No exact match" or "Blocked" because these skills are already installed as **local bundled skills**.

**Symptom:**
```
Resolving 'claude-code'...
No exact match for 'claude-code'. Did you mean one of these?
  ai-regression-testing...
```

**Fix:** Check if the skill is already installed:
```bash
devteam skills list
```

Bundled skills in `autonomous-ai-agents` are pre-installed:
- `claude-code` — Claude Code CLI delegation
- `codex` — OpenAI Codex CLI delegation
- `opencode` — OpenCode CLI delegation
- `kanban-codex-lane` — Kanban + Codex lane pattern
- `hermes-agent` — Core Hermes configuration

Hub installation is only needed for skills **not** in the bundled list.

## Pitfall 3: Profile Create Syntax

**Problem:** `hermes profile create devteam default` or `hermes profile create devteam --clone default` fails.

**Symptom:**
```
hermes: error: unrecognized arguments: default
```

**Fix:** Use the correct syntax:
```bash
# Clone from active (current) profile
hermes profile create devteam --clone

# Clone from a specific source
hermes profile create devteam --clone --clone-from default

# With description
hermes profile create devteam --clone --description "Expert coding agent..."
```

The `--clone` flag has **no value** — it just copies the active profile. Use `--clone-from` with a value to specify a source.

## Pitfall 4: Config Not Applied to Profile

**Problem:** Setting config without `--profile` updates the **default** profile, not the new one.

**Wrong:**
```bash
hermes config set agent.max_turns 150
# This sets it on the default profile, not devteam
```

**Correct:**
```bash
# Method 1: Use the profile wrapper
devteam config set agent.max_turns 150

# Method 2: Use --profile flag
hermes config set agent.max_turns 150 --profile devteam
```

The profile wrapper script (`devteam`) automatically sets the correct `HERMES_PROFILE` env var.

## Pitfall 5: Forgetting to Set Workspace

**Problem:** The agent uses the default workspace (`/home/thadd` or wherever you launched it) instead of the project workspace.

**Fix:** Always set `terminal.cwd`:
```bash
devteam config set terminal.cwd /mnt/c/Users/thadd/.openclaw/workspace
```

This ensures all `terminal` commands, `read_file` calls, and `search_files` operations start in the correct directory.

## Pitfall 6: Not Verifying the Profile Works

**Problem:** Creating the profile but never testing it leads to discovering misconfiguration hours later.

**Fix:** Run a quick system check immediately after creation:
```bash
devteam chat -q "System check: What profile am I, what tools do I have, and what's my workspace?"
```

This verifies:
- Profile loads correctly
- Toolsets are enabled
- Model/provider are configured
- Workspace is set

## Pitfall 7: Generic SOUL.md

**Problem:** The cloned `SOUL.md` from the default profile is a generic assistant persona. The coding agent acts like a chatbot instead of an engineer.

**Fix:** Replace `SOUL.md` with a coding-specific identity:
- "Read before writing"
- "Test before claiming done"
- "Small, reviewable changes"
- "Self-learning loop"

See `references/devteam-soul-template.md` for a complete template.

## Pitfall 8: No AGENTS.md

**Problem:** Without an `AGENTS.md`, the agent has no operational workflow guidance. It skips planning, forgets verification, and never saves skills.

**Fix:** Create `AGENTS.md` in the profile directory with:
- Discovery → Planning → Execution → Verification → Learning workflow
- Code quality rules
- Communication style
- Self-learning triggers

See `references/devteam-agents-template.md` for a complete template.

## Verification Checklist

After creating a coding profile, verify:
- [ ] `hermes profile list` shows the new profile
- [ ] `devteam skills list` shows expected skills
- [ ] `devteam config path` points to the profile directory
- [ ] `devteam chat -q "system check"` returns correct profile/tools/workspace
- [ ] `SOUL.md` contains coding-specific identity
- [ ] `AGENTS.md` contains operational workflow
