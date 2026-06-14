# Upstream Merge v0.6.9 → v0.6.10 (2026-06-03)

## Summary
Clean auto-merge from EKKOLearnAI/hermes-web-ui `origin/main`. No conflicts, no `.gif` contamination, no manual restoration needed. Spock Guardian post-merge hook handled everything automatically.

## Pre-merge state
- Local commit: `4d9f017` — "chore: merge upstream origin/main (38 commits) with Spock/EKKOLearnAI customizations preserved"
- Remote: `1d19be2` — "prepare 0.6.10 changelog (#1285)"
- Distance: 7 commits behind, 11 ahead

## Commits merged
1. `1d19be2` — prepare 0.6.10 changelog
2. `9461a44` — [codex] fix desktop runtime startup robustness
3. `dc52625` — [codex] add provider model cache refresh action
4. `b1bcec1` — document chat chain harness
5. `91bb68d` — Feat: user avatar upload and group-chat avatar sync
6. `2f1686d` — Sync bridge approval allowlist
7. `98bdc25` — route apikey.fun providers to presets

## Merge process
- `git fetch origin main` — clean
- `git merge origin/main --no-edit` — auto-merged via 'ort' strategy
- Spock Guardian hook auto-ran post-merge and reported:
  ```
  [Spock Guardian] Checking customization integrity after merge...
  [Spock Guardian] Spock customizations restored. Run 'npm run build' to rebuild.
  [Spock Guardian] Done.
  ```

## Build
- `npm install` — completed in ~6 s, added/removed 5 packages each
- `npm run build` — completed in ~1 m 25 s
- No `.gif` files in `dist/` (contamination check passed)
- Custom assets present:
  - `dist/client/logo.png` — 710 KB
  - `dist/client/assets/mp4/thinking-dark-B_T3hcgV.mp4` — 49 KB

## Server restart
- Environment: `NODE_ENV=production`, `HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui`, `HERMES_AGENT_BRIDGE_PYTHON=/home/thadd/hermes-agent-ui/venv/bin/python3`, `HERMES_WEB_UI_DISABLE_UPDATE_CHECK=true`
- Auth: `unset AUTH_DISABLED` explicitly before start
- Bridge: agent-broker ready on `ipc:///tmp/hermes-agent-bridge.sock`
- Health checks: port 8648 listening, server startup confirmed in logs

## Pitfalls avoided this merge
- No conflicts in `AppSidebar.vue` or `MessageList.vue`
- No `.gif` contamination (upstream did not switch assets this release)
- No auth issues (explicit `unset AUTH_DISABLED` during restart)
- No profile switching issues
- No bridge Python module errors

## Session-specific note
On this WSL setup, the active WebUI repo is at `/mnt/c/Users/thadd/hermes-web-ui` (the server's cwd), not `/home/thadd/hermes-web-ui-ekko` (a secondary checkout). Verify the running server's cwd with `readlink /proc/<PID>/cwd` before updating.
