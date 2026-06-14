# Web Dashboard Build Reference

Session record: building the Hermes web dashboard from source.

## Tech Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Frontend framework | React 19 | Beta/rc at time of install |
| Build tool | Vite 6 | Very fast, supports React 19 |
| CSS framework | Tailwind CSS v4 | Beta; uses `@import "tailwindcss"` instead of directives |
| UI components | shadcn/ui-inspired | Custom components in `web/src/components/ui/` |
| State management | React hooks + local state | No external state library needed |
| Backend API | FastAPI | Serves static files + JSON API routes |

## Build Output

After `npm run build`:
- `hermes_cli/web_dist/` — total ~1.6 MB
  - JS bundles: ~1.5 MB (minified + gzipped)
  - CSS: ~97 KB
  - `index.html`: entry point

## Key Build Commands

```bash
# Install (legacy peer deps needed for React 19 compat)
npm install --legacy-peer-deps

# Dev server (if available)
npm run dev

# Production build
npm run build
# Output: hermes_cli/web_dist/
```

## Installation Pitfall

When installing from a local clone into a venv alongside an existing Hermes install, `hermes --version` may still report the old PyPI path. Fix by explicitly targeting the venv Python:

```bash
uv pip install -e . --python /path/to/venv/bin/python
# Verify: hermes --version should show the local clone path
```

## Backend Startup

```bash
# Minimal start (no browser open, use existing build)
hermes dashboard --no-open --skip-build

# Custom port/host
hermes dashboard --port 9119 --host 127.0.0.1
```

## API Authentication

The config and health endpoints require a session token. After loading the dashboard in a browser, extract the token from dev tools (Application → Cookies or localStorage), then pass it as `Authorization: Bearer <token>`.

## Windows/WSL Notes

- Build runs fine in WSL Ubuntu.
- `nohup` for backgrounding works in WSL bash.
- For auto-start on WSL boot, consider a cron job or Windows Task Scheduler calling `wsl -d Ubuntu -e bash -lc "hermes dashboard --no-open --skip-build"`.