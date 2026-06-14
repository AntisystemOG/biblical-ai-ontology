# WebUI Model Default / Dropdown Mismatch Diagnostic

## Symptom

The Hermes WebUI model dropdown defaults to an old model (e.g., `kimi-k2.6`) and does not show a newer model (e.g., `kimi-k2.7-code:cloud`) even though the Hermes CLI config has it set under `model.default`.

## Quick Checks

### 1. Identify the active WebUI checkout

The launcher script `~/.hermes/webui/start-server.sh` tells you which directory is actually running:
```bash
cat ~/.hermes/webui/start-server.sh
```
Look for the `cd` line — usually `/home/thadd/hermes-web-ui-ekko`.

### 2. Confirm the running version

```bash
curl -sf http://127.0.0.1:8648/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('webui_version','unknown'))"
```

### 3. Inspect the Hermes profile config

```bash
cat ~/.hermes/profiles/<profile>/config.yaml | grep -A8 "^model:"
cat ~/.hermes/profiles/<profile>/config.yaml | grep -A10 "^providers:"
```

### 4. Check the legacy stale cache

```bash
ls -la ~/.hermes/webui/models_cache.json 2>/dev/null && head -20 ~/.hermes/webui/models_cache.json
```
If you see `_webui_version: "v0.51.x"`, this file is **not used** by current WebUI (≥ 0.6.x). It is leftover data. After confirming the current server is healthy, you can remove it:
```bash
mv ~/.hermes/webui/models_cache.json ~/.hermes/webui/models_cache.json.bak.$(date +%Y%m%d)
```

### 5. Check the live provider-model catalog cache

```bash
cat ~/.hermes/webui/cache/provider-model-catalog.json | python3 -m json.tool
```
This cache is refreshed by the WebUI's live fetch for `ollama-cloud`, `openrouter`, `cliproxyapi`, `lmstudio`, and `nvidia`. It does **not** include local custom providers such as `ollama-launch`.

### 6. Query the WebUI API directly

The browser's JWT is in `localStorage.hermes_api_key`. For a loopback diagnostic you can also check what the server would return by sniffing the `/api/hermes/available-models` response in the browser DevTools Network tab, or by logging in via the UI and using the Models page.

## Common Root Causes

| Cause | Evidence | Fix |
|-------|----------|-----|
| Active profile in WebUI differs from CLI | `localStorage.hermes_active_profile_name` or sessions table shows a different profile | Switch profile in the WebUI sidebar |
| `model.default` uses tagged name (`:cloud`) that the live catalog does not list | `config.yaml` has `kimi-k2.7-code:cloud`, catalog has `kimi-k2.7-code` | Add the tagged model to `providers.<name>.models` in `config.yaml`, or use the base name as default |
| `ollama-launch` custom provider only has one model listed | WebUI group `custom:ollama` shows one model | Add more models to the `models:` array in `config.yaml` |
| Stale session row overrides global default | `sessions.model` / `sessions.provider` differ from `config.yaml` | `UPDATE sessions SET model='', provider='';` then restart server |
| Running an older WebUI checkout | `/mnt/c/Users/thadd/hermes-web-ui` vs `/home/thadd/hermes-web-ui-ekko` | Update `start-server.sh` to point at the current checkout and rebuild |

## Model Name Suffixes

Ollama's `/v1/models` endpoint returns base model IDs such as `kimi-k2.7-code`. The `:cloud` suffix is a tag used by some launch scripts and the Hermes CLI to select a quantized variant. The WebUI matches strings literally, so `kimi-k2.7-code:cloud` will not match a catalog entry for `kimi-k2.7-code`.

Recommended patterns:
- **Explicit list**: keep `:cloud` in `model.default` and list it under `providers.<name>.models`.
- **Base name**: change `model.default` to the base name if you want live catalog matching.

## Relevant Files

- WebUI built-in presets: `<webui-checkout>/packages/server/src/shared/providers.ts`
- WebUI model API: `<webui-checkout>/packages/server/src/controllers/hermes/models.ts`
- Client model store: `<webui-checkout>/packages/client/src/stores/hermes/models.ts`
- Client app store / default selection: `<webui-checkout>/packages/client/src/stores/hermes/app.ts`
- Hermes profile configs: `~/.hermes/profiles/<profile>/config.yaml`
- WebUI DB sessions: `~/.hermes/webui/hermes-web-ui.db` (`sessions` table)
