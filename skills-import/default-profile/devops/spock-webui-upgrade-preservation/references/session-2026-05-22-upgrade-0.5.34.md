# Reference: 0.5.32 → 0.5.34 Upgrade — Guardian Hook + Rebase Interaction

## Problem Discovered

The Spock Guardian hook (`post-checkout` + `post-merge`) auto-restores files
from commit `f636b1b` after every checkout operation. During `git rebase`, Git
checks out commits repeatedly as it replays them. The hook fires on each
checkout, creating unstaged modifications that cause:

```
error: cannot rebase: You have unstaged changes.
error: Additionally, your index contains uncommitted changes.
```

## Solution: Disable Hooks During Rebase

```bash
# Before rebase
mv .git/hooks/post-checkout .git/hooks/post-checkout.bak
mv .git/hooks/post-merge   .git/hooks/post-merge.bak

# Perform rebase
git pull --rebase origin main

# After rebase succeeds
mv .git/hooks/post-checkout.bak .git/hooks/post-checkout
mv .git/hooks/post-merge.bak   .git/hooks/post-merge
```

## Second Problem: Post-Rebase Staging Noise

Upstream 0.5.34 changed only CSS properties in `AppSidebar.vue` (`gap: 6px→8px`,
flex rules). The Guardian hook fired during rebase and restored the file from
`f636b1b`, then Git staged the upstream CSS changes on top. The result:
staged upstream changes mixed with Spock branding text.

## Solution: Reset to HEAD and Re-Stage Only Spock Changes

```bash
# Reset file to the rebased version (which has Spock text from earlier commits)
git checkout HEAD -- packages/client/src/components/layout/AppSidebar.vue

# Now only real Spock changes remain unstaged; stage them
git add packages/client/src/components/layout/AppSidebar.vue

# Verify clean staging
git status --short
```

## Third Problem: Untracked Asset Checkout Error

After `git rebase --continue`, the Guardian hook may emit:
```
[Spock Guardian] RESTORING: packages/client/public/spock-avatar.png
error: pathspec 'packages/client/public/spock-avatar.png' did not match any file(s) known to git
```

This happens because `spock-avatar.png` is not tracked in the git index at the
rebase HEAD — it was added in commit `9caac49` but the hook tries to `git
checkout f636b1b --` it. This error is harmless; the file already exists from
the rebrand commit.

## Force-Push to Fork After Rebase

Rebase rewrites commit hashes. The fork (`spock` remote) needs force-push:

```bash
git push spock main --force-with-lease
```

If `--force-with-lease` rejects, inspect `git log spock/main..HEAD` before
using plain `--force`.

## Verification Checklist Used in This Session

| Check | Command |
|-------|---------|
| Source avatar | `grep "spock-avatar.png" packages/client/src/components/hermes/chat/SessionListItem.vue` |
| Sidebar branding | `grep "Spock" packages/client/src/components/layout/AppSidebar.vue` |
| Browser title | `grep "Spock" packages/client/index.html` |
| Avatar asset | `ls packages/client/public/spock-avatar.png` |
| Dist avatar | `ls dist/client/spock-avatar.png` |
| Dist JS patch | `grep "spock-avatar" dist/client/assets/js/OutlinePanel-CBYfEuCP.js` |
| Guardian hook | `ls -la .git/hooks/post-checkout .git/hooks/post-merge` |

## Key Lesson

The Guardian hook is a safety net for normal development (branch switches,
merges), but it actively interferes with rebase. Always disable before rebase
and re-enable after. Do the same for any Git operation that involves multiple
internal checkouts (cherry-pick, `git filter-branch`, etc.).
