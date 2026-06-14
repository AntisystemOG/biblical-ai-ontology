# WebUI Running Checkout / Rebuild Pitfall

## Symptom

The Hermes WebUI is running, but behavior does not match the source files you are editing. Changes to `packages/server/src/shared/providers.ts`, client components, or branding assets do not take effect.

## Root Cause

There are **two WebUI checkouts** on this system:
- `/home/thadd/hermes-web-ui-ekko` — the current, active checkout used by the launcher script
- `/mnt/c/Users/thadd/hermes-web-ui` — an older checkout on the Windows filesystem

The launcher script `~/.hermes/webui/start-server.sh` explicitly `cd`s into `/home/thadd/hermes-web-ui-ekko` and runs `dist/server/index.js` from there. Editing files in `/mnt/c/Users/thadd/hermes-web-ui` has no effect on the running server.

## Detection

```bash
cat ~/.hermes/webui/start-server.sh | grep -E "cd |node dist"
# Expected:
#   cd /home/thadd/hermes-web-ui-ekko
#   exec /home/thadd/node26/bin/node dist/server/index.js

git -C /home/thadd/hermes-web-ui-ekko log --oneline -1
git -C /mnt/c/Users/thadd/hermes-web-ui log --oneline -1
```

## Fix

Always operate in the active checkout:
```bash
cd /home/thadd/hermes-web-ui-ekko
```

After any source edit, rebuild and restart:
```bash
export NODE_ENV=production
/home/thadd/node26/bin/npm run build   # or npm install if dependencies changed
pkill -f "node dist/server/index.js"
sleep 2
bash ~/.hermes/webui/start-server.sh
```

## Related Files

- Active source: `/home/thadd/hermes-web-ui-ekko/packages/server/src/`
- Active build output: `/home/thadd/hermes-web-ui-ekko/dist/`
- Launcher script: `/home/thadd/.hermes/webui/start-server.sh`
- Windows-side copy (not active): `/mnt/c/Users/thadd/hermes-web-ui/`
