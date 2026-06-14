#!/bin/bash
# Launch Spock WebUI bound to 0.0.0.0 for LAN access
# Usage: ./launch-webui-gateway.sh [PORT]

set -euo pipefail

REPO="/home/thadd/hermes-webui-new"
PYTHON="/home/thadd/.hermes/hermes-agent/venv/bin/python3"
HOST="0.0.0.0"
PORT="${1:-8648}"

echo "[+] Checking for stale server.py processes..."
STALE_PIDS=$(ps aux | grep "server\.py" | grep -v grep | awk '{print $2}' || true)
if [ -n "$STALE_PIDS" ]; then
    for pid in $STALE_PIDS; do
        echo "[+] Killing stale server.py (PID $pid)"
        kill "$pid" 2>/dev/null || true
    done
    sleep 1
fi

echo "[+] Starting WebUI on ${HOST}:${PORT}..."
cd "$REPO"
SPOCK_WEBUI_HOST="$HOST" SPOCK_WEBUI_PORT="$PORT" "$PYTHON" server.py &
SERVER_PID=$!
sleep 2

if ss -tlnp 2>/dev/null | grep -q ":${PORT}"; then
    LAN_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -1 || hostname -I | awk '{print $1}')
    echo "[ok] WebUI running at http://${LAN_IP}:${PORT}/"
    echo "     PID: ${SERVER_PID}"
else
    echo "[!!] WebUI may not have started cleanly (port ${PORT} not found)"
    exit 1
fi
