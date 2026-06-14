# Spock Avatar Replacement — Session Detail

## Session 2026-05-22

### What the user wanted
Replace the session list profile icon (generic green circle with letter) with
the custom transparent Spock PNG from `C:\Users\thadd\Pictures\spock_icon_transparent.png`.

### Component responsible (May 2026 — updated for ProfileAvatar component)
`packages/client/src/components/hermes/chat/SessionListItem.vue`
- Line ~39: `const profileAvatar = computed(() => '/spock-avatar.png')` — always returns Spock image
- Line ~140: `<ProfileAvatar class="session-item-profile-avatar" :name="profileName" :avatar="profileAvatar" :size="16" />`

**Why ProfileAvatar:** Upstream replaced inline multiavatar with a dedicated `ProfileAvatar.vue` component (commit c90eba2). The Spock customization piggybacks on this by always passing `/spock-avatar.png` as the `:avatar` prop.

**ProfileAvatar component behavior:**
- Accepts `:avatar` string prop — renders `<img :src="avatar">` when provided
- Without `:avatar`, falls back to multiavatar SVG generation
- Located at `packages/client/src/components/hermes/profiles/ProfileAvatar.vue`

**If upstream removes ProfileAvatar:** Revert to inline `<img class="session-item-profile-avatar" src="/spock-avatar.png" alt="Spock">`

The avatar is rendered as a 16x16 circle. The browser auto-downscales whatever
image is served at `/spock-avatar.png`. No pre-resizing needed.

### Source and dist files to replace
- **Source:** `packages/client/public/spock-avatar.png`
- **Dist (served live):** `dist/client/spock-avatar.png`

Both must be replaced because the server serves from `dist/client/` directly.
The file in `public/` is the source-of-truth for future builds.

### Replacement procedure
```bash
# Copy the user's transparent PNG into both locations
cp "/mnt/c/Users/thadd/Pictures/spock_icon_transparent.png" \
   /mnt/c/Users/thadd/hermes-web-ui/packages/client/public/spock-avatar.png

cp "/mnt/c/Users/thadd/Pictures/spock_icon_transparent.png" \
   /mnt/c/Users/thadd/hermes-web-ui/dist/client/spock-avatar.png
```

### Add to protection system
After replacement, add `spock-avatar.png` to all 3 git hooks and the backup:
```bash
for hook in .git/hooks/post-merge .git/hooks/post-checkout .git/hooks/post-rewrite; do
  # Add "packages/client/public/spock-avatar.png" to PROTECTED_FILES array
  sed -i 's|PROTECTED_FILES=(|PROTECTED_FILES=(\n  "packages/client/public/spock-avatar.png"|' "$hook"
done

# Backup to immutable protector dir
mkdir -p ~/.hermes/spock-protector/packages/client/public
cp packages/client/public/spock-avatar.png \
   ~/.hermes/spock-protector/packages/client/public/spock-avatar.png
```

### No build required
Since `dist/client/` was updated directly, the change is live immediately.
No `npm run build` needed. A browser refresh shows the new avatar.

### File characteristics (for reference)
| | Old avatar | New Spock icon |
|---|---|---|
| Size | 507 x 181 | 860 x 721 |
| Format | PNG RGBA | PNG RGBA |
| Transparency | Yes | Yes |
| File size | 13KB | 710KB |

Both work identically in the 16px circular CSS container. The larger file is
sharper at higher DPI or if the CSS size ever increases.
