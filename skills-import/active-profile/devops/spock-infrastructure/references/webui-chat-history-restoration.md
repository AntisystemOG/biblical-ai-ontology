# WebUI Chat History Restoration — Full Script

**Trigger:** User says "my chat histories are gone" after WebUI update, repo migration, or missing `NODE_ENV=production`.

## Problem

The WebUI stores conversations in SQLite. There are multiple possible DB locations over time:
- `~/.hermes-web-ui/hermes-web-ui.db` (legacy, pre-v0.6.4)
- `~/.hermes/webui/hermes-web-ui.db` (current, v0.6.4+ with production mode)
- `packages/server/data/hermes-web-ui.db` (dev mode fallback — empty users table)
- `~/.hermes/profiles/<name>/home/.hermes-web-ui/hermes-web-ui.db` (profile-specific copies)

When the server changes data directories or when `NODE_ENV=production` is missing, old sessions become invisible even though the DB files still exist.

## Detection

```bash
# Find all WebUI DBs on the system
find /home/thadd -name "hermes-web-ui.db" -type f 2>/dev/null | while read p; do
  size=$(stat -c%s "$p")
  echo "$p ($size bytes)"
done

# Compare sessions between old and current DB
python3 -c "
import sqlite3, os
old = '/home/thadd/.hermes-web-ui/hermes-web-ui.db'
curr = '/home/thadd/.hermes/webui/hermes-web-ui.db'
for label, path in [('OLD', old), ('CURRENT', curr)]:
    if os.path.exists(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM sessions')
        sc = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM messages')
        mc = c.fetchone()[0]
        print(f'{label}: {sc} sessions, {mc} messages')
        conn.close()
"
```

## Restoration Script

This handles overlapping auto-increment message IDs by renumbering:

```python
import sqlite3

def merge_webui_chat_history(old_db_path, current_db_path):
    '''
    Merge sessions from an old WebUI DB into the current active DB.
    Handles overlapping auto-increment message IDs by renumbering.
    '''
    conn_old = sqlite3.connect(old_db_path)
    conn_old.row_factory = sqlite3.Row
    conn_curr = sqlite3.connect(current_db_path)
    conn_curr.row_factory = sqlite3.Row

    c_old = conn_old.cursor()
    c_curr = conn_curr.cursor()

    # Get max message ID in current DB
    c_curr.execute("SELECT MAX(id) FROM messages")
    max_id = c_curr.fetchone()[0] or 0

    # Find sessions in old DB missing from current
    c_old.execute("SELECT id FROM sessions")
    missing_sessions = []
    for row in c_old.fetchall():
        sid = row[0]
        c_curr.execute("SELECT id FROM sessions WHERE id=?", (sid,))
        if not c_curr.fetchone():
            missing_sessions.append(sid)

    total_sessions = 0
    total_messages = 0

    for sid in missing_sessions:
        # Copy session row
        c_old.execute("SELECT * FROM sessions WHERE id=?", (sid,))
        session = c_old.fetchone()
        if not session:
            continue

        cols = list(session.keys())
        placeholders = ','.join('?' for _ in cols)
        values = tuple(session[col] for col in cols)

        try:
            c_curr.execute(f"INSERT INTO sessions ({','.join(cols)}) VALUES ({placeholders})", values)
            total_sessions += 1
        except sqlite3.IntegrityError as e:
            print(f"ERROR inserting session {sid}: {e}")
            continue

        # Copy messages with renumbered IDs
        c_old.execute("SELECT * FROM messages WHERE session_id=?", (sid,))
        for msg in c_old.fetchall():
            max_id += 1
            msg_cols = list(msg.keys())
            new_values = {}
            for col in msg_cols:
                if col == 'id':
                    new_values[col] = max_id
                elif col == 'session_id':
                    new_values[col] = sid
                else:
                    new_values[col] = msg[col]

            insert_cols = list(new_values.keys())
            placeholders = ','.join('?' for _ in insert_cols)
            values = tuple(new_values[col] for col in insert_cols)
            c_curr.execute(f"INSERT INTO messages ({','.join(insert_cols)}) VALUES ({placeholders})", values)
            total_messages += 1

        # Update session message_count to actual
        c_curr.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (sid,))
        actual_count = c_curr.fetchone()[0]
        c_curr.execute("UPDATE sessions SET message_count=? WHERE id=?", (actual_count, sid))

    conn_curr.commit()

    # Verify
    c_curr.execute("SELECT COUNT(*) FROM sessions")
    final_sessions = c_curr.fetchone()[0]
    c_curr.execute("SELECT COUNT(*) FROM messages")
    final_messages = c_curr.fetchone()[0]

    conn_old.close()
    conn_curr.close()

    return {
        'restored_sessions': total_sessions,
        'restored_messages': total_messages,
        'total_sessions': final_sessions,
        'total_messages': final_messages,
    }

# Usage
result = merge_webui_chat_history(
    '/home/thadd/.hermes-web-ui/hermes-web-ui.db',
    '/home/thadd/.hermes/webui/hermes-web-ui.db'
)
print(f"Restored {result['restored_sessions']} sessions, {result['restored_messages']} messages")
print(f"Current DB now has {result['total_sessions']} sessions, {result['total_messages']} messages")
```

## Post-Restoration

1. **Restart the WebUI service** so it picks up the merged DB:
   ```bash
   systemctl --user restart hermes-webui.service
   ```
2. **Verify in browser** — reload `http://127.0.0.1:8648` and check the chat history sidebar
3. **Check for profile-specific DBs** — if the user uses multiple profiles, each may have its own isolated DB under `~/.hermes/profiles/<name>/home/.hermes-web-ui/`

## Prevention

Always set `NODE_ENV=production` and `HERMES_WEB_UI_HOME` consistently:
```bash
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
```
This prevents the server from creating a fresh dev DB at `packages/server/data/` that hides existing conversations.
