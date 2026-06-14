#!/bin/bash
# WebUI Customization Auto-Apply Script
# Run this after any WebUI update/rebuild to restore customizations

echo "=== Spock WebUI Customizer ==="

WEBUI_DIR="/home/thadd/hermes-web-ui-ekko"
IMAGES_DIR="/mnt/c/Users/thadd/.hermes/images"

# 1. Replace thinking avatar with Star Trek badge
echo "Replacing thinking avatar with Star Trek badge..."
if [ -f "$IMAGES_DIR/startrek badge.mp4" ]; then
    cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-light.mp4"
    cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-dark.mp4"
    echo "OK - thinking videos replaced"
else
    echo "ERROR: Star Trek badge video not found at $IMAGES_DIR/startrek badge.mp4"
    exit 1
fi

# 2. Rebuild client assets
echo "Rebuilding client assets (this takes ~2 minutes)..."
cd "$WEBUI_DIR"
/home/thadd/node26/bin/npm run build 2>&1 | tail -5

echo ""
echo "Done. New video is in: $WEBUI_DIR/dist/client/assets/mp4/"
echo "If the server is running, it auto-serves the new files (no restart needed for static assets)."