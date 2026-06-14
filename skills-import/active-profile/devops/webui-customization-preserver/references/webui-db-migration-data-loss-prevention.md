# WebUI Database Migration — Data Loss Prevention

## The Problem

The Hermes WebUI stores chat history in a SQLite database whose location is
determined by the `HERMES_WEB_UI_HOME` environment variable (or legacy
`SPOCK_WEBUI_STATE_DIR`).

**Historical paths:**
- **Legacy (pre-v0.6.4):** `~/.hermes-web-ui/hermes-web-ui.db`
- **Current (v0.6.4+):** `~/.hermes/webui/hermes-web-ui.db`

When systemd services, launcher scripts, or update procedures change this path
without migrating the DB, **all chat history appears to vanish** — but the old
DB is still sitting on disk, disconnected from the active server.

This happened during the v0.6.4 → v0.6.11 update: the systemd service
`hermes-webui.service` had `SPOCK_WEBUI_STATE_DIR=/home/thadd/.hermes/webui`
while an older copy of the DB still existed at
`~/.hermes-web-ui/hermes-web-ui.db` with 3 sessions and 447 messages.

## Detection

### 1. Check for multiple DB files on disk

```bash
find /home/thadd -name "hermes-web-ui.db" -type f 2>/dev/null | grep -v node_modules | grep -v .cache
```

**If more than one exists**, compare them:

```bash
python3 -c "
import sqlite3, os

dbs = [
    '/home/thadd/.hermes/webui/hermes-web-ui.db',
    '/home/thadd/.hermes-web-ui/hermes-web-ui.db',
    '/home/thadd/hermes-web-ui-ekko/packages/server/data/hermes-web-ui.db',
]

for db in dbs:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM sessions')
        sessions = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM messages')
        msgs = c.fetchone()[0]
        print(f'{db}: {sessions} sessions, {msgs} messages')
        conn.close()
"
```

### 2. Compare session lists between old and current DB

```bash
python3 -c "
import sqlite3

old_db = '/home/thadd/.hermes-web-ui/hermes-web-ui.db'
curr_db = '/home/thadd/.hermes/webui/hermes-web-ui.db'

conn_old = sqlite3.connect(old_db)
conn_curr = sqlite3.connect(curr_db)
c_old = conn_old.cursor()
c_curr = conn_curr.cursor()

c_old.execute('SELECT id, title, message_count FROM sessions')
old_sessions = {row[0]: row for row in c_old.fetchall()}

c_curr.execute('SELECT id FROM sessions')
curr_ids = {row[0] for row in c_curr.fetchall()}

print('Sessions ONLY in old DB (missing from current):')
for sid, data in old_sessions.items():
    if sid not in curr_ids:
        print(f'  {sid} | {data[1]!r} | {data[2]} msgs')

conn_old.close()
conn_curr.close()
"
```

## Recovery

If sessions exist in the old DB but not the current one:

### 1. Merge sessions and messages

Message IDs overlap because both DBs used SQLite `AUTOINCREMENT`. You must
renumber messages from the old DB before inserting them into the current one.

```bash
python3 << 'PYEOF'
import sqlite3

old_db = "/home/thadd/.hermes-web-ui/hermes-web-ui.db"
curr_db = "/home/thadd/.hermes/webui/hermes-web-ui.db"

conn_old = sqlite3.connect(old_db)
conn_old.row_factory = sqlite3.Row
conn_curr = sqlite3.connect(curr_db)
conn_curr.row_factory = sqlite3.Row

c_old = conn_old.cursor()
c_curr = conn_curr.cursor()

# Get max message ID in current DB
c_curr.execute("SELECT MAX(id) FROM messages")
max_id = c_curr.fetchone()[0] or 0

# Find missing sessions
c_old.execute("SELECT id FROM sessions")
missing_ids = []
for row in c_old.fetchall():
    sid = row[0]
    c_curr.execute("SELECT id FROM sessions WHERE id=?", (sid,))
    if not c_curr.fetchone():
        missing_ids.append(sid)

print(f"Missing sessions: {missing_ids}")

for sid in missing_ids:
    # Copy session row
    c_old.execute("SELECT * FROM sessions WHERE id=?", (sid,))
    session = c_old.fetchone()
    cols = list(session.keys())
    placeholders = ','.join('?' for _ in cols)
    values = tuple(session[col] for col in cols)
    c_curr.execute(f"INSERT INTO sessions ({','.join(cols)}) VALUES ({placeholders})", values)
    
    # Copy messages with renumbered IDs
    c_old.execute("SELECT * FROM messages WHERE session_id=? ORDER BY id", (sid,))
    msgs = c_old.fetchall()
    copied = 0
    for msg in msgs:
        max_id += 1
        msg_cols = list(msg.keys())
        new_values = {}
        for col in msg_cols:
            if col == 'id':
                new_values[col] = max_id
            else:
                new_values[col] = msg[col]
        
        insert_cols = list(new_values.keys())
        placeholders = ','.join('?' for _ in insert_cols)
        values = tuple(new_values[col] for col in insert_cols)
        c_curr.execute(f"INSERT INTO messages ({','.join(insert_cols)}) VALUES ({placeholders})", values)
        copied += 1
    
    # Update message_count to match actual
    c_curr.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (sid,))
    actual = c_curr.fetchone()[0]
    c_curr.execute("UPDATE sessions SET message_count=? WHERE id=?", (actual, sid))
    print(f"  {sid}: copied {copied} messages, count={actual}")

conn_curr.commit()

# Verify
c_curr.execute("SELECT COUNT(*) FROM sessions")
print(f"Total sessions: {c_curr.fetchone()[0]}")
c_curr.execute("SELECT COUNT(*) FROM messages")
print(f"Total messages: {c_curr.fetchone()[0]}")

conn_old.close()
conn_curr.close()
PYEOF
```

### 2. Verify in WebUI

Restart the WebUI service (if not already running) and reload the browser page.
The restored sessions should appear in the chat history sidebar.

## Prevention

### Before Any WebUI Update or Service Change

**Step 1: Identify the active data directory**

```bash
grep -E "HERMES_WEB_UI_HOME|SPOCK_WEBUI_STATE_DIR" ~/.config/systemd/user/hermes-webui.service
```

**Step 2: Snapshot the DB before changes**

```bash
active_dir=$(grep -oP "SPOCK_WEBUI_STATE_DIR=\K.*" ~/.config/systemd/user/hermes-webui.service 2>/dev/null || echo "~/.hermes/webui")
active_dir=${active_dir/#\~/\$HOME}
cp "$active_dir/hermes-web-ui.db" "$active_dir/hermes-web-ui.db.pre-update-$(date +%Y%m%d-%H%M%S)"
```

**Step 3: If changing `HERMES_WEB_UI_HOME` or `WorkingDirectory`, migrate the DB**

```bash
old_dir="/home/thadd/.hermes-web-ui"
new_dir="/home/thadd/.hermes/webui"

# Ensure new dir exists
mkdir -p "$new_dir"

# Copy DB if old exists and new is empty or smaller
if [ -f "$old_dir/hermes-web-ui.db" ]; then
    old_size=$(stat -c%s "$old_dir/hermes-web-ui.db" 2>/dev/null || echo 0)
    new_size=$(stat -c%s "$new_dir/hermes-web-ui.db" 2>/dev/null || echo 0)
    if [ "$old_size" -gt "$new_size" ]; then
        echo "Migrating DB from $old_dir to $new_dir..."
        cp "$old_dir/hermes-web-ui.db" "$new_dir/hermes-web-ui.db"
        cp "$old_dir/.token" "$new_dir/.token" 2>/dev/null || true
        echo "Done. Old DB preserved at $old_dir/hermes-web-ui.db"
    fi
fi
```

**Step 4: Update launcher scripts and systemd to use the same path**

All of these must agree:
- `~/.config/systemd/user/hermes-webui.service` — `SPOCK_WEBUI_STATE_DIR`
- Desktop `.bat` / `.lnk` launchers
- `hermes-web-ui` CLI wrapper
- Any cron jobs or watchdog scripts that reference the DB directly

### Post-Update Verification Checklist

Add these to the standard WebUI update verification:

- [ ] `hermes-web-ui.db` exists in the **active** data directory (check `lsof -p $(pgrep -f "node.*dist/server/index.js") | grep hermes-web-ui.db`)
- [ ] `find ~ -name "hermes-web-ui.db" | wc -l` — if >1, check for orphaned DBs with missing sessions
- [ ] Session count in active DB matches expected (run the Python comparison script)
- [ ] No dev-mode DB at `packages/server/data/hermes-web-ui.db` (indicates `NODE_ENV` was not `production`)

## Root Cause Summary

The data loss was not a database corruption or deletion. It was a **directory
migration** caused by:

1. WebUI v0.6.4+ changed the default data directory from `~/.hermes-web-ui/` to
   `~/.hermes/webui/` (controlled by `HERMES_WEB_UI_HOME`)
2. The systemd service was updated to set `SPOCK_WEBUI_STATE_DIR=/home/thadd/.hermes/webui`
3. The old DB at `~/.hermes-web-ui/hermes-web-ui.db` was never migrated
4. The server started using the new (empty) DB, so all old chats appeared gone

This is a **silent failure** — no error is logged, the server starts normally,
and the user only notices their history is missing.
