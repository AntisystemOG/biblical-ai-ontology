# Oracle Cloud Migration Plan — Spock / OpenClaw Gateway
_Created 2026-09-08 02:35 CDT · Thad directive: move to Oracle Cloud hosting_

---

## 0. Why this migration makes sense
Current host: Dell Latitude 7380 (2-core i7-6600U, 16 GB RAM) — CPU-bound, SQLite stall-flaps killed the gateway 3× on Sep 6 night, watchdog now restarts it ~hourly. Oracle Cloud gives us a stable always-on host for the trading machine (Kalshi book, claims windows, 8:15 AM picks, peak-exit watcher).

## 1. Target shape

| Item | Choice | Why |
|---|---|---|
| VM shape | **A1.Flex 2 OCPU / 12 GB RAM** (Ampere ARM) | Always-Free eligible. OpenClaw runs fine on 2 cores/ARM; 12 GB RAM removes the SQLite stall pressure. |
| OS | Ubuntu 22.04 LTS (aarch64) | Best-supported for Node 20+ and Python 3.11+. |
| Region | **us-ashburn-1 (Virginia)** — or us-chicago-1 if Oracle offers it at signup | Kalshi + NWS are US-East-friendly; lowest-latency US region wins at signup time. |
| Boot volume | 100 GB | Node modules + Python env + workspace + logs. |
| Networking | 1 public IP, SSH key-only, firewall: 22 (from home IP only), 18789 bound to localhost (Access via Tailscale or SSH tunnel, never public) | Gateway must never face the open internet. |

**Always-Free warning:** idle Always-Free instances can be reclaimed — keep the VM "active" (the OpenClaw workload itself keeps CPU moving; if needed add a 5-min CPU tick or upgrade to Pay-As-You-Go ~$15/mo to remove reclamation risk).

## 2. What moves (the full inventory)

### A. OpenClaw core
- `~/.openclaw/` config tree: `openclaw.json` (gateway config, model pins, plugin settings), `workspace/` (AGENTS.md, MEMORY.md, SOUL.md, REGISTRY.md, memory/*.md, data/, agents/).
- Secrets: Kalshi RSA key pair (trade API), Telegram bot token, any model-provider keys → re-enter as env/secrets on the new box, **never copy plaintext key files through chat**. Use `openclaw`'s own secret store or systemd EnvironmentFile with 0600 perms.
- Telegram channel config (bot token) — needs the same bot, new host = same token works.

### B. External project folders (must be copied to cloud)
- `C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner` → `~/kalshi/edge-scanner/`
- `C:\AI Projects\Prediction Market\Kalshi` (kalshi_client.py at parent)
- `C:\AI Projects\AI Tools and Skills` (reference library — can sync later, low priority)
- Desktop `Portfolio Positions` CSVs → sync to cloud or keep local + OneDrive.
- OneDrive `Spocks Reports` → cloud path `~/spocks-reports/` (financial advisor, whale watch outputs).

### C. Python environment
- Python 3.11+ on Ubuntu (ARM wheels exist for everything we use: pandas, numpy, requests, pyannote optional → skip whisper/torch unless needed; the trading stack is stdlib + pandas only).
- pip install: `pandas numpy requests` (Edge Scanner deps are light).

### D. Scheduled work that must survive the move
- All OpenClaw crons (they live in the gateway config — they migrate with `openclaw.json`).
- Windows Task Scheduler items that DON'T migrate: **OpenClaw Watchdog** (replaced by systemd unit with Restart=always + a lightweight watchdog script), gateway.vbs/gateway.cmd (replaced by systemd service), load governor (not needed on cloud).
- Kalshi cron semantics: all crons use America/Chicago — set VM timezone to America/Chicago (`timedatectl set-timezone America/Chicago`) so every cron expr stays wall-time-correct.

## 3. Migration phases

### Phase 0 — Prep (laptop, tonight, ~30 min)
1. `git push` the workspace (everything committed — verify `git status` clean).
2. Zip the full `~/.openclaw/` tree EXCLUDING: `media/inbound/` (large), `.openclaw/tmp/` scratch, session transcripts (optional — keep for continuity), `node_modules`.
3. Export the Kalshi edge scanner folder to a tarball.
4. Output: `spock_migrate_bundle.tar.gz` (est. <500 MB).

### Phase 1 — Oracle VM bootstrap (~1 hr, needs Thad for Oracle console)
1. Thad creates the OCI account/VM (Always-Free A1) and sends me: public IP + SSH key (or I generate the keypair on the laptop and he pastes the public key into the Oracle console).
2. I provision over SSH: `apt update && upgrade`, install Node 22 LTS, Python 3.12, git, `timedatectl set-timezone America/Chicago`.
3. Install OpenClaw: `npm i -g openclaw` → restore `~/.openclaw/` from the bundle → `openclaw doctor`.
4. systemd units: `openclaw-gateway.service` (Restart=always, RestartSec=10) + `kalshi-watchdog.timer` (the v3 logic ported to a shell script + systemd timer).
5. Telegram + Kalshi creds: enter via the OpenClaw secret store or env file (Thad pastes into the VM over SSH, never through chat).

### Phase 2 — Parallel burn-in (24-48 hrs, both machines alive)
1. Cloud gateway runs with **all crons disabled** (or `session.dmScope` pointed to a test channel) — validate: gateway up, doctor clean, Kalshi auth OK, Telegram auth OK.
2. Flip ONE cron at a time (start with the Kalshi position monitor, then daily-weather-picks) to the cloud gateway; keep the laptop's copy disabled for that job. Watch for 24 hrs.
3. Verify: digest.py runs on ARM, kalshi_client.py signs correctly, the settlement watcher fires, memory files append.

### Phase 3 — Cutover (a quiet window, e.g. a Sunday 2 AM)
1. Final workspace sync (git pull on cloud).
2. Disable ALL crons on laptop gateway; enable ALL crons on cloud gateway.
3. Send one Telegram test from the cloud gateway to confirm delivery.
4. Leave the laptop gateway running but idle for 72 hrs as a fallback (kill it only after a clean week).

### Phase 4 — Decommission laptop crons
1. Remove the Windows Scheduled Tasks (OpenClaw Watchdog, OpenClaw Gateway) after 72-hr clean run.
2. Keep the laptop as a cold backup (the workspace is in git; the Kalshi keys live in the cloud secret store).

## 4. Risks & mitigations

| Risk | Mitigation |
|---|---|
| ARM wheel gaps for the Python stack | Trading stack is stdlib+pandas — all ARM-safe. Skip torch/whisper unless needed. |
| Oracle reclaims idle Always-Free VM | Pay-As-You-Go upgrade (~$15/mo) or a 5-min CPU tick; the OpenClaw workload is constant anyway. |
| Kalshi API blocked from cloud IP (datacenter IP ranges sometimes flagged) | Test in Phase 2 burn-in BEFORE cutover; if blocked, route via a residential proxy or keep the book-monitoring on laptop until Kalshi whitelists. |
| Secrets exposure during transfer | Kalshi/Telegram keys entered directly on the VM over SSH — never through chat, never in the bundle. |
| Dual-gateway conflict during burn-in | Only ONE machine's crons enabled per job at any time — enforced in Phase 2 checklist. |
| Telegram delivery changes IP | Telegram bots don't care about source IP — no risk. |
| Latency to Kalshi trade API (Chicago region VM vs East-Coast exchange) | Sub-50ms either way — immaterial for our order sizes. |

## 5. What Thad needs to do (the only blockers needing him)
1. Create the Oracle account + Always-Free VM (or give me the tenancy OCID if an account exists).
2. Approve the shape/region choice.
3. Paste-in the SSH public key during VM creation (I'll generate it and hand it to him).
4. Approve the burn-in → cutover timing.

## 6. Open questions for Thad
1. **Always-Free vs Paid?** Always-Free A1 (4 OCPU/24GB total across instances) is generous — but reclamation risk exists on true-idle instances. Our workload is constant so it's likely fine; if he wants zero risk, PAYG ~$15/mo.
2. **Region preference?** Default: **us-ashburn-1** (Virginia) — Oracle's established US-East region, best for Kalshi + NWS latency. If a Chicago region is offered at signup, prefer it (lowest latency to the local NWS office). Either works; the difference is immaterial for our order sizes.
3. **Keep the laptop as hot standby or cold backup?** Recommend cold backup (it CPU-throttles anyway; running two gateways in parallel risks double-firing crons if I ever mis-flip a switch).

---

## 7. The one-page checklist (for execution day)

```
[ ] Laptop: git status clean, bundle created, checksum logged
[ ] Oracle VM: Ubuntu 22.04 ARM, tz=America/Chicago, SSH locked to key
[ ] openclaw installed + doctor exit 0
[ ] ~/.openclaw restored, git pulled
[ ] Kalshi client: auth test order-check (read-only) passes
[ ] Telegram: test message delivered
[ ] systemd: gateway enabled+active, watchdog timer armed
[ ] Crons: phase 2 (monitor only) 24h clean
[ ] Crons: full flip + 72 hr parallel quiet on laptop
[ ] Laptop: crons disabled, gateway.service stopped
[ ] Post-cutover: 24 hr of normal signals (picks, monitor, settle sweep)
```

---
_End of plan. Questions → Telegram; execution → next quiet window Thad approves._