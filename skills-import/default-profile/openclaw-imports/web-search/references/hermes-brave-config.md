# Hermes Web Search — Setup & Pitfalls

## Hermes vs OpenClaw

Hermes and OpenClaw both support Brave Search, but config paths differ:

| Platform | Config file | Key path |
|----------|-------------|----------|
| Hermes | `~/.hermes/config.yaml` | `web.brave_api_key` (YAML top-level) |
| OpenClaw | `openclaw.json` | `plugins.entries.brave.config.webSearch.apiKey` (JSON nested) |

Do **not** copy OpenClaw config examples into a Hermes `config.yaml` — they use different schemas.

## Hermes Config Snippet

```yaml
web:
  backend: firecrawl
  search_backend: brave          # NOT 'brave-free'
  brave_api_key: BSA-XXXXXXXXXXXXXXXXXXXXXXXXX
  extract_backend: ''
  use_gateway: false
```

After editing, restart the Gateway:
```bash
hermes gateway restart
```

## Pitfall: `brave-free` backend

Hermes defaults to `search_backend: brave-free` if Brave Search is selected but no key is provided. The free tier has a hard monthly cap ($0.01/month) and burns out immediately with any real usage. Switch to `search_backend: brave` with a paid API key.

## DuckDuckGo Scripts: Hermes Venv Required

DuckDuckGo fallback scripts need the `ddgs` Python package installed in **Hermes' own venv**, not system Python.

**Hermes venv location** (discovered May 2026):
```
/home/thadd/.hermes/hermes-agent/venv/
```

If `pip` is missing system-wide, use the venv directly:
```bash
/home/thadd/.hermes/hermes-agent/venv/bin/pip install ddgs
# Run scripts with venv python:
/home/thadd/.hermes/hermes-agent/venv/bin/python scripts/search.py "query"
```

### Package migration: `duckduckgo_search` → `ddgs`

The `duckduckgo-search` PyPI package has been renamed to `ddgs`. Legacy scripts that import `from duckduckgo_search import DDGS` or use `keywords=...` as the parameter will fail.

**Required changes:**
- Import: `from ddgs import DDGS` (was `from duckduckgo_search import DDGS`)
- Parameters: `query=query` (was `keywords=query`)
- Install: `pip install ddgs` (was `pip install duckduckgo-search`)

**Script patch example:**
```python
# Before (legacy)
from duckduckgo_search import DDGS
results = list(ddgs.text(keywords=query, ...))

# After (current)
from ddgs import DDGS
results = list(ddgs.text(query=query, ...))
```

## Restart after config changes

```bash
hermes gateway restart
```

The gateway must restart for web backend changes (including API key updates) to take effect.

## API Quota Exhaustion

Brave Search free tier (`USAGE_LIMIT_EXCEEDED`) returns HTTP 402. If you hit this:
1. Wait for monthly reset (~12 days from mid-month if burned), **or**
2. Upgrade to the Search plan at https://brave.com/search/api/ ($5/mo ≈ 1,000 queries).

Note: The user's existing `BSA-` key had a $0.01/mo cap that was exhausted immediately upon first use.

## Environment detection

Hermes is running in WSL (`~/.hermes/hermes-agent/venv/` exists). This does not change config layout — WSL is just Linux. The same YAML structure applies.
