# Enabling the Hermes API Server for Desktop Apps

The `fathah/hermes-desktop` Electron app connects to Hermes through an OpenAI-compatible HTTP API, not the messaging gateway directly.

## What Runs Where

| Component | Port | Purpose |
|-----------|------|---------|
| Hermes Gateway (Telegram/Discord) | varies | Messaging platform adapter |
| `api_server` platform adapter | **8642** | Desktop app API (OpenAI-compatible) |
| Old Python WebUI server | **8787** | Web-based chat UI (NOT for desktop app) |

The desktop app's `src/main/hermes.ts` hardcodes:
```ts
const LOCAL_API_URL = "http://127.0.0.1:8642";
```

## Enable in Config

Add to `~/.hermes/config.yaml` under the `gateway:` section:

```yaml
gateway:
  platforms:
    api_server:
      enabled: true
      host: "127.0.0.1"
      port: 8642
```

Then restart the Hermes gateway process.

## Verify

```bash
curl -H "Authorization: Bearer $HERMES_GATEWAY_TOKEN" http://127.0.0.1:8642/health
```

The token lives in `~/.hermes/.env` as `HERMES_GATEWAY_TOKEN`.

## Common Mistake

Trying to connect the desktop app to the old WebUI on port 8787. It will fail — the desktop needs the OpenAI-compatible API on 8642.
