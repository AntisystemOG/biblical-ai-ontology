---
source: session 2026-05-20
context: Spock WebUI thinking animation replacement
---

# Thinking Avatar Replacement Record

## What Was Changed (2026-05-20)

Replaced the default "locale girl" thinking/typing indicator animation that plays when the AI is generating a response in the WebUI chat. Replaced with a custom Star Trek badge video (`startrek badge.mp4`).

## Files Modified

```
packages/client/src/assets/thinking-light.mp4   ← copied from ~/.hermes/images/startrek badge.mp4
packages/client/src/assets/thinking-dark.mp4    ← copied from same
```

After copying, the build was run:
```bash
cd /home/thadd/hermes-web-ui-ekko
/home/thadd/node26/bin/npm run build
```

Build output includes the video with a content hash:
```
dist/client/assets/mp4/thinking-light-<hash>.mp4
```

## Component Reference

The animation is used in `MessageList.vue` only. Relevant lines:
- Import: lines 6-7 (`thinkingVideoLight`, `thinkingVideoDark`)
- Render: line ~176 (`<video>` tag with `:src` binding)

The video element is conditionally rendered when `chatStore.isRunActive` or `chatStore.abortState` is true.

## Pitfall: Build Required

The source MP4 in `src/assets/` is NOT served directly. Vite processes it during build and emits a hashed copy to `dist/client/assets/mp4/`. If the WebUI server is running from `dist/` (production mode), the source file edit alone does nothing — rebuild is mandatory.

## Reproduction Command for Future Updates

```bash
bash /mnt/c/Users/thadd/.openclaw/workspace/scripts/apply-webui-customizations.sh
```

This script is checked into the workspace repo for portability.

## Permanent Asset Storage

The canonical source file lives at:
```
C:\Users\thadd\.hermes\images\startrek badge.mp4
```

On the next WebUI update, the source `src/assets/*.mp4` files may be restored to upstream defaults. Re-run the re-apply script after any `git pull`/`npm run build` cycle.
