# ddgs Migration Guide (duckduckgo_search → ddgs)

**Package rename:** `duckduckgo_search` → `ddgs` (as of v9+, 2025+)

## What Changed

| Old | New |
|-----|-----|
| `pip install duckduckgo-search` | `pip install ddgs` |
| `from duckduckgo_search import DDGS` | `from ddgs import DDGS` |
| `DDGS.text(keywords=query, ...)` | `DDGS.text(query=query, ...)` |
| `DDGS.images(keywords=query, ...)` | `DDGS.images(query=query, ...)` |
| `DDGS.news(keywords=query, ...)` | `DDGS.news(query=query, ...)` |
| `DDGS.videos(keywords=query, ...)` | `DDGS.videos(query=query, ...)` |

## Common Failure

```
TypeError: DDGS.images() missing 1 required positional argument: 'query'
```

**Cause:** Old script still passing `keywords=` parameter.

**Fix:** Change `keywords=query` to `query=query` in all four search methods.

## Install Path (Hermes/WSL)

System `pip` is often missing. Target Hermes' venv directly:

```bash
# Uninstall old, install new
/home/thadd/.hermes/hermes-agent/venv/bin/pip uninstall -y duckduckgo-search
/home/thadd/.hermes/hermes-agent/venv/bin/pip install ddgs
```

## Script Migration Checklist

1. Replace import: `from duckduckgo_search import DDGS` → `from ddgs import DDGS`
2. Replace parameter in `.text()`: `keywords=query` → `query=query`
3. Replace parameter in `.images()`: `keywords=query` → `query=query`
4. Replace parameter in `.news()`: `keywords=query` → `query=query`
5. Replace parameter in `.videos()`: `keywords=query` → `query=query`
6. Test with a simple query: `ddgs.text(query="test", max_results=3)`

## Notes

- The old package still exists on PyPI but raises `RuntimeWarning: This package has been renamed to ddgs!`
- Rate limiting (403) is a separate issue from the package rename — DuckDuckGo aggressively rate-limits unauthenticated requests regardless of package version.
- The new `ddgs` package includes `fake-useragent` for better request masking.
