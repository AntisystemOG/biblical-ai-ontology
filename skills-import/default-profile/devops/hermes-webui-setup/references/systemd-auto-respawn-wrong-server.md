# systemd User Service Trapping Port 8648

## Problem

The EKKOLearnAI WebUI server runs on port 8648. A separate Python `server.py` from `~/hermes-webui-new/` (wrong repo) can occupy the same port, **and a systemd user service can auto-restart it indefinitely**, making it appear the "wrong server" respawns by magic.

## Symptom Sequence

1. `lsof -iTCP:8648` shows `python3 /home/thadd/hermes-webui-new/server.py` (PID e.g. 5204)
2. `kill -9 5204` — process dies
3. Within seconds, `lsof -iTCP:8648` shows a NEW PID (e.g. 5456, same command line)
4. Repeat kills → new PIDs keep appearing

## Root Cause

`~/.config/systemd/user/hermes-webui.service` with:

```ini
[Unit]
Description=Hermes Web UI
After=network.target
[Service]
ExecStart=/home/thadd/.hermes/hermes-agent/venv/bin/python3 /home/thadd/hermes-webui-new/server.py
Restart=on-failure
```

The `Restart=on-failure` directive respawns the process every time it is killed (the killed child returning non-zero causes systemd to restart).

## Fix

```bash
# Stop the service immediately
systemctl --user stop hermes-webui.service

# Disable it so it never restarts again
systemctl --user disable hermes-webui.service

# Verify
systemctl --user status hermes-webui.service
# → State: inactive (dead)
```

## Verifying the fix

After stopping/disabling:
```bash
lsof -iTCP:8648 -sTCP:LISTEN   # should be empty
ss -tlnp | grep :8648            # should be empty
```

Then start the correct EKKOLearnAI server:
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
node bin/hermes-web-ui.mjs start
```

## Prevention

Before creating any Desktop shortcut or launcher:
1. Check `systemctl --user status hermes-webui.service`
2. If it exists AND points to the wrong repo → `stop` + `disable`
3. Then check port 8648 and start the correct server

## Related Pitfalls

- `hermes-webui-new/server.py` is also started by scripts within Spock's old workspace. Those scripts do NOT respawn; only systemd does.
- The systemd service file can remain on disk after being disabled. It will NOT auto-start on boot, but could be accidentally re-enabled later.
