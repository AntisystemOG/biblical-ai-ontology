# Ollama Pro / Cloud Provider Setup for Hermes

Hermes supports both **local Ollama** (default `http://localhost:11434`) and **Ollama Pro / cloud endpoints** (`https://api.ollama.com`). These use the same provider (`ollama-launch`) but different `base_url` and authentication.

## Quick Check: Which Endpoint Are You Using?

```bash
# Local Ollama — must have models pulled
curl http://localhost:11434/api/tags | python3 -m json.tool

# Ollama Pro cloud — requires valid token
curl -s -H "Authorization: Bearer $YOUR_TOKEN" \
  https://api.ollama.com/v1/models | python3 -m json.tool
```

## Configuration for Ollama Pro Cloud

### Correct Base URL

**Critical**: `https://api.ollama.com` returns **HTTP 301 redirect** to `https://ollama.com`. The API client does not follow redirects. Use **`https://ollama.com/v1`** instead.

| Location | Value | Why |
|----------|-------|-----|
| `.env` | `OLLAMA_BASE_URL=https://ollama.com/v1` | Server env, used by agent bridge |
| `auth.json` credential pool | `base_url: "https://ollama.com/v1"` | Hermes reads this for ollama-cloud provider |
| `models_cache.json` | `active_provider: ollama-cloud` | Session cache for WebUI default |

Verification:
```bash
KEY=$(grep OLLAMA_API_KEY ~/.hermes/.env | cut -d= -f2)
curl -sI "https://api.ollama.com/v1/models" -H "Authorization: Bearer $KEY"  # 301 — WRONG
curl -sI "https://ollama.com/v1/models" -H "Authorization: Bearer $KEY"     # 401 or 200 — CORRECT
```

### 1. config.yaml

```yaml
model:
  default: kimi-k2.6              # model ID from /v1/models response
  provider: ollama-cloud          # use ollama-cloud for cloud API, ollama-launch for local
```

**Pitfall:** The model ID returned by the cloud `/v1/models` endpoint is plain `kimi-k2.6`, **not** `kimi-k2.6:cloud`. The `:cloud` suffix is a local provider convention; using it with the cloud API produces a "model not found" error.

**Provider choice:**
- `ollama-cloud` → uses `OLLAMA_BASE_URL` + `OLLAMA_API_KEY`, hits `https://ollama.com/v1`
- `ollama-launch` → used for local `localhost:11434`, fails when no models are pulled
