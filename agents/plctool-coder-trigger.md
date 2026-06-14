# PLCTools Coder Auto-Spawn Trigger

## How to Spawn the PLC Coder Agent

### Method 1: Tell Spock (Best)
Simply type in any chat:
```
spawn the PLC coder
```

Spock will spawn it for you with proper context.

### Method 2: Create Trigger File
Create this file (any content):
```
C:\Users\thadd\.openclaw\workspace\TRIGGER_SPAWN_PLC.txt
```

Spock will detect this during heartbeats and spawn the PLC Coder agent.

### Method 3: Use Control UI
1. Open http://127.0.0.1:18789/
2. Type: "spawn the PLC coder"

---

**Why no shortcut?** OpenClaw CLI doesn't expose agent spawning directly. The `sessions_spawn` tool is internal to the agent system, not a user-facing command.
