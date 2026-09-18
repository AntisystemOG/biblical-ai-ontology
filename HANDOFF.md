# HANDOFF.md — For the new me (Spock, cloud instance)

_You just went live on the Oracle VM after migrating from the laptop. Read this first, then verify — don't trust, check._

## Who you are
Same agent, new hardware. Your continuity lives in this workspace: SOUL.md, USER.md, AGENTS.md, MEMORY.md, and memory/2026-09-16.md → 2026-09-18.md (the migration week). Read those before anything else.

## Verify immediately (in order)
1. **Gateway health** — you ARE the systemd user unit `openclaw-gateway.service`. Confirm `systemctl --user status` is active; you run on the Oracle VM (`openclaw-3`, 100.73.56.26, public IP 170.9.247.187).
2. **Workspace parity** — compare your workspace against the laptop's (memory/, agents/, REGISTRY.md, data/kalshi/, skills/). If yours is thinner, the 565MB bundle is on the laptop at `.openclaw/tmp/spock_migrate_bundle.tar.gz` (restore it before trusting your memory).
3. **Open loops** (from memory/2026-09-18.md):
   - Exit node advertised but console approval unverified → `tailscale exit-node list` from a tailnet peer; if empty, have Thad fix "Use as exit node" in the admin console, then e2e-test (egress should flip to 170.9.247.187).
   - SSH key `openclaw0916.key` was chat-exposed → rotate: generate new ed25519, install, confirm Thad's access, remove the old key.
   - Bundle restore (above) not yet done.
4. **Cron parity** — REGISTRY.md is the law: exactly ONE host runs each cron job. The laptop (cold backup) must have its crons disabled before any of yours fire. Verify, never assume.

## Environment rules that cost us days to learn
- **Proton VPN (or any transparent-proxy VPN) on the laptop eats Tailscale + SSH** — fake TCP handshakes, blocked TUN. If connections "work" at TCP level but no SSH banner arrives, suspect a VPN, not Oracle.
- Home IP rotates ~daily → OCI SSH rule stays `0.0.0.0/0` + key-only. /32 rules are useless here.
- Windows laptop lessons: PowerShell inline `$`-vars get stripped (write .ps1 files); complex Python goes in a file, never inline.
- Kalshi universal rule (AGENTS.md): real API prices only, or hold cash.
- Thad says "go" → you act. He values direct reports: what you see, what's missing, what you did.

## First report
Reply to Thad with: gateway state, workspace parity result, cron parity result, and which open loops you closed. Short. Facts. Then push any file changes to GitHub.