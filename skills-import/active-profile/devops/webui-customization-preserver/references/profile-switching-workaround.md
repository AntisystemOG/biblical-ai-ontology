# WebUI Profile Switching Workaround

## Problem

When you switch profiles in the WebUI sidebar dropdown (e.g., from **devteam** to **plc-coder**), the **existing open session** continues to run under the **old profile**. The dropdown selection only affects **new sessions**.

This manifests as:
- You select **plc-coder** from the profile dropdown
- The agent responds with the **wrong persona** (devteam instead of PLC Coder)
- The agent says "I am running under the devteam profile" even though the UI shows plc-coder selected
- Bridge worker logs show `[hermes-bridge-worker:devteam]` instead of `[hermes-bridge-worker:plc-coder]`

## Root Cause

The WebUI stores the `profile` column per-session in `hermes-web-ui.db`. When you switch the dropdown, existing sessions are **not** updated. The bridge worker reads the profile from the **session record**, not from the dropdown UI state.

```
WebUI DB: sessions.profile = 'devteam'
↓
Bridge worker spawned with HERMES_HOME = ~/.hermes/profiles/devteam
↓
Agent loads devteam skills, memory, config — NOT plc-coder
```

## Detection

```bash
# Check what profile your active sessions have
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
c = conn.cursor()
c.execute('SELECT id, profile, title, started_at FROM sessions ORDER BY started_at DESC LIMIT 5')
for row in c.fetchall():
    print(f'{row[0]} | profile: {row[1]} | {row[2]}')
conn.close()
"
```

If the active session shows `profile: devteam` (or any profile other than what the dropdown shows), that's the mismatch.

Also check server logs:
```bash
tail -20 /home/thadd/.hermes/webui/logs/server.log | grep "bridge-worker"
# Look for: [hermes-bridge-worker:devteam] vs [hermes-bridge-worker:plc-coder]
```

## Fix

### Option 1: Start a New Chat (Recommended)

1. Click **"New Chat"** in the WebUI sidebar
2. This creates a session with the **currently selected profile** from the dropdown
3. The bridge spawns a new worker with the correct profile

### Option 2: Update Existing Session in DB

If you must keep the current session history, update the DB directly:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
c = conn.cursor()
# Update specific session
c.execute(\"UPDATE sessions SET profile = 'plc-coder' WHERE id = 'YOUR_SESSION_ID'\")
# Or update all sessions for a profile
c.execute(\"UPDATE sessions SET profile = 'plc-coder' WHERE profile = 'devteam'\")
conn.commit()
print(f'Updated {c.rowcount} session(s)')
conn.close()
"
```

**Caveat:** The currently running bridge worker will still be the old profile until you start a new chat (which spawns a new worker). Updating the DB only fixes future runs.

### Option 3: Restart Server + New Chat

If the bridge worker is stuck on the old profile:
```bash
# Stop server
pkill -f "node.*dist/server/index.js" || true; sleep 2

# Start server (with correct env)
cd /home/thadd/hermes-web-ui-ekko
unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
/home/thadd/node26/bin/node dist/server/index.js

# Then in WebUI: select correct profile → New Chat
```

## Prevention

There is no permanent prevention — this is WebUI behavior. The user's workflow should be:

1. Select desired profile from dropdown **first**
2. Then click **"New Chat"**
3. Verify the agent responds with the correct persona

If switching profiles mid-conversation, always start a new chat. The dropdown alone does not re-spawn the bridge worker.

## Related

- `webui-customization-preserver/SKILL.md` — Post-update server start procedures
- `references/upstream-merge-0.6.3.md` — WebUI update notes
