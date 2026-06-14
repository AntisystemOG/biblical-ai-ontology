# PLC Agent Quick Spawn

Quickly spawn the PLCTools coding assistant with persistent memory.

## Quick Commands

### Spawn PLC Coder Agent
```powershell
openclaw sessions spawn --label plctool-coder --mode run --runtime subagent --task "Spawn PLCTools coding assistant"
```

Or use the PowerShell alias:
```powershell
plccoder
```

## What Happens

1. **Spawns** a fresh subagent labeled "🔧 PLCTools Coder"
2. **Reads** `C:\Users\thadd\Documents\PLCTools\PROJECT_MEMORY.md` (persistent memory)
3. **Knows** what you were working on
4. **Updates** PROJECT_MEMORY.md when done

## Persistent Memory

The file `C:\Users\thadd\Documents\PLCTools\PROJECT_MEMORY.md` acts as shared memory:
- Current task/focus
- Recent work completed
- Known issues
- Next steps

This is how the subagent "remembers" between sessions.

## Manual Spawn via Chat

Just tell Spock:
> "Spawn the PLC coder" or "I need the PLC tool agent"

Spock will spawn it for you with the right context.