# Reference: Node Version Upgrade for hermes-web-ui (Tarball Method)

## Context

The `hermes-web-ui` repository requires `"node": ">=23.0.0"` in `package.json`. The user's managed Node install is at `~/.hermes/node/` with a symlink from `~/.local/bin/node`. The active version was v22.22.3, which satisfies production runtime (compiled `dist/` runs fine on Node 22) but blocks `npm run build` due to the engine check.

## Exact Upgrade Steps (from session 2026-05-20)

```bash
# 1. Stop all running Node processes
pkill -f "dist/server/index.js"
pkill -f "hermes_bridge"
sleep 2
ss -tlnp | grep 8648   # confirm port is free

# 2. Discover actual install path
which node                    # /home/thadd/.local/bin/node
readlink -f $(which node)   # /home/thadd/.hermes/node/bin/node
ls /home/thadd/.hermes/node/bin/   # node, npm, npx, corepack

# 3. Download latest v23 tarball
cd /tmp
curl -fsSL -o node-v23.tar.xz https://nodejs.org/dist/latest-v23.x/node-v23.11.1-linux-x64.tar.xz
du -h node-v23.tar.xz       # 30M

# 4. Back up old install
mv /home/thadd/.hermes/node /home/thadd/.hermes/node-backup-22

# 5. Extract new Node to same path
mkdir -p /home/thadd/.hermes/node
cd /home/thadd/.hermes/node
tar -xf /tmp/node-v23.tar.xz --strip-components=1

# 6. Verify chain
which node      # /home/thadd/.local/bin/node (symlink unchanged)
node --version  # v23.11.1
npm --version   # 10.9.2
```

## Rebuild After Upgrade

```bash
cd /home/thadd/hermes-web-ui-ekko
npm run build   # now passes the engine check
```

## Rolling Back

If something breaks, simply restore the backup directory:

```bash
rm -rf /home/thadd/.hermes/node
mv /home/thadd/.hermes/node-backup-22 /home/thadd/.hermes/node
node --version  # should show v22.22.3 again
```

## Key Insight: Production `dist/` vs Build-Time Engine Check

- `dist/server/index.js` (compiled server) runs fine on Node 22 — the engine check is an `npm` gate, not a runtime one.
- However, `npm run build` is blocked by `package.json` `engines` field.
- The `npm start` / `npm run dev:website` / `vite` commands are also blocked by npm.
- **Workaround without upgrading:** edit `"node": ">=22.0.0"` in `package.json`, then rebuild. But upgrading Node is cleaner and future-proof.
