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

1. OpenClaw workspace (`/mnt/c/Users/thadd/.openclaw/workspace`)
2. Hermes WebUI (`/home/thadd/hermes-web-ui-ekko`)
3. Any other repo only if explicitly referenced

## Authentication

The workspace uses HTTPS with stored credentials at `/mnt/c/Users/thadd/.git-credentials`. Set credential helper before push if needed:

```bash
git config --local credential.helper "store --file=/mnt/c/Users/thadd/.git-credentials"
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
