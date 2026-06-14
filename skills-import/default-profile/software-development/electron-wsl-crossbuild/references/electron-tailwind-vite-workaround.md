# Tailwind CSS Pre-Build for Electron + Vite Production Bundles

## Problem

In an Electron + Vite project with Tailwind CSS v3, the production Vite build produces CSS of only ~0.5 kB containing just the `@tailwind` directives and custom properties, but **none of the utility classes** (e.g., `bg-surface`, `text-paper-50`, `flex`, `items-center`).

This happens because:
1. The CSS file imported by `main.tsx` only has `@tailwind base; @tailwind components; @tailwind utilities;`
2. Vite's PostCSS pipeline doesn't run the Tailwind CLI scan to generate the utility CSS
3. The result is a broken UI — all layout and styling missing

## Root Cause

Vite processes CSS through PostCSS, but the Tailwind PostCSS plugin needs to scan all source files to generate utility classes. In some Electron+Vite configurations, the `content` path in `tailwind.config.js` doesn't resolve correctly during the build, or the PostCSS plugin never gets invoked for production.

## Solution: Pre-Build Tailwind as a Static Asset

### 1. Install Tailwind v3 (not v4)

```bash
npm uninstall tailwindcss
npm install tailwindcss@3.4.19 postcss autoprefixer
```

Tailwind v4 has a different PostCSS integration that breaks in Electron + Vite.

### 2. Configure tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './index.html',
  ],
  theme: {
    extend: {
      colors: {
        surface: '#12120f',
        background: '#1a1914',
        'text-100': '#f5f4ef',
        'text-200': '#b8b4a8',
        clay: {
          100: '#d97757',
          200: '#c26a4d',
          300: '#a85d44',
        },
        paper: {
          50: '#f5f4ef',
          100: '#e8e6df',
          200: '#d1cfc7',
        },
        ink: {
          50: '#8a8780',
          100: '#6c6a60',
          200: '#4f4d45',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

### 3. Configure postcss.config.js

```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 4. Create src/styles/global.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --claude-background-color: #1a1914;
    --claude-surface: #12120f;
    --claude-border: #6c6a6040;
    --claude-text-100: #f5f4ef;
    --claude-text-200: #b8b4a8;
    --claude-accent-clay: #d97757;
    --claude-accent-clay-hover: #c26a4d;
  }
}
```

### 5. Pre-Generate the Full Tailwind CSS Bundle

Run this **before** the Vite build:

```bash
npx tailwindcss -i ./src/styles/global.css -o ./src/styles/tailwind-build.css --minify
```

This produces `tailwind-build.css` containing:
- All Tailwind base styles
- All utility classes used in your source files
- Your custom CSS variables
- Typically 100–300 kB minified

### 6. Update main.tsx to Import the Pre-Built File

```tsx
// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/tailwind-build.css'  // <-- pre-built, NOT global.css

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### 7. Build Vite Production Bundle

```bash
NODE_ENV=production npx vite build --emptyOutDir
```

Verify the CSS output:
```bash
ls -lh dist/assets/index-*.css
# Should be ~100+ kB, not 0.5 kB
```

### 8. Build Electron Main Process

```bash
npx tsc --project tsconfig.electron.json
```

### 9. Package with electron-builder

```bash
npx electron-builder --win dir
```

## Build Script (package.json)

```json
{
  "scripts": {
    "tailwind:build": "tailwindcss -i ./src/styles/global.css -o ./src/styles/tailwind-build.css --minify",
    "build:renderer": "NODE_ENV=production vite build --emptyOutDir",
    "build:electron": "tsc --project tsconfig.electron.json",
    "build:all": "npm run tailwind:build && npm run build:renderer && npm run build:electron && npx electron-builder --win dir"
  }
}
```

## Verification

After the Vite build, check `dist/assets/index-*.css`:
- **Broken:** File size < 1 kB, contains only `@layer base` and `:root` variables
- **Working:** File size > 50 kB, contains `.bg-surface`, `.text-paper-50`, `.flex`, `.items-center`, etc.

## Pitfalls

1. **Importing global.css instead of tailwind-build.css** — Vite processes `global.css` through its own pipeline and skips the Tailwind CLI output.
2. **Forgetting to regenerate after design token changes** — If you update `tailwind.config.js` or add new utility classes in source files, re-run `npm run tailwind:build` before `npm run build:renderer`.
3. **Tailwind v4 in package.json** — Even if `tailwindcss@3` is installed, a transitive dependency or lockfile may resolve v4. Pin explicitly: `"tailwindcss": "3.4.19"`.
4. **Content paths don't match source layout** — If your React files are in `./renderer/src/` instead of `./src/`, update `content` in `tailwind.config.js` accordingly.

## Alternative: Vite Tailwind Plugin

Some projects use `@tailwindcss/vite` plugin. This works for pure Vite projects but has compatibility issues with Electron's dual-process build (renderer + main). The pre-build approach is more reliable for Electron.

## Critical: CSS Custom Property Scope

When reverse-engineering an existing Electron app, the extracted source may use CSS custom properties (`var(--foo)`) extensively. A common failure mode is:

1. You copy the Tailwind directives and base styles into `global.css`
2. You pre-build Tailwind successfully (large CSS output)
3. You import `tailwind-build.css` in `main.tsx`
4. **The UI still looks broken** — elements using `var(--claude-fg)` render with transparent/default colors

### Why It Happens

CSS custom properties (`:root { --x: y }`) are only available if they are in the actual stylesheet that reaches the renderer. Electron's `index.html` often has an **inline `<style>` block** with hardcoded colors that shadows your CSS file. If the inline style doesn't define the same custom properties, all `var(--*)` references in components resolve to nothing.

### The Fix

Define the variables in **both** `global.css` (for the Tailwind build) **and** `index.html` (for the initial paint before CSS loads):

```html
<!-- index.html -->
<style>
  :root {
    --claude-bg: #262624;
    --claude-fg: #f5f4ef;
    --claude-secondary: #a6a39a;
    --claude-accent: #d97757;
    --claude-surface: #262624;
    --claude-surface-hover: #3d3d3b;
    --claude-border: #eaddd81a;
    --claude-border-strong: #6c6a6040;
  }
  html, body, #root {
    background: var(--claude-bg);
    color: var(--claude-fg);
  }
</style>
```

```css
/* global.css (input to Tailwind CLI) */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --claude-bg: #262624;
    --claude-fg: #f5f4ef;
    --claude-secondary: #a6a39a;
    --claude-accent: #d97757;
    --claude-surface: #262624;
    --claude-surface-hover: #3d3d3b;
    --claude-border: #eaddd81a;
    --claude-border-strong: #6c6a6040;
  }
}
```

### Verification

After building, open `dist/index.html` and confirm:
1. The inline `<style>` block in `<head>` defines all CSS custom properties
2. `dist/assets/index-*.css` is >10 KB (not <1 KB)
3. No hardcoded `#0f0f10` or `#ececf1` colors remain in `index.html`

If the CSS output is still <1 KB, Tailwind utilities aren't being generated — see "Pre-Generate the Full Tailwind CSS Bundle" above.
