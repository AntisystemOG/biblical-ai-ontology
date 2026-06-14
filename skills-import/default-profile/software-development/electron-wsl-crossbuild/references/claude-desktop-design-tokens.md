# Extracting Design Tokens from a Real Electron Desktop App

## Target: Claude Desktop (MSIX Package)

Real app location: `C:\Program Files\WindowsApps\Claude_1.8089.1.0_x64__pzs8sxrjxfjjc`
Tech stack: Electron 41.6.1, Vite, React 18.3.1, Tailwind CSS 3.4.19

## Step 1: Locate and Copy app.asar

```powershell
Get-ChildItem "C:\Program Files\WindowsApps" -Filter "*Claude*" -Directory
```

Copy `app.asar` to a working directory. You only need read access to the MSIX folder.

## Step 2: Extract

```bash
npm install -g asar
asar extract app.asar ./claude-src/
```

## Step 3: Read the CSS Bundle

The production CSS is in `claude-src/dist/assets/index-*.css` (minified but searchable). Key files:

- `window-shared.css` — CSS custom properties (design tokens)
- `tailwind.config.js` (if present in source) — extended theme
- `package.json` — exact versions of dependencies

## Extracted Tokens (Claude Desktop)

### Colors
| Token | Value | Tailwind Name |
|-------|-------|---------------|
| Background (dark) | `#1a1914` | — |
| Surface | `#12120f` | — |
| Text primary | `#f5f4ef` | `text-100` |
| Text secondary | `#b8b4a8` | `text-200` |
| Border | `#6c6a6040` | `border-400` |
| Accent (clay) | `#d97757` | `clay-100` |
| Accent hover | `#c26a4d` | `clay-200` |
| Paper-50 | `#f5f4ef` | `paper-50` |
| Paper-100 | `#e8e6df` | `paper-100` |
| Paper-200 | `#d1cfc7` | `paper-200` |
| Ink-50 | `#8a8780` | `ink-50` |
| Ink-100 | `#6c6a60` | `ink-100` |
| Ink-200 | `#4f4d45` | `ink-200` |

### CSS Custom Properties
```css
:root {
  --claude-background-color: #1a1914;
  --claude-surface: #12120f;
  --claude-border: #6c6a6040;
  --claude-text-100: #f5f4ef;
  --claude-text-200: #b8b4a8;
  --claude-accent-clay: #d97757;
  --claude-accent-clay-hover: #c26a4d;
}
```

### Layout Values
| Element | Value |
|---------|-------|
| Sidebar width | `260px` |
| Top bar height | `48px` |
| Composer min-height | `64px` |
| Border radius (cards) | `12px` |
| Border radius (buttons) | `8px` |
| Font stack | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` |

### Typography Scale
| Token | Size | Weight |
|-------|------|--------|
| `text-xs` | `0.75rem` | 400 |
| `text-sm` | `0.875rem` | 400 |
| `text-base` | `1rem` | 400 |
| `text-lg` | `1.125rem` | 500 |
| `text-xl` | `1.25rem` | 600 |

## Step 4: Apply in Your Clone

1. Copy the Tailwind config theme extensions
2. Set the CSS custom properties in your `global.css`
3. Import pre-built Tailwind (see `electron-tailwind-vite-workaround.md`)
4. Match spacing values (padding, margins, gaps) from the original

## Cleanup

```bash
rm -rf ./claude-src/
```

Never modify the original `C:\Program Files\WindowsApps` directory.
