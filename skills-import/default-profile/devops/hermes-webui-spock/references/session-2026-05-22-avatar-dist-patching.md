# Session 2026-05-22 — Spock Avatar + Backup Techniques

## Technique: Patching Compiled Vue Dist JS When Build Is Broken

When `npm run build` fails (rolldown missing native binding), the compiled
`dist/client/assets/js/*.js` files must be patched directly.

### Pattern for avatar replacement in compiled JS

**Old pattern (multiavatar-generated span):**
```js
n("span",{class:"session-item-profile-avatar",innerHTML:e.value},null,8,z)
```
Where `z=["innerHTML"]` is the Vue dynamic props array.

**New pattern (static Spock img):**
```js
n("img",{class:"session-item-profile-avatar",src:"/spock-avatar.png",alt:"Spock"},null,8,z)
```
With `z=["src"]` (not `z=["innerHTML"]`) since `<img>` has no innerHTML.

### Critical: Fix Vue patch flags
When changing element type from `<span>` to `<img>`, the dynamic props array
must be updated. If `z=["innerHTML"]` is left unchanged, Vue runtime will try
to patch `innerHTML` on an `<img>` element and silently fail.

**Files requiring patches (as of this session):**
- `dist/client/assets/js/OutlinePanel-CBYfEuCP.js`
- `dist/client/assets/js/OutlinePanel-P0pfhZX2.js`

### Python script for safe dist JS patching
```python
import re

for fname in ['OutlinePanel-CBYfEuCP.js', 'OutlinePanel-P0pfhZX2.js']:
    f = f'/mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/js/{fname}'
    with open(f, 'r') as fh:
        content = fh.read()
    
    # Replace element + patch flags
    content = content.replace(
        'n("span",{class:"session-item-profile-avatar",innerHTML:e.value},null,8,z)',
        'n("img",{class:"session-item-profile-avatar",src:"/spock-avatar.png",alt:"Spock"},null,8,z)'
    )
    content = content.replace('z=["innerHTML"]', 'z=["src"]')
    
    with open(f, 'w') as fh:
        fh.write(content)
```

## Technique: Preserving Spock Across Upstream Avatar Component Refactors

Upstream replaced inline multiavatar rendering with a `ProfileAvatar` component.
The safe way to preserve Spock across this refactor:

**In `SessionListItem.vue`:**
```vue
<script setup>
const profileName = computed(() => props.session.profile || 'default')
const profileAvatar = computed(() => '/spock-avatar.png')  // Always Spock
</script>

<template>
  <ProfileAvatar
    class="session-item-profile-avatar"
    :name="profileName"
    :avatar="profileAvatar"
    :size="16"
  />
</template>
```

This works because `ProfileAvatar.vue` accepts an `:avatar` string prop and
renders `<img :src="avatar">` when provided. If upstream removes ProfileAvatar
entirely, revert to inline `<img src="/spock-avatar.png">`.

## Technique: Complete Local Backup of WebUI

**Exclude:** `node_modules/` (658MB, reinstallable via `npm install`)
**Include:** Everything else including `.git/`, `dist/`, source, assets

```bash
rsync -avh --exclude='node_modules' --exclude='.next' \
  "/mnt/c/Users/thadd/hermes-web-ui/" \
  "/mnt/c/Users/thadd/Documents/SpockWebUI/"
```

**Result:** ~139MB backup with full git history and compiled dist.

### Restore from backup
```bash
cd C:\Users\thadd\Documents\SpockWebUI
node dist/server/index.js   # immediate start (compiled dist included)
# OR rebuild:
npm install && npm run build
```

### Verification script
```bash
echo "=== Backup Verification ==="
ls packages/client/public/spock-avatar.png
ls dist/client/spock-avatar.png
grep -q "spock-avatar" packages/client/src/components/hermes/chat/SessionListItem.vue && echo "✓ Source patched"
grep -q "spock-avatar" dist/client/assets/js/OutlinePanel-CBYfEuCP.js && echo "✓ Dist patched"
ls .git && echo "✓ Git repo present"
ls packages/client/src/components/layout/AppSidebar.vue && echo "✓ AppSidebar present"
```

## Key Lesson: Always Patch Both Source AND Dist

When the build system is broken, changes to `.vue` source files are NOT
automatically reflected in the running server. The server serves from
`dist/client/`. Two-step process:

1. **Patch source** — for future builds and git commits
2. **Patch dist** — for immediate effect without rebuilding

Failure to patch dist means the running WebUI shows the OLD behavior even
though the source file looks correct.
