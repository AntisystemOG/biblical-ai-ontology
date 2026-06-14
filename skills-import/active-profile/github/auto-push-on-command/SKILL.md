---
name: auto-push-on-command
description: "Automatic GitHub push responder: when Thad says 'push' or 'push to github', detect relevant repos, commit any pending changes, and push."
triggers:
  - "push"
  - "push to github"
  - "push it"
  - "push everything"
  - "github push"
toolsets: ["terminal"]
---

# Auto-Push on Command

When Thad says **"push"** (or variants), detect which repositories have uncommitted/unpushed changes, stage+commit+push them.

## Behavior

1. **Check the active workspace repo first** — `C:\Users\thadd\.openclaw\workspace`
   ```bash
   cd /mnt/c/Users/thadd/.openclaw/workspace && git status --short
   ```
   - If uncommitted changes → `git add -A && git commit -m "<auto-msg>" && git push origin main`
   - If committed but unpushed → `git push origin main`

2. **Check the WebUI repo** — `/home/thadd/hermes-web-ui-ekko`
   ```bash
   cd /home/thadd/hermes-web-ui-ekko && git status --short
   ```
   - Same pattern as above. Commit message should reference the change.

3. **Report back clearly:**
   - Which repo(s) were pushed
   - Commit hash
   - What was in the commit (file list)
   - If nothing to push, say so

## Commit Message Rules

- If a commit was just made in the current session and the user says "push", reuse the existing commit — don't make a new empty one.
- Auto-generated messages should be descriptive: `feat: <what changed>` or `fix: <what fixed>`
- When in doubt, look at `git status --short` and summarize

## Priority Order

1. **Active project repo** (wherever Hermes workspace is — e.g. `/mnt/c/Users/thadd/.claude/projects/...`)
   - Always check `git status` here first, even if other repos also have changes.
2. OpenClaw workspace (`/mnt/c/Users/thadd/.openclaw/workspace`)
3. Hermes WebUI (`/home/thadd/hermes-web-ui-ekko`)
4. Any other repo only if explicitly referenced

## Authentication

The workspace uses HTTPS with stored credentials at `/mnt/c/Users/thadd/.git-credentials`. Set credential helper before push if needed:

```bash
git config --local credential.helper "store --file=/mnt/c/Users/thadd/.git-credentials"
```

## WSL Push-Failure Protocol

When `git push` fails with `could not read Username for 'https://github.com': No such device or address`, **do not keep trying**. WSL has no cached GitHub creds. Options:

1. **Check for gh CLI auth** — `gh auth status`. If authenticated, use `gh` for subsequent pushes.
2. **Check for PAT in remote URL** — If remote is HTTPS and no credential helper, ask user for preferred auth method (PAT, SSH, or switch to Windows-side Git).
3. **Always set git identity before committing in WSL:**
   ```bash
   git config user.name  "$(git log --format='%an' -1 2>/dev/null || echo 'Hermes Agent')"
   git config user.email "$(git log --format='%ae' -1 2>/dev/null || echo 'agent@hermes.local')"
   ```

## Example Outputs

**Has changes:**
```
Pushed spock-workspace: main → main, commit a1b2c3d
- scripts/apply-webui-customizations.sh
- Spocks Reports/daily-brief-2026-05-20.md

Pushed hermes-web-ui: main → main, commit e4f5g6h
- packages/client/src/assets/thinking-light.mp4
```

**Nothing to push:**
```
Nothing to push. Both repos are clean and up to date.
```
