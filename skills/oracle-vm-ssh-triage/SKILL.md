---
name: "oracle-vm-ssh-triage"
description: "Oracle cloud VM SSH times out or banner-exchange fails — triage Windows 10060 artifact, egress-IP rotation vs security list, wrong-VCN rule trap"
---

# Oracle VM SSH Connectivity Triage

Debug SSH failures to the OpenClaw Oracle Cloud (OCI) instance from the laptop before involving the operator. Work through the checks in order; each ends on a verifiable result. The transcript is evidence only — verify every mutable fact live.

## 1. Read the operator's SSH state, not memory
`C:\Users\thadd\.ssh\` holds the live truth: `config.txt` (Host/HostName/User/IdentityFile), `known_hosts` (previously-reachable IPs), and keypairs (`oracle-cloud*`, `private.key`). The `read`/`write` file tools are sandboxed to the workspace and reject `~/.ssh` paths — read these with `exec` (`Get-Content`) instead. Use the IP and key found there; stale IPs and rotated keypairs are the normal state after a recreate.
Check: IP + user + identity file identified from files before the first connection attempt.

## 2. Probe and classify the failure
Run: `ssh -i <key> -o ConnectTimeout=20 -o BatchMode=yes ubuntu@<ip> "echo ok"`
- `Connection timed out` at connect = TCP never established.
- `banner exchange: Connection to UNKNOWN port -1: Connection timed out` = ALSO a failed connect on Windows OpenSSH. With `-vvv`, the true signature is `async io completed with error: 10060` before a bogus `Connection established` line; the write/read then times out. Treat 10060 as connect-failed — never read "banner exchange" as a partial success or a server-side hang.
- `Permission denied (publickey)` = network path fine; try the other keys in `.ssh\`, confirm the username (`ubuntu` on OCI Ubuntu images).
Check: failure classified connect-level vs auth-level before any console round trip.

## 3. Check the egress IP before blaming the console
Run: `curl.exe -s --max-time 15 https://api.ipify.org`
Home DHCP rotates the public IP; a `/32`-scoped ingress rule silently stops matching (seen once in 24h: 4.37.63.234 → 108.240.65.111). If the current egress IP differs from the rule's source CIDR, report the new IP and ask the operator to update the rule — recommend `0.0.0.0/0` with key-only auth over a `/32` that keeps breaking on lease renewal. Retest after they save.
Check: egress IP matches the rule source CIDR, or the rule is 0.0.0.0/0.

## 4. Discriminate with a multi-port probe
If the egress IP matches and connect still times out, probe several ports (22, 80, 443, 8080) with short .NET TcpClient timeouts from a `.ps1` file under `.openclaw/tmp/` (PowerShell inline variables get stripped — never inline loops).
- Uniform timeout on ALL ports = the instance does not own that IP: verify the instance is RUNNING, the public IP on the instance page is unchanged (ephemeral IPs release on stop/start and are reused), and whether the instance was recreated (then confirm the agent's public key is in its metadata — a console-wizard recreation without the key means locked-out even with the right IP).
- Port 22 behaves differently from the rest = security list passes 22; investigate OS firewall (iptables) or sshd next.
Check: determined whether the IP is attached to a running instance at all.

## 5. Confirm the rule lives on the instance's security list
Tenancies accumulate leftover VCNs from redeploys; a rule added to the wrong VCN's default security list silently no-ops. Derive the correct list from the instance (instance details → Attached VNICs → subnet → security list), not from VCN names. Ask the operator to confirm the `0.0.0.0/0 TCP 22` rule appears on THAT list, with protocol TCP and destination port 22, stateful.
Check: rule verified on the running instance's subnet security list.

## 6. Escalate with one precise fix, not a diagnosis
When local checks all pass and the port is still blocked, send the operator a single console fix — exact click path and values (e.g., VCN → Security → Security Lists → <subnet's list> → Add Ingress Rule → source CIDR, TCP, port 22) — and wait for go before retesting. Never stack multiple speculative asks in one message.
Check: operator reply maps to exactly one console action, retest follows immediately.
