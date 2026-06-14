# Post-Update Chat History Recovery Tools

## Background

After a WebUI update or systemd service change, the data directory may shift
(e.g. from `~/.hermes-web-ui/` to `~/.hermes/webui/`). The server then connects
to a new DB where no sessions exist, and the user sees **empty chat history**
even though the old DB is still intact on disk.

Two automated tools handle this:

1. `webui-chat-recall.py` — detect and merge missing sessions from legacy DBs
2. `webui-db-sync.py` — convert DB sessions to JSON files for WebUI rendering

---

## Tool 1: `webui-chat-recall.py`

**Path:** `/home/thadd/.hermes/profiles/plc-coder/scripts/webui-chat-recall.py`

### What it does

- Walks the filesystem and finds **every** `hermes-web-ui.db` under `/home/thadd`
- Uses `lsof` or systemd service parsing to determine the **active** DB
- Compares session counts between legacy DBs and the active DB
- If a legacy DB has more sessions, it lists the missing ones
- With `--merge`, copies missing sessions from legacy → active with message ID
  renumbering (to avoid `AUTOINCREMENT` collisions)
- Sets `show_cli_sessions=true` in `settings.json`

### Usage

```bash
# Detection-only (safe to run anytime)
python3 /home/thadd/.hermes/profiles/plc-coder/scripts/webui-chat-recall.py

# Merge missing sessions into active DB
python3 /home/thadd/.hermes/profiles/plc-coder/scripts/webui-chat-recall.py --merge
```

### Sample output

```
============================================================
WebUI Chat Recall Tool
============================================================

Active DB (inferred): /home/thadd/.hermes/webui/hermes-web-ui.db
Total DBs found: 6
  /home/thadd/.hermes/webui/hermes-web-ui.db: 10 sessions, 997 messages  <-- ACTIVE
  /home/thadd/.hermes-web-ui/hermes-web-ui.db: 3 sessions, 447 messages

CAUTION: Legacy DB has more sessions than active!
  Legacy: /home/thadd/.hermes-web-ui/hermes-web-ui.db (3 sessions)
  Active: /home/thadd/.hermes/webui/hermes-web-ui.db (10 sessions)

  Missing sessions:
    - mpnpcq6i067nzw | profile=devteam | msgs=423 | do you recall our last converation?
    - mpnp0dowi3hysz | profile=devteam | msgs=2 | hi do you know your role?
    - mpdrlpouoocunf | profile=default | msgs=22 | hi

Run with --merge to copy these sessions into the active DB.
```

---

## Tool 2: `webui-db-sync.py`

**Path:** `/home/thadd/.hermes/profiles/plc-coder/scripts/webui-db-sync.py`

### What it does

- Reads the **active** SQLite DB
- Finds sessions that exist in the DB but have no `.json` file in
  `~/.hermes/webui/sessions/`
- Converts each DB session + messages to the WebUI JSON format
- Creates the `.json` file and inserts it into `_index.json`
- The WebUI sidebar renders JSON sessions from `_index.json`, so these appear
  immediately after restart

### Usage

```bash
# Detection-only
python3 /home/thadd/.hermes/profiles/plc-coder/scripts/webui-db-sync.py --dry-run

# Create JSON files + update _index.json
python3 /home/thadd/.hermes/profiles/plc-coder/scripts/webui-db-sync.py
```

### When to run

After `--merge` (if the merged sessions still don't show in WebUI), OR if
`show_cli_sessions=true` is set but the sidebar remains empty.

---

## Integration into WebUI Update Workflow

After any WebUI update, run this sequence **before** telling the user the
update is complete:

```bash
# Step 1: Check for orphaned DBs and merge missing sessions
python3 /home/thadd/.hermes/profiles/plc-coder/scripts/webui-chat-recall.py --merge

# Step 2: Sync any DB-only sessions to JSON files
python3 /home/thadd/.hermes/profiles/plc-coder/scripts/webui-db-sync.py

# Step 3: Restart WebUI
systemctl --user restart hermes-webui.service

# Step 4: Verify
sleep 3
curl -sf http://127.0.0.1:8648/health | python3 -c "
import json,sys
h=json.load(sys.stdin)
print(f\"WebUI: {h.get('webui_version')} | sessions: check sidebar\")
"
```

---

## Root cause summary

The WebUI stores session data in **two places**:
1. SQLite DB (`hermes-web-ui.db`) — populated by the agent bridge during CLI sessions
2. JSON files (`sessions/*.json` + `_index.json`) — used by WebUI for sidebar rendering

When the data directory changes:
- The **new** DB is empty even though sessions exist in the old one
- `show_cli_sessions=false` hides CLI-sourced sessions in the sidebar
- Even if sessions are in the DB, they don't appear without JSON files
- The merge must renumber message IDs because both DBs used `AUTOINCREMENT`

---

## Prevention checklist (for future updates)

- [ ] Before update: snapshot the active DB (`cp hermes-web-ui.db pre-update-$(date +%s)`)
- [ ] After update: run `webui-chat-recall.py` (detection mode)
- [ ] After update: verify `settings.json` has `show_cli_sessions=true`
- [ ] After merge: run `webui-db-sync.py` to create JSON files
- [ ] After restart: open the WebUI and confirm all sessions are visible

---

## Tool 3: `webui-recall-sessions.sh` — One-Shot Recovery

**Path:** `/home/thadd/.hermes/scripts/webui-recall-sessions.sh`

This is a convenience bash wrapper that runs both tools, restarts the service,
and performs a health check:

```bash
bash /home/thadd/.hermes/scripts/webui-recall-sessions.sh
```

**What it does:**
1. Detects and merges missing sessions (`webui-chat-recall.py --merge`)
2. Syncs DB sessions to JSON (`webui-db-sync.py`)
3. Restarts `hermes-webui.service`
4. Health-checks on `127.0.0.1:8648`

---

## Pitfall: Malformed `SPOCK_WEBUI_STATE_DIR` in systemd service

The systemd unit file may contain a trailing quote inside the env var value:

```
SPOCK_WEBUI_STATE_DIR=/home/thadd/.hermes/webui"
```

This causes naive `source <(systemctl --user show hermes-webui.service -p Environment)`
parsers to emit a literal `"` at the end of the path, making file operations fail.

**Detection:**
```bash
grep "SPOCK_WEBUI_STATE_DIR" ~/.config/systemd/user/hermes-webui.service
```

**Fix in any consumer script:**
```python
value = line.split('=', 1)[1].strip('"\'')
```
The `webui-chat-recall.py` script already handles this; custom scripts must too.

---

## Files

| File | Purpose |
|---|---|
| `webui-chat-recall.py` | Detect and merge missing sessions between DBs |
| `webui-db-sync.py` | Convert DB sessions to JSON for WebUI rendering |
| `webui-recall-sessions.sh` | Combined recovery shortcut (merge + sync + restart + health check) |
| `settings.json` | Controls `show_cli_sessions` visibility toggle |
| `_index.json` | WebUI sidebar index of sessions |
| `sessions/*.json` | Per-session conversation data |
