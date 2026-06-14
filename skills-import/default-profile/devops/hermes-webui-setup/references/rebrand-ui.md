# Re-branding Reference: User-Facing vs Internal "Hermes" Strings

## Overview

When replacing "Hermes" branding with a custom name (e.g., "Spock") in the **compiled** Web UI, the `dist/client/assets/js/index-*.js` file contains approximately **~170 total occurrences** of the string `Hermes`. Most of these are internal identifiers and must be preserved.

## Rule of Thumb

> **Replace ONLY user-facing text in JSON string values.** Leave all camelCase identifiers, API routes, variable names, CLI references, and configuration strings untouched.

## Strings That ARE Safe to Replace (User-Facing)

The following are the ~21 user-facing strings typically found in a single compiled JS file:

| Pattern | Replacement | Context |
|---------|-------------|---------|
| `title:"Hermes Web UI"` | `title:"Spock Web UI"` | Login screen title (present in ~8 language variants) |
| `emptyState:"Start a conversation with Hermes Agent"` | `emptyState:"Start a conversation with Spock"` | Empty chat state (present in ~9 language variants) |
| `alt:"Hermes",class:"empty-logo"` | `alt:"Spock",class:"empty-logo"` | Logo alt text in sidebar |

**Language variants found** (do not rely on these being exhaustive — run a grep to confirm):
- English: `emptyState:"Start a conversation with Hermes Agent"`
- German: `emptyState:"Starte eine Konversation mit dem Hermes-Agenten"`
- French: `emptyState:"Commencez une conversation avec l'agent Hermès"` — note accent on `è`
- Spanish: `emptyState:"Inicia una conversación con el agente Hermes"`
- Portuguese: `emptyState:"Comece uma conversa com o agente Hermes"`
- Korean: `emptyState:"Hermes 에이전트와 대화 시작"`
- Japanese: `emptyState:"Hermes エージェントとの会話を開始"`
- Other CJK variants may exist for Chinese.

## Strings That MUST Be Left Alone (Internal)

The remaining ~150+ occurrences describe internal architecture and integrations. Replacing these causes confusion or breakage:

| Example | Why Keep It |
|---------|-------------|
| `hermesBridge`, `hermesBridgeSocketPath` | Code identifiers; server-side socket path |
| `Search scope: Web UI local session database only. Read-only Hermes history sessions are not included` | Feature description referencing actual system name |
| `Read-only inventory of discoverable Hermes plugin manifests` | Plugin system is called "Hermes Plugins" |
| `Enable Copilot in Hermes` | Integration instructions for Copilot in Hermes ecosystem |
| `Hermes CLI provider/model config is not rewritten` | Accurate documentation of separation between Web UI and CLI |
| `Track skill loads and edits from Hermes sessions` | Analytics refers to actual session source |
| `Fix Hermes markdown media rendering` | Refers to a specific component |
| `model.provider`, `ollama-cloud` provider strings | Configuration schema identifiers |
| `hermes_bridge.py` | Agent bridge script filename |

## Practical Grep Check

Before declaring the re-brand complete, run:

```bash
cd ~/hermes-web-ui-ekko
grep -n 'Hermes' dist/client/assets/js/index-*.js | grep -E 'title:|emptyState:|alt:'
# Confirm all user-facing strings are replaced.

grep -n 'Hermes' dist/client/assets/js/index-*.js | grep -vE 'title:|emptyState:|alt:' | wc -l
# Expect ~150+ remaining. This is correct.
```

## Browser Cache Pitfall

The compiled JS files are served with standard HTTP caching headers. After modifying `dist/client/`, the browser may continue showing the old version:

- **Fix:** `Ctrl + Shift + R` (Chrome, Firefox, Edge) — hard reloads without cache
- **Alternative:** Open an incognito/private window
- **Alternative:** DevTools → Network → "Disable cache" → reload

Simply restarting the Node server is **not sufficient**; the issue is client-side asset caching.

## Logo & Favicon Replacement

Built client directory structure:

```
dist/client/
├── index.html          # <title> tag here
├── logo.png            # Sidebar logo (PNG, ≥256px)
├── favicon.ico         # Favicon (ICO or PNG mask)
└── assets/js/index-*.js # Compiled strings here
```

**Generating assets from SVG:**

```bash
# Requirements: librsvg2-bin (provides rsvg-convert)
rsvg-convert -w 512 -h 512 /tmp/spock-logo.svg -o dist/client/logo.png
rsvg-convert -w 196 -h 196 /tmp/spock-logo.svg -o dist/client/favicon.ico
```

> Note: `favicon.ico` in this project is actually a PNG file despite the `.ico` extension; the server serves it without format negotiation.

## Summary Checklist

- [ ] `index.html` `<title>` updated
- [ ] `logo.png` replaced (restart server to effect)
- [ ] `favicon.ico` replaced
- [ ] `index-*.js` user-facing strings replaced (surgical, regex or sed)
- [ ] Verify zero unintended replacements in JS (spot-check key internal strings)
- [ ] Restart Node server
- [ ] **Hard-refresh browser: `Ctrl + Shift + R`**
- [ ] Verify: tab title, sidebar logo alt, empty-chat message, login title