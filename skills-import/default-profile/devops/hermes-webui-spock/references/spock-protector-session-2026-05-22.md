# Spock Protector — Session-Specific Additions

## Session 2026-05-22: Locking Customizations + Systemd PATH Fix

### Discovery: systemd PATH does NOT inherit user PATH

When the WebUI server restarted via systemd, it crashed with:
```
FATAL: Uncaught exception
Error: spawn hermes ENOENT
    at ChildProcess._handle.onexit (node:internal/child_process:286:19)
```

The server tries to spawn `hermes gateway run --replace` as a subprocess.
The `hermes` binary exists at `/home/thadd/.local/bin/hermes` and is on the
user's PATH, but systemd `ExecStart` services do NOT inherit shell PATH.

**Fix:** Add explicit PATH to the service file:
```ini
Environment="PATH=/home/thadd/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

After adding this, the server started correctly and spawned the agent bridge.

### Discovery: Hermes cron script paths must be relative

When creating the cron watchdog via `cronjob(action='create')`, passing an
absolute path like `/home/thadd/.hermes/scripts/spock-protector/guard.sh`
was rejected with:
```
Script path must be relative to ~/.hermes/scripts/.
```

**Fix:** Place script under `~/.hermes/scripts/` and pass only the relative
filename (e.g. `spock-protector/guard.sh`). The scheduler resolves it under
`~/.hermes/scripts/` automatically.

### systemd service path to use

The systemd service `ExecStart` must be:
```
ExecStart=/home/thadd/.hermes/node/bin/node dist/server/index.js
```

NOT `bin/hermes-web-ui.mjs start` (that spawns a second process wrapper).
The direct `node dist/server/index.js` approach gives systemd direct control
over the main process PID, enabling reliable restart on failure.

### Complete current service file (2026-05-22)

```ini
[Unit]
Description=Spock WebUI (EKKOLearnAI)
After=network.target

[Service]
Type=simple
WorkingDirectory=/mnt/c/Users/thadd/hermes-web-ui
Environment="HERMES_HOME=/home/thadd/.hermes"
Environment="SPOCK_WEBUI_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3"
Environment="SPOCK_WEBUI_AGENT_DIR=/home/thadd/.hermes/hermes-agent"
Environment="SPOCK_WEBUI_STATE_DIR=/home/thadd/.hermes/webui"
Environment="SPOCK_WEBUI_HOST=0.0.0.0"
Environment="SPOCK_WEBUI_PORT=8648"
Environment="PATH=/home/thadd/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/thadd/.hermes/node/bin/node dist/server/index.js
Restart=on-failure
RestartSec=5
StandardOutput=append:/home/thadd/.spock/webui.log
StandardError=append:/home/thadd/.spock/webui.log

[Install]
WantedBy=default.target
```

Service is enabled for auto-start on boot:
```bash
systemctl --user daemon-reload
systemctl --user enable hermes-webui.service
systemctl --user start hermes-webui.service
```

### Cron job ID for watchdog

- Job name: `spock-guardian-watchdog`
- Job ID: `88a43850fcff`
- Schedule: `*/5 * * * *`
- Script: `spock-protector/guard.sh` (relative to `~/.hermes/scripts/`)
- Mode: `no_agent: true` (script-only, no LLM loop)

### Current file locations

| File | Path |
|------|------|
| systemd service | `/home/thadd/.config/systemd/user/hermes-webui.service` |
| Cron guard script | `/home/thadd/.hermes/scripts/spock-protector/guard.sh` |
| Git hooks | `/mnt/c/Users/thadd/hermes-web-ui/.git/hooks/post-{merge,checkout,rewrite}` |
| Immutable backups | `/home/thadd/.hermes/spock-protector/` |
| Emergency restore | `/home/thadd/.hermes/spock-protector/restore-spock.sh` |
| Update reject | `/home/thadd/.hermes/scripts/spock-protector/update-reject.sh` |
| Server log | `/home/thadd/.spock/webui.log` |
| Desktop launcher | `C:\Users\thadd\Desktop\Launch Hermes WebUI.bat` |
