# Upstream Merge: v0.6.6 → v0.6.7 (May 31, 2026)

## Situation

Local `main` already contains v0.6.6 + Spock branding (7 local commits).  
Upstream released v0.6.7 as a tag `a7be7c0` with 5 new commits since the merge-base.

## Merge-Base Discovery

```bash
cd /home/thadd/hermes-web-ui
git fetch --tags origin
git merge-base HEAD v0.6.7
# Result: 9df79c33be4ee74b1ad25351d90f821d1bc6aca6
# This is ALSO the tip of origin/main at the time of the v0.6.6 merge
```

So v0.6.7 only adds 5 commits beyond what was already merged:
```
c998a53 [codex] add MCP tools visibility management (#1170)
96bdf8d fix Windows desktop startup readiness (#1167)
e5c5f98 fix message list session transitions (#1172)
9d1da73 update 0.6.7 changelog and provider url handling (#1174)
a7be7c0 bump package versions to 0.6.7 (#1175)
```

## The "Stash Pop Fails" Pattern

When attempting to restore Spock customizations from stash after merge:
```bash
git stash pop
# error: Your local changes to the following files would be overwritten by merge:
#       packages/client/src/components/hermes/chat/SessionListItem.vue
#       packages/client/src/components/layout/AppSidebar.vue
```

**Why:** The v0.6.7 upstream code did NOT reintroduce `RouteLinkItem` or `<a>` tag behavior in these files. The working tree already has the Spock customizations (buttons instead of links). The stash contains the exact same changes. There is nothing to apply.

**Correct action:** Just drop the stash.
```bash
git stash drop stash@{0}
```

**Verification the customizations survived:**
```bash
grep -c "RouteLinkItem" packages/client/src/components/layout/AppSidebar.vue
# → 0 (good — still using buttons)

grep -c 'is="a"' packages/client/src/components/hermes/chat/SessionListItem.vue
# → 0 (good — still using <button> not <a>)
```

## Spock Guardian Hook

The `post-merge` git hook ran automatically:
```
[Spock Guardian] Checking customization integrity after merge...
[Spock Guardian] Spock customizations restored. Run 'npm run build' to rebuild.
[Spock Guardian] Done.
```

This hook appears to work correctly for v0.6.7. The 5 new commits do not touch the branded files.

## Post-Merge Verification (same checklist as v0.6.6)

```bash
cd /home/thadd/hermes-web-ui

# Version
grep '"version"' package.json   # → "0.6.7"

# Spock branding
grep "logo-text\|Spock" packages/client/src/components/layout/AppSidebar.vue
grep "spock-avatar" packages/client/src/components/hermes/profiles/ProfileAvatar.vue
grep "title" packages/client/index.html

# No .gif corruption in MessageList.vue
grep -n "thinking.*\.gif" packages/client/src/components/hermes/chat/MessageList.vue \
  && echo "FAIL" || echo "OK"

# No RouteLinkItem reintroduced
grep -c "RouteLinkItem" packages/client/src/components/layout/AppSidebar.vue   # → 0
```

## What v0.6.7 Actually Brings

1. **MCP tools visibility management** — per-server tool include/exclude lists
2. **Windows desktop startup fixes** — hidden console windows, port 8748 default
3. **Message list session transitions** — per-session scroll position, fade-in
4. **Provider base URL handling improvements** — `providerBaseUrl.ts` utility
5. **Version bump** — 0.6.7

No new files conflict with Spock branding. No manual conflict resolution needed.
