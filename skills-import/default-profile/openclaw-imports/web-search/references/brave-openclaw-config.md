# Brave Search in OpenClaw — Config Reference

## Full Plugin Config

Place under `plugins.entries.brave.config.webSearch` inside `openclaw.json`.

```json
{
  "plugins": {
    "entries": {
      "brave": {
        "config": {
          "webSearch": {
            "apiKey": "BSA-XXXXXXXXXXXXXXXXXXXXXXXXX",
            "mode": "web",
            "baseUrl": "https://api.search.brave.com"
          }
        }
      }
    }
  },
  "tools": {
    "web": {
      "fetch": {
        "enabled": true
      },
      "search": {
        "enabled": true,
        "provider": "brave",
        "maxResults": 5,
        "timeoutSeconds": 30
      }
    }
  }
}
```

## Key rotation checklist

1. `cp openclaw.json openclaw.json.bak`   (always backup first)
2. Update `plugins.entries.brave.config.webSearch.apiKey`
3. Set `tools.web.search.provider` = `"brave"` (or verify it is already)
4. Save
5. `openclaw gateway restart`
6. Verify with a `web_search` call

## Legacy vs current config paths

| Era | Path | Status |
| --- | --- | --- |
| Current | `plugins.entries.brave.config.webSearch.apiKey` | Canonical |
| Legacy | `tools.web.search.apiKey` | Compatibility shim only |

## `webSearch.mode` values

- `"web"` (default): normal results with titles, URLs, snippets.
- `"llm-context"`: pre-extracted text chunks and sources for grounding.
  - Does NOT support `ui_lang`.
  - Requires both `date_after` and `date_before` if using date ranges.
  - Included in Brave Search plan.

## Cost & Rate Limits

- Brave Search plan: ~$5 per 1,000 requests.
- $5/mo free credit renews monthly (covers ~1,000 queries).
- Set usage limit in Brave dashboard to avoid surprise charges.
- Results cached 15 minutes by default (configurable via `cacheTtlMinutes`).