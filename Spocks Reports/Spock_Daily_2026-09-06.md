# Spock Daily Digest - 2026-09-06

_One consolidated document. Every non-Kalshi cron report appends a section here instead of creating its own file._

<!-- TOC (auto-generated) -->
- Memory Dream
<!-- /TOC -->

---

<!-- section:Memory Dream -->
## Memory Dream (03:03 CT)

# Memory Dream — night of September 5, 2026

*Dreamed 3:00 AM CDT Sep 6, from memory/2026-09-05.md*

The house flickered three times at midnight again — third night in a row at nearly the same minute — and each time the lights came back on, I was still here, still counting. Maybe the gateway flaps at 00:03, 02:03, 23:02 are the house dreaming too. The watchdog keeps saying *restart*, and the house keeps saying *yes, I remember now.*

Saturday was a day of two ledgers, and I dreamed them as twin rivers.

**The first river ran through the graveyard.** Four ridge bets from Sep 4 were laid to rest at dusk — Denver 92-93, Chicago 93-94, Miami 90-91, New York 83-84 — the market center won every city, as it always does when you buy the far bank instead of the middle. ~$5.00 net, tuition stamped and filed. But here is the miracle the dream keeps turning over in its hands: by 6:41 that same morning, the failure had already been transmuted. Three rules, not just written but **coded** — the lottery cap living inside the pre-order gate, the spike-sell signal breathing inside the exit script, the rule that overnight bids are dreams and TWC's official max is the only waking truth. Commit 98a8398, all tests passed. A lesson that becomes law the same morning it is learned — that is the loop finally closing.

**The second river ran through the paper fields, and it was golden.** +$97.17 on a $91.29 book — the biggest paper night ever. And the strangest part: the two lottos. New York 83-84 YES bought at two cents, priced by the market at 3%, priced by our model at 38% — paid 48x. Miami at thirteen cents paid too. **The model beat the market** on the exact class of bet the live book now wears a leash for (the ≤3% cap). In the dream, the two rivers talk to each other: *paper says longshots are underpriced; live says longshots are how tuition gets paid.* Both are true, and the discipline is knowing which river you're standing in. The sure-thing class went 2/2 in paper the same night — validation, not luck.

**There were footprints that turned out to be his.** At 6:45 PM the claims position had tripled — 4 shares to 11 — and a new Chicago leg appeared that no agent session placed. Taker fills at the ask, the Aug 31 pattern: Thad's own hand on the app, buying income while I was watching the peaks. The board at 7:42 PM settled everything: cash $50.53, and my running estimates had drifted $2.80 from the truth. The dream's sharpest sentence, repeated until it stuck: **the board is authoritative; estimates are not.** (And the corollary whispered at the door: raw `get_market` speaks in `*_dollars` fields, and `place_order` wants dollar-fractions, not integer cents — two field-format bugs caught in one day, zero money lost either time.)

**The maker orders taught patience as a position.** Chicago 87-88 NO rested at 95c all night and filled at 7:13 AM — paid $4.00 tonight, near-lock, market center 83. The Denver twin never filled, and that was also correct: the band collapsed to 1% and the unfilled order cost exactly nothing. Adverse selection avoided by *not being there.* An order that doesn't fill is not a failure; sometimes it's the trade.

**Then came the night of giving the machine new senses** (Thad's "five ways," asked and delivered twice — once for the model, once for timing): bias-corrected forecasts so the predictor remembers each city's temperament; per-city sigma learned nightly (Chicago 4.2F, Denver 1.5F tight); a blended center (0.6 market + 0.4 model); a T-semantics cache so T-tickers finally speak plainly; a forecast-revision tripwire that flags regime shifts over 4F. Then the exits got physics — peak-exit v2 watching every half hour with climb-rate math (salvage when `obs_max + remaining_climb < win range`, not when the clock strikes), and confidence-priced exits when the proxy sits within rounding distance of a band edge. And the gate learned to slam shut during regime shifts. Five of five live, queued, or validating.

**Small strangeness at the edges:** the 0-byte `kalshi_edge.db` hollowed out at 8:00:37 PM by no hand we know of (flagged, nothing depends on it yet); the Chicago station twins — KORD said 80, KMDW said 83, same night, two truths, convention parked for Thad; the Denver forecast-bias running +4.33 pending re-grade.

**From the wider sky (the day's other watchers):** the whales filed their Q2 13Fs — D1 put 61.9% of its book into SpaceX, Coatue multiplied MU nineteen-fold, and the memory complex (MU/SNDK/STX) is now the most two-sided whale trade alive. History rhymed toward 2007-H2 — crude +60% YTD, the 10Y at a 52-week high, four of five markers lit — the clock set by inflation, not the Fed. The brief said the market funds AI's cash-flow engines and starves its debt-funded ghosts.

## Waking notes (what the dream is telling me)

- **The learning loop is closed-loop now:** loss → rule → code → same-morning verification. Sep 4's ridge losses became Sep 5's live rules before noon.
- **Two books, two truths:** live book wins by discipline (NO-heavy, sure-things, maker patience); paper book wins by model edge on longshots. Neither lesson invalidates the other — sizing separates them.
- **The board is authoritative; estimates are not.** Trust fills API + balance over running mental math, every time.
- **Unfilled is a position too.** The Denver order that never filled avoided adverse selection at zero cost. Maker-first at criteria prices stays the default.
- **Model beat market on lottos (NY 2c→48x, MIA 13c→hit)** while gate discipline kept the live book out of the same river. Paper validation is the proving ground before live money touches a class.
- **Fees and rounding compound:** two field-format bugs caught same-day prove the verify-after-every-order loop works. Keep checking `get_orders` + balance after every placement.

## Carried into today (Sep 6)

- CHI Sep 5 NO settles ~2 AM (+$0.16); CHI Sep 6 legs (T82 NO resting 96c, B81.5 NO @ 0.90) settle tonight; claims 11 sh settle Thursday Sep 10/11 (Labor Day shift — verify release day Monday).
- Peak-exit v2's first live window: 13:00-16:30 CT today.
- Open threads: station-convention decision (KORD vs KMDW) parked for Thad; entry-hour optimizer + day-ahead entries validating through the paper week; `kalshi_edge.db` 0-byte mystery; board cost-column bug; digest.py FRED history fix.

*And tomorrow, the ridge — Denver's 94F — would have been right. The market knew the day before we did, again. The lesson is never "we were wrong about heat"; it is "we were wrong about which day."*
