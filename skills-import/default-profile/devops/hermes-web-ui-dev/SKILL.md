---
name: hermes-web-ui-dev
description: |
  Modify, theme, or rebrand the EKKOLearnAI Hermes Web UI (Vue 3 + Vite + Naive UI + SCSS).
  Covers logo/assets, sidebar styling, theme variables, component overrides.
  
  When Thad says "web ui" or "webui", he ALWAYS refers to the EKKOLearnAI/hermes-web-ui
  repository at `/mnt/c/Users/thadd/hermes-web-ui`. Default to that repo for all
  queries unless a different repo is explicitly named.
---

# Hermes Web UI Development

## Architecture

- **Framework:** Vue 3 + TypeScript + Vite
- **UI Library:** Naive UI (`n-` prefix components)
- **State:** Pinia stores under `src/stores/hermes/`
- **Styling:** SCSS with CSS custom properties; dark mode via `.dark` class
- **Entry:** `packages/client/index.html` → `src/main.ts` → `src/App.vue`
- **CWD for commands:** `/home/thadd/hermes-web-ui-ekko`
- **Public assets:** `packages/client/public/` (served at root `/`)
- **Bunded assets:** `packages/client/src/assets/`

## Project Structure

```
packages/client/
├── index.html                    # HTML entry
├── public/
│   └── logo.png                  # Logo served at /logo.png (used by sidebar, login, empty states)
├── src/
│   ├── App.vue                   # Top-level layout; mobile drawer toggle
│   ├── main.ts                   # App bootstrap
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppSidebar.vue    # Collapsible sidebar (nav groups, footer, selectors)
│   │   │   ├── ModelSelector.vue
│   │   │   ├── ProfileSelector.vue
│   │   │   ├── LanguageSwitch.vue
│   │   │   └── ThemeSwitch.vue
│   │   └── hermes/
│   │       ├── chat/
│   │       │   ├── MessageItem.vue           # Assistant avatar uses /logo.png
│   │       │   ├── MessageList.vue           # Empty state logo
│   │       │   └── HistoryMessageList.vue
│   │       └── group-chat/
│   │           └── GroupMessageList.vue       # Empty state logo
│   ├── views/
│   │   ├── LoginView.vue                      # Logo at 80×80
│   │   └── hermes/
│   │       ├── ChatView.vue
│   │       └── ... (all other page views)
│   ├── stores/hermes/app.ts      # sidebarOpen, sidebarCollapsed, connected, serverVersion
│   └── styles/
│       ├── variables.scss        # $sidebar-width, $bg-sidebar, $border-color, $text-primary, etc.
│       └── theme.ts              # CSS custom property mapping
```

## Key File Locations

| Element | File | Reference |
|---------|------|-----------|
| App logo (sidebar top-left) | `AppSidebar.vue` line ~21 | `const logoPath = '/logo.png'` |
| Login logo | `LoginView.vue` line ~114 | `<img src="/logo.png" width="80" height="80">` |
| Mobile drawer toggle logo | `App.vue` line ~65 | `<img src="/logo.png" style="width: 24px; height: 24px">` |
| Assistant chat avatar | `MessageItem.vue` line ~778 | `src="/logo.png"` |
| Chat empty state logo | `MessageList.vue` line ~164 | `<img src="/logo.png" class="empty-logo">` |
| Group chat empty logo | `GroupMessageList.vue` line ~43 | `<img src="/logo.png" class="empty-logo">` |

**All point to the same asset:** `/logo.png` served from `packages/client/public/logo.png`.

## Replacing the Logo

1. **Prepare your image** — any PNG/JPG/SVG (SVG works if the browser supports it).
2. **Copy to both locations** (public + assets):
   ```bash
   cp /path/to/your-logo.png packages/client/public/logo.png
   cp /path/to/your-logo.png packages/client/src/assets/logo.png
   ```
3. **Rebuild** (see Deploy flow for your setup).

## Sidebar Customisation

`AppSidebar.vue` is the single file for:
- Collapsible nav groups (Conversation, Agent, Monitoring, System)
- Footer (logout, connection status, version, update button)
- Selectors (model, profile)

**Logo styling** — `logo-img` class:
- `width: 28px; height: 28px; border-radius: 0;`
- Adjacent `.logo-text` = "Hermes" (18px, weight 600, letter-spacing 0.5px)

## Theme Variables (SCSS)

Found in `src/styles/variables.scss`:
- `$sidebar-width` — sidebar width (default ~220–260px)
- `$bg-sidebar` — sidebar background
- `$bg-card` — card surfaces
- `$border-color` — dividers
- `$text-primary`, `$text-secondary`, `$text-muted` — text hierarchy
- `$accent-primary` — brand accent (used for active nav items)

Dark mode is toggled via the `.dark` class on a parent element. SCSS rules use `.dark & { ... }` for overrides.

## Common Tasks

### Change sidebar brand text
Edit `logo-text` in `AppSidebar.vue` template (line ~73):
```html
<span class="logo-text">Your Brand</span>
```

### Override sidebar width
In `src/styles/variables.scss`:
```scss
$sidebar-width: 240px;
```

### Override active item colour
In `src/styles/variables.scss` or scoped style block:
```scss
$accent-primary: #00aaff;
```

## Deploy / Build

Typical workflows (confirm which this project uses):

| Method | Command | Notes |
|--------|---------|-------|
| Vite dev | `npm run dev` | Hot reload, port proxy |
| Vite build | `npm run build` | Outputs to `dist/` |
| Docker | `docker compose up` | See `docker-compose.yml` |
| pm2 | `pm2 start ecosystem.config.js` | If Node server exists |
| Desktop launcher | `Start Hermes WebUI.bat` | Windows shortcut → runs `node dist/server/index.js` |

**Critical distinction:** If the user runs from a pre-built `dist/` — e.g., a Windows `.bat` launcher that calls `node dist/server/index.js` — then changes to `packages/client/public/` **do NOT take effect** until a rebuild. The server serves the stale `dist/` assets.

**Quick-swap workflow for testing without rebuilding:**
```bash
# The live assets are in dist/client/, not packages/client/public/
cp /path/to/new-logo.png dist/client/logo.png
# Then restart the server process
```
Then `Ctrl+F5` in the browser to bust cache.

**Permanent change (required for next build):**
```bash
cp /path/to/new-logo.png packages/client/public/logo.png
cp /path/to/new-logo.png packages/client/src/assets/logo.png
npm run build
```

For WSL desktop-launcher specifics, see `references/hermes-webui-desktop-launcher.md`.

After any logo/asset or `.vue` change, **rebuild** is required for production. Dev server (`npm run dev`) hot-reloads automatically.

## Thinking / Typing Indicator (Streaming Animation)

When the AI is generating a response, the UI shows an animated indicator above the message list instead of the static logo. This is **not an image — it is a looping `<video>` element**.

### Source Assets

| Variant | File | Imported As |
|---------|------|-------------|
| Light mode | `packages/client/src/assets/thinking-light.mp4` | `thinkingVideoLight` |
| Dark mode | `packages/client/src/assets/thinking-dark.mp4` | `thinkingVideoDark` |

Both are imported in `MessageList.vue` (lines 6-7) and rendered as `<video autoplay loop muted playsinline>` when `chatStore.isRunActive` or `chatStore.abortState` is true.

### Replacing the Thinking Animation

**Option A — Swap MP4 files (fastest, best quality):**
```bash
# Replace dark/light variants, keep filenames
cp /path/to/new-thinking-light.mp4 packages/client/src/assets/thinking-light.mp4
cp /path/to/new-thinking-dark.mp4  packages/client/src/assets/thinking-dark.mp4
# Rebuild (or dev server hot-reloads automatically)
```

Keep both variants, or point both imports to the same file if you only have one MP4.

**Reproducible pattern (survives upstream updates):**
Store the canonical replacement video in a persistent location (e.g. `~/.hermes/images/`), then run the re-apply script after any WebUI update:

```bash
# One-time: create re-apply script
cat > /path/to/workspace/scripts/apply-webui-customizations.sh << 'SCRIPT'
#!/bin/bash
WEBUI_DIR="/home/thadd/hermes-web-ui-ekko"
IMAGES_DIR="/mnt/c/Users/thadd/.hermes/images"
cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-light.mp4"
cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-dark.mp4"
cd "$WEBUI_DIR" && /home/thadd/node26/bin/npm run build 2>&1 | tail -5
SCRIPT
chmod +x /path/to/workspace/scripts/apply-webui-customizations.sh
```

Run this script every time the WebUI is updated/rebuilt from upstream.

**Build output note:** Vite copies the video to `dist/client/assets/mp4/` with a content hash (e.g. `thinking-light-B_T3hcgV.mp4`). Only a rebuild updates this hashed file; copying to `src/assets/` alone does not change the live app if the server is running from `dist/`.

**Option B — Switch to GIF (requires component edit):**
Change the `<video>` tag to `<img>` in `MessageList.vue` and point GIF assets instead. GIFs are larger and limited to 256 colors — MP4 is preferred for quality.

**Option C — Replace with CSS-only animation:**
Remove the `<video>` element and its imports, and add a CSS keyframes animation (e.g., pulsing badge, dot wave) in the same scoped style block.

## Pitfalls

- Changing only `public/logo.png` but not `src/assets/logo.png` — the asset import path may fall back to the old one during bundling.
- SVG logos: `public/logo.png` can be an SVG if you also update all hardcoded `src="/logo.png"` references — some components expect `.png`. Safer to keep a `.png` in public and an `.svg` in assets if both are needed.
- **Thinking indicator is a video, not an image** — do not try to replace it with a `.png` or `.jpg` without also changing the `<video>` tag to `<img>`.
- Forgetting to rebuild: Vite static assets are embedded at build time.
- SCSS variables must be imported with `@use "@/styles/variables" as *;` in each `<style scoped lang="scss">` block.
- `naive-ui` components use their own theme tokens; override via `n-config-provider` or CSS vars, not just SCSS.
