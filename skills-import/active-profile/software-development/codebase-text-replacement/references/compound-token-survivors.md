# Compound-Token Survivor Checklist

After a bulk word-boundary replacement (`\bOldName\b` → `NewName`), these forms are the most common survivors that still contain the old term:

## Patterns to grep for post-replacement

| Pattern | Example survivor | Risk level | Action |
|---|---|---|---|
| camelCase / PascalCase merge | `openOldNameDialog` | Usually intentional boundary | Verify with user if identifiers should change |
| kebab-case (CSS, filenames, config) | `old-name`, `old-name-btn` | High | Likely should be renamed |
| snake_case (env vars, keys, Python) | `OLD_NAME`, `old_name_key` | High | Likely should be renamed |
| CSS class prefix | `.oldname-` | High | Rename to avoid stale styling |
| data-attribute keys | `data-oldname-*` | High | Rename or i18n desync |
| HTTP header names | `X-OldName-Token` | Critical | Must match backend rename |
| URL paths / API segments | `/oldname/v1/` | Critical | Must match backend rename |
| Docker volume / service names | `oldname_data` | Medium | Verify compose/network still valid |
| LocalStorage keys | `oldname-theme` | High | Breaking change for returning users |
| Query-parameter keys | `?oldname=true` | High | Must match backend parsing |

## Quick grep commands

```bash
# snake_case
rg -i 'old_name|oldname_' /path/to/project

# kebab-case
rg -i 'old-name|oldname-' /path/to/project

# camelCase merge (harder; look for lowercase-oldname-uppercase transitions)
rg -i 'oldname[A-Z]' /path/to/project

# data attributes / headers / localStorage
rg -i 'data-oldname|x-oldname|localStorage.*oldname' /path/to/project
```

## Decision tree

- **UI-visible label** → Rename.
- **Internal code identifier used in one file only** → Rename if low risk.
- **Cross-file API contract (header, URL, event name, LS key)** → Rename **only** if both sides updated.
- **User-facing persisted key (localStorage, query param, cookie)** → Keep old key OR add migration shim to avoid data loss.