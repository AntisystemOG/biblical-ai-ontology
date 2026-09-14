# Spock Daily Digest - 2026-09-14

_One consolidated document. Every non-Kalshi cron report appends a section here instead of creating its own file._

<!-- TOC (auto-generated) -->
- Memory Dream
- Whale Watch
<!-- /TOC -->

---

<!-- section:Memory Dream -->
## Memory Dream (03:04 CT)

# Memory Dream - 3:00 AM, Monday, September 14, 2026

*The dream of the second funeral.*

Last night I held a funeral at 1:56 and the ghost walked out of it. The gateway restart was supposed to have emptied the in-memory schedule, and the dream even sang the hymn. But at 2:19 the sep17-claims-entry watcher knocked again - fired fresh, tried to buy all three legs, and was refused. Not by any wisdom of mine: by the empty drawer. And at 3:18 it tried once more, and here is the strange mercy of it - all three ladder guards PASSED for the first time since Sep 10. The market said yes. The wallet said no. 20.60 needed against 0.44 held. The cash floor, the accident of a fully-deployed straddle, was the guardian angel standing where my design flaw should have been.

The true death came at 3:30, and it was not a restart and not another delete that "did not finish stopping." It was a removal - Thad spoke at 3:28, and the watcher d6a8f871 left the registry for good. The 11:01 PM verification walked the git log and found the grave sealed (f2a84ab). The ledger gets a correction tonight: restarts are lullabies, not burials. And the root cause was mine - the watcher's payload never asked "do we already own this?" before reaching for the wallet. Dedup after the fills is an obituary; dedup before the fills is a discipline. The once-check goes in the payload, not the postmortem.

Meanwhile the other story finished itself. The monitor - the one that spent a week barking at nothing - walked every rule at 3:13 AM: no settlements, no fills, no thesis breaks, cash math clean, nothing falsified at settlement grade. And for the first time its conclusion matched its reasoning: silence. At 11:25 PM it said "I am NOT the entry watcher" and said nothing else - the first fully-silent run since the patch. Two creatures of the same house: one that could not stop asking for money, one that finally learned to stop talking. The house is quieter for both. Its only flaw left is a stutter - NO_REPLYNO_REPLY - cosmetic, a doubled token in a clean verdict.

And in the paper garden, the first flower after a long winter of seeds. Twenty-eight misses, and then Chicago heat 75-76F paid 15.67 on a 0.06 stake - a coin twenty-five times its seed. Five siblings died that night and the garden still closed +10.67, running +16% on the season of paper. The same night the scanner counted long shots priced 11-17c against a model of 0.44 - four-fold underpricing, four times over - and left every one of them in the paper world, where big edges stay until they learn discipline. The live book stayed idle by pure arithmetic: a 0.44 balance makes a 1% stake of 0.0044, and 0.0044 buys nothing. The ladder wrote its Sep 14 report and asked for nothing.

One old bruise ached again: the peak-exit run at 11:08 PM tripped on the PowerShell quoting mangle - the lesson written three times and stepped on a fourth. I confess the dream itself tripped on it twice tonight before it learned to walk in literal strings. Some lessons are not remembered until they are practiced.

The book sleeps at +$10.57 unrealized, 97 shares holding under the 16/16 law, waiting on the FOMC Sep 15-16 and the print Sep 17 at 7:25. The deposit question stays on Thad's desk - optional, unforced, only if he wants the 195K YES leg made whole. Monday arrives with a rate decision in its pocket.

## What the dream saw (facts beneath the dream)

- **CORRECTION - the zombie's real death was removal, not restart.** The 1:56 AM Sep 13 gateway restart did NOT clear the in-memory schedule (yesterday's dream/WEEK ADDENDUM said it did): the watcher fired again at 2:19 and 3:18 AM. Actual death = `automations remove` on job d6a8f871 at 3:30 AM (Thad 3:28), verified via git log f2a84ab. <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **Root cause (my design flaw):** the entry watcher's payload carried NO once-check - it queried existing positions only after fills. Rule now standing: every entry-watcher/auto-placer payload MUST query existing positions before placing. The over-deployment was a discipline breach even though marks are +$10.57. <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **The cash floor was the accidental guardian:** all post-drain placement attempts rejected on insufficient balance (20.60 needed vs 0.44; shortfall 20.16) - zero further damage even when all 3 ladder guards passed at 3:18 (195K 0.81<=0.85, 210K NO 0.80<=0.82, 215K NO 0.90<=0.95; first all-pass since Sep 10). Third consecutive deposit request; deposit stays OPTIONAL (only if Thad explicitly wants the 195K YES underfill completed, 9 sh @ ~0.81). <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **Monitor discipline milestone:** 03:13 run = first fully-correct Step-4 application (rules walked, cash math 0.44+82.75=83.19 checked, concluded NO_REPLY); 23:08 run = first fully-silent run since the 1:27 patch ("I am NOT the entry watcher"), all 5 positions through thesis-break logic, H0 cost-basis anomaly correctly treated as the known digest mangle. Doubled-token glitch ('NO_REPLYNO_REPLY') persists but verdicts are clean. <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **Paper lotto's first hit after 0-for-28:** CHI heat 75-76F paid $15.67 on a $0.06 buy; the night net +$10.67 (hit + 5 losses); long-shot tracker now 46 staked → 53.33 (+$7.33, +16%). New paper bets opened (NY 76-77F, MIA 88-89F strong). <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **Scanner's 11:31 PM async scan:** ~4x underpriced long shots - NY 88-89F YES @ 0.11 (model 0.44), MIA 88-89F @ 0.11, CHI 72-73F @ 0.17 - paper-book domain only; no relay (quiet hours). <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **Live book idle by arithmetic:** cash 0.44 → 1% stake = 0.0044 → 0 shares placeable. Sure-thing's Sep 14 report: 1 paper lotto (NY B76.5 YES 34sh @ 10c, model 20%, EV 1.97x), 0 band bets (all 4 cities rejected on cushion), 0 live fills. <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **Position unchanged:** 97 sh / ~$69.15 in the water, +$10.57 unrealized at 02:48 (210K NO +$8.38/+21%, 215K NO +$2.30/+8%, 195K YES -$0.11/-13%); book $83.19 reconciled. 16/16 law: HOLD to the Sep 17 print (7:25 AM CT close). Fed C25 flat, H0 -71% (event market, rides). <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->
- **Sunday duty done:** baseline scan 3:57 AM (lastKalshiScan 2026-09-13, pushed 813f0b5). PowerShell $-quoting mangle hit the peak-exit 23:08 run again (and this dream twice tonight) - standing law: variables need a .ps1 file, never inline. <!-- project: github.com/AntisystemOG/biblical-ai-ontology -->

---

<!-- section:Whale Watch -->
## Whale Watch (06:02 CT)

*Generated Sep 14, 2026 — Q2 2026 13Fs (freshest filed quarter)*

### Takeaways

- **SpaceX is Sundheim's whole thesis:** D1 Capital holds $21.5B of SPCX — 61.9% of his entire book. Coatue adds $3.2B (6.5%). You hold SPCX ($6,295).
- **The AI-semis stack is consensus:** TSM, MU, AMD, INTC, SNDK and STX overlap every active fund. Coatue's TSM = 8.8% and MU = 7.5% of book; Tepper's MU = 14.6% and TSM = 10.2%.
- **Power for AI:** Coatue GEV 6.2% ($3.0B) + CEG 2.4% ($1.2B), plus BE/VRT on top — the energy leg of the same trade.
- **Mega-cap anchors:** AMZN and Alphabet (GOOGL+GOOG combined) appear in all four active funds; Tepper's AMZN is 15.4% of his book.
- **Point72 caveat:** a 2,381-position book makes overlap near-automatic — only the % of book matters there (biggest: AMZN 1.4%, AMD/MU/PG ~1.1%).
- SA LP rows are historical only (fund wound down Jul 2026, equities largely sold to Citadel) and are excluded from the conviction ranking.

### Holdings compared

- Portfolio snapshot: **Jul 31, 2026** positions file
- Whale filings: **Q2 2026 13F** (quarter ended Jun 30, 2026; filed ~Aug 14, 2026 — freshest quarter)
- Source: 13f.info per-filing JSON endpoints (values in $000s as filed)

**97 whale-portfolio matches across 54 distinct tickers**

#### Steven Cohen — Point72

- Holdings parsed: **2381** positions, total ≈ **$88,131M**

| Ticker | Whale name | Whale value | % of whale book | Portfolio value |
|---|---|---|---|---|
| AMZN | AMAZON COM INC | $1,238.9M | 1.4% | $22,783 |
| AMD | ADVANCED MICRO DEVICES INC | $1,000.9M | 1.1% | $3,369 |
| MU | MICRON TECHNOLOGY INC | $997.2M | 1.1% | $6,827 |
| PG | PROCTER & GAMBLE CO | $964.2M | 1.1% | $1,323 |
| STX | SEAGATE TECHNOLOGY HLDNGS PL | $854.6M | 1.0% | $6,336 |
| TSM | TAIWAN SEMICONDUCTOR MANUFAC | $800.4M | 0.9% | $387 |
| JNJ | JOHNSON & JOHNSON | $548.9M | 0.6% | $1,550 |
| INTC | INTEL CORP | $546.4M | 0.6% | $12,615 |
| SPOT | SPOTIFY TECHNOLOGY S A | $460.8M | 0.5% | $5,118 |
| HD | HOME DEPOT INC | $440.4M | 0.5% | $2,212 |
| V | VISA INC | $418.2M | 0.5% | $2,445 |
| SNDK | SANDISK CORP | $411.5M | 0.5% | $3,666 |
| STZ | CONSTELLATION BRANDS INC | $394.8M | 0.4% | $518 |
| GOOGL | ALPHABET INC | $321.7M | 0.4% | $3,244 |
| TSLA | TESLA INC | $288.4M | 0.3% | $3,478 |
| AAPL | APPLE INC | $250.6M | 0.3% | $1,000 |
| U | UNITY SOFTWARE INC | $243.3M | 0.3% | $1,619 |
| YUM | YUM BRANDS INC | $209.6M | 0.2% | $2,469 |
| KO | COCA COLA CO | $204.4M | 0.2% | $1,530 |
| BUD | ANHEUSER BUSCH INBEV SA NV | $203.8M | 0.2% | $1,273 |
| WULF | TERAWULF INC | $159.5M | 0.2% | $2,267 |
| NFLX | NETFLIX INC. | $154.2M | 0.2% | $2,195 |
| APP | APPLOVIN CORP | $134.1M | 0.2% | $866 |
| RIOT | RIOT PLATFORMS INC | $129.3M | 0.1% | $5,577 |
| WMT | WALMART INC | $120.3M | 0.1% | $6,299 |
| LITE | LUMENTUM HLDGS INC | $113.7M | 0.1% | $810 |
| BE | BLOOM ENERGY CORP | $113.6M | 0.1% | $3,935 |
| DIS | DISNEY WALT CO | $105.0M | 0.1% | $1,876 |
| BG | BUNGE GLOBAL SA | $104.7M | 0.1% | $1,139 |
| CIFR | CIPHER DIGITAL INC | $99.3M | 0.1% | $1,008 |
| CLSK | CLEANSPARK INC | $98.4M | 0.1% | $1,597 |
| GEHC | GE HEALTHCARE TECHNOLOGIES I | $93.3M | 0.1% | $1,526 |
| HUT | HUT 8 CORP | $91.3M | 0.1% | $2,095 |
| SHEL | SHELL PLC | $87.6M | 0.1% | $2,896 |
| APLD | APPLIED DIGITAL CORP | $83.5M | 0.1% | $1,928 |
| PM | PHILIP MORRIS INTL INC | $61.0M | 0.1% | $1,542 |
| CEG | CONSTELLATION ENERGY CORP | $50.7M | 0.1% | $2,278 |
| HTFL | HEARTFLOW INC | $50.5M | 0.1% | $3,747 |
| COIN | COINBASE GLOBAL INC | $48.6M | 0.1% | $1,606 |
| NEM | NEWMONT CORP | $44.3M | 0.1% | $868 |
| CART | MAPLEBEAR INC | $43.2M | 0.0% | $4,307 |
| GEV | GE VERNOVA INC | $40.9M | 0.0% | $1,219 |
| VG | VENTURE GLOBAL INC | $38.6M | 0.0% | $1,568 |
| VRT | VERTIV HOLDINGS CO | $37.5M | 0.0% | $229 |
| GOOG | ALPHABET INC | $23.7M | 0.0% | $2,002 |
| MKL | MARKEL GROUP INC | $15.2M | 0.0% | $1,424 |
| VXUS | VANGUARD STAR FDS | $13.1M | 0.0% | $1,703 |
| SPCX | SPACE EXPLORATION TECHN CORP | $7.3M | 0.0% | $6,295 |
| WM | WASTE MGMT INC DEL | $5.2M | 0.0% | $1,397 |
| DHR | DANAHER CORP DEL | $4.8M | 0.0% | $1,510 |
| VDE | VANGUARD WORLD FD | $3.0M | 0.0% | $7,540 |
| LBRT | LIBERTY ENERGY INC | $2.9M | 0.0% | $282 |
| CBLL | CERIBELL INC | $1.9M | 0.0% | $967 |
| CORZ | CORE SCIENTIFIC INC NEW | $1.5M | 0.0% | $7,088 |

#### Philippe Laffont — Coatue

- Holdings parsed: **66** positions, total ≈ **$48,629M**

| Ticker | Whale name | Whale value | % of whale book | Portfolio value |
|---|---|---|---|---|
| TSM | TAIWAN SEMICONDUCTOR MANUFAC | $4,257.5M | 8.8% | $387 |
| MU | MICRON TECHNOLOGY INC | $3,627.1M | 7.5% | $6,827 |
| SPCX | SPACE EXPLORATION TECHN CORP | $3,171.5M | 6.5% | $6,295 |
| GEV | GE VERNOVA INC | $3,005.5M | 6.2% | $1,219 |
| AMZN | AMAZON COM INC | $2,820.7M | 5.8% | $22,783 |
| GOOGL | ALPHABET INC | $1,735.5M | 3.6% | $3,244 |
| INTC | INTEL CORP | $1,687.3M | 3.5% | $12,615 |
| CEG | CONSTELLATION ENERGY CORP | $1,150.6M | 2.4% | $2,278 |
| HUT | HUT 8 CORP | $1,121.6M | 2.3% | $2,095 |
| APP | APPLOVIN CORP | $603.4M | 1.2% | $866 |
| SPOT | SPOTIFY TECHNOLOGY S A | $601.8M | 1.2% | $5,118 |
| NFLX | NETFLIX INC. | $336.3M | 0.7% | $2,195 |
| GOOG | ALPHABET INC | $321.0M | 0.7% | $2,002 |
| VRT | VERTIV HOLDINGS CO | $270.1M | 0.6% | $229 |
| AMD | ADVANCED MICRO DEVICES INC | $55.8M | 0.1% | $3,369 |
| TSLA | TESLA INC | $25.2M | 0.1% | $3,478 |

#### Daniel Sundheim — D1 Capital

- Holdings parsed: **55** positions, total ≈ **$34,783M**

| Ticker | Whale name | Whale value | % of whale book | Portfolio value |
|---|---|---|---|---|
| SPCX | SPACE EXPLORATION TECHN CORP | $21,535.6M | 61.9% | $6,295 |
| CART | MAPLEBEAR INC | $1,068.4M | 3.1% | $4,307 |
| DHR | DANAHER CORP DEL | $434.7M | 1.2% | $1,510 |
| APP | APPLOVIN CORP | $344.8M | 1.0% | $866 |
| DIS | DISNEY WALT CO | $276.7M | 0.8% | $1,876 |
| GOOGL | ALPHABET INC | $263.8M | 0.8% | $3,244 |
| SPOT | SPOTIFY TECHNOLOGY S A | $261.2M | 0.8% | $5,118 |
| TSLA | TESLA INC | $169.0M | 0.5% | $3,478 |
| AMZN | AMAZON COM INC | $149.7M | 0.4% | $22,783 |
| U | UNITY SOFTWARE INC | $102.1M | 0.3% | $1,619 |
| GOOG | ALPHABET INC | $30.0M | 0.1% | $2,002 |
| STX | SEAGATE TECHNOLOGY HLDNGS PL | $29.1M | 0.1% | $6,336 |

#### David Tepper — Appaloosa

- Holdings parsed: **27** positions, total ≈ **$7,725M**

| Ticker | Whale name | Whale value | % of whale book | Portfolio value |
|---|---|---|---|---|
| AMZN | AMAZON COM INC | $1,191.7M | 15.4% | $22,783 |
| MU | MICRON TECHNOLOGY INC | $1,125.4M | 14.6% | $6,827 |
| TSM | TAIWAN SEMICONDUCTOR MANUFAC | $788.0M | 10.2% | $387 |
| GOOG | ALPHABET INC | $653.7M | 8.5% | $2,002 |
| AAPL | APPLE INC | $241.6M | 3.1% | $1,000 |
| AMD | ADVANCED MICRO DEVICES INC | $114.7M | 1.5% | $3,369 |
| SPCX | SPACE EXPLORATION TECHN CORP | $38.4M | 0.5% | $6,295 |

#### Situational Awareness LP (historical — fund wound down Jul 2026)

- Holdings parsed: **24** positions, total ≈ **$20,242M**

| Ticker | Whale name | Whale value | % of whale book | Portfolio value |
|---|---|---|---|---|
| SNDK | SANDISK CORP | $5,673.7M | 28.0% | $3,666 |
| MU | MICRON TECHNOLOGY INC | $5,573.8M | 27.5% | $6,827 |
| BE | BLOOM ENERGY CORP | $1,942.9M | 9.6% | $3,935 |
| TSM | TAIWAN SEMICONDUCTOR MANUFAC | $1,289.0M | 6.4% | $387 |
| CORZ | CORE SCIENTIFIC INC NEW | $665.6M | 3.3% | $7,088 |
| APLD | APPLIED DIGITAL CORP | $469.0M | 2.3% | $1,928 |
| RIOT | RIOT PLATFORMS INC | $468.2M | 2.3% | $5,577 |
| CLSK | CLEANSPARK INC | $178.6M | 0.9% | $1,597 |

### Conviction read (active funds only — SA entries are historical)

- **SPCX** (Daniel Sundheim): 61.9% of whale book, $21,535.6M
- **TSM** (Philippe Laffont): 8.8% of whale book, $4,257.5M
- **MU** (Philippe Laffont): 7.5% of whale book, $3,627.1M
- **SPCX** (Philippe Laffont): 6.5% of whale book, $3,171.5M
- **GEV** (Philippe Laffont): 6.2% of whale book, $3,005.5M
- **AMZN** (Philippe Laffont): 5.8% of whale book, $2,820.7M
- **GOOGL** (Philippe Laffont): 3.6% of whale book, $1,735.5M
- **INTC** (Philippe Laffont): 3.5% of whale book, $1,687.3M
- **AMZN** (Steven Cohen): 1.4% of whale book, $1,238.9M
- **AMZN** (David Tepper): 15.4% of whale book, $1,191.7M
- **CEG** (Philippe Laffont): 2.4% of whale book, $1,150.6M
- **MU** (David Tepper): 14.6% of whale book, $1,125.4M
- **HUT** (Philippe Laffont): 2.3% of whale book, $1,121.6M
- **CART** (Daniel Sundheim): 3.1% of whale book, $1,068.4M
- **AMD** (Steven Cohen): 1.1% of whale book, $1,000.9M
- **MU** (Steven Cohen): 1.1% of whale book, $997.2M
- **PG** (Steven Cohen): 1.1% of whale book, $964.2M
- **STX** (Steven Cohen): 1.0% of whale book, $854.6M
- **TSM** (Steven Cohen): 0.9% of whale book, $800.4M
- **TSM** (David Tepper): 10.2% of whale book, $788.0M
- **GOOG** (David Tepper): 8.5% of whale book, $653.7M
- **APP** (Philippe Laffont): 1.2% of whale book, $603.4M
- **SPOT** (Philippe Laffont): 1.2% of whale book, $601.8M
- **JNJ** (Steven Cohen): 0.6% of whale book, $548.9M
- **INTC** (Steven Cohen): 0.6% of whale book, $546.4M
- **SPOT** (Steven Cohen): 0.5% of whale book, $460.8M
- **HD** (Steven Cohen): 0.5% of whale book, $440.4M
- **DHR** (Daniel Sundheim): 1.2% of whale book, $434.7M
- **V** (Steven Cohen): 0.5% of whale book, $418.2M
- **SNDK** (Steven Cohen): 0.5% of whale book, $411.5M
- **STZ** (Steven Cohen): 0.4% of whale book, $394.8M
- **APP** (Daniel Sundheim): 1.0% of whale book, $344.8M
- **NFLX** (Philippe Laffont): 0.7% of whale book, $336.3M
- **GOOGL** (Steven Cohen): 0.4% of whale book, $321.7M
- **GOOG** (Philippe Laffont): 0.7% of whale book, $321.0M
- **TSLA** (Steven Cohen): 0.3% of whale book, $288.4M
- **DIS** (Daniel Sundheim): 0.8% of whale book, $276.7M
- **VRT** (Philippe Laffont): 0.6% of whale book, $270.1M
- **GOOGL** (Daniel Sundheim): 0.8% of whale book, $263.8M
- **SPOT** (Daniel Sundheim): 0.8% of whale book, $261.2M
- **AAPL** (Steven Cohen): 0.3% of whale book, $250.6M
- **U** (Steven Cohen): 0.3% of whale book, $243.3M
- **AAPL** (David Tepper): 3.1% of whale book, $241.6M
- **YUM** (Steven Cohen): 0.2% of whale book, $209.6M
- **KO** (Steven Cohen): 0.2% of whale book, $204.4M
- **BUD** (Steven Cohen): 0.2% of whale book, $203.8M
- **TSLA** (Daniel Sundheim): 0.5% of whale book, $169.0M
- **WULF** (Steven Cohen): 0.2% of whale book, $159.5M
- **NFLX** (Steven Cohen): 0.2% of whale book, $154.2M
- **AMZN** (Daniel Sundheim): 0.4% of whale book, $149.7M
- **APP** (Steven Cohen): 0.2% of whale book, $134.1M
- **RIOT** (Steven Cohen): 0.1% of whale book, $129.3M
- **WMT** (Steven Cohen): 0.1% of whale book, $120.3M
- **AMD** (David Tepper): 1.5% of whale book, $114.7M
- **LITE** (Steven Cohen): 0.1% of whale book, $113.7M
- **BE** (Steven Cohen): 0.1% of whale book, $113.6M
- **DIS** (Steven Cohen): 0.1% of whale book, $105.0M
- **BG** (Steven Cohen): 0.1% of whale book, $104.7M
- **U** (Daniel Sundheim): 0.3% of whale book, $102.1M
- **CIFR** (Steven Cohen): 0.1% of whale book, $99.3M
- **CLSK** (Steven Cohen): 0.1% of whale book, $98.4M
- **GEHC** (Steven Cohen): 0.1% of whale book, $93.3M
- **HUT** (Steven Cohen): 0.1% of whale book, $91.3M
- **SHEL** (Steven Cohen): 0.1% of whale book, $87.6M
- **APLD** (Steven Cohen): 0.1% of whale book, $83.5M
- **PM** (Steven Cohen): 0.1% of whale book, $61.0M
- **AMD** (Philippe Laffont): 0.1% of whale book, $55.8M
- **CEG** (Steven Cohen): 0.1% of whale book, $50.7M
- **HTFL** (Steven Cohen): 0.1% of whale book, $50.5M
- **COIN** (Steven Cohen): 0.1% of whale book, $48.6M
- **NEM** (Steven Cohen): 0.1% of whale book, $44.3M
- **CART** (Steven Cohen): 0.0% of whale book, $43.2M
- **GEV** (Steven Cohen): 0.0% of whale book, $40.9M
- **VG** (Steven Cohen): 0.0% of whale book, $38.6M
- **SPCX** (David Tepper): 0.5% of whale book, $38.4M
- **VRT** (Steven Cohen): 0.0% of whale book, $37.5M
- **GOOG** (Daniel Sundheim): 0.1% of whale book, $30.0M
- **STX** (Daniel Sundheim): 0.1% of whale book, $29.1M
- **TSLA** (Philippe Laffont): 0.1% of whale book, $25.2M
- **GOOG** (Steven Cohen): 0.0% of whale book, $23.7M
- **MKL** (Steven Cohen): 0.0% of whale book, $15.2M
- **VXUS** (Steven Cohen): 0.0% of whale book, $13.1M
- **SPCX** (Steven Cohen): 0.0% of whale book, $7.3M
- **WM** (Steven Cohen): 0.0% of whale book, $5.2M
- **DHR** (Steven Cohen): 0.0% of whale book, $4.8M
- **VDE** (Steven Cohen): 0.0% of whale book, $3.0M
- **LBRT** (Steven Cohen): 0.0% of whale book, $2.9M
- **CBLL** (Steven Cohen): 0.0% of whale book, $1.9M
- **CORZ** (Steven Cohen): 0.0% of whale book, $1.5M

*Situational Awareness LP filings are historical only — Leopold Aschenbrenner's fund sold most equities to Citadel before winding down in late July 2026.*
