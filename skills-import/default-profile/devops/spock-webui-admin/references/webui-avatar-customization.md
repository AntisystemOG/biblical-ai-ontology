# EKKOLearnAI WebUI Avatar Customization — 2026-05-22

Thad's WebUI (`hermes-web-ui`, EKKOLearnAI / Spock branded) uses `@multiavatar/multiavatar` to generate SVG avatars for profile icons throughout the interface.

## Universal Spock Avatar Fix (Current — May 2026)

**The correct approach: modify `ProfileAvatar.vue` — the single component that renders EVERY avatar in the UI.**

`packages/client/src/components/hermes/profiles/ProfileAvatar.vue`:
```vue
<script setup lang="ts">
import { computed } from 'vue'
import type { ProfileAvatar } from '@/api/hermes/profiles'

const props = withDefaults(defineProps<{
  name: string
  avatar?: ProfileAvatar | null
  size?: number
}>(), {
  size: 24,
})

const style = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  flexBasis: `${props.size}px`,
}))
</script>

<template>
  <span class="profile-avatar-view" :style="style">
    <img
      v-if="avatar?.type === 'image' && avatar.dataUrl"
      class="profile-avatar-image"
      :src="avatar.dataUrl"
      alt=""
      draggable="false"
    >
    <img
      v-else
      class="profile-avatar-image"
      src="/spock-avatar.png"
      alt=""
      draggable="false"
    >
  </span>
</template>
```

**What this fixes:**
- Session list avatars (sidebar) ✓
- Message bubble avatars (chat) ✓
- Group chat avatars ✓
- Profile selector avatars ✓
- Kanban task card assignee avatars ✓
- Profile modal avatars ✓
- Any future component using ProfileAvatar ✓

**Remove:** The `@multiavatar/multiavatar` import, `fallbackSeed` computed, and `generatedSvg` computed are no longer needed.

## ProfileAvatar Component Contract

The component ONLY renders `<img>` when the `:avatar` prop is an **object** with `type === 'image'` and a truthy `dataUrl`. A plain string causes multiavatar SVG fallback.

**Correct (SessionListItem.vue):**
```js
const profileAvatar = computed(() => ({ type: 'image' as const, dataUrl: '/spock-avatar.png' }))
```

**Wrong (fallback to anime):**
```js
const profileAvatar = computed(() => '/spock-avatar.png')
```

## Dist Patch (when build is broken / immediate effect)

The compiled Vue JS is minified to a single line. If `npm run build` is broken, manually patch `dist/client/assets/js/OutlinePanel-*.js`:

```python
old = 'n("span",{class:"session-item-profile-avatar",innerHTML:e.value},null,8,z)'
new = 'n("img",{class:"session-item-profile-avatar",src:"/spock-avatar.png",alt:"Spock"},null,8,z)'
content = content.replace(old, new)
content = content.replace('z=["innerHTML"]', 'z=["src"]')
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

## favicon.ico Conversion

`index.html` references `/favicon.ico`, not `/favicon.png`. Convert `spock-avatar.png` to multi-resolution `.ico`:

```python
from PIL import Image
src = '/mnt/c/Users/thadd/hermes-web-ui/packages/client/public/spock-avatar.png'
dst = '/mnt/c/Users/thadd/hermes-web-ui/packages/client/public/favicon.ico'
img = Image.open(src)
if img.mode != 'RGBA': img = img.convert('RGBA')
sizes = [(16,16), (32,32), (64,64), (128,128)]
frames = [img.resize(s, Image.LANCZOS) for s in sizes]
frames[0].save(dst, format='ICO', sizes=sizes, append_images=frames[1:])
```

## Stale dist/ Build Pitfall

**Symptom:** Source files are correct but browser still shows anime avatars.

**Root cause:** The server serves compiled `dist/client/` — not source `.vue` files. If `dist/` was built before the avatar fix, it delivers stale code.

**Detection:**
```bash
ls -la dist/client/index.html          # Check build timestamp
git log --oneline -3                    # Compare to fix commit
grep -c "multiavatar" dist/client/assets/js/*.js   # Should be 0
```

**Fix:** `npm run build` then restart server. If build times out and wipes `dist/server/`, restore from backup:
```bash
rsync -avh /mnt/c/Users/thadd/Documents/SpockWebUI/dist/server/ dist/server/
```

## Spock Guardian Git Hook

Thad's repo has a `[Spock Guardian]` post-checkout / post-rewrite hook that auto-restores customizations after git operations. The hook now:
- Restores from `~/.hermes/spock-protector/` file backups FIRST (authoritative)
- Then runs `git checkout f636b1b -- <file>` for clean git state
- No conditional checks — always restores

Protected files include `ProfileAvatar.vue`, `favicon.ico`, `spock-avatar.png`, and all other branding assets.

## Other Avatar Locations (all fixed by ProfileAvatar.vue)

| Component | Purpose | File |
|-----------|---------|------|
| SessionListItem.vue | Session sidebar avatar | `packages/client/src/components/hermes/chat/SessionListItem.vue` |
| MessageItem.vue | Chat message bubble avatar | `packages/client/src/components/hermes/chat/MessageItem.vue` |
| GroupMessageItem.vue | Group chat message sender | `packages/client/src/components/hermes/group-chat/GroupMessageItem.vue` |
| GroupChatPanel.vue | Group chat agent list | `packages/client/src/components/hermes/group-chat/GroupChatPanel.vue` |
| ProfileSelector.vue | Sidebar profile dropdown | `packages/client/src/components/layout/ProfileSelector.vue` |
| ProfileCard.vue | Profile manager modal | `packages/client/src/components/hermes/profiles/ProfileCard.vue` |
| KanbanTaskCard.vue | Kanban assignee avatar | `packages/client/src/components/hermes/kanban/KanbanTaskCard.vue` |

All of these use `ProfileAvatar.vue`. One change to the component fixes every avatar in the UI.
