# EKKOLearnAI `hermes-web-ui` Setup Reference

The `EKKOLearnAI/hermes-web-ui` is a full-featured browser-based WebUI for Hermes Agent (not the built-in Hermes dashboard, not the Spock WebUI). It runs a Koa/Vue 3/Socket.IO server and requires Node.js >=23 to build.

## Prerequisites

- Node.js >=23.0.0 (system Node 22.x will fail with EBADENGINE at `npm install`)
- If system Node is too old, use the **direct binary bootstrap** pattern (see `blocked-terminal-recovery/references/nodejs-binary-bootstrap.md`):
  ```bash
  curl -fsSL https://nodejs.org/dist/v26.1.0/node-v26.1.0-linux-x64.tar.xz -o /tmp/node26.tar.xz
  rm -rf ~/node26 && mkdir ~/node26
  tar xf /tmp/node26.tar.xz -C ~/node26 --strip-components=1
  ~/node26/bin/node --version  # → v26.1.0
  ```

## Installation Steps

```bash
# 1. Clone
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git ~/hermes-web-ui-ekko

# 2. Install + build (invoke with explicit local Node binary)
cd ~/hermes-web-ui-ekko
~/node26/bin/npm install
# npm runs `prepare && build` automatically; builds both client and server
```

## Running the Server

The built entry point is `dist/server/index.js`. Launch with required env vars:

```bash
env \
  HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui \
  PORT=8648 \
  BIND_HOST=0.0.0.0 \
  WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace \
  AUTH_DISABLED=1 \
  ~/node26/bin/node dist/server/index.js
```

| Env Var | Default | Notes |
|---------|---------|-------|
| `HERMES_WEB_UI_HOME` | `~/.hermes-web-ui` | Where token, DB, uploads, logs live. Set to `~/.hermes/webui` to collocate with other Hermes state |
| `PORT` | 8648 | Server listen port |
| `BIND_HOST` | `0.0.0.0` | Bind address. Use `0.0.0.0` to allow Windows browser access from WSL |
| `WORKSPACE_BASE` | `/opt/data/workspace` | Root directory for the file browser in the UI |
| `AUTH_DISABLED` | `false` | Set `1` to disable token auth (useful for local dev) |

## Verification

```bash
curl -s http://127.0.0.1:8648/health | python3 -m json.tool
# Expected:
# {
#   "status": "ok",
#   "platform": "hermes-agent",
#   "version": "v0.14.0",
#   "webui_version": "0.5.30",
#   "gateway": "running"
# }
```

From Windows: `http://<WSL_IP>:8648` (use `wsl hostname -I` to get current IP).

## Migrating OpenClaw Workspace

The `WORKSPACE_BASE` env var makes the file browser show your OpenClaw files. To also copy the OpenClaw content into the WebUI's own storage:

```bash
mkdir -p /home/thadd/.hermes/webui/openclaw-migrated
cp -r /mnt/c/Users/thadd/.openclaw/workspace/* /home/thadd/.hermes/webui/openclaw-migrated/
```

## Running as Background Daemon

```bash
# terminal(background=true)
cd ~/hermes-web-ui-ekko && env \
  HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui \
  PORT=8648 \
  BIND_HOST=0.0.0.0 \
  WORKSPACE_BASE=/mnt/c/Users/thadd/.openclaw/workspace \
  AUTH_DISABLED=1 \
  ~/node26/bin/node dist/server/index.js
```

Then verify via separate `curl` call.

## Comparison Table

| System | Port | Stack | Node Req | Best For |
|--------|------|-------|----------|----------|
| EKKOLearnAI WebUI | 8648 | Koa + Vue 3 + Socket.IO | >=23 | Full-featured dashboard with terminal, file browser, multi-platform config |
| Hermes Dashboard | 9119 | FastAPI + React | None (Python) | Built-in, minimal setup |
| Spock WebUI | 8787 | Python + Flask | None | Legacy, systemd-based |

## References

- `spock-webui-admin/references/webui-system-differences.md` — Detailed comparison of all three WebUI systems
- `blocked-terminal-recovery/references/nodejs-binary-bootstrap.md` — Direct Node binary download pattern
