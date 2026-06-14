# CSS Variables Theme Toggle Pattern

A minimal, no-build-step dark/light mode toggle using CSS custom properties.

## When to use
- Single-file HTML dashboards
- Any project where adding a build step is undesirable
- When you want instant theme switching without FOUC

## The Pattern

### 1. Define CSS variables for both themes

```css
:root {
    /* Dark (default) */
    --bg-body: #0f1419;
    --bg-header: #111b26;
    --text-primary: #e0e6ed;
    --text-muted: #6b7280;
    --border-color: #2a3441;
    --color-pos: #10b981;
    --color-neg: #ef4444;
}

[data-theme="light"] {
    --bg-body: #f8fafc;
    --bg-header: #ffffff;
    --text-primary: #1e293b;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    --color-pos: #059669;
    --color-neg: #dc2626;
}
```

### 2. Use variables everywhere — never hardcode colors

```css
body {
    background: var(--bg-body);
    color: var(--text-primary);
}
.header {
    background: var(--bg-header);
    border-bottom: 1px solid var(--border-color);
}
.pos { color: var(--color-pos); }
.neg { color: var(--color-neg); }
```

### 3. Toggle button in HTML

```html
<button id="themeToggleBtn" title="Toggle light/dark mode">🌙</button>
```

### 4. JavaScript for switching and persistence

```javascript
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('theme', next);
    document.getElementById('themeToggleBtn').textContent = next === 'dark' ? '🌙' : '☀️';
}

// Init on page load
(function initTheme() {
    const saved = localStorage.getItem('theme');
    const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    const theme = saved || (prefersLight ? 'light' : 'dark');
    applyTheme(theme);
    document.getElementById('themeToggleBtn').textContent = theme === 'dark' ? '🌙' : '☀️';
})();

document.getElementById('themeToggleBtn').addEventListener('click', toggleTheme);
```

## Key decisions

- **`data-theme` on `<html>`** — not `<body>`, so `:root` selector in CSS picks it up.
- **Variable naming convention** — prefix by semantic role (`bg-*`, `text-*`, `border-*`, `color-*`) not by color name. This makes light theme mapping obvious.
- **Respect `prefers-color-scheme`** on first visit, then let user override.
- **No class toggling on every element** — a single attribute on `<html>` drives the entire page.

## Quick migration from hardcoded colors

1. Copy all hardcoded colors from existing CSS into `:root` variables (keep dark values).
2. Replace every `color: #hex;` with `color: var(--name);`.
3. Add `[data-theme="light"]` block with light equivalents.
4. Insert the 4 lines of JS above.
5. Done — instant toggle, no build step.
