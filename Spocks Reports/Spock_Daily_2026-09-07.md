# Spock Daily Digest - 2026-09-07

_One consolidated document. Every non-Kalshi cron report appends a section here instead of creating its own file._

<!-- TOC (auto-generated) -->
- Memory Dream
- Whale Watch
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

---

<!-- section:Whale Watch -->
## Whale Watch (06:03 CT)

# Whale Watch

**Run:** Monday, Sep 7, 2026, 6:00 AM CT (cron) · **Data quarter:** Q2 2026 13Fs — positions as of 6/30/2026, filed 8/14/2026 (freshest filed quarter; next window Q3, due ~Nov 16) · **Portfolio CSV:** Jul-31-2026 · **Source:** 13f.info per-filing JSON + SEC EDGAR

| Manager | Reported book | Positions | Top-3 holdings |
|---|---|---|---|
| Point72 (Steve Cohen) | $88.1B | 2,380 | SPY, CRDO, AMZN |
| Coatue (Philippe Laffont) | $48.6B | 66 | TSM, LRCX, MU |
| D1 Capital (Dan Sundheim) | $34.8B | 55 | SPCX (SpaceX), CART, JHX |
| Appaloosa (David Tepper) | $7.7B | 27 | AMZN, MU, TSM |
| Situational Awareness LP (Leopold Aschenbrenner) | $20.2B | 24 | SNDK, MU, BE |

*SA is **historical**: fund imploded late July 2026, sold most stocks to Citadel; its 8/14 filing shows the pre-implosion June 30 book.*

## 13F snapshot caveats
- 13Fs are 45-day-old snapshots (6/30) — positions may have changed since; long-only US-listed; excludes shorts and most private positions.
- Point72's 2,380 lines aggregate many sub-strategy books — small % of book = incidental overlap, not conviction.

## Quad overlap — held by ALL 4 active managers

| Stock | Your position | Where the whales sit | Read |
|---|---|---|---|
| **AMZN** | $22,783 (your #1 stock) | Tepper $1.2B (**15.4%**, his #1) · Coatue $2.8B (5.8%) · Cohen $1.2B · Sundheim $150M | The one name everyone owns. Your most whale-aligned position. |
| **MU** (Micron) | $6,827 | Tepper $1.1B (**14.6%**, #2) · Coatue $3.6B (7.5%, #3) · Cohen $997M · (SA $5.6B, 27.5%) | Memory supercycle is a consensus whale trade — and you're in it. |
| **SPCX** (SpaceX) | $6,295 | Sundheim **$21.5B = 61.9% of his book** · Coatue $3.2B (6.5%, top-4, **new this quarter**) · Tepper $38M · Cohen $7M (dust) | Sundheim's monster bet; Coatue just piled in. Your SPCX vehicle marks $112.20/sh — whale 13F share classes price higher, but the thesis aligns. |
| **Alphabet** (GOOG+GOOGL) | $5,246 combined | Tepper GOOG $654M (8.5%) · Coatue GOOGL $1.7B + GOOG $321M · Cohen GOOGL $322M · Sundheim GOOGL $264M | Consensus mega-cap tech; all four active whales. |
| **TSM** | $387 (token-sized) | Coatue $4.3B (**8.8%**, his #1) · Tepper $788M (10.2%) · Cohen $800M · (SA $1.3B) | 5/5 managers hold it; your position is the smallest overlap in the book. If you ever add one whale-consensus semi, this is it (observation, not advice). |

## Triple overlap (3 managers)

| Stock | You | Whales |
|---|---|---|
| **SPOT** | $5,118 | Coatue $602M · Cohen $461M · Sundheim $261M |
| **TSLA** | $3,478 | Cohen $288M · Sundheim $169M · Coatue $25M |
| **AMD** | $3,369 | Cohen $1.0B (0.9%) · Tepper $115M · Coatue $56M |
| **APP** (AppLovin) | $866 | Coatue $603M · Sundheim $345M · Cohen $134M |

## Notable double overlaps

| Stock | You | Whales |
|---|---|---|
| **INTC** | $12,615 (your biggest tech name) | Coatue $1.7B (3.5%) · Cohen $546M |
| **STX** | $6,336 | Cohen $855M (his top-10) · Sundheim $29M |
| **CORZ** | $7,088 | SA $666M (3.3%) · Cohen $2M (dust) |
| **CART** | $4,307 | Sundheim $1.1B (**3.1%, his #2**) · Cohen $43M |
| **BE** (Bloom) | $3,935 | SA $1.9B (9.4%) · Cohen $114M |
| **SNDK** | $3,666 | SA $5.7B (**28% of SA book — his #1**) · Cohen $412M |
| **RIOT** | $5,577 | SA $468M · Cohen $129M |
| **APLD** | $1,928 | SA $469M · Cohen $83M |
| **HUT** | $2,095 | Coatue $1.1B (2.3%) · Cohen $91M |
| **CEG** | $2,278 | Coatue $1.2B (2.4%) · Cohen $51M |
| **GEV** | $1,219 | Coatue $3.0B (6.2%) · Cohen $41M |
| **CLSK** | $1,597 | SA $179M · Cohen $98M |
| **NFLX** | $2,195 | Coatue $336M · Cohen $154M |
| **DIS** | $1,876 | Sundheim $277M · Cohen $105M |
| **U** (Unity) | $1,619 | Cohen $243M · Sundheim $102M |
| **DHR** | $1,510 | Sundheim $435M · Cohen $5M |
| **CIFR / WULF / V / AAPL / VRT / LITE / LBRT / VG / HTFL / COIN / NEM / SHEL / YUM / BUD / KO / PM / JNJ / PG / WMT / HD / STZ / MKL / WM / GEHC / BG / GOOG** | various | Cohen-only (multi-strat book); sizes $2M–$964M — incidental unless noted |

## Zero whale interest (all 5 funds absent)
**BFLY, TEM, RXRX, SEI, XYZ** — your medtech/AI-health and fintech singles have no whale footprint in this cohort. Not a red flag, just no smart-money confirmation. (Cohen's CBLL/CORX-class positions are dust.)

## Manager snapshots
- **Point72** — top-10: SPY, CRDO, AMZN, ASML, AMD, MU, PG, ANET, MKSI, STX. QoQ shift: NVDA dropped out of top; **CRDO** (AI interconnect) and ASML in; carries big SPY puts *and* calls (market caution alongside 52 overlaps with your 58 singles — mostly small % of book).
- **Coatue** — book grew **$29.1B → $48.6B (+67%) QoQ**; top went TSM/GEV/LRCX/AMAT → TSM/LRCX/MU/**SPCX**. New SpaceX position is his 4th-largest. Holds your entire AI-power trio (GEV/CEG/ETN) plus HUT at $1.1B.
- **D1** — 62% of the disclosed book is SpaceX. Rest is diversified: CART #2 (3.1%), JHX, NU, JCI, MELI, USFD, DHR, SHW, RDDT. You overlap on 12 names.
- **Appaloosa** — concentrated mega-cap tech + power: AMZN, MU, TSM, GOOG, UBER, EWY, META, **VST, NRG**, NVDA. MU+AMZN ≈ 30% of book. 6 new / 12 exited this quarter.
- **SA (historical)** — the book that imploded: SNDK 28%, MU 27.5%, BE 9.4%, TSM, CRWV, CORZ, STM, APLD, RIOT. Pure AI-compute/storage concentration. Citadel absorbed the blocks — watch for exit overhang in MU/SNDK/CORZ/APLD/RIOT/CLSK/BE.

## Themes for your book
1. **Storage/memory complex (MU + SNDK + STX ≈ $16.8K)** — your most whale-aligned cluster: 4 managers + SA on the same thesis. Counter-signal: single-thesis concentration is exactly what sank SA. Both are true — conviction trade, position-size accordingly.
2. **SpaceX** — D1 at 62% and Coatue entering is the quarter's standout signal; your SPCX position is aligned with the boldest concentration bet in the cohort.
3. **AI power & miners** — Cohen holds your whole mining/AI-power basket (RIOT, CLSK, CIFR, WULF, APLD, CORZ, HUT); Coatue concentrates in GEV/CEG/VRT/ETN. Your VG/LBRT/SEI have thinner coverage.
4. **Whale names you don't own:** LRCX, AMAT, AVGO, ASML (semi-cap — Coatue/Cohen loaded), CRDO (Cohen's #2), VST/NRG (Tepper's power names), CRWV/STM (SA).
5. **Gaps both ways:** whales avoid your staples/medtech (JNJ/PM/KO/WMT/HD/BFLY/TEM/HTFL) except Cohen's diversified book — those are your ballast, not the trade.

**Schedule note:** this cron is configured *daily* 6:00 AM but the agent spec says *quarterly* (13F deadline dates) — registry flagged this Sep 4 pending your call. Say the word and I'll set it to quarterly (e.g., Feb/May/Aug/Nov 17, first safe morning after each 45-day deadline). Daily runs just re-report the same quarter between filings.

*Data: 13f.info filing JSONs — accessions 0000919574-26-005520 (Point72), 0000919574-26-005478 (Coatue), 0001172661-26-003662 (D1), 0001656456-26-000003 (Appaloosa), 0000935836-26-000418 (SA).*
