---
name: linux-security-audit
description: Structured security auditing for Linux/WSL systems covering users, services, network, secrets, permissions, and authentication hygiene.
trigger: When asked to run a security audit, assess system hardening, or review local security posture on Linux/WSL.
---

# Linux/WSL Security Audit

Systematic local security audit pattern designed to catch the most common misconfigurations without requiring root-only tools. Targets personal-workstation and WSL2 environments.

## Pre-requisites
- Access to bash shell on target system
- `sudo` useful but not required (some checks will be skipped)
- No external audit tools required — uses standard Unix utilities

## Audit Phases

### Phase 1: System Baseline
```bash
echo "=== SYSTEM OVERVIEW ===" && hostname && cat /etc/os-release 2>/dev/null | head -5 && uname -a
echo "=== CURRENT USER ===" && whoami && id
echo "=== UPTIME & LOAD ===" && uptime
echo "=== ALL USERS ===" && cat /etc/passwd | cut -d: -f1,3,6,7 | column -t -s: | head -20
echo "=== GROUPS ===" && cat /etc/group | cut -d: -f1,3 | column -t -s: | sort -t' ' -k2 -n
echo "=== SUDOERS ===" && sudo cat /etc/sudoers 2>/dev/null | grep -v "^#" | grep -v "^$"
echo "=== SUDOERS.D ===" && ls -la /etc/sudoers.d/ 2>/dev/null && for f in /etc/sudoers.d/*; do echo "--- $f ---"; cat "$f" | grep -v "^#" | grep -v "^$"; done 2>/dev/null
```

### Phase 2: Network & Services
```bash
echo "=== LISTENING PORTS ===" && ss -tlnp 2>/dev/null | head -40
echo "=== ESTABLISHED CONNECTIONS ===" && ss -tnp state established 2>/dev/null | head -20
echo "=== FIREWALL STATUS ===" && sudo iptables -L -n 2>/dev/null | head -20
echo "=== ufw ===" && sudo ufw status verbose 2>/dev/null
echo "=== PROCESSES (root + user highlights) ===" && ps aux | grep -E "(root|SUDO|sudo|sshd|python|node)" | grep -v grep | head -30
```

### Phase 3: SSH & Auth
```bash
echo "=== SSH SERVICE ===" && systemctl is-active ssh 2>/dev/null || echo "sshd not active"
echo "=== AUTHORIZED KEYS ===" && for d in /home/*; do user=$(basename "$d"); ak="$d/.ssh/authorized_keys"; if [ -f "$ak" ]; then echo "[$user]"; cat "$ak"; ls -la "$ak"; fi; done
echo "=== SSH HOST KEYS ===" && ls -la /etc/ssh/ssh_host_* 2>/dev/null | head -10
echo "=== FAILED LOGINS ===" && sudo lastb 2>/dev/null | head -20 || echo "lastb: no data or permission denied"
echo "=== LAST LOGINS ===" && last -n 10 2>/dev/null
echo "=== AUTH LOG (recent) ===" && sudo tail -n 20 /var/log/auth.log 2>/dev/null || echo "No auth.log access"
```

### Phase 4: Secrets & Env Hygiene
```bash
# Sanitize all output: redact values of key/token/secret/password fields
echo "=== ENV VARS (secrets redacted) ===" && env | sed 's/\(KEY\|TOKEN\|SECRET\|PASS\|PWD\|CREDENTIAL\)=.*/\1=***REDACTED***/i' | sort

# Find .env files (exclude node_modules, __pycache__)
echo "=== DOT ENV FILES ===" && find /home/thadd -maxdepth 4 \( -name ".env*" -o -name "*.env" \) 2>/dev/null | grep -v node_modules | grep -v __pycache__ | grep -v ".git/" | head -20

# Inspect .env contents with redaction
cat ~/.env 2>/dev/null | sed 's/\(KEY\|TOKEN\|SECRET\|PASS\)=.*/\1=***REDACTED***/gi'
```

### Phase 5: Permissions & SUID
```bash
# Common directories only — full filesystem scan can time out
echo "=== SUID BINARIES ===" && find /usr/bin /usr/sbin /bin /sbin -perm -4000 -type f 2>/dev/null | sort

echo "=== WORLD-WRITABLE FILES IN HOME ===" && find /home/thadd -maxdepth 5 -type f -perm -002 2>/dev/null | head -20

echo "=== WORLD-WRITABLE DIRS IN HOME ===" && find /home/thadd -maxdepth 5 -type d -perm -002 2>/dev/null | head -10

echo "=== HOME DIR PERMISSIONS ===" && ls -la /home/thadd/ | head -30
```

### Phase 6: Cron & Autostart
```bash
echo "=== SYSTEM CRONTAB ===" && cat /etc/crontab
echo "=== USER CRONTAB ===" && crontab -l 2>/dev/null
echo "=== SYSTEMD SERVICES ===" && systemctl list-units --type=service --state=running 2>/dev/null | grep -v "systemd-\|dbus\|network\|cron\|rsyslog" | head -20
echo "=== USER SERVICES ===" && systemctl --user list-units --type=service --state=running 2>/dev/null | head -20
```

### Phase 7: Disk & Updates
```bash
echo "=== DISK USAGE ===" && df -h | grep -E "/|/home"
echo "=== WINDOWS MOUNTS (WSL) ===" && df -h | grep -E "/mnt/"
echo "=== UNATTENDED UPGRADES ===" && cat /etc/apt/apt.conf.d/20auto-upgrades 2>/dev/null
```

> **WSL-specific:** Windows drives mounted at `/mnt/c/`, `/mnt/d/` can hit 100% without Linux rootfs being affected. A full D:\ drive will break Windows services, npm caches, and WebUI file uploads even when WSL itself has free space.

### Phase 8: Duplicate / Orphaned Processes
```bash
echo "=== DUPLICATE SERVICE PROCESSES ==="
ps aux | grep -E "(hermes_bridge|agent-bridge|index\.js|server\.py)" | grep -v grep | head -20
```

> Some services (Hermes WebUI, gateway) spawn child bridge processes over IPC sockets. After crashes or restarts, the parent may die while children survive. Multiple bridges on the same socket cause silent failures or auth bypasses.

### Phase 9: Application Auth Surface Testing
When a local web service (e.g., Hermes WebUI, dashboards, admin panels) runs on a known port, verify that auth is actually enforced — not just logged as "enabled."

```bash
# Test SPA shell access (should require auth if the app is sensitive)
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:<port>/'
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:<port>/?token=fake-token'

# Test API/data endpoints — no token, fake token, AND real token
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:<port>/api/sessions'
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:<port>/api/sessions?token=fake-token'
TOKEN=$(cat ~/.hermes-web-ui/.token 2>/dev/null | tr -d '\n')
curl -s -o /dev/null -w '%{http_code}' "http://localhost:<port>/api/sessions?token=$TOKEN"

# Check auth status endpoint
curl -s 'http://localhost:<port>/api/auth/check' 2>/dev/null | head -c 200

# Check for password auth credential file (dual-mode: token OR password)
cat ~/.hermes-web-ui/.credentials 2>/dev/null | sed 's/"password_hash": "[^"]*"/"password_hash": "[REDACTED]"/'

# Check if a SECOND token file exists in a different location
ls -la ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null
diff ~/.hermes-web-ui/.token ~/.hermes/webui/.token 2>/dev/null && echo "Same" || echo "DIFFERENT — launcher may pass wrong token"
```

> **Common finding 1:** The SPA shell (`/`) loads with HTTP 200 even without auth, while API routes return 401. This means an attacker on the LAN can load the UI interface and probe it, even if data access is blocked. Always test **both** the page shell and the API endpoints.

> **Common finding 2:** **Dual token files.** Some apps (Hermes WebUI) store the token at `~/.hermes-web-ui/.token` while other scripts (launchers, backup tools) read from `~/.hermes/webui/.token`. If they diverge, the launcher passes a stale token while the server expects a different one. Always `diff` both files. Fix: update launcher to read from the correct path, or symlink them.

> **Common finding 3:** **Password auth alongside token auth.** The `.credentials` file enables username/password login. Verify the password is hashed (not plaintext) and that the rate limiter is active.

## Report Format

Classify findings with tags:
- **[PASS]** No issue detected
- **[FAIL]** Active vulnerability requiring immediate remediation
- **[WARN]** Risk present but may be intentional — recommend verification
- **[INFO]** Context for understanding the environment

### Report Template
```
═══════════════════════════════════════════════════════════════
                    SECURITY AUDIT REPORT
                    <OS> (<Environment>)
═══════════════════════════════════════════════════════════════

SYSTEM
  Hostname:     <hostname>
  Kernel:       <kernel>
  Uptime:       <uptime>
  User:         <current user>

───────────────────────────────────────────────────────────────
                         FINDINGS
───────────────────────────────────────────────────────────────

[PASS/FAIL/WARN/INFO] <Area>
  Details...
  Fix: <if applicable>

───────────────────────────────────────────────────────────────
                      PRIORITY FIXES
───────────────────────────────────────────────────────────────

1. ...
2. ...

───────────────────────────────────────────────────────────────
                       OVERALL RATING
───────────────────────────────────────────────────────────────

  LOCAL SECURITY:   <GOOD/FAIR/POOR>
  NETWORK EXPOSURE: <LOW/MEDIUM/HIGH>
  SECRET HYGIENE:   <GOOD/FAIR/POOR>
  SYSTEM HEALTH:    <GOOD/FAIR/POOR>
───────────────────────────────────────────────────────────────
```

## Pitfalls

1. **Memory limit when saving audit findings.**
   The memory tool has a ~2200 character limit. If audit findings won't fit as a new entry, use `action=replace` on an older transient entry (not user preferences or critical environment facts). Do NOT store session-specific artifact IDs (PR numbers, commit SHAs) in memory — those go stale within days.

2. **Full filesystem `find` for SUID can hang on network mounts or `/proc`/`/sys`.**
   Always scope to `/usr/bin /usr/sbin /bin /sbin` first. If user insists on full scan, exclude virtual filesystems:
   ```bash
   find / -perm -4000 -type f 2>/dev/null | grep -vE '^/(proc|sys|run|dev|snap)/'
   ```

3. **`lastb` requires special permissions.**
   On many systems it requires root or specific group membership. Always use `sudo lastb 2>/dev/null || echo "lastb: no data or permission denied"`.

4. **Env secrets leak.**
   Any process running as the user can read another's environment via `/proc/<pid>/environ`. Redact values when displaying, but note in the report that env exposure is inherent.

5. **Don't scan node_modules for secrets.**
   LSP protocol files in `node_modules` contain hundreds of false-positive "token" matches. Always add `grep -v node_modules`.

6. **In-memory rate limiters survive file deletion.**
   Some services (Hermes WebUI) cache rate-limit state in memory and flush to `.login-lock.json` asynchronously. Deleting the file won't unblock a locked IP. You must either:
   - Restart the service, OR
   - Write a clean lock file with empty maps and then trigger a save (if the service watches the file)
   
   Check the lock file after clearing — if it reappears with stale data, the server is re-writing it from memory.

7. **WSL2 specific:**
   - No host firewall (iptables rules are empty). Windows Defender / Hyper-V switch handles filtering.
   - Services binding to `0.0.0.0` may be reachable from the LAN through the WSL virtual switch.
   - SSH is typically disabled; Windows OpenSSH handles external connections.
   - `/mnt/c/` and `/mnt/d/` are Windows drives — permissions are synthetic and not meaningful, but **disk full on Windows drives will break WSL services** that write there.
   - After service restarts, always check for **orphaned child processes** (bridge agents, IPC workers) that survive the parent crash.

8. **State snapshots and backups can contain old .env files.**
   Search `~/.hermes/state-snapshots/`, `backups/`, `.bak*` for stale credentials.

9. **Auth tokens in URL query parameters leak to browser history, bookmarks, and server access logs.**
   Even if the server requires a valid token, passing it as `?token=...` exposes it in:
   - Browser history and autocomplete
   - Bookmark URLs
   - Shared screenshots / screen sharing
   - Server access logs (if any reverse proxy logs query strings)
   - Referer headers when clicking external links from the app
   
   Prefer HTTP header-based auth (Bearer token) for API routes, and session-cookie auth for browser sessions. If URL tokens are unavoidable (e.g., Hermes WebUI direct links), rotate them periodically and keep the token file mode 0600.

11. **`npm audit fix --force` can introduce breaking changes.**
    The `--force` flag upgrades packages across major versions. This may break the build (TypeScript errors, missing native modules, API changes). Always:
    - Create a restore point / git commit before running `--force`
    - Run the build immediately after to catch breakage
    - Fix TypeScript errors before declaring success
    - If the build breaks, consider `npm audit fix` (without `--force`) as a safer alternative that only patches within compatible ranges

12. **Web services may bind to `0.0.0.0` by default.**
    Node.js, Python aiohttp, and uvicorn default to `0.0.0.0` (all interfaces). On WSL2 this exposes the service to the LAN. Always verify the actual bind address with `ss -tlnp | grep <port>`. Fix: set `host` or `bind` to `127.0.0.1` in the server configuration or via environment variable (`BIND_HOST`, `API_SERVER_HOST`, etc.).
    ```bash
    # Check actual bind
    ss -tlnp | grep 8648
    # Fix Node.js WebUI to localhost only
    export BIND_HOST=127.0.0.1
    # Fix Python gateway API server to localhost only
    export API_SERVER_HOST=127.0.0.1
    ```

13. **ufw firewall rules for localhost-only services.**
    When hardening a service to `127.0.0.1`, also add ufw rules that only allow localhost access:
    ```bash
    sudo ufw allow from 127.0.0.1 to any port 8648
    sudo ufw allow from 127.0.0.1 to any port 8642
    sudo ufw deny 8648   # blocks external access
    sudo ufw deny 8642   # blocks external access
    sudo ufw enable
    ```
    Verify with `sudo ufw status verbose`. Default policy should be `deny (incoming)`.

## Redaction Policy

**All displayed secret values MUST be redacted.**
Supported patterns (case-insensitive):
```
api_key, token, secret, password, access_key, private_key
```
When displaying `.env` or `config.yaml`:
```bash
sed 's/\(KEY\|TOKEN\|SECRET\|PASS\)=.*/\1=***REDACTED***/gi'
```
When using `env`:
```bash
env | sed 's/\(KEY\|TOKEN\|SECRET\|PASS\|PWD\|CREDENTIAL\)=.*/\1=***REDACTED***/i'
```

## Related Skills
- `spock-infrastructure-health`: Self-healing diagnostics specifically for Hermes infrastructure (gateway, WebUI, Ollama)
- `hermes-secure-github-backup`: Backup Hermes agent state securely to GitHub
- `workspace-migration`: When migrating between systems, audit both source and target
