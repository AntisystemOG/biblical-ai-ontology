# Spock Daily Digest - 2026-09-06

_One consolidated document. Every non-Kalshi cron report appends a section here instead of creating its own file._

<!-- TOC (auto-generated) -->
- Memory Dream
- Whale Watch
- History Rhymes
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

---

<!-- section:Whale Watch -->
## Whale Watch (06:07 CT)

# Whale Watch

**Run:** Sunday, Sep 6, 2026 — 6:05 AM CT | **Data:** Q2 2026 13F filings (holdings as of Jun 30, 2026, filed Aug 14, 2026) vs portfolio CSV Jul-31-2026 | **Sources:** 13f.info holdings data (SEC EDGAR accessions 0000919574-26-005520, 0001172661-26-003662, 0001656456-26-000003, 0000919574-26-005478, 0000935836-26-000418)

## TL;DR

- **Tepper's top 4 positions are ALL in your book**: AMZN (#1, $1.19B), MU (#2, $1.13B), TSM (#3, $788M), GOOG (#4, $654M). His only bearish position is an AAPL put ($242M).
- **Coatue's #1 position is TSM ($4.26B)** and #3 is MU ($3.63B) — plus 13 more overlaps including a $1.12B HUT (Hut 8) position, 12x bigger than yours relative to fund size.
- **D1's #2 position is CART/Instacart ($1.07B)**, and its #1 is SpaceX ($21.5B — 62% of the fund). You own SPCX shares too.
- **Crowded-trade warning:** memory (MU/SNDK/STX) is the most whale-crowded corner of your portfolio — and the one that just blew up Situational Awareness LP.
- Point72 overlaps nearly everything (3,900+ positions) — treat as noise, not signal.

## Fund-by-Fund

### Appaloosa LP (David Tepper) — $7.7B, 27 positions
Tepper's book is a concentrated bet you're already making:

| His rank | Ticker | His value | In your portfolio? |
|---|---|---|---|
| #1 | AMZN | $1,192M | ✅ Yes ($22.3K + Roth) |
| #2 | MU | $1,125M | ✅ Yes ($6.8K) |
| #3 | TSM | $788M | ✅ Yes (Roth $387) |
| #4 | GOOG | $654M | ✅ Yes ($2.0K) |
| — | AMD | $115M | ✅ Yes ($3.4K) |
| — | AAPL | **PUT** $242M | ⚠️ You own AAPL long |

Also in his book (not yours): UBER, EWY (Korea ETF), META, VST, NVDA, NRG. **His #1 bearish position is an AAPL put** — worth knowing since you hold AAPL shares.

### Coatue Management (Philippe Laffont) — $48.6B, 66 positions
15 of 66 positions overlap your portfolio. His top-10: TSM, LRCX, MU, SPCX, AMAT, GEV, AMZN, AVGO, ETN, GOOGL.

| Ticker | His value | Note |
|---|---|---|
| TSM | $4,258M | **His #1 position** |
| MU | $3,627M | #3 |
| GEV | $3,005M | GE Vernova — grid/power theme |
| AMZN | $2,821M | |
| GOOGL | $1,735M | |
| INTC | $1,687M | Intel is a whale favorite |
| CEG | $1,151M | Constellation Energy |
| HUT | $1,122M | **Hut 8 — you own it too** |
| APP | $603M | AppLovin |
| SPOT | $602M | |
| NFLX | $336M | |
| GOOG | $321M | |
| VRT | $270M | Vertiv |
| AMD | $56M | |
| TSLA | $25M | |

### D1 Capital (Daniel Sundheim) — $34.8B, 55 positions (top-10 = 77% of book)
- **#1 SPCX (SpaceX) $21.5B — 62% of the entire fund.** You own SPCX ($6.3K across accounts) — same boat as Sundheim's largest position.
- **#2 CART (Instacart) $1,068M** — you own CART.
- #8 DHR (Danaher) $435M — you own DHR.
- Other overlaps: APP $345M, DIS $277M, GOOGL $264M, SPOT $261M, TSLA $169M, AMZN $150M, U (Unity) $102M, GOOG $30M, STX $29M.
- Not in your book: JHX, NU, JCI, MELI, USFD, SHW, RDDT.

### Point72 (Steve Cohen) — $90.7B, 3,923 rows (multi-strategy — overlap = noise)
Biggest single-stock longs in your book: AMZN $1.19B long, AMD $907M, PG $935M, STX $820M, TSM $786M, MU $617M, INTC $480M. His #2 fund-wide position is CRDO (Credo, $1.74B) — not in your portfolio. **Hedge warning:** he runs large PUT books on JNJ ($484M), TSLA ($199M), MU ($381M), SNDK ($168M), APP ($99M) — Point72 hedges everything, so these are positioning, not necessarily bearish conviction.

### Situational Awareness LP (Leopold Aschenbrenner) — HISTORICAL ONLY
His final 13F: 26 positions, $20.2B — **SNDK ($5.67B) + MU ($5.57B) = ~55% of the book**, plus BE ($1.94B), TSM ($1.29B), CORZ, APLD, RIOT, CLSK — 8 of his positions are in your portfolio. The fund then sold its entire public stock book to Citadel in late July 2026 after the AI/memory trade unraveled (~67% drawdown month). **Lesson: the memory trade you share with the whales was crowded enough to destroy its biggest bull. Size accordingly.**

## Overlap Themes

1. **Memory/semis (MU, SNDK, STX, TSM)** — most crowded whale theme in your book. Tepper #2, Coatue #1/#3, SA ~55%. You're at ~$16.8K across MU/SNDK/STX — riding a crowded trade that already claimed one fund.
2. **AI power (GEV, CEG, VRT, BE)** — Coatue holds all four; you own all four too.
3. **Amazon + Alphabet** — long at every fund tracked; your largest single-name exposure (AMZN $22.3K, GOOGL/GOOG $4.8K) matches the crowd.
4. **Digital-asset infra (HUT, RIOT, CORZ, APLD, CLSK, CIFR, WULF)** — Coatue's $1.1B HUT is the standout conviction overlap; Point72/SA touched the rest smaller.
5. **Consumer/tech (CART, APP, SPOT, DIS, U, DHR)** — D1's specialty; CART is his #2.

## Watch-Outs

- **AAPL:** Tepper's largest bearish position is an AAPL put ($242M).
- **Memory concentration:** MU + SNDK + STX ≈ 8% of your equity book; the whale crowd is longest exactly here (and the SA implosion shows how fast it can turn).
- **Stale data:** 13F positions are as of Jun 30 — two months old; Tepper/Coatue may have already trimmed memory into the August run-up.

*Point72/D1/Appaloosa/Coatue data: 13f.info (SEC EDGAR). Portfolio: Fidelity CSV Jul-31-2026. Values in $ thousands where noted "K", millions "M".*

---

<!-- section:History Rhymes -->
## History Rhymes (07:01 CT)

**Data through Friday, Sep 4, 2026 close (yfinance).** Markets closed Sunday; Monday Sep 7 is Labor Day — next session is Tuesday Sep 8, a holiday-shortened week (claims Thursday, FOMC Sep 15-16).

### Current Market Snapshot (Fri Sep 4 close)

| Metric | Level | 1D | 1M | 3M | 6M |
|---|---|---|---|---|---|
| S&P 500 | 7,718.6 | -0.4% | -0.5% | +4.2% | +13.0% |
| Nasdaq | 26,507 | -0.3% | -0.7% | +2.2% | +16.5% |
| Dow | 53,414 | -0.5% | -1.2% | +5.2% | +11.4% |
| Russell 2000 | 2,975.7 | +0.3% | **-1.9%** | +4.2% | +15.1% |
| 10Y Treasury | **4.78%** | +3bp | +12bp | +23bp | +70bp |
| 2Y Treasury | **4.55%** | +4bp | +19bp | +27bp | +88bp |
| 13-wk T-bill | 3.76% | +2bp | +5bp | +13bp | +16bp |
| VIX | 14.53 | +1.5% | -2.5% | -23.2% | -31.3% |
| USD Index | 99.16 | +0.2% | -0.4% | -0.9% | +0.2% |
| Crude (WTI) | **$91.48** | +0.2% | **+17.0%** | +0.2% | +0.6% |
| Gold | $4,476.6 | -0.3% | +3.1% | +3.3% | -13.0% |
| Bitcoin | $79,923 | +0.1% | **+23.9%** | +24.9% | +17.3% |
| NVDA | $230.36 | +0.8% | +2.9% | +10.4% | +25.8% |
| MSFT | $499.70 | -2.0% | +0.1% | **+21.6%** | +22.2% |
| AAPL | $319.97 | -2.5% | +2.2% | +6.2% | +23.2% |
| TSLA | $354.08 | **-5.9%** | +7.8% | **-13.4%** | -12.7% |

*Yields quoted raw percent per yfinance (Aug 27 gotcha honored); bp changes computed from levels. 6M % changes are relative, so +17.25% on the 10Y = +0.70pp (4.08%→4.78%).*

### The Setup in One Paragraph

Equities sit at/near record highs (S&P 7,718) after a strong 6 months (+13%), but momentum has stalled (-0.5% over the past month) just as the bond market — not the Fed — is repricing inflation risk: Friday's hot August payrolls beat sent the 2Y (+19bp/mo) and 10Y (+70bp over 6 months) higher **while** the front bill (3.76%) says the Fed still cuts. Meanwhile crude just jumped +17% in a month to $91, gold holds near $4,476 (more than double its 2024 level), Bitcoin ripped +24% in a month, and the VIX at 14.5 signals near-total complacency. Cutting into rising long yields, an oil spike, and record concentration is one of the rarest — and most historically loaded — macro textures there is.

### The Distinctive Signature: Fed Cutting, Bond Vigilantes Rising

The curve's shape (3M 3.76% < 2Y 4.55% < 10Y 4.78%) with the 2Y *rising fastest* is a market pricing **cuts now, re-tightening later** — an easing Fed that the bond market expects to be forced to reverse. That exact forward-path shape has appeared only a handful of times:

- **1999-2000** — Fed cut fall 1998 (LTCM), then 10Y went 4.6%→6.8% while the Fed re-hiked to 6.5%; equities rallied into March 2000, then broke.
- **1980-81** — brief easing into year-end, inflation forced re-tightening, double-dip.
- **1967-68** — Fed eased as inflation re-accelerated; gold ran; the bill came due 1968-70.

### Key Historical Rhymes (ranked)

**1. 1999-2000 dot-com analog — similarity: HIGH (the primary rhyme).**
The full checklist is checking boxes again: CAPE ~40-45 (approximate; top-1% of 155 years, vs ~44 at the 2000 peak), record top-10 index concentration (~36-40% vs ~27% in 2000), tech ≈ one-third of the index, speculative retail temper (Bitcoin +24%/month echoes 1999 IPO mania), mega-cap growth dominance (MSFT +21.6%/3M = the Cisco trade), and — critically — **the same rates shape**: Fed easing bias priced while intermediate/long yields grind higher into the top. In 1999-2000 the "this time is different" story was the internet; today it's AI. The market topped in March 2000 not on bad news but on rising long yields + a Fed that had stopped cutting. The rhyme's key lesson: **watch the 10Y and the Fed's September statement, not the earnings headlines.**

**2. 2007 — similarity: MODERATE-HIGH (the macro-texture rhyme).**
September 2007: crude breaking toward $90-100 records (today: $91), the Fed mid-cutting-cycle, S&P at all-time highs (top came Oct 9, 2007), VIX 13-15 (today: 14.5), and stress hiding beneath a calm surface (then subprime/credit; now 4.78% long yields + $91 oil pressing margins). The 2007 rhyme says: low VIX + record crude + early Fed cuts is a **top-forming texture, not a launch pad**. Energy leadership while tech wobbles (TSLA -13.4%/3M, small caps -1.9%/1M) also echoes 2007's rotation into commodities.

**3. 1972-73 Nifty Fifty — similarity: MODERATE (the concentration + oil-shock rhyme).**
Extreme large-cap-quality concentration (Mag 7 ≈ Nifty Fifty), an energy price spike building (+17% crude in a month), a Fed easing while inflation re-accelerates. 1972's concentrated leaders then spent 1973-74 under the twin squeeze of an oil shock and rising yields. Lesson: concentrated quality leaders are **not** a safe haven when the shock is inflationary — they derate with everything else.

**4. 1987 — similarity: MODERATE (the momentum + seasonality rhyme).**
A relentless 1H melt-up (S&P +13%/6M vs 1987's similar arc), long yields grinding higher (1987: 7%→10%; today 4.08%→4.78% in 6 months), gold strong into the peak, and September — the month of the 1987 breakdown after the Aug 25 top. Today's mechanical flows (vol-targeting, CTAs, options gamma) play the portfolio-insurance role. 1987 is the rhyme that says: **September with rising yields after a melt-up is historically the most dangerous month of the year to be maximally long at low hedge cost.**

**5. Counter-scenario (the base-rate check): 1994-95 / 2013 / Oct 2023.**
Sometimes a bond-led repricing is just that: 1994's 10Y surge flattened equities for a year but produced no bear — followed by the 1995 soft-landing melt-up; 2013 and Oct 2023's 5% scare both resolved with equities higher once the yield spike passed. If the AI earnings engine (NVDA +25.8%/6M) keeps compounding, this is the benign path: a 5-10% yield-driven chop, not a 2000.

### Pattern Scorecard

| Dimension | Sep 2026 reading | Closest historical match | Similarity |
|---|---|---|---|
| Valuation (CAPE ~40-45, top-10 ~36-40%) | Extreme | Mar 2000 | High |
| Leadership concentration (Mag 7 = index) | Extreme | 1972 / 2000 | High |
| Fed easing bias + rising 2Y/10Y | Present | 1999-2000 | High |
| Oil shock building ($91, +17%/mo) | Present | 1973 / 2007-08 | Moderate |
| VIX complacency (14.5) at highs | Present | Sep-Oct 2007 | Moderate-High |
| Gold ~2x in ~2 years (debasement bid) | Present | 1970s decade-long | Moderate |
| 1M speculative burst (BTC +24%) | Present | Late 1999 / 2020-21 | Moderate |
| September after melt-up, rising yields | Present | Sep 1987 / Sep 2007 | Moderate-High |
| Earnings engine still compounding (AI caps) | Present | 1995 / 1997 | The counterweight |

### What the Rhymes Agree On (the convergent signals)

1. **The 10Y at 4.78% is the market's real Fed.** In 2000, 2007, and 1987, equity tops arrived as long yields peaked, not as news soured. Watch 4.9-5.0% as the zone where every rhyme above turns hostile.
2. **A September statement that hints "done cutting" is the trigger** — that was the March 2000 mechanic exactly.
3. **Concentration cuts both ways**: the same Mag-7 weight that lifted the index is the mechanism that would amplify a downside move; the 1972-73 rhyme says quality does not hedge an inflation shock.
4. **Oil at $91 with a +17%/month velocity is the quiet tell** — in 1973 and 2007 the energy bid preceded the equity problem by weeks-to-months.
5. **The 1994-95 counter-scenario is live** and would look like sideways chop with painful bond headlines, then new highs. The discriminator between 2000-path and 1994-path: **AI-capex earnings delivery through Q3-Q4 reports.**

### Bottom Line

The Sep 2026 texture rhymes most strongly with **1999-2000 (valuation + rates shape + concentration)** overlaid on **2007 (oil, VIX complacency, cutting Fed)**, with 1987's September seasonality as the near-term risk window. History's verdict on this combination: the market doesn't die of bad news — it dies of a repriced discount rate while the news is still good. The bear case doesn't need a recession to start; it needs the 10Y to keep doing what it has done for six straight months. Respect the 1994-95 counter-scenario (chop, then higher) if AI earnings keep landing — but at VIX 14.5, hedges have rarely been this cheap relative to the density of the rhymes.

*Pattern analysis, not a prediction and not investment advice. Approximate valuation figures (CAPE, concentration, forward P/E) carried from the agent's prior-run baselines; price/yield data is live yfinance through Sep 4, 2026.*
