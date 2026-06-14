---
name: hermes-coder-profiles
description: "Create and configure specialized Hermes profiles for autonomous software development, multi-project coding, and self-learning agent workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, profiles, coding, multi-agent, autonomous-development, devtools]
    related_skills: [hermes-agent, kanban-orchestrator, kanban-worker, claude-code, codex, opencode]
---

# Hermes Coder Profiles

Create dedicated Hermes profiles that act as autonomous software engineering agents — capable of coding across multiple projects, self-learning through skills and memory, delegating work via Kanban, and coordinating with other agents.

## Why Dedicated Coding Profiles?

The default Hermes profile is a generalist. A `devteam`-style profile is a specialist:
- **Extended turn budget** (150 vs 90) for complex coding sessions
- **High reasoning effort** for architecture decisions
- **Relaxed tool enforcement** so the agent uses tools proactively without excessive prompting
- **Rich toolset** covering the full developer stack: terminal, file I/O, code execution, web research, browser testing, vision analysis, delegation, Kanban, cron, and debugging
- **Persistent project awareness** via `AGENTS.md` and custom `SOUL.md`
- **Self-learning triggers** that automatically save patterns, pitfalls, and workflows as skills

## Quick Start: Create a Coding Profile

```bash
# 1. Create and clone from default
hermes profile create devteam --clone --description "Expert coding agent with terminal, file, code execution, web search, git, and self-learning skills."

# 2. Set workspace
hermes profile create devteam --config set terminal.cwd /path/to/your/workspace

# 3. Enable full developer toolset
hermes profile create devteam --config set toolsets '["terminal", "file", "code_execution", "web", "search", "browser", "vision", "skills", "memory", "session_search", "delegation", "cronjob", "todo", "kanban", "debugging", "clarify"]'

# 4. Extend session limits
hermes profile create devteam --config set agent.max_turns 150
hermes profile create devteam --config set agent.reasoning_effort high
hermes profile create devteam --config set agent.tool_use_enforcement relaxed
```

## Complete Configuration Reference

### Profile Creation

```bash
hermes profile create <name> --clone [--description "..."]
```

| Flag | Effect |
|------|--------|
| `--clone` | Copy config.yaml, .env, SOUL.md from active profile |
| `--clone-all` | Full copy including sessions, skills, memory |
| `--clone-from SOURCE` | Clone from a specific source profile |
| `--no-alias` | Skip wrapper script creation |
| `--no-skills` | Create empty profile without bundled skills |
| `--description` | Sets orchestrator routing context for Kanban |

**Wrapper script:** Hermes automatically creates `/home/thadd/.local/bin/<name>` (e.g., `devteam`). Use this to invoke the profile directly.

### Toolsets for Coding (JSON array string)

The `toolsets` config value must be a **JSON array string**, not a YAML list:

```bash
# CORRECT — JSON array string
hermes config set toolsets '["terminal", "file", "code_execution", "web", "search", "browser", "vision", "skills", "memory", "session_search", "delegation", "cronjob", "todo", "kanban", "debugging", "clarify"]'

# WRONG — YAML list syntax (will fail or be ignored)
hermes config set toolsets "[terminal, file, code_execution]"
```

### Recommended Coding Configuration

```yaml
model:
  default: kimi-k2.6          # or your preferred model
  provider: ollama-cloud      # or anthropic, openrouter, etc.

toolsets: '["terminal", "file", "code_execution", "web", "search", "browser", "vision", "skills", "memory", "session_search", "delegation", "cronjob", "todo", "kanban", "debugging", "clarify"]'

agent:
  max_turns: 150
  reasoning_effort: high
  tool_use_enforcement: relaxed
  gateway_timeout: 1800

terminal:
  backend: local
  cwd: /mnt/c/Users/thadd/.openclaw/workspace
  timeout: 180
```

### Verification

```bash
# Quick system check
devteam chat -q "System check: What profile am I, what tools do I have, and what's my workspace?"
```

## Customizing Profile Identity

### SOUL.md — The Agent's Core Identity

Replace the cloned generic `SOUL.md` with one tailored for software engineering:

Key principles to embed:
- **Read before writing** — search and read existing code before modifying
- **Test before claiming done** — run the test suite, add regression tests
- **Small, reviewable changes** — commit early and often
- **Document the "why"** — comments explain intent, not mechanics
- **Self-learning loop** — after every significant task, ask: "What did I learn? Save it as a skill."

See `references/devteam-soul-template.md` for a complete working template.

### AGENTS.md — Operational Workflow

Create an `AGENTS.md` in the profile directory to define:
- Discovery → Planning → Execution → Verification → Learning workflow
- Multi-project awareness (read local project `CLAUDE.md` before working)
- Code quality rules (types, error handling, testing, security)
- Kanban integration for large tasks
- Git discipline (branch naming, commit message format)
- Communication style with the user

See `references/devteam-agents-template.md` for a complete working template.

## Multi-Project Awareness

A coding agent should maintain context across multiple projects. Configure known project paths in the profile's memory or `AGENTS.md`:

```
Key projects:
- OpenClaw workspace → /mnt/c/Users/thadd/.openclaw/workspace
- Spock WebUI → /mnt/c/Users/thadd/hermes-web-ui
- Hermes config → /home/thadd/.hermes/
```

When the user says "work on the WebUI" or "fix the bot", the agent knows where to go.

## Self-Learning System

### Triggers for Saving Skills

Save a skill when the agent:
- Solves a problem that took 3+ tool calls
- Discovers a non-obvious workflow or tool combination
- Finds a pitfall that wasted significant time
- Creates a reusable script, template, or configuration

### Triggers for Saving Memory

Save to memory when the agent:
- Learns a user preference about code style or workflow
- Discovers an environment quirk (e.g., "WSL needs this flag")
- Finds a particularly useful library or tool

### Built-In Coding Agent Delegation

The profile inherits skills for delegating to specialized CLI coding agents:
- **Claude Code** (`claude-code` skill) — `claude -p "task"` for one-shots
- **OpenAI Codex** (`codex` skill) — `codex exec "task"` for autonomous coding
- **OpenCode** (`opencode` skill) — Alternative agent CLI

These are already bundled; no hub installation needed.

## Hub Skills vs Local Bundled Skills

**Critical pitfall:** `hermes skills install claude-code` or `hermes skills install kanban-worker` will fail with "No exact match" or "Blocked" because these are **already installed as local bundled skills**.

To verify what skills a profile has:
```bash
devteam skills list
```

Bundled skills in the `autonomous-ai-agents` category (all pre-installed):
- `claude-code` — Claude Code CLI delegation
- `codex` — OpenAI Codex CLI delegation
- `opencode` — OpenCode CLI delegation
- `kanban-codex-lane` — Kanban worker + Codex lane pattern
- `hermes-agent` — Core Hermes configuration and spawning

## Advanced: Kanban Integration

For large projects requiring multiple specialists:

1. Break the task into subtasks using the agent's planning phase
2. Create Kanban cards with clear acceptance criteria
3. Assign them to appropriate profiles (e.g., `devteam` for coding, `designer` for UI)
4. Link dependencies between cards
5. Let the Kanban dispatcher spawn workers automatically

The `kanban-orchestrator` and `kanban-worker` skills cover this in depth.

## Emergency Recovery

If a profile becomes corrupted or misconfigured:
```bash
# Delete and recreate
hermes profile delete devteam
hermes profile create devteam --clone --description "..."
# Re-apply configuration
```

If you only need to reset a single config value:
```bash
hermes config set agent.max_turns 150 --profile devteam
```

## References

- `references/devteam-soul-template.md` — Complete SOUL.md template for a coding agent
- `references/devteam-agents-template.md` — Complete AGENTS.md template for operational workflow
- `references/profile-creation-pitfalls.md` — Common mistakes when creating profiles
