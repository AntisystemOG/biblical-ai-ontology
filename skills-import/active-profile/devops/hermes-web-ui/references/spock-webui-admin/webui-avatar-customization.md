# EKKOLearnAI WebUI Avatar Customization

Thad's WebUI (`hermes-web-ui`, EKKOLearnAI / Spock branded) uses `@multiavatar/multiavatar` to generate SVG avatars for session profile icons in the session list sidebar.

## Relevant Files

- **Source**: `packages/client/src/components/hermes/chat/SessionListItem.vue`
  - Uses `multiavatar(profileName)` to generate SVG via `v-html`
  - 16×16px circle avatar next to profile name
- **Compiled dist**: `dist/client/assets/js/OutlinePanel-*.js`
  - Vue SFC compiled into minified single-line JS with `n()` render calls
- **Group chat**: `packages/client/src/components/hermes/group-chat/GroupMessageItem.vue`
  - Also uses multiavatar for message sender avatars

## Replacing with a Static Image

### Source edit (for future builds)

```vue
<!-- In SessionListItem.vue -->
<script setup>
// Remove: import multiavatar from '@multiavatar/multiavatar'
// Replace:
const spockAvatarUrl = '/spock-avatar.png'
</script>

<template>
  <!-- Old: -->
  <span class="session-item-profile-avatar" v-html="profileAvatar" />
  <!-- New: -->
  <img class="session-item-profile-avatar" :src="spockAvatarUrl" alt="Spock" />
</template>
```

Copy the desired image to `packages/client/public/` and `dist/client/` so it is served at `/spock-avatar.png`.

### Dist patch (when build is broken / immediate effect)

The compiled Vue JS is minified to a single line. The pattern to replace:

```js
// Old — compiled Vue render fn with innerHTML dynamic prop
n("span",{class:"session-item-profile-avatar",innerHTML:e.value},null,8,z)

// New — img with static src
n("img",{class:"session-item-profile-avatar",src:"/spock-avatar.png",alt:"Spock"},null,8,z)
```

**Critical:** Also update the dynamic props array from `z=["innerHTML"]` to `z=["src"]` so Vue's patch flag is correct for the `img` element.

## sed Pitfall with Single-Line Minified JS

The compiled `.js` file is a single minified line. Using `sed` with `/` delimiters when the replacement string contains `/` (e.g., `/spock-avatar.png`) will corrupt the file because sed sees the image path `/spock` as a sed delimiter.

**Wrong:**
```bash
sed -i 's/old/new\/spock-avatar.png/g' file.js
```

**Correct:** Use Python or another tool for replacements in minified JS:
```python
old = 'n("span",{class:"session-item-profile-avatar",innerHTML:e.value},null,8,z)'
new = 'n("img",{class:"session-item-profile-avatar",src:"/spock-avatar.png",alt:"Spock"},null,8,z)'
content = content.replace(old, new)
```

Or use a sed delimiter that does not appear in the replacement string, e.g., `|`:
```bash
sed -i 's|old|new/spock-avatar.png|g' file.js
```

## ProfileAvatar Component Override (Current Upstream — May 2026)

The upstream repo now uses a dedicated `ProfileAvatar.vue` component. It ONLY
renders an `<img>` when the `:avatar` prop is an object with `type === 'image'`
and a truthy `dataUrl`. A plain string causes multiavatar SVG fallback.

**In `SessionListItem.vue` (CORRECT — Spock override):**
```vue
<script setup>
import ProfileAvatar from '@/components/hermes/profiles/ProfileAvatar.vue'
const profileName = computed(() => props.session.profile || 'default')
const profileAvatar = computed(() => ({ type: 'image' as const, dataUrl: '/spock-avatar.png' }))
</script>

<template>
  <ProfileAvatar class="session-item-profile-avatar" :name="profileName" :avatar="profileAvatar" :size="16" />
</template>
```

**WRONG (fallback to multiavatar):**
```vue
const profileAvatar = computed(() => '/spock-avatar.png')
// ProfileAvatar sees a string, not {type:'image',dataUrl:'...'}, so it falls
// back to multiavatar(props.name || 'default') → generic anime character
```

**ProfileAvatar component source (`packages/client/src/components/hermes/profiles/ProfileAvatar.vue`):**
```vue
<img
  v-if="avatar?.type === 'image' && avatar.dataUrl"
  class="profile-avatar-image"
  :src="avatar.dataUrl"
/>
<span v-else class="profile-avatar-svg" v-html="generatedSvg" />
```

**Merge strategy for rebase conflicts in SessionListItem.vue:**
- Accept upstream's `NTooltip`, `ProfileAvatar` component imports, and new computed properties
- Keep the Spock `profileAvatar = computed(() => ({ type: 'image', dataUrl: '/spock-avatar.png' }))` override
- Keep the `spock-avatar.png` asset in `packages/client/public/`

## Spock Guardian Git Hook

Thad's repo has a `[Spock Guardian]` post-checkout / post-rewrite hook that auto-restores customizations (e.g., `AppSidebar.vue`, `spock-avatar.png`) after any git operation that rewrites files. This means:
- After `git checkout`, `git pull`, `git rebase`, or `git stash pop`, the hook may restore or overwrite files.
- If you patch compiled dist JS manually, the hook may restore the original on the next checkout.
- Always verify the file state after git operations if customizations seem to revert.

## Other Avatar Locations

| Component | Purpose | File |
|-----------|---------|------|
| SessionListItem.vue | Session sidebar avatar | `packages/client/src/components/hermes/chat/SessionListItem.vue` |
| GroupMessageItem.vue | Group chat message sender | `packages/client/src/components/hermes/group-chat/GroupMessageItem.vue` |
| ChatPanel.vue | Main chat panel avatar | Search for `multiavatar` in chat components |

Use `grep -rln "multiavatar" packages/client/src/` to find all occurrences.
