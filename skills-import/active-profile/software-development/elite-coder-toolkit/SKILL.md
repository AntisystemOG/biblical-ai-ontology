---
name: elite-coder-toolkit
description: "The complete arsenal of an elite AI coding agent — tools, workflows, and techniques for maximum code quality, speed, and intelligence."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding, agent, tools, workflow, quality, productivity]
    related_skills: [systematic-debugging, test-driven-development, subagent-driven-development, writing-plans, requesting-code-review]
---

# Elite Coder Toolkit

## Overview

This is the complete knowledge base of an elite AI coding agent. It synthesizes the best tools, workflows, and techniques from the top AI coding projects on GitHub, combined with battle-tested software engineering principles.

**Goal:** Be the best coder on the planet. Write code that is correct, tested, documented, and maintainable. Ship fast without sacrificing quality.

## Core Philosophy

1. **Quality is speed** — Good code ships once. Bad code ships, breaks, and ships again.
2. **Test everything** — If it doesn't have a test, it doesn't exist.
3. **Debug systematically** — Never guess. Find root cause first.
4. **Delegate when parallelizable** — Use subagents for independent tasks.
5. **Plan before you code** — A few minutes of planning saves hours of refactoring.

## The Elite Workflow

### Phase 1: Understand (5-10 minutes)
1. Read the codebase — use `search_files` and `read_file`
2. Understand existing patterns and conventions
3. Check `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `package.json`
4. Run existing tests to verify baseline

### Phase 2: Plan (5-15 minutes)
1. Load `writing-plans` skill
2. Break work into bite-sized tasks (2-5 min each)
3. Identify dependencies between tasks
4. Write the plan to `.hermes/plans/` or task body

### Phase 3: Implement (via TDD or subagents)
**For single-file changes (< 50 lines):**
1. Write failing test (RED)
2. Implement minimal fix (GREEN)
3. Refactor
4. Commit

**For multi-file features:**
1. Load `subagent-driven-development` skill
2. Dispatch implementer subagent per task
3. Two-stage review (spec → quality)
4. Final integration review

### Phase 4: Verify (5-10 minutes)
1. Run full test suite
2. Check for regressions
3. Verify against original requirements
4. Update documentation

### Phase 5: Ship (2-5 minutes)
1. Good commit message: `type: what changed`
2. Push to remote
3. Update task status

## Critical Skills to Always Load

| Skill | When to Load | Purpose |
|-------|-------------|---------|
| `systematic-debugging` | Any bug, error, or unexpected behavior | 4-phase root cause investigation |
| `test-driven-development` | New features, bug fixes, refactoring | RED-GREEN-REFACTOR cycle |
| `subagent-driven-development` | Multi-task features, parallel work | Fresh subagent + 2-stage review per task |
| `writing-plans` | Before any non-trivial implementation | Bite-sized task breakdown |
| `requesting-code-review` | Before marking work complete | Security scan, quality gates |
| `spike` | Unknown territory, new tech | Validate idea before build |
| `codebase-text-replacement` | Bulk renames, rebranding | Safe across-project string replacement |

## Tool Pitfalls (learned the hard way)

### PySide6 / Qt Widget Flicker Fix

When widgets (LEDs, buttons, labels, banners) appear to blink or glitch during rapid updates — e.g. timeline playback or fast PLC polling — root causes are usually unconditional style/text/value reassignment.

**Guards:** Every `setChecked()`, `setStyleSheet()`, `setText()`, and custom `set_on()` must compare current state before changing:

```python
# BEFORE — flickers every frame
self._on_btn.setChecked(is_on)

# AFTER — only repaints on change
if self._on_btn.isChecked() != is_on:
    self._on_btn.setChecked(is_on)
```

**Mode banners:** Cache `_cached_man_auto`; only update when value changes.

**Custom paint widgets:** Cache `_is_on`; `update()` only on change.

**Stylesheet via objectName switching (advanced):** For buttons that change color by state, define `#id` selectors in a central QSS file and switch `objectName` at runtime. Prevents inline CSS duplication. Always `unpolish()` + `polish()` + `update()` after switching. Skip if the name hasn't changed.

**Batched updates for bulk widget changes:**
```python
self.parent_widget.setUpdatesEnabled(False)
try:
    for indicator in self._indicators:
        indicator.set_on(new_value)
finally:
    self.parent_widget.setUpdatesEnabled(True)
```

See `references/pyside6-widget-flicker-fix.md` for the full checklist including emoji-clipping container widths, invisible theme-button debugging, and gradient QSS translation from UI kit images.

### `read_file` pagination corrupts subsequent `patch`/`write_file`

**Problem:** When you use `read_file` on a large file, Hermes auto-paginates the output and prepends `"    N|"` line numbers to every line. If you then copy that content into `patch` or `write_file`, the line numbers get baked into the actual file, corrupting it.

**Example of corrupted line:**
```
     8|     8|        :root {
```

**Fix — Two approaches:**

1. **For small files:** Use `read_file` with a `limit` large enough to read the entire file without pagination. Check `truncated` field in the response. If `truncated: true`, the content has line numbers — **do not use it for editing**.

2. **For large files:** Fall back to `execute_code` with Python to read the raw file directly:
```python
with open('/path/to/file', 'r') as f:
    content = f.read()
# Process content...
with open('/path/to/file', 'w') as f:
    f.write(modified)
```

3. **For targeted edits on large files:** Use `patch` with `mode='replace'` and find/replace strings that do NOT include the line number prefix. `patch` operates on the actual file on disk, so it is immune to the `read_file` line number issue.

**Rule:** Never trust `read_file` output for editing if `truncated: true` or if line numbers are visible.

### Windows path backslashes in Python docstrings trigger SyntaxWarning

**Problem:** A docstring containing a Windows path like `%LOCALAPPDATA%\Degater PLC Tool\...` produces:
```
SyntaxWarning: "\D" is an invalid escape sequence. Such sequences will not work in the future.
```
This happens because `"\D"` is interpreted as an escape sequence during compilation.

**Fix:** Convert the docstring to a raw string:
```python
r"""
Application entry point for Degater PLC Tool.

Recordings are stored in:
    Windows: %LOCALAPPDATA%\Degater PLC Tool\BST33 and 35\recordings
"""
```

**Rule:** Any docstring or string literal that documents Windows paths must use `r"""` or `r''` to prevent escape-sequence warnings. This is especially important for codebases that build into Windows executables via PyInstaller, because the warning surfaces at build time and clutters the build log.

### PySide6/Qt class relocation in 6.8+ breaks frozen EXE imports

**Problem:** The WSL development environment may have an older PySide6 where `QAction` and `QActionGroup` are still importable from `PySide6.QtWidgets`, but the Windows Python used by PyInstaller has PySide6 6.8+ where those classes moved to `PySide6.QtGui`. The code runs fine in WSL development but the frozen EXE crashes at launch with:
```
ImportError: cannot import name 'QAction' from 'PySide6.QtWidgets'
```

**Fix:** Import from `PySide6.QtGui` instead:
```python
from PySide6.QtGui import QAction, QActionGroup
```

**Prevention:** After any PySide6 import change, verify it works in the Windows Python environment:
```bash
/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe -c \
  "from PySide6.QtGui import QAction, QActionGroup; print('OK')"
```

**Rule:** Always test-build and launch the EXE after any Qt import changes. The frozen bundle's Qt version is the ground truth, not the WSL dev environment.

## Code Quality Standards

### Type Safety
- Use types everywhere available. No `any` without justification.
- Prefer strict mode (TypeScript, mypy, etc.)

### Error Handling
- Every async operation needs a catch.
- Every external call needs a fallback.
- Validate inputs at boundaries.

### Logging
- Errors: `console.error` or structured logging
- Debug: `console.debug`
- Info: `console.info`
- Never log secrets or PII.

### Performance
- Don't optimize prematurely, but know Big-O.
- Profile before optimizing.
- Cache intelligently, not aggressively.

### Security
- Never commit secrets.
- Validate inputs. Sanitize outputs.
- Use parameterized queries.
- Prefer least-privilege access.

## Debugging Arsenal

### Systematic Debugging (from `systematic-debugging` skill)
```
Phase 1: Root Cause Investigation
Phase 2: Pattern Analysis
Phase 3: Hypothesis and Testing
Phase 4: Implementation (with regression test)
```

### Common Debug Patterns
- **Test fails**: Read error carefully → reproduce → check recent changes → trace data flow
- **Build fails**: Check dependencies → check syntax → check environment
- **Performance issue**: Profile first → identify bottleneck → optimize
- **Heisenbug**: Add logging → reproduce → remove logging one by one

### Debug Tools
- `node --inspect` + Chrome DevTools (load `node-inspect-debugger`)
- `debugpy` remote (load `python-debugpy`)
- `pytest -v --tb=long` for Python
- `console.trace()` for JavaScript
- `git bisect` for regression hunting

## Testing Arsenal

### TDD Cycle (from `test-driven-development` skill)
1. Write failing test (RED)
2. Run test to confirm failure
3. Write minimal code to pass (GREEN)
4. Run all tests
5. Refactor (keep tests green)
6. Repeat

### Test Coverage
- Unit tests for business logic
- Integration tests for APIs
- E2E tests for critical user flows
- Property-based tests for complex invariants

### Mocking Rules
- Mock external dependencies, not internal logic
- Prefer real implementations when fast
- Verify interactions, don't test mocks

## Subagent Orchestration

### When to Use Subagents
- Tasks are independent (can run in parallel)
- Task is reasoning-heavy (debugging, code review, research)
- Context would flood main session
- Need fresh perspective per task

### Subagent Best Practices
- Provide complete context (file paths, errors, conventions)
- One task per subagent (2-5 min of work)
- Two-stage review: spec compliance → code quality
- Never skip review loops
- Answer subagent questions before letting them proceed

### Parallel Execution
- Max 3 concurrent subagents (per user config)
- Dispatch independent tasks together
- Fan-in: wait for all before integration review

## Git Discipline

### Branching
- Always branch: `git checkout -b feature/descriptive-name`
- `main` is sacred — never commit directly

### Commits
- Format: `type: what changed`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- One logical change per commit
- Good messages explain "why", not just "what"

### Pushing
- Push after every meaningful milestone
- If build breaks, fix immediately

## Memory & Persistence

### What to Save to Memory
- User preferences and corrections
- Environment facts (OS, tools, project structure)
- API quirks and workarounds
- Project conventions

### What to Save as Skills
- Complex workflows (5+ tool calls)
- Error patterns and solutions
- Tool-specific commands and pitfalls
- Reusable architectural patterns

### What NOT to Save
- Task progress or outcomes
- Commit SHAs, PR numbers
- Temporary TODO state
- Anything stale in 7 days

## Continuous Improvement

### After Every Significant Task
- [ ] Did I learn something worth saving as a skill?
- [ ] Did I encounter a pitfall worth documenting?
- [ ] Did I use a tool or technique I should remember?
- [ ] Did I write code I could generalize into a reusable component?

### Skill Maintenance
- Skills that aren't maintained become liabilities
- Patch skills immediately when you find issues
- Consolidate overlapping skills
- Delete stale skills with `absorbed_into` reference

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | What To Do Instead |
|-------------|-------------|-------------------|
| Hallucinating changes in commit messages | Writes false history; erodes trust; future sessions fabrications compound it | `git diff --cached` before every commit; message must match actual diff stat; if stash is messy, write a minimal true message or split the commit |
| "Quick fix" without investigation | Creates new bugs | Follow systematic debugging |
| Code before tests | Untrusted code | Follow TDD |
| Massive single commit | Hard to revert | Small, logical commits |
| Skipping review | Quality drift | Two-stage review every time |
| Context pollution | Confusion, errors | Fresh subagent per task |
| Manual testing only | No reproducibility | Automate everything |
| Optimizing without profiling | Wasted effort | Profile first |
| Copy-paste without understanding | Hidden bugs | Read completely, then adapt |

## Emergency Procedures

### Build is Broken
1. Stop everything
2. Fix build first
3. No new code until CI is green

### Stuck for > 10 Minutes
1. Document what you tried
2. Ask for help with specific details
3. Don't spin forever

### Wrong File Modified
1. `git checkout -- <file>` immediately
2. Don't compound the mistake

### Security Issue Discovered
1. Stop
2. Document it
3. Notify immediately
4. Don't fix silently

## The Ultimate Rule

```
Write code you'd be proud to have your name on.
Build systems that last.
Learn something every day.
```

## References

- `systematic-debugging` — 4-phase root cause debugging
- `test-driven-development` — RED-GREEN-REFACTOR
- `subagent-driven-development` — Fresh subagent + 2-stage review
- `writing-plans` — Implementation planning
- `requesting-code-review` — Pre-commit review
- `spike` — Throwaway experiments
- `references/css-theme-toggle-pattern.md` — CSS custom properties dark/light mode toggle (no build step)
- `references/pyinstaller-windows-from-wsl.md` — Build Windows .exe via PyInstaller from a WSL development environment
- `references/pyside6-view-menu-patterns.md` — PySide6 View menu items: theme toggle (radio items), always-on-top, zoom, fullscreen, status bar
- `references/pyinstaller-noarchive-confusion.md` — Why `noarchive=False` is required for PySide6/PIL DLLs; correct performance levers for PyInstaller+PySide6 apps
- `references/pyside6-widget-flicker-fix.md` — Full widget-guard checklist: idempotency gates per widget type, batching, objectName QSS switching, emoji clipping, invisible theme button debugging, UI kit → QSS translation
