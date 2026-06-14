#!/bin/bash
# Spock Infrastructure Watchdog — Silent when healthy, noisy when broken

declare -A CHECKS

# 1. Gateway health
HEALTH=$(curl -s --max-time 3 http://172.24.60.180:8648/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('gateway')=='running' else 1)" 2>/dev/null)
if [ $? -ne 0 ]; then
    CHECKS[gateway]="DOWN — no health response"
    # Auto-heal attempt
    pkill -f "dist/server/index.js" 2>/dev/null
    sleep 2
    bash /home/thadd/.hermes/webui/start-server.sh > /home/thadd/.hermes/webui/logs/auto-restart.log 2>&1 &
    CHECKS[gateway]+=" (restarted)"
else
    CHECKS[gateway]="OK"

    # 2. Ollama connectivity (only worth checking if gateway is up)
    API_KEY=$(grep OLLAMA_API_KEY /home/thadd/.hermes/.env 2>/dev/null | cut -d= -f2)
    OLLAMA_OK=$(curl -s --max-time 5 "https://ollama.com/v1/models" -H "Authorization: Bearer $API_KEY" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'data' in d else 1)" 2>/dev/null)
    if [ $? -eq 0 ]; then
        CHECKS[ollama]="OK"
    else
        CHECKS[ollama]="FAIL — Ollama API unreachable (token exhausted or network issue)"
    fi
fi

# 3. Cron heartbeat
if [ -f /home/thadd/.hermes/cron/.tick.lock ]; then
    AGE=$(($(date +%s) - $(stat -c %Y /home/thadd/.hermes/cron/.tick.lock)))
    if [ $AGE -gt 300 ]; then
        CHECKS[cron]="STALE — tick.lock is ${AGE}s old"
        rm -f /home/thadd/.hermes/cron/.tick.lock
        CHECKS[cron]+=" (force-cleared)"
    else
        CHECKS[cron]="OK"
    fi
else
    CHECKS[cron]="OK (no lock)"
fi

# 4. Database integrity
DB_OK=$(sqlite3 /home/thadd/.hermes/state.db "PRAGMA integrity_check;" 2>/dev/null | head -1)
if [ "$DB_OK" != "ok" ]; then
    CHECKS[state_db]="CORRUPT — $DB_OK"
else
    CHECKS[state_db]="OK"
fi

# 5. Disk space
USAGE=$(df /home/thadd/.hermes | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USAGE" -gt 90 ]; then
    CHECKS[disk]="CRITICAL ${USAGE}% full"
    # Auto-clean old sessions
    find /home/thadd/.hermes/sessions -mtime +7 -delete 2>/dev/null
    CHECKS[disk]+=" (cleaned sessions >7 days)"
elif [ "$USAGE" -gt 80 ]; then
    CHECKS[disk]="WARNING ${USAGE}% full"
else
    CHECKS[disk]="OK ${USAGE}%"
fi

# Report only if anything is not OK
HAS_ISSUES=0
for key in "${!CHECKS[@]}"; do
    [[ "${CHECKS[$key]}" == OK* ]] || { HAS_ISSUES=1; break; }
done

if [ $HAS_ISSUES -eq 1 ]; then
    echo "⚠️ SPOCK INFRASTRUCTURE ALERT — $(date)"
    echo "========================================="
    for key in gateway ollama cron state_db disk; do
        echo "  $key: ${CHECKS[$key]}"
    done
    echo ""
    echo "Actions taken where auto-repair was possible."
    echo "Check logs: /home/thadd/.hermes/webui/logs/auto-restart.log"
fi

# Always exit 0 — cron should not retry on our output code
exit 0
