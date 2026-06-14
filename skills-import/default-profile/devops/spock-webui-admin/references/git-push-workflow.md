# Git Push Workflow for Thad's Hermes WebUI Fork

## Remotes

Thad's WebUI repo has two remotes:

| Remote | URL | Purpose |
|--------|-----|---------|
| `origin` | `https://github.com/EKKOLearnAI/hermes-web-ui.git` | Upstream |
| `spock` | `https://github.com/AntisystemOG/hermes-web-ui.git` | Thad's fork |

Always push customizations to `spock`, not `origin`.

## Authentication

Thad's `GITHUB_PAT` environment variable contains a GitHub personal access token. Use it for HTTPS pushes:

```bash
GITHUB_PAT_RAW="${GITHUB_PAT}"
git push "https://${GITHUB_PAT_RAW}@github.com/AntisystemOG/hermes-web-ui.git" main
```

If `GITHUB_PAT` is not available, the token may need to be retrieved from the shell environment or `.env` file.

## Commit Isolation

This repo has hundreds of unstaged changes from previous work. **Never commit everything.** Isolate only the files you actually changed:

```bash
# Stage only your changes
git add packages/client/public/spock-avatar.png
git add packages/client/src/components/hermes/chat/SessionListItem.vue

# Commit with a descriptive message
git commit -m "feat(ui): replace multiavatar with Spock image for session list avatars"
```

## Handling Divergent Branches

Thad's fork is often ahead of upstream. Before pushing, pull the latest fork state:

```bash
git fetch spock

# If rebasing, set rebase preference
git config pull.rebase true

# Stash pre-existing changes temporarily
git stash push -m "pre-existing changes" --include-untracked

# Pull and rebase
git pull "https://${GITHUB_PAT_RAW}@github.com/AntisystemOG/hermes-web-ui.git" main

# If conflicts, resolve them, then continue
git add -u
GIT_EDITOR="cat" git rebase --continue

# Push
git push "https://${GITHUB_PAT_RAW}@github.com/AntisystemOG/hermes-web-ui.git" main

# Pop stash (may have conflicts; if so, resolve or reset --hard)
git stash pop
git reset --hard HEAD   # clean up if stash pop created merge conflicts
```

## Spock Guardian Hook

After `git rebase --continue`, the `[Spock Guardian]` hook auto-restores customizations. It may emit:
```
[Spock Guardian] Checking after rewrite...
[Spock Guardian] RESTORING: packages/client/public/spock-avatar.png
error: pathspec 'packages/client/public/spock-avatar.png' did not match any file(s) known to git
[Spock Guardian] Spock customizations restored.
```

This is usually harmless — verify the file exists after the hook runs.

## sed Pitfall in Compiled JS

When patching compiled `dist/client/assets/js/*.js` files (minified to a single line), **never use `sed` with `/` delimiters** if the replacement string contains `/` (e.g., `/spock-avatar.png`). The `/` in the path is interpreted as a sed delimiter and corrupts the file.

**Wrong:**
```bash
sed -i 's/old/new\/spock-avatar.png/g' file.js
```

**Correct — use Python:**
```python
old = 'n("span",{class:"session-item-profile-avatar",innerHTML:e.value},null,8,z)'
new = 'n("img",{class:"session-item-profile-avatar",src:"/spock-avatar.png",alt:"Spock"},null,8,z)'
content = content.replace(old, new)
```

**Correct — use `|` delimiter:**
```bash
sed -i 's|old|new/spock-avatar.png|g' file.js
```

## Post-Push Cleanup

After the push, the stash pop may introduce merge conflicts from pre-existing changes. The safest cleanup:

```bash
git reset --hard HEAD   # discards all working tree changes
```

This returns the repo to the clean committed state. If you need the pre-existing changes, do not run this — resolve conflicts manually instead.
