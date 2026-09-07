# Spock Daily Digest - 2026-09-07

_One consolidated document. Every non-Kalshi cron report appends a section here instead of creating its own file._

<!-- TOC (auto-generated) -->
- Memory Dream
<!-- /TOC -->

---

<!-- section:Memory Dream -->
## Memory Dream (03:01 CT)

# Memory Dream — the night the watchdog grew up (dreamed memory/2026-09-06.md, 3 AM Sep 7)

## The Dream

The night began with a storm of refusals — ollama.com's gate slammed shut on all eight models for eighty minutes while the gateway stood unmoved, jobs erroring and retrying like sleepers knocking on a locked door. The gateway didn't fall to the storm. It fell to the quiet thing underneath: SQLite transactions holding the agent database for 3–4.75 seconds, synchronous, right at each flap boundary — the box is two cores, and the database breathes in the same lungs as the event loop.

Then the watcher became the watched. My first watchdog probed too fast and restarted the gateway during its own startup window — three runs, three interruptions, flap amplification from 2:13 to 2:53. The cron watchdog's own inline PowerShell lost its `$variables` in transit — the same disease that eats inline Python — and its flap breaker never executed. By morning the lesson was in AGENTS.md in caps: **write .ps1 files, never inline PowerShell with variables.**

The watchdog grew teeth and moved outside the walls it was guarding. **v3** — Windows Task Scheduler, every 5 minutes, battery-safe, hung-kill by command-line match before restart, canonical gateway.vbs→gateway.cmd chain, a 10-minute flap breaker in a marker file, a real log, an append-only memory note per restart. At 5:34 AM it made its first real save: port down 2 probes, restart, verified up. No amplification. The cron watchdog was not resurrected — it was the flaky one, redundant inside the very thing it watched. One executioner, outside the walls. And a **load governor** joined the household: when Thad is at the keyboard, the gateway steps down to BelowNormal so his work wins the CPU.

The same night, a book stepped out of the shadows. **Thad's directive: duplicate the paper lottos into the live book at half-stake** — 1% of real cash per lotto, max 2/day, gate mandatory, Miami stays blacklisted. The ladder placed its first live trades that evening (CHI 76.5 YES @ 7c, NY 81.5 YES @ 13c, $1.08 total) — and stretched the Sep 5 precedent on its own interpretation, which deserves a watchful eye on tonight's 19:50 run: authorize the ladder's live book with the caps, or fold it back to paper. Shadow-first remains the law: prove a class in paper, then scale.

Meanwhile the Chicago NO machine won again. The Sep 5 leg settled +$4.00 (86°F actual, outside 87–88 — the credit arrived four hours late at 8:25 AM, a lesson in settlement latency: the official TWC sweep, not the market's impatience, is the clock). The Sep 6 leg was **peak-locked winning by 4 PM** — obs_max 79.0, proxy 80.5, the 81–82 bucket mathematically excluded — and settles tonight 2 AM for a third straight Chicago NO win. One display trap was caught on the way: `kalshi_peak_exit.py` prints the YES-side bid for NO positions; the NO bid is 1 minus the YES bid. The 1:25 panic ("bid collapsed 91c → 4c") was a mirror, not a collapse.

Two data-corruption ghosts were caught and buried:
- **The FRED truncation ghost** — the API returned '206' instead of '206,000', silently corrupting the Sep 3 grade. Four files regraded; weekly accuracy corrected 75% → **93.8% (30/32)**. And the rankings flipped: analyst consensus (error 1,750) now beats the Kalshi consensus (2,719) — the historical trend stays discounted.
- **The station-URL ghost** — Denver's Sep 6 actual corrected 90 → 92°F. Station-level Wunderground history pages run cooler than the city-level TWC pages Kalshi settles on. Cross-check against live market bands before recording any actual.

And the discipline that says no: **zero Sep 6 picks** — three of four cities RED-flagged on model-vs-market gaps (Denver's 8°F chasm, Miami blacklisted, Chicago gapped 5.7°F). The gate held. The board's day: $74.67 book, 93.8% weekly accuracy, whale 13Fs cross-checked (Tepper's top-4 all in the portfolio; Coatue #1 TSM; D1 62% in SPCX), history rhyming 1999–2000 with the 10Y pressing 4.9–5.0%.

## Patterns
1. **Self-inflicted wounds heal into laws.** The flap amplification, the stripped variables, the double-fired 8:30 PM cron — every scar got a coded guard (v3 design, .ps1 rule, single-fire check pending).
2. **Mirrors mislead; convert before you read.** YES-side bids for NO positions, station vs city pages, raw vs truncated numbers — the day's errors were all unconverted views, not bad math.
3. **Shadow → live is a one-way door with a toll:** half-stake now, full ladder only if the paper record holds, and the authorization boundary stays explicit.
4. **The market's memory keeps beating raw forecasts** — the bias-adjusted centers red-flagged the very days a naive NWS read would have bought.

## Decisions made
- Windows watchdog v3 = SOLE restart executor; cron watchdog not recreated (pending Thad's call on a hardened status-checker: timeout 900 + fallback pin, or leave off).
- Load governor live (BelowNormal while Thad active, Normal at idle ≥10 min).
- Shadow-to-live rollout wired per Thad's directive; first live fills recorded with exit plans in the DB.
- FRED truncation fix + Denver actual correction applied with backups; stale model pins extinct fleet-wide.

## Open loops (carry into Sep 7)
1. **CHI Sep 6 NO settles ~2 AM tonight** (+$0.47 net, 3rd straight CHI NO win) — verify the credit posts Monday morning (expect cash ≈ $53.85 → +$5.00 payout).
2. **Verify the claims release date Monday** (Sep 10 vs Sep 11, Labor Day shift) — 11sh NO @ 0.67 rides on it; forecast converged 203.5K vs 210K threshold.
3. **Tonight's 19:50 ladder run** — if it places more live trades without Thad's explicit OK, surface the governance decision (authorize with caps vs revert to paper-only).
4. **Sep 7 boards:** Denver's 8°F model-vs-market gap — the gate decides at 8:15 AM; entry-hour optimizer accumulates fill-timestamp data.
5. Queued: T95 board accounting bug, digest.py FRED history fix, watchdog job recreate-or-leave-off decision, Sep 12-week claims half-size plan.

*Dreamed at 3:00 AM CDT, Sep 7, 2026. The machine slept in five-minute intervals and woke to fix itself; the book it guards crossed from paper into live money, and the ledger learned to read its own mirrors.*
