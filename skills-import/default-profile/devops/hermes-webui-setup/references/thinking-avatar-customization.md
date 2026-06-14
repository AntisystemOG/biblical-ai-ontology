# Thinking Avatar (Custom Thinking Video) Customization

## What It Is

When the agent is "thinking" (reasoning/thinking.delta events), the UI shows a looping video next to the message. By default it's a small animation of a little girl thinking.

Thad replaced this with a custom Star Trek badge `thinking-light.mp4` / `thinking-dark.mp4`.

## Source Assets Location

In the EKKOLearnAI repo:
- Source: `packages/client/src/assets/thinking-light.mp4`
- Source: `packages/client/src/assets/thinking-dark.mp4` (can be same file)
- Public/served: `packages/client/public/` (not used for thinking video)

The build process copies and hashes these into `dist/client/assets/mp4/` for production.

## Steps to Customize (Production = dist/)

If running from `dist/` via desktop launcher:

1. **Place your custom video** (48px square recommended, short loop under 100KB for instant load):
   ```bash
   cp /path/to/my-thinking-badge.mp4 \
      /mnt/c/Users/thadd/hermes-web-ui/packages/client/src/assets/thinking-light.mp4
   cp /path/to/my-thinking-badge.mp4 \
      /mnt/c/Users/thadd/hermes-web-ui/packages/client/src/assets/thinking-dark.mp4
   ```

2. **Overwrite the compiled dist file** directly (no rebuild needed for testing):
   The dist file is hashed (e.g., `dist/client/assets/mp4/thinking-light-XXXXXX.mp4`). Rather than chasing the hash, either:
   - Rebuild with `npm run build:website` (requires Node 23+), OR
   - Find the current hash by looking in the dist:
     ```bash
     ls /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/mp4/
     # → thinking-light-B_T3hcgV.mp4
     ```
     Then overwrite that specific file with your custom video:
     ```bash
     cp /path/to/my-thinking-badge.mp4 \
        /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/mp4/thinking-light-B_T3hcgV.mp4
     ```

3. **Restart server** (static assets may be cached in server memory). A server restart guarantees the new file is served.

4. **Hard-refresh browser** (`Ctrl + Shift + R`) to clear browser cache.

## Customization Script Pattern

Keep a re-apply script in your workspace for after any WebUI update/rebuild:

```bash
#!/bin/bash
WEBUI_DIR="/mnt/c/Users/thadd/hermes-web-ui"
IMAGES_DIR="/mnt/c/Users/thadd/.hermes/images"

cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-light.mp4"
cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-dark.mp4"

echo "Done. Rebuild with 'npm run build:website' or manually copy to dist/client/assets/mp4/"
```

**IMPORTANT:** Point `WEBUI_DIR` to the **authoritative** repo at `/mnt/c/Users/thadd/hermes-web-ui`, NOT to any legacy clone like `/home/thadd/hermes-web-ui-ekko`. Multiple repos exist in Thad's environment — always target the one at `/mnt/c/Users/thadd/hermes-web-ui`.

## Video Format Tips

- Resolution: 48x48 or 96x96 (CSS scales it)
- Duration: 2-5 seconds, seamless loop
- Size: Under 100KB for instant load
- Format: H.264 MP4 (web compatible)
- Transparent background: Use WebM with alpha if you need transparency; MP4 doesn't support it

## Troubleshooting

**"Still showing the old video after copy"**
- Did you restart the server? Static file serving may cache the old file.
- Did you hard-refresh the browser? Browser caches aggressively.
- Did you check both `thinking-light.mp4` AND `thinking-dark.mp4`? Dark mode uses the dark variant.
- Is the dist file actually the right size? `ls -lh dist/client/assets/mp4/` — should be ~49KB for the badge, not ~8MB (the original little-girl animation).

**"Video is the old one in dev mode but new one in production"**
Dev mode (`vite --host`) serves from `packages/client/src/assets/` directly. Production (`dist/`) requires either a rebuild or manual overwrite of the hashed dist file.
