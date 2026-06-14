# SPOCK PROTECTOR — Support Scripts Reference
# Created: 2026-05-22
# Current baseline commit: 5c0bd0b

## Script Inventory

### 1. guard.sh — Cron Watchdog
**Path:** `~/.hermes/scripts/spock-protector/guard.sh`
**Schedule:** Every 5 minutes via cron job `88a43850fcff`
**What it does:**
- Compares all 10 protected source files against git commit `SPOCK_COMMIT`
- Compares 3 dist pairs (favicon, logo, spock-avatar) against source
- Alerts (but does NOT auto-restore) if systemd service is corrupted
- Logs all actions to `~/.hermes/spock-protector/guard.log`

**Does NOT auto-rebuild dist.** If files are restored, user must run `npm run build` manually.

### 2. pre-update-check.sh — Pre-flight Safety Check
**Path:** `~/.hermes/scripts/spock-protector/pre-update-check.sh`
**Run:** Manually before any `hermes update` or via `spock-update.sh` wrapper
**Checks (7 layers):**
1. Local repo exists at `/mnt/c/Users/thadd/hermes-web-ui`
2. `SPOCK_COMMIT` exists in git
3. All 10 protected source files exist and match baseline (git diff --quiet)
4. Dist files match source (diff -q) — missing dist is OK (dev mode)
5. Systemd service points to local repo (not global npm)
6. Git hooks installed and contain "Spock Guardian" string
7. Auth token file exists at `~/.hermes/webui/.token`

**Exit code:** 0 = safe to update, 1 = blocked
**Output:** Per-file ✓ OK / ✗ FAIL / ⚠ WARNING status

**Pitfall — "DIRTY" errors:**
If you edit a protected file without committing, the check fails with "DIRTY: file (not matching Spock commit)". Fix:
```bash
cd /mnt/c/Users/thadd/hermes-web-ui
git add <file>
git commit -m "feat(spock): ..."
# Then update SPOCK_COMMIT in all scripts
```

### 3. spock-update.sh — Safe Update Wrapper
**Path:** `~/.hermes/scripts/spock-protector/spock-update.sh`
**Usage:** `bash spock-update.sh`
**Flow:**
1. Runs `pre-update-check.sh` → fails fast if unsafe
2. Prompts user for confirmation (skips if non-interactive)
3. Runs `hermes update`
4. Runs `restore-spock.sh --build` to re-apply customizations + rebuild
5. Detects systemd hijack and alerts if service points elsewhere

**Always use this instead of raw `hermes update`.**

### 4. restore-spock.sh — Hard Restore
**Path:** `~/.hermes/spock-protector/restore-spock.sh`
**Usage:**
- `bash restore-spock.sh` — restore files only
- `bash restore-spock.sh --build` — restore + run `npm run build`
- `bash restore-spock.sh --force-build` — same

**What it restores:**
- 10 protected source files from git checkout `SPOCK_COMMIT`
- Dist copies from immutable backup at `~/.hermes/spock-protector/`

### 5. update-reject.sh — Update Blocker
**Path:** `~/.hermes/scripts/spock-protector/update-reject.sh`
**Usage:** Call instead of `npm update` to block with instructions.
Pass `--force` to override.

## Immutable Backup Location
`~/.hermes/spock-protector/` mirrors the repo path structure:
```
~/.hermes/spock-protector/
├── packages/client/public/
│   ├── favicon.png
│   ├── logo.png
│   └── spock-avatar.png
├── packages/client/index.html
├── packages/client/src/assets/
│   ├── logo.png
│   ├── thinking-dark.mp4
│   └── thinking-light.mp4
├── packages/client/src/components/layout/AppSidebar.vue
├── packages/client/src/components/hermes/chat/SessionListItem.vue
└── vite.config.website.ts
```

## Registry File
`~/.hermes/spock-protector/PROTECTED_FILES.txt` — canonical list of all 13 protected artifacts including systemd service, auth token, and Windows launcher.

## Cron Job
```
Job ID:    88a43850fcff
Name:      spock-guardian-watchdog
Schedule:  */5 * * * *
Script:    spock-protector/guard.sh
No agent:  true (silent unless restoring)
```
