# Spock Protector — 3-Layer Branding Defense

Session: 2026-05-22  Thad: "lock the customizations from being changed. make a rule to read any update and block changes I've made"

## Problem

Hermes WebUI auto-updates via npm install a fresh vanilla copy at
`~/.hermes/node/lib/node_modules/hermes-web-ui/`. This destroys Spock branding
(title, logo, thinking avatar, sidebar text) and may cause the wrong server
to run on port 8648.

## Solution: 3-Layer Guardian System

All layers guard commit `f636b1b` — "feat: rebrand to Spock".

### Layer 1 — Git Hooks (Immediate)

Files: `.git/hooks/post-merge`, `.git/hooks/post-checkout`, `.git/hooks/post-rewrite`

```bash
#!/bin/bash
SPOCK_COMMIT="f636b1b"
PROTECTED_FILES=(
  "packages/client/index.html"
  "packages/client/public/logo.png"
  "packages/client/src/assets/logo.png"
  "packages/client/src/assets/thinking-dark.mp4"
  "packages/client/src/assets/thinking-light.mp4"
  "packages/client/src/components/layout/AppSidebar.vue"
  "vite.config.website.ts"
)

cd "$(git rev-parse --show-toplevel)" || exit 1
for FILE in "${PROTECTED_FILES[@]}"; do
  if ! git diff --quiet "$SPOCK_COMMIT" -- "$FILE" 2>/dev/null; then
    git checkout "$SPOCK_COMMIT" -- "$FILE"
    echo "[Spock Guardian] RESTORED: $FILE"
  fi
done
```

Install all three hooks with `chmod +x`.

### Layer 2 — Cron Watchdog (Persistent)

Cron job `88a43850fcff` (spock-guardian-watchdog) runs every 5 min silently.
Only outputs when a file was tampered with and restored.

Script: `/home/thadd/.hermes/scripts/spock-protector/guard.sh`

```bash
#!/bin/bash
REPO="/mnt/c/Users/thadd/hermes-web-ui"
SPOCK_COMMIT="f636b1b"
FILES=(
  "packages/client/index.html"
  "packages/client/public/logo.png"
  "packages/client/src/assets/logo.png"
  "packages/client/src/assets/thinking-dark.mp4"
  "packages/client/src/assets/thinking-light.mp4"
  "packages/client/src/components/layout/AppSidebar.vue"
  "vite.config.website.ts"
)

cd "$REPO" || exit 1
RESTORED=0
for FILE in "${FILES[@]}"; do
  if ! git diff --quiet "$SPOCK_COMMIT" -- "$FILE" 2>/dev/null; then
    git checkout "$SPOCK_COMMIT" -- "$FILE"
    RESTORED=1
  fi
done
[ "$RESTORED" -eq 1 ] && echo "[$(date)] Spock Guardian: Customizations restored."
```

Created via `hermes cron create` with `no_agent: true`, `script: spock-protector/guard.sh`.

### Layer 3 — Hard Restore Script (Emergency)

Path: `/home/thadd/.hermes/spock-protector/restore-spock.sh`

- Restores from immutable backup copies (not git — works even if repo is corrupted)
- Accepts `--build` to auto-rebuild dist after restore
- Also does `git checkout f636b1b -- <file>` for clean git state

```bash
/home/thadd/.hermes/spock-protector/restore-spock.sh --build
```

Backups live at `/home/thadd/.hermes/spock-protector/` mirroring the repo paths.

### Update Reject Script

Path: `/home/thadd/.hermes/scripts/spock-protector/update-reject.sh`

Blocks automatic npm updates unless `--force` is passed. Prints instructions for
the safe update workflow: fetch + merge + restore script + rebuild.

## Safe Update Workflow

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
git fetch origin
git merge origin/main
/home/thadd/.hermes/spock-protector/restore-spock.sh --build
```

This pulls upstream changes, then re-applies Spock branding on top.

## Verification

```bash
cd /mnt/c/Users/thadd/hermes-web-ui
echo "=== Spock Branding Check ==="
grep -o "title>.*</title" packages/client/index.html | head -1
grep -o 'alt="[^"]*"' packages/client/src/components/layout/AppSidebar.vue | head -2
grep -o 'logo-text>[^&]*' packages/client/src/components/layout/AppSidebar.vue | head -1
ls -lh packages/client/public/logo.png packages/client/src/assets/thinking-light.mp4
```

Expected: title=Spock, alt=Spock, logo-text=Spock, logo ~710KB, video ~49KB.
