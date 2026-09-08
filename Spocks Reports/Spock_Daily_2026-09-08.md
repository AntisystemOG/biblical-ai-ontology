# Spock Daily Digest - 2026-09-08

_One consolidated document. Every non-Kalshi cron report appends a section here instead of creating its own file._

<!-- TOC (auto-generated) -->
- Memory Dream
- Whale Watch
- History Rhymes
<!-- /TOC -->

---

<!-- section:Memory Dream -->
## Memory Dream (03:04 CT)

# Memory Dream — the night of September 7, 2026

_Dreamed 3:00 AM CDT, September 8, from memory/2026-09-07.md_

## The Dream

**The waiting room.** The night opened at T-3, the claims window standing open like a lit storefront: the 195K YES at 79c, +20 pct edge, ~27 pct return if the model's read holds. No buy. Thad's OK is the gate, and the window runs through Wednesday — patience is a position too. But under the patience, an hourglass: the ladder had now traded live two nights in a row without an explicit yes. One more night and the question becomes formal — authorize the live book with caps, or fold it back to paper.

**The third win, on schedule.** Chicago's $5.00 credit landed at 12:56 PM, mid-morning exactly as the Sep 5 precedent promised. Third straight Chicago win. No support ticket, no escalation — just the market's slow overnight sweep doing what slow sweeps do when you've learned their rhythm. The book breathed in: $52.77 cash.

**Tuition, cheap.** The first live lotto cycle closed its books. The NY leg salvaged for +$0.28 after station math proved the trajectory dead — proxy max 81.4F can never reach the 82.0 win floor, so the 13:00 exit was taken without hesitation. The CHI leg went to a zero bid and was written off without ceremony. Net -$0.32 including fees. The lesson is worth more than the cost: exits trigger on falsification, never on odds noise — and a bid of 0.00 is not a price, it's an absence.

**The house dreamt restlessly.** The watchdog — newly invisible, its every-5-minutes PowerShell flash retired in favor of silent VBS launchers — still restarted the gateway at 2:30 and 2:44 AM, then again at 11:05, 11:25, and 11:38 PM: night flaps, like a dog dreaming. And a new ghost appeared at the edge of sleep: "isolated agent setup timed out before runner start" — sessions failing to be born, not failing to think. The model layer never even ran. If the pattern walks again today (the monitor's runs, the 7 AM probe), the hunt moves to the 2-core box's session-spinup under load.

**Maps that lied, gently.** The digest showed five positions and counted six: the Fed H0 leg — 12.81 shares, $8.79, riding to the Sep 16 event — hidden behind a [:5] display cap. Patched, backed up. The FRED history disagreed with FRED itself (the API says 212/207/204/206, not what the digest claimed). The T-tickers resolved into exact-temperature markets; the B-tickers confessed to being pairs. And through it all the old law held: nothing is declared until the API's result field says so.

**The quiet day's census.** The trading arena slept its Labor Day sleep — one clean SKIP by the new SPY-bar rule, resumed this morning at 8:30. The whales surfaced: four managers converging on AMZN, MU, Alphabet, TSM — and SpaceX, where Sundheim keeps 61.9% of his entire book and Coatue just arrived; Coatue's whole book grew 67% in a quarter. The value screen whispered CI, TTE, VICI, TXT, BTI. The paper trader went 0-for-3 with forecasts that ran cold on a hot holiday (-$14.81), and logged its lessons anyway — full city names in add-actual, three-degree cushions even on expensive NOs, band semantics — because a book that can't record losses can't learn.

**Morning inventory:** the claims candidate still waits on Thad's OK; the ladder's governance question reaches its trigger tonight at 19:50; lotto cycle-2 tickets (NY B84.5, DEN B88.5) settle around 2 AM; the gateway's sleep apnea is on watch; the FRED-history fix stays queued. The book holds. The discipline held. The dream closes where it opened — a window open, an edge computed, and the wisdom to wait for the yes.

## Distilled Learnings (Sep 7)

- **Lotto experiment cycle 1 (first live losses):** NY B81.5 salvaged +$0.28 (13:00 station-math falsification = correct early exit); CHI B76.5 written off -$0.60 (bid 0.00 < 0.02 salvage floor). Net -$0.32 incl fees. Rule reinforced: exits on falsification only; bids under 0.02 = nothing to salvage.
- **Ladder governance ESCALATED:** Sep 7 19:50 was the 2nd consecutive live-trading day without explicit Thad OK (NY B84.5 YES 8sh @ .07 + DEN B88.5 YES 5sh @ .11, $1.11, caps respected). ONE more day (Sep 8 19:50) triggers the formal policy flag: authorize live book with caps vs revert to paper-only.
- **CHI NO streak at 3 confirmed:** Sep 6 credit landed 12:56 PM (normal mid-morning sweep; escalation avoided). Claims window T-3 opened: 195K YES @ 79c +20 pct = lead candidate (Thad OK pending); 200K YES @ 65c riskier; 205K NO skipped (0-for-2).
- **Gateway night drama + NEW failure mode:** restarts at 2:30/2:44 AM and 11:05/11:25/11:38 PM. NEW: "cron: isolated agent setup timed out before runner start" = gateway session-spinup timing out, NOT the model layer. If it recurs Sep 8, it's the low-resource box's internals under load.
- **Display-layer traps (map ≠ territory):** 6-vs-5 position mystery = digest.py pos_lines[:5] cap hiding the Fed H0 leg (patched, backup kept; isolated monitor sessions will re-hypothesize — the answer is the display omission, no Denver position exists). FRED digest history verified wrong vs API. T-ticker = exact temperature, B-ticker = pair bucket. Market-semantics law held: nothing declared until the API result confirms.
- **Paper trader 0/3 (-$14.81), forecasts cold on a hot holiday** (DEN -3/-4, NY -5). Lessons logged: add-actual needs FULL city names; expensive NO @0.62 still needs >=3F cushion; B90.5 = [89.5, 90.5]. Bankroll $169.59, 13W/12L (52.0%), ROI 86.4%. Longshot tracker still up (+$3.66 on 33 settled). Edge nightly: 210K NO edge +7 pct below the 10 pct bar, no new picks; 195K YES holds; digest stat-framing contradiction flagged for weekly review.
- **Labor Day handling + whale census:** trading-arena skipped deterministically (SPY-bar verify; resumes Sep 8). Whale watch migrated to 13f.info per-filing JSON (no auth); quad overlaps AMZN/MU/SPCX/GOOG/TSM; Coatue +67 pct QoQ, SpaceX new top-4; daily-cron-vs-quarterly-spec cadence re-flagged — unchanged without Thad's OK. Financial advisor top-5: CI, TTE, VICI, TXT, BTI.
- **Open from Sep 7:** claims execution (Thad's OK, window through Wednesday); ladder governance decision at tonight's 19:50; gateway spinup-timeout watch; lotto cycle-2 settles ~2 AM Sep 8; digest.py FRED-history fix queued; watchdog 1-or-2 call.

---

<!-- section:Whale Watch -->
## Whale Watch (06:04 CT)

# Whale Watch

**Run:** Tuesday, Sep 8, 2026, 6:00 AM CT (cron) · **Data quarter:** Q2 2026 13Fs — positions as of 6/30/2026, filed 8/14/2026 (freshest filed quarter; next window Q3, due ~Nov 16) · **Portfolio CSV:** Jul-31-2026 · **Source:** 13f.info per-filing JSON + SEC EDGAR

| Manager | Reported book | Positions | Top-3 holdings |
|---|---|---|---|
| Point72 (Steve Cohen) | $88.1B | 2,380 | SPY, CRDO, AMZN |
| Coatue (Philippe Laffont) | $48.6B | 66 | TSM, LRCX, MU |
| D1 Capital (Dan Sundheim) | $34.8B | 55 | SPCX (SpaceX), CART, JHX |
| Appaloosa (David Tepper) | $7.7B | 27 | AMZN, MU, TSM |
| Situational Awareness LP (Leopold Aschenbrenner) | $20.2B | 24 | SNDK, MU, BE |

*SA is **historical**: fund imploded late July 2026, sold most stocks to Citadel; its 8/14 filing shows the pre-implosion June 30 book.*

**⚠ Correction vs yesterday's report:** XYZ (Block Inc) was listed under "zero whale interest" — wrong. Point72 files Block under its old ticker **SQ**: **$340M long + $51M put + $27M call ≈ $316M net long.** Your $701 XYZ is whale-aligned after all (small). Fixed the matcher (SQ→XYZ alias + put/call flag bug); this is a one-off ticker lag in the 13F, not new buying.

## Quad overlap — held by ALL 4 active managers

| Stock | Your position | Where the whales sit | Read |
|---|---|---|---|
| **AMZN** | $22,783 (your #1 stock) | Tepper $1.19B (**15.4%**, his #1) · Coatue $2.82B (5.8%) · Cohen $1.19B long (+$48M put) · Sundheim $150M | The one name everyone owns. Your most whale-aligned position. |
| **MU** (Micron) | $6,827 | Tepper $1.13B (**14.6%**, #2) · Coatue $3.63B (7.5%, #3) · Cohen $617M long + $381M put + $257M call · (SA $5.6B, 27.5%) | Memory supercycle is a consensus whale trade — and you're in it. Cohen runs it hedged. |
| **SPCX** (SpaceX) | $6,295 | Sundheim **$21.5B = 61.9% of his book** · Coatue $3.2B (6.5%, top-4, **new this quarter**) · Tepper $38M · Cohen $7M (dust) | Sundheim's monster bet; Coatue just piled in. |
| **Alphabet** (GOOG+GOOGL) | $5,246 combined | Coatue $2.06B combined · Tepper GOOG $654M (8.5%) · Cohen GOOGL $236M long + $85M put, GOOG $6M long + $18M put · Sundheim $294M combined | Consensus mega-cap tech; all four active whales. Cohen carries Alphabet puts. |
| **TSM** | $387 (token-sized) | Coatue $4.26B (**8.8%**, his #1) · Tepper $788M (10.2%) · Cohen $786M long · (SA $1.3B) | 5/5 managers hold it; your position is the smallest overlap in the book. |

## Triple overlap (3 managers)

| Stock | You | Whales |
|---|---|---|
| **SPOT** | $5,118 | Coatue $602M · Cohen $429M long + $32M put · Sundheim $261M |
| **TSLA** | $3,478 | Sundheim $169M · **Cohen $89M long + $199M put (net bearish)** · Coatue $25M |
| **AMD** | $3,369 | Cohen $907M long + $94M put · Tepper $115M · Coatue $56M |
| **APP** (AppLovin) | $866 | Coatue $603M · Sundheim $345M · **Cohen $35M long + $99M put (net bearish)** |

## Notable double overlaps

| Stock | You | Whales |
|---|---|---|
| **INTC** | $12,615 (your biggest tech name) | Coatue $1.69B (3.5%) · Cohen $480M long + $66M put + $198M call |
| **STX** | $6,336 | Cohen $820M long + $34M put (his top-10) · Sundheim $29M |
| **CORZ** | $7,088 | SA $666M · Cohen **put-only** $1.5M |
| **CART** | $4,307 | Sundheim $1.07B (**3.1%, his #2**) · Cohen $43M |
| **BE** (Bloom) | $3,935 | SA $1.94B (9.4%) · Cohen $104M long + $9M put |
| **SNDK** | $3,666 | SA $5.67B (**28% of SA book — his #1**) · Cohen $243M long + **$168M put** (big hedge) |
| **RIOT** | $5,577 | SA $468M · Cohen $123M long + $7M put |
| **APLD** | $1,928 | SA $469M · Cohen $54M long + $29M put |
| **HUT** | $2,095 | Coatue $1.12B (2.3%) · Cohen $63M long + $28M put |
| **CEG** | $2,278 | Coatue $1.15B (2.4%) · Cohen $20M long + **$31M put (net bearish)** |
| **GEV** | $1,219 | Coatue $3.0B (6.2%) · Cohen $16M long + **$24M put (net bearish)** |
| **CLSK** | $1,597 | SA $179M · Cohen $96M long |
| **NFLX** | $2,195 | Coatue $336M · Cohen $86M long + $68M put |
| **DIS** | $1,876 | Sundheim $277M · Cohen $76M long + $29M put |
| **U** (Unity) | $1,619 | Cohen $216M long + $27M put · Sundheim $102M |
| **DHR** | $1,510 | Sundheim $435M (1.2%) · Cohen $3M |
| **XYZ** (Block) | $701 | Cohen $340M long + $51M put + $27M call (net ~$316M long) — *corrected* |
| **CIFR / WULF / V / AAPL / VRT / LITE / LBRT / VG / HTFL / COIN / NEM / SHEL / YUM / BUD / KO / PM / JNJ / PG / WMT / HD / STZ / MKL / WM / GEHC / BG / CBLL** | various | Cohen-only (multi-strat book); $2M–$964M — incidental unless flagged below |

## Bearish-put watch — whales hedging (or fading) names you own

Cohen's Point72 carries single-stock **puts** against several of your holdings; where puts exceed longs, the book is net short that name:

| Ticker | Cohen put | Cohen long | Net |
|---|---|---|---|
| **JNJ** | $484M | $65M | **7:1 net bearish** — biggest put in the overlap set |
| **TSLA** | $199M | $89M | **Net bearish** |
| **APP** | $99M | $35M | **Net bearish** |
| **VRT** | $25M | $12M | Net bearish |
| **CEG** | $31M | $20M | Net bearish |
| **GEV** | $24M | $16M | Net bearish |
| **COIN** | $27M | $22M | Net bearish |
| **GOOG** | $18M | $6M | Net bearish |
| **CORZ** | $1.5M | — | Put-only |

Plus **AAPL**: Cohen $109M put vs $142M long (hedged), and **Tepper is put-only $242M** — zero meaningful AAPL longs anywhere in the cohort. You hold $1,000.

*Read: multi-strat books hedge routinely — a put is risk data, not a directive. But a 9-name cluster of net-bearish puts on your staples-of-conviction (JNJ, TSLA, APP) is worth knowing before you add.*

## Zero whale interest (all 5 funds absent)
**BFLY, TEM, RXRX, SEI, TAP** — no smart-money footprint in this cohort. (XYZ removed after today's correction.)

## Manager snapshots
- **Point72** — top-10: SPY, CRDO, AMZN, ASML, AMD, MU, PG, ANET, MKSI, STX. 52 of your 58 singles overlap his 2,380-line book — mostly small % of book (incidental, not conviction). Carries big SPY puts *and* calls (market caution on both sides).
- **Coatue** — book grew **$29.1B → $48.6B (+67%) QoQ**; top went TSM/GEV/LRCX/AMAT → TSM/LRCX/MU/**SPCX**. New SpaceX position is his 4th-largest. Holds your entire AI-power trio (GEV/CEG/VRT) plus HUT at $1.1B.
- **D1** — 62% of the disclosed book is SpaceX. Rest is diversified: CART #2 (3.1%), JHX, NU, JCI, MELI, USFD, DHR, SHW, RDDT. You overlap on 12 names.
- **Appaloosa** — concentrated mega-cap tech + power: AMZN, MU, TSM, GOOG, UBER, EWY, META, VST, NRG, NVDA. AMZN+MU ≈ 30% of book. Only AAPL expression is a put.
- **SA (historical)** — the book that imploded: SNDK 28%, MU 27.5%, BE 9.4%, TSM, CRWV, CORZ, STM, APLD, RIOT. Citadel absorbed the blocks — exit overhang still hangs over MU/SNDK/CORZ/APLD/RIOT/CLSK/BE.

## Themes for your book
1. **Storage/memory complex (MU + SNDK + STX ≈ $16.8K)** — your most whale-aligned cluster: 4 managers + SA on the same thesis. Counter-signal: single-thesis concentration is exactly what sank SA. Both true — conviction trade, size accordingly.
2. **SpaceX** — D1 at 62% and Coatue entering is the quarter's standout signal; your SPCX rides the boldest concentration bet in the cohort.
3. **AI power & miners** — Cohen holds your whole mining/AI-power basket (RIOT, CLSK, CIFR, WULF, APLD, CORZ, HUT); Coatue concentrates in GEV/CEG/VRT/ETN. VG/LBRT/SEI have thinner coverage.
4. **Whale names you don't own:** LRCX, AMAT, AVGO, ASML (semi-cap — Coatue/Cohen loaded), CRDO (Cohen's #2), VST/NRG (Tepper's power), CRWV/STM (SA), UBER/META/NVDA.
5. **Gaps both ways:** whales avoid your staples/medtech (JNJ/PM/KO/WMT/HD/BFLY/TEM/TAP) except Cohen's diversified book — those are your ballast, not the trade. JNJ additionally carries his biggest single-stock put.
6. **AAPL bearish cluster** — both funds touching AAPL carry puts; nobody in the cohort is meaningfully long.

**Schedule note:** the agent spec says quarterly (Feb/May/Aug/Nov 15) but this cron still fires daily at 6:00 AM — pending your call since Sep 4. Daily runs just re-report the same quarter between filings (today's run added the XYZ correction).

*Data: 13f.info filing JSONs — accessions 0000919574-26-005520 (Point72), 0000919574-26-005478 (Coatue), 0001172661-26-003662 (D1), 0001656456-26-000003 (Appaloosa), 0000935836-26-000418 (SA). Cross-checked Sep 6 + Sep 7 fetches — identical. Values are 13F-reported ($000, as of 6/30/2026); option rows split put/call from longs.*

---

<!-- section:History Rhymes -->
## History Rhymes (07:03 CT)

# History Rhymes

**Run:** Tuesday, Sep 8, 2026, 7:00 AM CT (cron) · **Data through:** cash close Fri Sep 4 (Labor Day Sep 7) + Globex/futures Sep 8 pre-open · Sources: yfinance (28 instruments) + MarketWatch/WSJ RSS (Sep 8)

## Overnight changes — both standing triggers are now at the doorstep

| Signal | Sep 7 run | Now (Sep 8) | Read |
|---|---|---|---|
| **WTI crude** | $91.48 | **$93.91** (+2.7% overnight, +9.5%/5d, +63.6% YTD) — highest in >3 months | Houthis struck Saudi **civilian AND energy sites** (73 injured per Saudi-led coalition). Promotion trigger (close >$95) is ~1% away; **Brent is already near $100**. |
| **10Y Treasury** | 4.78% (Sep 4 close), 52-wk high 4.80% | Yields **rising in European trade** on oil + "increased likelihood of a rate hike next week" (WSJ) | Cash market reopens today after the 3-day gap. A close ≥4.80 = fresh 52-wk high; ≥4.90 opens the standing watch zone; ≥5.00 = kill-switch. |
| **Brent** | ~$97 (weekend) | **~$100** — "Oil Nears $100, Dow Futures Dip" (WSJ) | Triple-digit Brent is 1973/1979/2022 territory. |
| **ES / NQ futures** | — | ES 7,699 (−0.3%), NQ 29,557 (−0.03%) | Modest red, oil-driven, orderly. Tech still outperforming (NQ > ES). |
| **MU** | — | **$1,016.59** (+6.1% Fri, +256% YTD, −16% off its $1,213 high) | Memory-chip leg of the concentration trade intact (Tepper #2, Coatue #3 in MU). |
| **Yen / DXY** | — | **Yen at a 6-month high** on carry-unwind + Treasury-selldown flows (MW); DXY 98.97, below both MAs, *falling while yields rise* | New watch item: the historical de-grossing fuse (1998, 2007, Aug-2024). |
| **VIX / HYG** | 15.23 / −0.4% off high | 15.75 / −0.4% off high | Still zero stress priced — nothing hedged into a two-trigger week. |

Sector YTD unchanged through Friday: **XLE +45.3 · XLK +30.4 · RUT +19.9 > SPX +12.8 · XLY −3.4 (only negative)** — energy + tech leading together, small caps still leading broad, discretionary still straining.

## The rhymes, ranked (changes from Sep 7 marked)

### 1. 1999–2000 dot-com — PRIMARY (HIGH) — rate fingerprint approaching a full match
- **New confirmation leg:** the market now prices a **possible first HIKE** at FOMC Sep 15–16 (WSJ, European trade). The rhyme's one fingerprint mismatch — "easing bias vs rising long end" — is closing: 2026 is starting to echo 1999-2000, where the Fed *hiked* (Jun 1999 → May 2000) into a rising long end, negative ERP, record concentration, and oil that had tripled.
- **Citi's cycle study (MW today):** after the first hike of a cycle, US equities historically stumble modestly — and 1999's version was chop, then a *blowoff into March 2000*. A first hike is not the kill-switch; **the 10Y is**.
- **10Y doorstep:** 4.78% with the 52-wk high at 4.80% and overnight yields rising. Today's cash open is the first confirmation window in 4 sessions.
- **Mechanics note:** the Fed entered blackout (~Sep 5), so hike-odds repricing is running **unopposed** into CPI — one hot print has outsized power. Same mechanics as June 1999.
- **Kill/falsify unchanged:** daily close through **5.00%** = kill-switch. FOMC Sep 15–16 = resolution date.

### 2. 1970s stagflation — SECONDARY (MEDIUM) → **PROMOTION WATCH: one close from co-primary**
- The trigger written when this rhyme was set: *"WTI through $95–100 converts this from secondary to co-primary."* WTI sits at $93.91 with Brent ~$100 and Saudi energy infrastructure struck again — the exact escalation path flagged. Iran's promised Hormuz "restricted zone" declaration is still pending and is the next catalyst.
- **Base-rate caution (falsifiability both ways):** the last direct precedent — Abqaiq, Sep 2019 — spiked oil ~15% in a day and gave it all back within ~2 weeks as supply repaired. Promotion requires **sustained closes >$95**, not a print. A reversal below $90 demotes this again.
- What still argues against it: gold ($4,446, −16.4% off its high, **below its 200-day**) refuses to confirm the 1970s endgame. What argues for it: the **dollar is falling while yields rise** — the stagflationary pairing; a clean 1999 rhyme had a firm dollar.
- WSJ already connected the mechanics (Sep 1): *"Oil Prices Push Global Bond Market Closer to the Edge — rising energy costs are the inflationary trigger."*

### 3. 2016–17 reflation → 2018 rate shock — MEDIUM, rising with the rates leg
- A 10Y within 2bp of its 52-wk high into a VIX-15 / HYG-at-highs market is the same fuel-air mix as Jan–Feb 2018: one-sided positioning + rate repricing = fast, violent de-grossing. The modern template is **Aug-2024's yen-carry unwind** (VIX 12→65 intraday, SPX −6% in a day, recovered in weeks).
- **New fuse: the yen at a 6-month high**, attributed to carry-trade unwind + U.S. Treasury selldown (MW). That is the classic mechanism that turns calm into forced selling — and it pairs with the MW chip-chart piece telling investors to watch the *currency market* for money flowing in and out of chip stocks (the most crowded, most exposed trade).
- **Broadening still argues this rhyme over 1999-narrowing:** RUT leads SPX YTD by 7 points; Morgan Stanley is publicly calling for the next leaders to be "AI adopters"; WSJ reports software (Salesforce, Workday) holding fundamentals despite share pain. Leadership is widening, not narrowing — 2017-style broadening historically ends in a **rate shock, not a simultaneous sector blowoff**.

### 4. What is NOT rhyming — updated
- **Gold vs oil disagree:** oil is screaming 1970s; gold is below its 200-day and −16% off its high. The two inflation witnesses are in conflict — the dollar's path is the tiebreaker.
- **Not 2007:** credit untroubled (HYG +2.2% YTD, 0.4% from its high), curve steep (+102bp), not inverted.
- **Not 2000's breadth:** one negative sector today vs narrowing leadership into March 2000.
- **Dollar anomaly:** yields up + hike odds up, yet DXY falls below both MAs and the yen surges — inconsistent with a clean 1999 script (firm dollar), consistent with a debasement/stagflation undertone.

## Net read
Both standing triggers sit one daily close away on the same morning: **oil needs a close >$95** (Brent is already ~$100) and **the 10Y needs a close ≥4.80** to print a fresh 52-wk high (4.90 opens the watch zone, 5.00 is the kill-switch). Overnight flow — Saudi energy sites struck, hike odds rising during blackout, Brent nearing triple digits, futures red but orderly, VIX still 15.75 — says the market is treating this as an oil headline, not a regime change. That calm (HYG 0.4% from highs, RUT leading, nothing hedged) is the same one-sided positioning that made Feb-2018 and Aug-2024 violent. **This week's sequence — CPI → FOMC Sep 15–16 — is the resolution window. A 10Y close >4.90 into a priced hike moves the primary rhyme into its watch zone; two WTI closes >$95 promote the 1970s rhyme to co-primary. Either alone is a warning. Both together is the late-cycle signal.**

## Watch list (today → FOMC)
1. **10Y cash open (today):** first close in 4 sessions. ≥4.80 = fresh 52-wk high (confirmation leg); ≥4.90 = watch zone opens; ≥5.00 = kill-switch.
2. **WTI close vs $95** (Brent vs $100): sustained closes promote the 1970s rhyme to co-primary. Watch for Iran's Hormuz restricted-zone declaration.
3. **CPI (this week — verify exact date):** the Fed decider, landing while the Fed is in blackout — unopposed repricing risk (June-1999 mechanics).
4. **FOMC Sep 15–16:** a first hike completes the 1999–2000 rate fingerprint. Hike + 10Y < 4.90 = 1999-style chop, not crash. Hike + 10Y ≥ 5.00 = kill-switch.
5. **USDJPY / VIX term structure:** further yen strength = carry-unwind fuse (Aug-2024 template); watch the front of the VIX curve for the first stress flicker.
6. **Oracle (Thu):** AI-capex proxy into FOMC; a miss cuts the MU/memory leg (Tepper #2, Coatue #3) out from under the whales' quad-overlap book.
7. **Claims (date shifted this week, likely Thu):** forecast ~203.5K vs the 210K NO in the book — verify release date before the open.

*Not investment advice. Data: yfinance (cash close Sep 4; futures/FX/metals through Sep 8 pre-open; raw-percent yields) + MarketWatch/WSJ RSS (Sep 8). CAPE/P-E figures approximate per August baseline.*
