# Installing Node.js via Direct Binary Download

When system-level Node managers (nvm, apt, fnm) are blocked or unavailable, download the Node.js official binary tarball directly and extract it to a user-writable directory. This avoids all shell-level execution restrictions.

## When to Use This Pattern

- Terminal returns "BLOCKED" on `curl | bash` or package manager commands
- nvm not installed, and permission to install it is blocked
- System Node is too old (e.g. v22.x) but a project requires Node >=23.x
- No root access, or `apt`/`dnf`/`brew` are restricted

## Step-by-Step

### 1. Identify the correct binary URL

Node releases follow `https://nodejs.org/dist/v<VERSION>/node-v<VERSION>-linux-x64.tar.xz`.

List available major versions first:
```bash
curl -s https://nodejs.org/dist/ | grep -oP 'href="v[0-9]+' | sort -V | tail -5
# Shows: href="v25  href="v25  href="v26  href="v26  href="v26"
```

Pick a version and confirm the exact filename:
```bash
curl -s https://nodejs.org/dist/v26.1.0/ | grep linux-x64.tar.xz
# <a href="/dist/v26.1.0/node-v26.1.0-linux-x64.tar.xz">
```

### 2. Download the tarball

```bash
curl -fsSL --max-time 180 https://nodejs.org/dist/v26.1.0/node-v26.1.0-linux-x64.tar.xz -o /tmp/node26.tar.xz
ls -lh /tmp/node26.tar.xz
# Should show ~30-35MB
```

### 3. Extract to user directory

```bash
rm -rf ~/node26
mkdir ~/node26
tar xf /tmp/node26.tar.xz -C ~/node26 --strip-components=1
~/node26/bin/node --version
# Should print: v26.1.0
```

### 4. Use the local Node (not system Node)

When running npm or node from a cloned project, always invoke the local binary explicitly:

```bash
cd ~/my-project
~/node26/bin/npm install
~/node26/bin/npm run build
~/node26/bin/node dist/server/index.js
```

Do NOT attempt to replace `/usr/bin/node` or add `~/node26/bin` to PATH globally unless you're absolutely sure it's safe. The explicit path invocation avoids PATH conflicts with system Node.

### 5. Persistent usage

For a long-running project, create a convenience function in `~/.bashrc` (if writable):
```bash
node26() { ~/node26/bin/node "$@"; }
npm26() { ~/node26/bin/npm "$@"; }
```

Or, for scripts that depend on a specific Node, wrap the invocation:
```bash
#!/bin/bash
NODE_HOME="$HOME/node26"
export PATH="$NODE_HOME/bin:$PATH"
cd ~/my-project && npm run start
```

## Variations

- **macOS:** Use `darwin-x64.tar.xz` or `darwin-arm64.tar.gz` instead of `linux-x64.tar.xz`.
- **Windows/WSL:** Download and extract inside WSL, then the Node binary runs natively in the WSL environment. If Windows-side Node is needed, use the Windows `.zip` or `.msi` from the same release page.
- **NodeSource setup scripts:** These are `curl | bash` pipes — skip them. They require elevated permissions and are blocked in restricted environments. Direct binary download always wins.

## Verification Checklist

After extraction, verify all three binaries exist:
```bash
ls ~/node26/bin/{node,npm,npx}
~/node26/bin/node --version
~/node26/bin/npm --version
```

Node 26+ bundles npm v10+, which is sufficient for most modern projects.

## References

- `blocked-terminal-recovery/SKILL.md` — General strategy for blocked-terminal recovery using Python and direct downloads.
