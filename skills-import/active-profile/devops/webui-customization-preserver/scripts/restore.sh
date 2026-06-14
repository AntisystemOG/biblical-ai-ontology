#!/bin/bash
set -e

WEBUI_DIR="/home/thadd/hermes-web-ui-ekko"
IMAGES_DIR="/mnt/c/Users/thadd/.hermes/images"

echo "[1/5] Stopping server..."
pkill -f "node.*dist/server/index.js" || true
sleep 2

echo "[2/5] Restoring Spock logo..."
cp "$IMAGES_DIR/logo.png" "$WEBUI_DIR/packages/client/public/logo.png"
cp "$IMAGES_DIR/logo.png" "$WEBUI_DIR/packages/client/src/assets/logo.png"

echo "[3/5] Restoring thinking videos..."
cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-light.mp4"
cp "$IMAGES_DIR/startrek badge.mp4" "$WEBUI_DIR/packages/client/src/assets/thinking-dark.mp4"

echo "[4/5] Rebuilding..."
cd "$WEBUI_DIR"
~/node26/bin/npm run build 2>&1 | tail -5

echo "[5/5] Verifying dist output..."
test -f "$WEBUI_DIR/dist/client/logo.png" && echo "  ✓ logo.png in dist"
test -f "$WEBUI_DIR/dist/client/assets/mp4/thinking-"*.mp4 && echo "  ✓ thinking video in dist"

echo ""
echo "Done. Now restart the server WITH NODE_ENV=production:"
echo "  export NODE_ENV=production HERMES_WEB_UI_HOME=/home/thadd/.hermes/webui"
echo "  /home/thadd/node26/bin/node dist/server/index.js"
