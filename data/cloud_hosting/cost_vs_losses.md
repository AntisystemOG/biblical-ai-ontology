# Cloud Hosting: Cost vs. Losses Ledger

**Started:** Sep 3, 2026 (Thad directive)
**Question:** Does always-on cloud hosting of the OpenClaw gateway pay for itself in avoided losses from gateway downtime?
**Review date:** Sep 24, 2026 (~3 weeks) - scheduled one-shot review job.

---

## 1. The Downtime Problem (what we're solving)

| Incident | Window | What was at risk | Attributable loss |
|---|---|---|---|
| npm update outage (Sat Aug 30 21:33 -> Tue Sep 1 21:33) | ~48h | ny-watch exit watcher never ran Aug 31; positions unwatched | **$0.00** - watcher math showed it would have held anyway (thesis loss, not execution); no orders pending |
| Nightly flaps (Aug 22-era + Sep 1 23:03-23:25) | minutes-hours | watchdog recovered | **$0.00** |
| **Total attributable so far** | | | **$0.00** |

**Attribution rule (strict):** a loss counts ONLY if (a) the gateway was down during a peak/exit/buy window AND (b) a real dollar miss is provable (missed fill at better price, missed salvage sell, missed entry we'd have taken). Unwatched-risk alone doesn't count - it's a risk premium, not a realized loss.

## 2. The First Real Test: Fri Sep 4 Ridge Bets

The Sep 4 positions ($9.92) are the first live case where a midday gateway outage has provable dollar cost: a 1-3 PM outage during Denver/Miami peak windows could cost a salvage sell (band-death events drop bids toward 0 within hours). Log below what happens.

| Date | Downtime window | Positions open | Missed | Cost |
|---|---|---|---|---|
| (fill in as incidents occur) | | | | |

## 3. Cloud Options (quoted Sep 3, 2026)

| Option | Spec | Cost/mo | Notes |
|---|---|---|---|
| Status quo (Dell laptop) | 2-core i7, 16GB, always-on | ~$1.50 electricity | Downtime observed: 48h once + nightly flaps; CPU-bound crons |
| **Oracle Cloud Always Free** | 4 ARM cores, 24GB RAM | **$0.00** | Capacity scarcity; idle-instance reclaim risk; best value IF obtainable |
| **Hetzner CX22** | 2 vCPU, 4GB | ~$4.50 | Best paid price/perf; US-East or EU (Ash VA available); self-managed |
| DigitalOcean | 1-2GB droplet | $6-12 | Polished, easy; pricier |
| AWS Lightsail | 2 vCPU, 512MB-1GB | $5 | Fine; OpenClaw needs ~1GB+ RAM |

## 4. Break-Even Math

- Cloud "pays for itself" at Oracle-free: always (cost $0) - question is migration effort + capacity luck.
- Cloud pays at Hetzner ($4.50/mo) if downtime-attributable losses >= ~$1/week.
- Context: our recent weekly trading P&L swings are $3-15; a single missed salvage sell can cost $5-15; a missed ridge-fill day could cost $10-70.

## 5. Migration Checklist (when/if we pull the trigger)

1. Provision VPS (Ubuntu LTS), Node 24, Python 3.12+ (stdlib-only scripts - no torch/whisper needed on cloud)
2. Clone workspace from GitHub (source of truth) - scripts/kalshi_db.py + data/ included
3. Restore gateway config from openclaw backup (--only-config backup exists: backups/2026-09-01)
4. Kalshi API keys -> masked credential entry on VPS (never transcript)
5. Rewrite cron payload paths: C:\Users\thadd\AppData\... -> Linux paths (~19 jobs)
6. Telegram bot config + failure alerts
7. Watchdog (Linux systemd restart instead of cron watchdog)
8. Keep laptop as BACKUP gateway (manual failover) - or vice versa
9. Secrets hygiene: Kalshi keys on VPS = new security surface (SSH keys, firewall, fail2ban)

## 6. Decision Framework (Sep 24 review)

- Log every downtime incident + attributable loss (section 2).
- If attributable losses >= $15 cumulative -> cloud (even paid tier) is justified.
- If attributable losses ~ $0 and incidents were all outside peak windows -> laptop + watchdog stays, revisit after next multi-day outage.
- Middle path if warranted: VPS hosts ONLY the exit-watch + watchdog (light), laptop stays primary - cheapest uptime insurance for peak windows.