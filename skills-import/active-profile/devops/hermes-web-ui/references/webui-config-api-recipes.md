# WebUI Config API Quick Recipes

Verified commands for diagnosing and fixing Hermes WebUI model/provider issues via the server's REST API.

## Prerequisites

- WebUI server running on `127.0.0.1:8648`.
- Valid JWT for a super-admin user. The WebUI stores the JWT signing secret in `~/.hermes/webui/.token`.

## Generate a JWT from the local secret (Python)

```python
import json, hmac, hashlib, base64, time

secret = open('/home/thadd/.hermes/webui/.token').read().strip()
now = int(time.time())
payload = {
    "sub": "1",
    "username": "AntiSyStem",
    "role": "super_admin",
    "type": "access",
    "aud": "hermes-web-ui",
    "iat": now,
    "exp": now + 3600,
}

def b64url(d):
    return base64.urlsafe_b64encode(json.dumps(d, separators=(',', ':')).encode()).rstrip(b'=').decode()

unsigned = f"{b64url({'alg':'HS256','typ':'JWT'})}.{b64url(payload)}"
sig = base64.urlsafe_b64encode(hmac.new(secret.encode(), unsigned.encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
jwt = f"{unsigned}.{sig}"
print(jwt)
```

## Inspect available models for a profile

```bash
JWT=$(python3 - <<'PY'
# ...paste the JWT generation snippet above...
PY
)
curl -sf "http://127.0.0.1:8648/api/hermes/available-models?profile=plc-coder" \
  -H "Authorization: Bearer $JWT" | python3 -m json.tool
```

## Add a local Ollama custom provider

Required fields: `name`, `base_url`, `model`. WebUI also requires a non-empty `api_key` for custom providers even if the endpoint does not need one.

```bash
curl -sf -X POST "http://127.0.0.1:8648/api/hermes/config/providers" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ollama Launch",
    "base_url": "http://127.0.0.1:11434/v1",
    "model": "kimi-k2.7-code:cloud",
    "api_key": "ollama",
    "context_length": 128000
  }'
```

## Set the default model and provider

```bash
curl -sf -X PUT "http://127.0.0.1:8648/api/hermes/config/model" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "default": "kimi-k2.7-code:cloud",
    "provider": "ollama-launch",
    "base_url": "http://127.0.0.1:11434/v1",
    "api_key": "ollama"
  }'
```

## Refresh live provider model catalog cache

```bash
curl -sf -X POST "http://127.0.0.1:8648/api/hermes/provider-models/cache/refresh" \
  -H "Authorization: Bearer $JWT"
```

## Read the full profile config

```bash
curl -sf "http://127.0.0.1:8648/api/hermes/config?profile=plc-coder" \
  -H "Authorization: Bearer $JWT" | python3 -m json.tool | head -80
```

## Common diagnosis output

A healthy `plc-coder` profile using a local Ollama provider should show:
```json
{
  "default": "kimi-k2.7-code:cloud",
  "default_provider": "custom:ollama-launch",
  "groups": [
    { "provider": "ollama-cloud", ... },
    { "provider": "custom:ollama-launch", "models": ["kimi-k2.7-code:cloud"] }
  ]
}
```

If `default_provider` is `ollama-cloud` and the only group is `ollama-cloud`, the local provider is missing from `custom_providers:` in `config.yaml`.

## Pitfall: providers: vs custom_providers:

The Hermes CLI understands a keyed `providers:` section, but the WebUI model dropdown only exposes providers listed in the legacy list-shaped `custom_providers:` array. A provider that exists only under `providers:` will be invisible to the WebUI and the default will fall back to a built-in provider (usually `ollama-cloud`).

## Pitfall: "Missing API key" when adding a local Ollama provider

The WebUI `POST /api/hermes/config/providers` endpoint returns `400 Missing API key` if the `api_key` field is empty or omitted, even for local endpoints that do not require authentication. Pass a placeholder such as `"ollama"`.
