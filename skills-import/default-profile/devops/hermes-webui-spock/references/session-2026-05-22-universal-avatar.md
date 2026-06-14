# Session 2026-05-22 — Universal Spock Avatar Fix

## Problem
After fixing `SessionListItem.vue` to show Spock in the sidebar, two anime avatars still appeared:
1. Sidebar "default" profile — small green-circle avatar (from multiavatar fallback)
2. Message bubble "assistant" avatar — larger green-circle avatar (from `MessageItem.vue` pulling `profile.avatar` from backend)

## Root Cause
`ProfileAvatar.vue` — the component used by ALL avatar locations — had a `v-else` fallback to `multiavatar(seed)` generating anime characters. When:
- No custom avatar was uploaded for the profile
- The `:avatar` prop was null/undefined
- The `:avatar` prop was a plain string instead of `{type:'image',dataUrl:'...'}`

The component rendered `<span v-html="generatedSvg">` with a multiavatar-generated anime character.

## Components Affected
Every component using `<ProfileAvatar>` was affected:
- `SessionListItem.vue` (sidebar, 16px)
- `MessageItem.vue` (chat bubbles, 40px)
- `ProfileSelector.vue` (profile dropdown, 24px and 34px)
- `GroupChatPanel.vue` (group chat agents, 28px)
- `GroupMessageItem.vue` (group messages, 36px)
- `KanbanTaskCard.vue` (assignees, variable)
- `ProfileCard.vue` (profile modal, 28px and 72px)

## Fix
Modified `packages/client/src/components/hermes/profiles/ProfileAvatar.vue`:

1. **Removed** `import multiavatar from '@multiavatar/multiavatar'`
2. **Removed** `fallbackSeed` and `generatedSvg` computed properties
3. **Changed** the `v-else` branch from `<span v-html="generatedSvg">` to `<img src="/spock-avatar.png">`

This single change fixes ALL avatars everywhere because every avatar in the UI routes through `ProfileAvatar.vue`.

## Verification
```bash
# Build must succeed with no multiavatar references in compiled JS
cd /mnt/c/Users/thadd/hermes-web-ui && npm run build
grep -c "spock-avatar" dist/client/assets/js/*.js        # Should be >0
grep -c "multiavatar\|profile-avatar-svg" dist/client/assets/js/*.js  # Should be 0
```

## Files Changed
- `packages/client/src/components/hermes/profiles/ProfileAvatar.vue` — universal Spock fallback
- `~/.hermes/spock-protector/PROTECTED_FILES.txt` — added ProfileAvatar.vue
- `~/.hermes/spock-protector/restore-spock.sh` — added ProfileAvatar.vue

## Key Lesson
When replacing avatars in a Vue component system, find the LOWEST common component (ProfileAvatar.vue) rather than patching each caller individually. One fix at the root covers all callers automatically.
