# OpenClaw Issue: Subagent Sessions Show as Separate Entries Instead of Grouped Under Parent

## Bug Description

When spawning subagents via `sessions_spawn`, the Control UI dropdown shows subagents as **separate, independent sessions** rather than being grouped under or linked to the parent session. This creates confusion because:

1. Users see multiple "agents" (parent + subagents) as if they are peers
2. It's unclear which session is the "main" one vs. spawned helpers
3. Switching between them feels broken - clicking a subagent doesn't always switch context correctly

## Expected Behavior

**Option A (Preferred):** Subagents should be visually indicated as children:
- Parent: "🧠 Spock (Main)"
- Subagent: "└─ 🔧 PLCTools Coder (Subagent)"

**Option B:** Don't show subagents in the main dropdown at all - they should be accessed differently (e.g., inline in chat or via a "subagents" panel)

**Option C:** At minimum, ensure clicking a subagent session in the dropdown actually switches to that conversation thread

## Actual Behavior

The dropdown shows raw session keys like:
- `agent:main:telegram:direct:6358...` (This is me - Spock)
- `agent:main:subagent:f4ac7ef1...` (This is the PLC Coder)

Both appear as if they are independent, but the subagent was spawned BY the parent and should be contextually linked.

## Steps to Reproduce

1. Start a session with main agent (Spock)
2. Spawn a subagent using `sessions_spawn` with a label (e.g., "plctool-coder")
3. Open Control UI dropdown
4. Observe: both parent and subagent appear as separate, equal entries
5. Try to click subagent - context switching may not work properly

## Environment

- OpenClaw version: 2026.5.2 (8b2a6e5)
- Platform: Windows 10
- Agent: main with multiple subagents

## Related Issues

- #5088 - Session dropdown could show labels instead of session keys (FIXED but this is a regression/related)
- #45120 - Session dropdown shows key instead of label (2026.3.12 regression) (FIXED)

## Additional Context

The subagent system works functionally, but the UI/UX creates confusion. Users expect:
1. Clear visual hierarchy (parent → child)
2. Ability to switch between them seamlessly
3. Understanding of which agent handles what

Currently, the dropdown feels like it's showing "multiple agents" rather than "one agent with helpers".

---

**Reported by:** Thad (via Spock agent)
**Date:** 2026-05-05