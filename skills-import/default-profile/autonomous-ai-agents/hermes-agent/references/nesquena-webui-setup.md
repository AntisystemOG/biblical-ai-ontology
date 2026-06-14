# Nesquena Hermes WebUI — Alternative Dashboard Setup

Third-party WebUI at https://github.com/nesquena/hermes-webui (7.8k+ stars). Dark-themed three-panel layout (sidebar, chat, file browser). Pure Python + vanilla JS — no npm build step.

## Quick Install

```bash
cd ~
git clone https://github.com/nesquena/hermes-webui.git hermes-webui-new
cd hermes-webui-new
```

Install deps into your existing Hermes venv (do NOT create a separate venv — the WebUI needs to import `run_agent`):

```bash
/home/thadd/.hermes/hermes-agent/venv/bin/pip3 install -r requirements.txt
```

## Branding & Home Directory Setup

The upstream repo ships with "Spock" branding and `~/.spock` paths. You can **keep Spock branding** or **rebrand to Hermes** — choose one path before first run.

### Option A: Keep Spock branding (user's preference)

Leave `ctl.sh` and `bootstrap.py` as-is. The WebUI will show "Spock WebUI" and use `~/.spock` for its own state. **However**, the `hermes` agent subprocess must still find `config.yaml` under `~/.hermes`. Achieve this by setting `HERMES_HOME` in the service env:

```bash
# In systemd service or launch env:
export HERMES_HOME="/home/thadd/.hermes"          # agent finds config.yaml here
export HERMES_WEBUI_STATE_DIR="/home/thadd/.spock/webui"  # WebUI SQLite + logs
```

### Option B: Rebrand to Hermes

```bash
# Fix HERMES_HOME default from ~/.spock to ~/.hermes
sed -i 's|HERMES_HOME="${HERMES_HOME:-${HOME}/.spock}"|HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"|' ctl.sh

# Fix "Spock" → "Hermes" in user-facing messages
sed -i 's/Spock WebUI/Hermes WebUI/g' ctl.sh
```

### Bootstrap auto-discovery overrides

Regardless of branding choice, pin the Python interpreter and agent directory so bootstrap doesn't guess wrong:

```bash
export HERMES_WEBUI_PYTHON="/home/thadd/.hermes/hermes-agent/venv/bin/python3"
export HERMES_WEBUI_AGENT_DIR="/home/thadd/.hermes/hermes-agent"
```

## Running

```bash
# Foreground
cd ~/hermes-webui-new
python3 server.py

# Or via ctl.sh daemon wrapper
./ctl.sh start     # background daemon
./ctl.sh status    # check health
./ctl.sh stop      # kill daemon
./ctl.sh logs      # tail log
```

## Systemd Auto-Start (WSL)

WSL with `systemd=true` in `/etc/wsl.conf` supports user services. Use `Type=simple` (NOT `forking`) — ctl.sh's PID file tracking conflicts with systemd's forking expectations.

```ini
# ~/.config/systemd/user/hermes-webui.service
[Unit]
Description=Hermes WebUI
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/thadd/hermes-webui-new
Environment="HERMES_WEBUI_PYTHON=/home/thadd/.hermes/hermes-agent/venv/bin/python3"
Environment="HERMES_WEBUI_AGENT_DIR=/home/thadd/.hermes/hermes-agent"
Environment="HERMES_HOME=/home/thadd/.hermes"
Environment="HERMES_WEBUI_STATE_DIR=/home/thadd/.hermes/webui"
Environment="HERMES_WEBUI_HOST=127.0.0.1"
Environment="HERMES_WEBUI_PORT=8787"
ExecStart=/home/thadd/.hermes/hermes-agent/venv/bin/python3 /home/thadd/hermes-webui-new/server.py
Restart=on-failure
RestartSec=5
StandardOutput=append:/home/thadd/.hermes/webui.log
StandardError=append:/home/thadd/.hermes/webui.log

[Install]
WantedBy=default.target
```

Then:
```bash
systemctl --user daemon-reload
systemctl --user enable hermes-webui.service
systemctl --user start hermes-webui.service
```

## Troubleshooting

### "No LLM provider configured" in chat panel

Symptom: WebUI loads fine, all API calls return 200, but chat says "Error: No LLM provider configured. Run hermes model to select a provider..."

Root cause: the WebUI spawns the `hermes` CLI as a subprocess. The error is emitted by the agent itself, not the WebUI server. Most commonly, **Ollama is running but has zero models installed** (`curl http://127.0.0.1:11434/api/tags` returns `{"models":[]}`). The agent loads the provider config (e.g. `ollama-launch` with model `llama3.1`) but Ollama cannot serve it.

Fixes:
1. **Pull a model** if you want local inference: `ollama pull llama3.1`
2. **Switch provider** in WebUI or CLI: run `hermes model` and pick a cloud provider (OpenRouter, Anthropic, etc.)
3. **Check Ollama endpoint** — if using Ollama Pro/cloud, verify `OLLAMA_BASE_URL` points to the correct endpoint, not localhost

**Ollama Pro / cloud specific misconfiguration:**
- `config.yaml` `base_url` must be `https://api.ollama.com/v1`, NOT `http://127.0.0.1:11434`
- `config.yaml` `model` must be the plain ID from the cloud API (`kimi-k2.6`), NOT `kimi-k2.6:cloud`
- `auth.json` credential pool `ollama-cloud` entry must have `base_url: https://api.ollama.com`, NOT `http://localhost:11434`
- See `references/ollama-pro-cloud-setup.md` for the complete config snippet

Verification: after fixing, run `hermes chat -q "hello"` in a terminal. If that works, the WebUI chat will too.

### "Spock" vs "Hermes" branding mismatch

If you see "Hermes" in some places and "Spock" in others, you applied a partial rebrand. The repo uses "Spock" in `ctl.sh` strings, `bootstrap.py` docstring, and `HERMES_HOME` default. Either rebrand all of them (sed across all three files) or revert all patches and keep Spock branding with the split-directory approach above.

### Systemd service fails immediately

`Type=forking` with `ctl.sh` often fails because ctl.sh writes a PID file and forks, but systemd loses track. Use `Type=simple` with direct `server.py` execution instead. See the systemd example below.

Both can run simultaneously — assign different ports:
- Official: `hermes dashboard` → port 9119
- Nesquena: `server.py` → port 8787 (default)

## Troubleshooting — "Session not found" on chat/draft but session loads in sidebar

**Symptom:** The WebUI sidebar shows the session, `GET /api/session?session_id=...` returns data, but `POST /api/chat/start` or `POST /api/session/draft` returns `{"error":"Session not found"}`.

**Root cause:** The WebUI's `SESSION_DIR` (where JSON sidecars live) is split from the CLI's `state.db` (where canonical session data lives). The GET endpoint has a fallback to `state.db` metadata on `KeyError`, but the POST chat/draft handlers do **not** — they require the sidecar file `SESSION_DIR / {sid}.json` to exist.

This happens when `HERMES_WEBUI_STATE_DIR` points to a directory that does **not** contain the session sidecar, even though `state.db` has the session row. Common cause: the systemd service sets `HERMES_WEBUI_STATE_DIR=/home/user/.spock/webui` while the actual session data (sidecar + `state.db` + journals + attachments) lives in `~/.hermes/webui/`.

**Fix:** Point `HERMES_WEBUI_STATE_DIR` to the directory that actually holds the sidecars, not the CLI state directory.

```ini
# In ~/.config/systemd/user/hermes-webui.service
Environment="HERMES_WEBUI_STATE_DIR=/home/thadd/.hermes/webui"
```

Then reload and restart:
```bash
systemctl --user daemon-reload
systemctl --user restart hermes-webui.service
```

**Why not migrate the sidecar to `.spock`?** The sidecar file contains relative paths to run journals, turn journals, and attachments that are co-located with it. Moving only the JSON sidecar breaks journal/attachment resolution. It is safer to update the env var than to migrate files piecemeal.

**Verification:** After restart, test both endpoints:
```bash
curl -s "http://127.0.0.1:8787/api/session?session_id=YOUR_SID"
curl -s -X POST http://127.0.0.1:8787/api/session/draft \
  -H "Content-Type: application/json" \
  -d '{"session_id":"YOUR_SID","text":"test"}'
```
Both should succeed.

## When to Use Which

| | Official Dashboard | Nesquena WebUI |
|--|-------------------|----------------|
| Build step | npm + React | None (pure Python) |
| Look | Minimal config/status panels | Full chat + file browser + sidebar |
| Speed | Slower startup (needs build) | Instant |
| Dependency | Needs `npm run build` | Needs Hermes agent import path |
| Best for | Config editing, status checks | Daily chat, session browsing |
