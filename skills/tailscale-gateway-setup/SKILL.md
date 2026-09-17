---
name: "tailscale-gateway-setup"
description: "Tailscale serve setup on cloud OpenClaw gateway — \"Serve is not enabled\" journal gate, user-unit supervisor, laptop mesh WSAEACCES triage"
---

# Tailscale on the Cloud OpenClaw Gateway

Enable tailnet-only Control UI access on the Oracle VM gateway (`gateway.tailscale.mode: serve`). The transcript is evidence only — verify every mutable fact live over SSH. For connectivity failures before reaching this point, run oracle-vm-ssh-triage first.

## 1. Survey the instance over SSH in one call
SSH with the current key/IP (a key pasted into chat lands in `C:\Users\thadd\.openclaw\media\inbound\` — copy it to `~\.ssh\`, lock the ACL with `icacls <file> /inheritance:r /grant:r "thadd:F"`; file tools are sandboxed to the workspace, so copy with `exec Copy-Item`). Survey: `command -v openclaw tailscale node; tailscale status 2>&1 | head -6; pgrep -af 'openclaw.*gateway'; curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/`.
Check: gateway process, bind health (HTTP 200 on loopback), tailscaled active, tailnet peer IP known.

## 2. Inspect the gateway config without dumping secrets
The `read`/`write` file tools are sandboxed to the workspace and cannot reach the VM config; pipe a redacting python script via stdin: `Get-Content <script> -Raw | ssh ... "python3 -"`, and the script loads `~/.openclaw/openclaw.json` and prints only the `gateway` object with any token/secret/password/key string values replaced by `***`. Record `auth.mode`, `bind`, `tailscale.mode`, and `controlUi.allowedOrigins` — the onboarding wizard pre-seeds the `.ts.net` serve URL there, which is the target hostname for serve mode.
Check: current tailscale mode + the exact serve hostname known.

## 3. Identify the supervisor before touching anything
Run `systemctl --user list-units --no-pager | grep -i openclaw`, `ls ~/.config/systemd/user/`, and `loginctl show-user <user> -p Linger`. The wizard installs a systemd USER unit with `Linger=yes` — that unit is the gateway's supervisor. Never create a system-level OpenClaw unit: both units contend for the gateway-lifecycle state lock and the gateway crash-loops ("another OpenClaw process owns gateway-lifecycle"). If a stray system-level unit exists, remove it first (`sudo systemctl disable --now`, delete the file, `sudo systemctl daemon-reload`), then confirm `systemctl --user status openclaw-gateway` is active.
Check: exactly one supervisor — the user unit, Linger=yes.

## 4. Set serve mode and read the user journal
`openclaw config set gateway.tailscale.mode serve`, then restart via the user unit (`systemctl --user restart openclaw-gateway` or `openclaw gateway restart`). Diagnose startup with `journalctl --user -u openclaw-gateway -n 50 --no-pager` — system-level `journalctl -u` shows nothing for user units. A restart-loop breaker trips after 3 unclean boots in 300s and suppresses channel auto-start; when a human step is pending, `systemctl --user stop` the unit instead of letting it thrash.
Check: startup error captured from the user journal, or clean boot confirmed.

## 5. Clear the tailnet serve-enable gate (operator click)
First serve-mode boot fails with "Gateway failed to start: Serve is not enabled on your tailnet" plus a URL `https://login.tailscale.com/f/serve?node=<nodeKey>`. Only the operator's Tailscale login can open it — send that exact URL as the single ask and keep the unit stopped while waiting. After they confirm, start the unit and verify in order: `curl` returns 200 on `127.0.0.1:18789`, `sudo tailscale serve status` shows the hostname proxy, and `curl -s -o /dev/null -w '%{http_code}' https://<machine>.<tailnet>.ts.net/` from the VM itself returns 200.
Check: gateway active + serve proxy registered + tailnet URL answers 200 from the VM.

## 6. Verify the laptop mesh passes real packets
`tailscale ping <vm-ip>` only proves the daemon path (it works via DERP relays even when the OS tunnel is broken). Then test the OS path: native `ping` and `tailscale nc <vm-ip> <port>`. If daemon pings succeed but native ping = "General failure" and `tailscale nc` = WSAEACCES "forbidden by access permissions" while host routes exist (`route print -4` shows /32 routes via the local 100.x IP) and the adapter is Up, the TUN/WFP state is stale — `tailscale down`/`up` does NOT heal it; restart the Windows service `TailscaleIPN` (needs elevation; if blocked from the channel, hand the operator the one step: tray Quit + relaunch or reboot). Control UI auth over the mesh needs no gateway password: `gateway.auth.allowTailscale` defaults true in serve mode, so the operator's Tailscale identity satisfies the UI.
Check: laptop reaches the .ts.net URL, or the operator restart step is handed off.
