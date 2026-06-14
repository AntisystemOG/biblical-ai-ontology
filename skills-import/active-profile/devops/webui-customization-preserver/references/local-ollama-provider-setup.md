# Local Ollama Provider Setup in Hermes WebUI

## Problem

The WebUI's model selector only shows providers from a hardcoded registry. Even if your Hermes `config.yaml` already defines a `providers.ollama-launch` section, the WebUI will not display it unless all three server-side registries are updated and the local Ollama server actually has models installed.

**Symptoms:**
- `curl /api/hermes/available-models` only returns `ollama-cloud` (remote), never `ollama-launch` (local)
- Local Ollama is running (`http://127.0.0.1:11434` responds) but WebUI shows 0 providers or only remote ones
- Changing `config.yaml` provider to `ollama-launch` has no effect on the WebUI dropdown

## Architecture — Three Registries Must Align

| Registry | File | Purpose | What It Controls |
|---|---|---|---|
| **Provider Presets** | `packages/server/src/shared/providers.ts` | Frontend dropdown labels & base URLs | What the user sees in the model selector |
| **Env Map** | `packages/server/src/services/config-helpers.ts` | Auth requirements & env var mapping | Whether the provider appears without credentials |
| **Auth Exemptions** | `packages/server/src/controllers/hermes/models.ts` | OAuth / no-auth gating | Whether the provider is skipped during model enumeration |
| **Live Fetch List** | `packages/server/src/controllers/hermes/models.ts` | Dynamic model fetching | Whether the server queries the provider's `/models` endpoint |

## Hermes Config (Source of Truth for Agent)

Your `~/.hermes/profiles/<profile>/config.yaml` controls the **agent's** provider, not the WebUI's display:

```yaml
model:
  default: kimi-k2.6
  provider: ollama-launch   # agent uses this
providers:
  ollama-cloud:
    api: https://ollama.com/v1
    default_model: kimi-k2.6
    models: [kimi-k2.6]
  ollama-launch:             # must also exist here for agent fallback
    api: http://127.0.0.1:11434/v1
    default_model: llama3.2   # whatever you pulled locally
    models: [llama3.2]
```

**Important:** `model.provider: ollama-launch` tells the **Hermes CLI/agent** to use the local server. The WebUI has its own model selection that may override this per-session.

## Step-by-Step: Adding a Local Provider to the WebUI

### Step 1 — Add to Provider Presets

`packages/server/src/shared/providers.ts`:

```typescript
export const PROVIDER_PRESETS: ProviderPreset[] = [
  // ... existing presets ...
  {
    label: 'Ollama Cloud',
    value: 'ollama-cloud',
    builtin: true,
    base_url: 'https://ollama.com/v1',
    models: [],
  },
  {
    label: 'Ollama Local',       // <-- ADD THIS
    value: 'ollama-launch',
    builtin: true,
    base_url: 'http://127.0.0.1:11434/v1',
    models: [],                   // empty = fetch live
  },
  // ... more presets ...
]
```

**Rule:** `value` must match the key in Hermes `config.yaml` (`providers.ollama-launch`).

### Step 2 — Add to Env Map

`packages/server/src/services/config-helpers.ts`:

```typescript
export const PROVIDER_ENV_MAP = {
  // ... existing entries ...
  'ollama-cloud': { api_key_env: 'OLLAMA_API_KEY', base_url_env: 'OLLAMA_BASE_URL' },
  'ollama-launch': { api_key_env: '', base_url_env: 'OLLAMA_BASE_URL' },  // <-- ADD THIS
  // ...
}
```

**`api_key_env: ''`** means "no API key required" — critical for local servers.

### Step 3 — Exempt from Auth Gating

`packages/server/src/controllers/hermes/models.ts` around line 342:

```typescript
for (const [providerKey, envMapping] of Object.entries(PROVIDER_ENV_MAP)) {
  if (envMapping.api_key_env && !envHasValue(envMapping.api_key_env)) continue
  if (!envMapping.api_key_env) {
    if (providerKey === 'copilot') {
      // ... copilot checks ...
    } else if (providerKey === 'ollama-launch' || providerKey === 'lmstudio') {
      // Local providers require no auth — always include  <-- ADD THIS
    } else if (!isOAuthAuthorized(providerKey)) {
      continue
    }
  }
  // ... rest of loop ...
}
```

Without this exemption, the `else if (!isOAuthAuthorized(providerKey))` branch skips `ollama-launch` because it has no `api_key_env` and no OAuth tokens.

### Step 4 — Enable Live Model Fetching

`packages/server/src/controllers/hermes/models.ts` around line 184:

```typescript
function providerShouldFetchLiveModels(providerKey: string): boolean {
  return providerKey === 'openrouter' ||
    providerKey === 'cliproxyapi' ||
    providerKey === 'ollama-cloud' ||
    providerKey === 'lmstudio' ||
    providerKey === 'ollama-launch'   // <-- ADD THIS
}
```

This causes the server to call `GET http://127.0.0.1:11434/v1/models` and populate the dropdown dynamically.

### Step 5 — Rebuild Server Bundle

```bash
cd /home/thadd/hermes-web-ui
export PATH=/home/thadd/node26/bin:$PATH
node scripts/build-server.mjs
```

**Note:** The client (`vite build`) does NOT need rebuilding for provider changes — they are server-side only.

### Step 6 — Restart Server

```bash
pkill -f "node.*dist/server/index.js" || true; sleep 2

unset AUTH_DISABLED
export NODE_ENV=production
export HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui
export HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3
export PORT=8648
export BIND_HOST=0.0.0.0

cd /home/thadd/hermes-web-ui
/home/thadd/node26/bin/node dist/server/index.js
```

### Step 7 — Verify

```bash
token=$(cat ~/.hermes/webui/.token)

# Check available providers
curl -sf http://127.0.0.1:8648/api/hermes/available-models \
  -H "Authorization: Bearer $token" | jq '.groups[] | {provider, label, base_url, models_count: (.models | length)}'

# Should now include:
# {
#   "provider": "ollama-launch",
#   "label": "Ollama Local",
#   "base_url": "http://127.0.0.1:11434/v1",
#   "models_count": N
# }
```

## Step 8 — Install Models in Local Ollama

If `models_count` is 0, the local server is running but empty:

```bash
# List what's available
ollama list

# Pull a model
ollama pull llama3.2
ollama pull deepseek-coder-v2

# Verify
curl -sf http://127.0.0.1:11434/api/tags | jq '.models[].name'
```

**Without at least 1 model installed**, the WebUI shows the provider label but an empty model list.

## Common Failures

### "Provider not in dropdown" — missing from PROVIDER_PRESETS
**Check:** `grep "ollama-launch" packages/server/src/shared/providers.ts`
**Fix:** Add the preset object (Step 1 above).

### "Provider in dropdown but 0 models" — missing from providerShouldFetchLiveModels
**Check:** Server logs for `available-models http://127.0.0.1:11434/v1 returned` or timeouts
**Fix:** Add to `providerShouldFetchLiveModels` (Step 4 above).

### "Provider not listed at all" — auth gating
**Check:** Temporarily comment out the `else if (!isOAuthAuthorized(providerKey))` block and restart
**Fix:** Add local-provider exemption (Step 3 above).

### "Models fetched but not matching default_model"
The WebUI automatically includes the configured `default_model` even if the provider doesn't list it. Check `includeConfiguredDefaultModel()` in `models.ts`.

## Relationship to Hermes CLI Config

The WebUI and Hermes CLI use **different config systems**:

| System | Config File | Controls |
|---|---|---|
| Hermes CLI | `~/.hermes/profiles/<profile>/config.yaml` | Agent bridge, default model for new sessions |
| WebUI Server | `~/.hermes/webui/hermes-web-ui.db` + hardcoded registries | Dropdown display, per-session model override |

**When you select a model in the WebUI**, it updates the **session** record in the WebUI DB. The Hermes `config.yaml` is only read by the CLI/bridge worker, not by the WebUI server.

**To make local Ollama the default for ALL new WebUI sessions:**
1. Update the WebUI DB directly (not recommended — internal API)
2. Or: update `config.yaml` `model.provider` to `ollama-launch`, then restart the bridge
3. Or: use the WebUI settings panel after the provider appears in the dropdown

## Version-Specific Notes

- **v0.6.4:** `PROVIDER_PRESETS` and `PROVIDER_ENV_MAP` were the only files needing changes. The `models.ts` auth exemption was the non-obvious fix.
- **Future versions:** If upstream adds a built-in `ollama-local` preset, remove the custom entries to avoid duplicates.

## Verification Script

```bash
#!/bin/bash
set -e

echo "=== Checking provider registries ==="
grep -c "ollama-launch" packages/server/src/shared/providers.ts \
  && echo "  ✓ PROVIDER_PRESETS" || echo "  ✗ PROVIDER_PRESETS MISSING"

grep -c "ollama-launch" packages/server/src/services/config-helpers.ts \
  && echo "  ✓ PROVIDER_ENV_MAP" || echo "  ✗ PROVIDER_ENV_MAP MISSING"

grep "ollama-launch.*lmstudio" packages/server/src/controllers/hermes/models.ts \
  && echo "  ✓ Auth exemption" || echo "  ✗ Auth exemption MISSING"

grep "providerShouldFetchLiveModels" packages/server/src/controllers/hermes/models.ts | grep "ollama-launch" \
  && echo "  ✓ Live fetch" || echo "  ✗ Live fetch MISSING"

echo ""
echo "=== Checking local Ollama ==="
curl -sf http://127.0.0.1:11434/api/tags > /dev/null \
  && echo "  ✓ Ollama running" || echo "  ✗ Ollama NOT RUNNING"

model_count=$(curl -sf http://127.0.0.1:11434/api/tags | jq '.models | length')
echo "  Local models: $model_count"

echo ""
echo "=== Checking WebUI ==="
token=$(cat ~/.hermes/webui/.token)
curl -sf http://127.0.0.1:8648/api/hermes/available-models \
  -H "Authorization: Bearer $token" | jq '.groups[] | select(.provider == "ollama-launch") | {provider, label, models_count: (.models | length)}'
```
