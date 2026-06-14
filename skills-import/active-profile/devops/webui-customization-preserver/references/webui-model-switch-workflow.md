# Switching Default LLM Model in WebUI + Hermes

End-to-end workflow for changing the active default model (e.g., `kimi-k2.6:cloud` → `kimi-k2.7-code:cloud`).

## Affected Components

| Component | File | What to change |
|---|---|---|
| Profile config | `~/.hermes/profiles/<profile>/config.yaml` | `model.default`, provider `default_model` and `models` list |
| WebUI provider presets | `packages/server/src/shared/providers.ts` | Add model to each provider's `models` array |
| WebUI session DB | `~/.hermes/webui/hermes-web-ui.db` | Update existing session rows (optional) |
| Agent core metadata | `agent/model_metadata.py` | Add context window entry for the new model |

## Step-by-Step

### 1. Verify the new model exists in Hermes registry

```bash
grep -n "kimi-k2.7" /home/thadd/hermes-agent-ui/hermes_cli/models.py
```

If the model is not registered in `models.py`, it may still work if the provider supports it, but the model picker won't show it and context-length lookups may fall through to stale OpenRouter metadata.

### 2. Update profile config.yaml

```bash
profile="plc-coder"
cd ~/.hermes/profiles/$profile
# Backup
cp config.yaml config.yaml.bak.$(date +%Y%m%d_%H%M%S)
# Replace old model string with new one
sed -i 's/kimi-k2\.6:cloud/kimi-k2.7-code:cloud/g' config.yaml
sed -i 's/kimi-k2\.6/kimi-k2.7-code/g' config.yaml
# Verify
grep -n "kimi-k2" config.yaml
```

**Important:** The `ollama-launch` provider uses `:cloud` suffix (e.g., `kimi-k2.7-code:cloud`) while the `ollama-cloud` provider uses bare names (e.g., `kimi-k2.7-code`). Keep both formats in sync.

### 3. Update WebUI provider presets

File: `packages/server/src/shared/providers.ts`

Add the new model ID to **every** provider list that carries the old model. For example, if `kimi-k2.6` was in:
- `kimi-coding` provider
- `kimi-coding-cn` provider
- `nvidia` provider
- `ai-gateway` provider
- `opencode` provider
- `nous` recommended models

Add `kimi-k2.7-code` (or `moonshotai/kimi-k2.7-code` for OpenRouter-style providers) **before** the old model so it appears first in dropdowns.

```bash
cd /home/thadd/hermes-web-ui-ekko
# Count how many places need updating
grep -n "kimi-k2.6" packages/server/src/shared/providers.ts
# Patch each location
```

### 4. Update agent core context metadata

File: `/home/thadd/hermes-agent-ui/agent/model_metadata.py`

Add the new model with its context window to prevent stale OpenRouter metadata from underreporting it as 32K:

```python
"moonshotai/Kimi-K2.7-Code": 262144,
```

Place it near the other Kimi entries for readability.

### 5. Update existing WebUI sessions (optional)

If you want existing sessions to also use the new model:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/thadd/.hermes/webui/hermes-web-ui.db')
c = conn.cursor()
c.execute(\"UPDATE sessions SET model = 'kimi-k2.7-code' WHERE model = 'kimi-k2.6'\")
print(f'Updated {c.rowcount} sessions')
conn.commit()
conn.close()
"
```

### 6. Rebuild WebUI and restart

```bash
cd /home/thadd/hermes-web-ui-ekko
~/node26/bin/npm run build
systemctl --user restart hermes-webui.service
```

### 7. Verify end-to-end

```bash
# Profile config
grep "default:" ~/.hermes/profiles/plc-coder/config.yaml
# Provider presets (count occurrences)
grep -c "kimi-k2.7-code" packages/server/src/shared/providers.ts
# Agent metadata
grep -c "Kimi-K2.7-Code" /home/thadd/hermes-agent-ui/agent/model_metadata.py
# WebUI health
curl -sf http://127.0.0.1:8648/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('version'))"
# Service status
systemctl --user is-active hermes-webui.service
```

## Pitfalls

### Provider ID format mismatch
Some providers use bare model IDs (`kimi-k2.7-code`) while OpenRouter-compatible providers use prefixed IDs (`moonshotai/kimi-k2.7-code`). Check existing entries in `providers.ts` to match the format used by that provider.

### `:cloud` suffix handling
The `models_dev.py` suffix-aware fallback strips `:cloud` and `-cloud` suffixes during context-length lookup. If your new model uses a suffix not in the fallback list, add it there too.

### Missing context metadata causes 32K fallback
If `model_metadata.py` doesn't have an entry for the new model, the agent falls back to OpenRouter metadata which often underreports Kimi models as 32,768 tokens. This triggers the 64K minimum-context guard and causes incorrect compression behavior.

### WebUI DB sessions don't auto-update
Existing sessions keep their old `model` column value. New sessions pick up the profile default. Update the DB if you want historical sessions to show the new model in the UI.

## Related References

- `references/webui-reasoning-config-system.md` — Per-chat reasoning depth (future feature)
- `references/hermes-core-update-with-webui.md` — How to update Hermes core without touching WebUI
