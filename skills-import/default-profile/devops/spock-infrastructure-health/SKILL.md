---
name: spock-infrastructure-health
description: "Self-healing diagnostics for Hermes infrastructure: gateway, cron agents, webui, ollama tokens, and memory databases. Detect, diagnose, repair."
triggers:
  - "gateway is down"
  - "cron agent not running"
  - "webui connection lost"
  - "ollama tokens exhausted"
  - "automated health check"
  - "self-heal"
  - "check all systems"
toolsets: ["terminal", "cronjob", "file"]
---

# Spock Infrastructure Health & Self-Healing

Comprehensive diagnostics for the running Hermes stack. Covers:

1. **Gateway process** — port 8648 bridge
2. **Cron agents** — 6 scheduled jobs
3. **WebUI** — Ollama Cloud connection
4. **Ollama tokens** — budget exhaustion monitoring
5. **Memory databases** — corruption / truncation
6. **Disk space** — WSL / `.hermes` growth

---

## 1. Gateway Process Health

### Quick Reality Check: Is the server actually running?

Before investigating code changes, build errors, or crashes, always verify the process exists AND is listening on the expected port:

```bash
ss -tlnp | grep 8648
```
- **Empty** → server is down. The "crash" is a stopped process, not a code error.
- **Shows `python3` PID on `0.0.0.0:8648`** → server is alive. Now investigate routes/API errors.
- **Shows `python3` PID on `127.0.0.1:8787`** → server is running but on the WRONG port. Common cause: systemd service uses `HERMES_WEBUI_*` env vars instead of `SPOCK_WEBUI_*`. See `launch-webui-gateway` skill, "Systemd Service Configuration" section.

### Service Active But Wrong Port Syndrome

When using systemd, `systemctl --user status hermes-webui.service` can show `active (running)` while the server silently fell back to `127.0.0.1:8787` because env vars were ignored.

**Detection:**
```bash
systemctl --user status hermes-webui.service   # "active"
ss -tlnp | grep :8648                          # nothing!
cat /proc/$(pgrep -f server.py)/environ | tr '\0' '\n' | grep -i spock
```

**Heal:**
```bash
# Fix env var names in the service file, reload, restart
# See launch-webui-gateway skill for the exact service unit template.
systemctl --user daemon-reload
systemctl --user restart hermes-webui.service
sleep 2
ss -tlnp | grep :8648  # should now show the listener
```

### Classic "WebUI crashed" check

```bash
curl -s http://172.24.60.180:8648/health 2>/dev/null || echo "DEAD"
pgrep -f "hermes.*gateway" | head -3
```

**Heal if dead (Python server.py + systemd):**
```bash
# Verify which stack is supposed to be active before choosing restart method
# For Thad's current setup: hermes-webui-new (Python) via systemd user service
systemctl --user restart hermes-webui.service
sleep 3
curl -s -o /dev/null -w "%{http_code}" http://$(hostname -I | awk '{print $1}'):8648/
# → 200
```

**Heal if dead (legacy Node.js ekko stack — verify with `ps aux | grep node`):**
```bash
pkill -f "dist/server/index.js" 2>/dev/null || true
sleep 2
bash /home/thadd/.hermes/webui/start-server.sh > /home/thadd/.hermes/webui/logs/auto-restart.log 2>>&1 &
echo $! > /home/thadd/.hermes/webui/server.pid
```

**Verify:**
```bash
sleep 3
curl -s http://172.24.60.180:8648/health | python3 -c "import sys,json; r=json.load(sys.stdin); print('OK' if r.get('gateway')=='running' else 'STILL DOWN')"
```

---

## 2. Cron Agent Health

**Read active jobs:**
```bash
python3 -c "
import json
with open('/home/thadd/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)
for j in jobs:
    print(f'{j.get(\"id\", \"?\")}: {j.get(\"name\", \"unknown\")} — schedule={j.get(\"schedule\", \"none\")} enabled={j.get(\"enabled\", \"unknown\")}')
"
```

**Check last runs:**
```bash
ls -lt /home/thadd/.hermes/cron/ | head -10
```

**Heal stuck cron:**
If `.tick.lock` is stale (>5 min old):
```bash
rm -f /home/thadd/.hermes/cron/.tick.lock
# Next tick will self-correct
```

**Restart specific agent:**
```bash
# Hermes CLI
cd /home/thadd/.hermes && source hermes-agent/venv/bin/activate
hermes cron run <JOB_ID>
```

---

## 3. WebUI ↔ Ollama Cloud Bridge

**Check:**
```bash
# Look for connection errors in last 50 lines
grep -i "ollama\|connection\|error\|timeout" /home/thadd/.hermes/webui/logs/server.log | tail -50
```

**Heal bridge loss:**
```bash
# Step 1: Verify .env integrity
python3 -c "
with open('/home/thadd/.hermes/.env') as f:
    for line in f:
        if line.startswith('OLLAMA_API_KEY=') or line.startswith('AUTH_DISABLED=') or line.startswith('OLLAMA_BASE_URL='):
            print(line.strip())
"

# Step 2: If OLLAMA_API_KEY empty or AUTH_DISABLED malformed:
# Load hermes-webui-ollama-fix skill and follow full recovery
```

**See also:** `hermes-webui-ollama-fix` skill for step-by-step bridge recovery.

---

## 4. Ollama Token Budget

**Check remaining:**
```bash
# From MEMORY: Thad's explicit instruction to "use all the ollama tokens we can, they expire and start over"
# We need a way to query current usage. Ollama Pro API has /v1/models or dashboard.
# Fallback: check local cache for model list (indicates connectivity)
curl -s https://ollama.com/v1/models -H "Authorization: Bearer $(grep OLLAMA_API_KEY /home/thadd/.hermes/.env | cut -d= -f2)" 2>/dev/null | python3 -c "
import sys,json
try:
    r = json.load(sys.stdin)
    models = r.get('data', [])
    print(f'Models available: {len(models)}')
    for m in models[:3]:
        print(f'  {m.get(\"id\", \"unknown\")}')
except:
    print('OLLAMA API NOT RESPONDING — token may be exhausted or invalid')
" || echo "API UNREACHABLE"
```

**When tokens are low:**
1. Switch to model with lower max_tokens (qwen3:8b instead of kimi-k2.6)
2. Use `--thinking <N>` on kimi to reduce output tokens
3. Prompt user to consider which agents are critical vs expendable

---

## 5. Memory Database Health

**Check state.db size:**
```bash
ls -lh /home/thadd/.hermes/state.db | awk '{print $5}'
# Expected: 5–50MB. If >500MB, may be bloated with old sessions.
```

**Check corruption:**
```bash
sqlite3 /home/thadd/.hermes/state.db "PRAGMA integrity_check;" 2>&1 | head -1
```

**Truncate if bloated (after backup):**
```bash
# BEFORE truncating anything:
cp /home/thadd/.hermes/state.db /home/thadd/.hermes/backups/state-$(date +%Y%m%d-%H%M).db

# If integrity_check fails:
sqlite3 /home/thadd/.hermes/state.db << 'EOF'
REINDEX;
VACUUM;
PRAGMA integrity_check;
EOF
```

---

## 6. Disk Space (WSL)

**Check:**
```bash
df -h /home/thadd/.hermes | tail -1
df -h / | tail -1
```

**Common growth vectors:**
- `sessions/` — JSON logs from every interaction
- `state.db-wal` — write-ahead log can grow large if gateway crashes uncleanly
- `audio_cache/` — TTS audio files
- `backups/` — state snapshots

**Clean safely:**
```bash
# Remove old session files (>7 days)
find /home/thadd/.hermes/sessions -mtime +7 -delete 2>/dev/null

# Vacuum state.db
sqlite3 /home/thadd/.hermes/state.db "VACUUM;" 2>/dev/null

# Clear audio cache
rm -f /home/thadd/.hermes/audio_cache/*.mp3 2>/dev/null
```

---

## 8. External System-Level Watchdog (Critical Architecture Note)

### The Problem: Hermes Cannot Restart Itself

A cron job **inside** Hermes (`hermes cron create`) cannot restart Hermes itself — if Hermes is dead, the scheduler is dead, and no cron fires.

**Detection:** You already have `gateway-watchdog` running every 15 minutes as an internal cron. This is for diagnostics *within* a running process — it cannot resurrect a dead one.

**Solution:** A **system-level cron** (managed via `crontab -e` on WSL, or systemd timer, or Windows Task Scheduler) that checks `pgrep hermes` from *outside* the Hermes runtime.

### Implementation: Hermes Watchdog with Windows Shortcuts

**1. Create the watchdog script** (`~/.hermes/scripts/hermes-watchdog.sh`):
```bash
LOGFILE="$HOME/.hermes/logs/watchdog.log"
mkdir -p "$(dirname "$LOGFILE")"

if ! pgrep -f "hermes_cli.main gateway run" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Gateway NOT running — restarting..." >> "$LOGFILE"
    pkill -f "hermes gateway" 2>/dev/null
    sleep 2
    nohup /home/thadd/.hermes/hermes-agent/venv/bin/hermes gateway run --replace \
        > "$HOME/.hermes/logs/gateway_watchdog_restart.log" 2>&1 &
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Gateway restarted (PID $!)" >> "$LOGFILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Gateway OK" >> "$LOGFILE"
fi

if ! pgrep -f "hermes-webui-new/server.py" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WebUI NOT running — restarting..." >> "$LOGFILE"
    cd /home/thadd/hermes-webui-new || exit 1
    nohup /home/thadd/.hermes/hermes-agent/venv/bin/python server.py \
        > "$HOME/.hermes/logs/webui_watchdog_restart.log" 2>&1 &
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WebUI restarted (PID $!)" >> "$LOGFILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WebUI OK" >> "$LOGFILE"
fi
```

**2. Install system crontab:**
```bash
crontab -e
# Add:
*/10 * * * * /bin/bash /home/thadd/.hermes/scripts/hermes-watchdog.sh
```

**3. Windows desktop shortcuts** (`C:\Users\thadd\Desktop\Hermes\`):
- `Start Hermes Watchdog.bat` — enables cron + runs immediate check via WSL
- `Stop Hermes Watchdog.bat` — disables the cron only (Hermes keeps running)
- `.lnk` shortcuts on the desktop itself with custom icons

**Log:** `~/.hermes/logs/watchdog.log` — silent when healthy, reports only when restarting.

### Architecture Decision Table
| Layer | Can Restart Hermes? | Cost |
|-------|---------------------|------|
| Internal `hermes cron` | No — dies with Hermes | LLM tokens per tick |
| WSL system crontab | Yes | Zero tokens, shell only |
| systemd service | Yes | Best for production |

---

## Pitfalls

| Mistake | Consequence |
|---------|-------------|
| Running `VACUUM` on a locked state.db | SQLite error, possible corruption |
| Deleting `.tick.lock` during active cron run | Next tick starts early, race condition |
| Trusting only `pgrep` for gateway check | Process may exist but be unresponsive; always use `curl /health` |
| Not backing up state.db before vacuum | Irreversible data loss if vacuum fails |
| Checking Ollama tokens only at session start | May exhaust mid-session without warning |
| Running start script in foreground with `&` backgrounding | Command may fail silently or hang; use proper background mode |
| `AUTH_DISABLED` set to anything other than `"1"` | Auth remains fully enabled; must be exact `"1"` |

---

## See Also

- `references/webui-down-vs-broken.md` — Diagnostic guide for "WebUI crashed" reports that are actually just a stopped process
- `references/webui-disconnected-auth-audit.md` — "Disconnected" after restarts + auth surface testing findings
- `hermes-webui-ollama-fix` — Ollama Cloud bridge recovery
- `hermes-webui-setup` — Full WebUI lifecycle
- `hermes-secure-github-backup` — Agent state backup to GitHub
- `backup-agent-state` — Runtime state snapshotting
