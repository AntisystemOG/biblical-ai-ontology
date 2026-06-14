# Web UI Chat Unresponsive — Stale Session DB Overrides

## Symptom
The Web UI loads and accepts messages, but the assistant never responds. The browser dev tools show no errors, and the WebSocket appears connected. Sometimes the first message of a new session works, but existing conversations remain dead.

## Another Root Cause: Ollama Cloud Base URL Returns HTTP 301

If the Web UI logs show `APIStatusError [HTTP 301] Moved Permanently` instead of HTTP 404, the Ollama Cloud base URL is wrong.

The hostname `api.ollama.com` **redirects** (301) to `ollama.com`. The Node server's internal OpenAI-compatible client does **not** follow 301 redirects, so every API call fails.

**Wrong (301 redirect):** `https://api.ollama.com/v1/chat/completions`  
**Correct:** `https://ollama.com/v1/chat/completions`

The fix must touch three places before they are consistent:

1. **`~/.hermes/.env`**
```bash
OLLAMA_BASE_URL=https://ollama.com/v1
```

2. **`~/.hermes/auth.json`** (credential pool)
```json
{
  "credential_pool": {
    "ollama-cloud": [
      {
        "base_url": "https://ollama.com/v1",
        "token": "..."
      }
    ]
  }
}
```

3. **`~/.hermes/config.yaml`** (if `ollama-cloud` is the active provider)
```yaml
model:
  default: kimi-k2.6
  provider: ollama-cloud
```

**Verify before starting:**
```bash
KEY=$(grep OLLAMA_API_KEY ~/.hermes/.env | cut -d= -f2)
curl -sI "https://api.ollama.com/v1/models" -H "Authorization: Bearer $KEY"  # 301 — WRONG
curl -sI "https://ollama.com/v1/models" -H "Authorization: Bearer $KEY"     # 401/200 — CORRECT
```

**Also verify model availability:**
```bash
curl -s "https://ollama.com/v1/models" -H "Authorization: Bearer $KEY" | python3 -m json.tool | grep -i kimi-k2.6
```

## Root Cause
The `hermes-web-ui` SQLite DB caches the `model` and `provider per session row. When the underlying Hermes Agent config changes (e.g., switching from `ollama-cloud` to `ollama-launch`, or updating the default model from `kimi-k2.6` to `kimi-k2.6:cloud`), existing session rows retain the old values. The `handleBridgeRun.ts` path in the Node server reads `sessionRow.model` and `sessionRow.provider` and passes them into the Agent Bridge. If those rows point to a model that is not available on the local provider (or a provider whose base_url has changed), the bridge queries `http://localhost:11434` for a non-local model and receives HTTP 404 after retries.

This is **not** a config-file bug. `~/.hermes/config.yaml`, `~/.hermes/auth.json`, `.env`, and `models_cache.json` can all be correct and the chat still silently fails because of session-level overrides in the DB.

## Reproduction
1. Start Web UI with `provider: ollama-cloud`, `model: cogito-2.1:671b` in config.
2. Create a chat session in the UI.
3. Stop server, change config to `provider: ollama-launch`, `model: kimi-k2.6:cloud`.
4. Restart server.
5. Reopen the same chat session in the browser.
6. Send a message → no response. Agent Bridge logs show retries against `http://localhost:11434/v1/chat/completions` → 404.

## Verification

Inspect the DB directly:

```bash
sqlite3 /home/thadd/packages/server/data/hermes-web-ui.db \
  "SELECT id, provider, model, title FROM sessions WHERE provider <> 'ollama-launch' OR model NOT LIKE '%cloud';"
```

Or Python:

```python
import sqlite3
conn = sqlite3.connect('/home/thadd/packages/server/data/hermes-web-ui.db')
c = conn.cursor()
c.execute("SELECT id, provider, model FROM sessions")
for row in c.fetchall():
    print(row)
```

## Fix Options

**Option A: Update all stale rows (preferred for preserving history)**

```sql
UPDATE sessions SET model = 'kimi-k2.6:cloud', provider = 'ollama-launch';
```

If you need to be more selective:

```sql
UPDATE sessions SET model = 'kimi-k2.6:cloud', provider = 'ollama-launch'
WHERE provider = 'ollama-cloud';
```

**Option B: Delete stale sessions (nuclear, loses chat history)**

```sql
DELETE FROM sessions WHERE provider <> 'ollama-launch' OR model NOT LIKE '%cloud';
```

**Option C: Ensure `models_cache.json` and session are aligned after any model/provider change**

```bash
# Update models_cache.json
jq '.active_provider = "ollama-launch" | .default_model = "kimi-k2.6:cloud"' \
  /home/thadd/.hermes/webui/models_cache.json > /tmp/models_cache.json && \
  mv /tmp/models_cache.json /home/thadd/.hermes/webui/models_cache.json

# Then update DB
sqlite3 /home/thadd/packages/server/data/hermes-web-ui.db \
  "UPDATE sessions SET model = 'kimi-k2.6:cloud', provider = 'ollama-launch';"
```

> Always restart the Node server after DB changes, because the server may cache session data in memory.

## Prevention

After any change to `~/.hermes/config.yaml` that touches `default_model` or `provider`, run a DB hygiene pass:

```bash
#!/bin/bash
# scripts/webui-fix-stale-sessions.sh
DB=$HOME/packages/server/data/hermes-web-ui.db
NEW_MODEL="kimi-k2.6:cloud"
NEW_PROVIDER="ollama-launch"

sqlite3 "$DB" "UPDATE sessions SET model = '$NEW_MODEL', provider = '$NEW_PROVIDER';"
echo "Fixed $(sqlite3 \"$DB\" \"SELECT changes();\") session(s)."
```

## Key Insight

The EKKOLearnAI Web UI does **not** automatically synchronize `model`/`provider` in existing session rows when the Hermes global config changes. The Web UI's `services/hermes/run-chat/handle-bridge-run.ts` treats the session row as the single source of truth for that conversation. Global config only affects *new* sessions unless you manually align the DB.
