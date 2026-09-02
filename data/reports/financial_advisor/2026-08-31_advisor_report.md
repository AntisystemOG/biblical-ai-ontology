# Weekly Value Screen — Financial Advisor Report

**Date:** Monday, August 31, 2026 — 9:00 AM CDT (pre-market)
**Universe screened:** ~280 U.S. large/mid-cap stocks, all 11 sectors, market cap ≥ $5B
**Sources:** Yahoo Finance API (live quotes, fundamentals, analyst consensus), Finviz (insider transactions, rating actions). Real API data only — no simulated prices.

## Market Context (Friday close)

| Index | Level | Day |
|---|---|---|
| S&P 500 | 7,677.35 | -0.45% |
| Dow Jones | 53,234.75 | -0.61% |
| Nasdaq | 26,286.2 | -0.44% |
| VIX | 15.38 | calm |

Markets are near all-time highs with volatility muted. Cheap is a relative game right now — the screen below finds names trading at deep discounts **to their own sector**, not just absolute P/E.

## Methodology

1. Fetched live quotes for a ~280-ticker large-cap universe via Yahoo Finance (cookie+crumb authenticated API).
2. Computed **sector-relative P/E**: each stock's trailing and forward P/E versus the median of its sector peers in the universe (filters out sectors that are just structurally cheap/expensive). Stocks with distorted one-off P/Es excluded at this stage.
3. Shortlisted the 16 deepest discounts (≥ ~56% below sector median), then pulled full fundamentals per name: ROE, debt/equity, current ratio, FCF yield, EV/EBITDA, PEG, analyst targets/ratings.
4. Composite score (0–100): valuation discount (29), PEG (10), FCF yield (7), ROE (8), current ratio (4), leverage (7), analyst upside (10), rating (5), intrinsic-value estimate (8).
5. Insider activity + recent rating actions pulled from Finviz for the top 6 finalists.

**Sector medians used (trailing / forward P/E):** Tech 33.0/19.3 · Healthcare 29.3/15.6 · Financials 14.2/11.3 · Cons. Disc. 20.8/16.3 · Staples 22.7/15.6 · Energy 17.9/13.4 · Industrials 29.6/22.4 · Materials 19.7/13.6 · Real Estate 28.6/31.6 · Comm. Svcs 17.0/13.5

---

# Top 5 Picks

## 1. The Cigna Group (CI) — $278.45 · Healthcare · Score 58

| Metric | Value | vs Healthcare median |
|---|---|---|
| Trailing P/E | 11.5x | 29.3x → **61% discount** |
| Forward P/E | 8.3x | 15.6x → **47% discount** |
| FCF yield | 10.8% | strong |
| EV/EBITDA | 7.7x | cheap |
| PEG | 0.83 | < 1 |
| ROE | ~20% | quality |
| Dividend | 2.2% | |
| Analysts | 24 · Buy · median target $343 (+23.2%) | |
| Balance sheet | D/E 74%, current ratio 0.85 (normal for an insurer) | |

**Thesis:** Managed-care/med-services names have been the market's dumping ground; Cigna is a diversified health-services complex (Evernorth PBM + pharmacy + insurance) trading at roughly half its sector's multiple on every line of the ledger, with double-digit FCF yield and ~20% ROE. Consensus says +23% to target. The "cheap because hated" profile — but earnings keep arriving, and buybacks at these prices compound per-share value fast.

**Risks:** PBM regulation (Evernorth reform risk), industry-wide medical cost trend, GLP-1 benefit design. Insider transactions were net negative (−5.4%) — watch as a counter-signal.

---

## 2. Fidelity National Information Services (FIS) — $41.00 · Payments/Fin-infra · Score 58

| Metric | Value |
|---|---|
| Trailing P/E | 6.3x vs tech median 33.0x → **81% discount** (deepest on the screen) |
| Forward P/E | 6.1x |
| FCF yield | 12.5% |
| EV/EBITDA | 11.9x · PEG 0.23 · Dividend 4.1% |
| Analysts | 23 · Buy · median target $50 (+22.0%) |
| 52-wk range position | 11% (near lows) |
| **Insider transactions** | **+2.99% net BUYING** — best insider signal on the screen |

**Thesis:** The banking/payments core-processing franchise is priced like a melting ice cube while the tech sector median sits at 33x. Trailing P/E is flattered by one-off items, but 6.1x forward with 12.5% FCF yield and a 4% dividend leaves a wide margin of safety. The Worldpay majority-stake sale closing should fund deleveraging — the main balance-sheet overhang (D/E 133%, current ratio 0.54). Insiders adding at $40s is the tell: they know the deleveraging math.

**Risks:** Leverage (the #1 thing to track), execution of Worldpay separation, bank-tech capex cycles. Weak current ratio means lumpy cash timing; not a buy-the-dip-and-forget name.

---

## 3. Viatris (VTRS) — $16.27 · Healthcare · Score 60.7 (2nd highest score)

| Metric | Value |
|---|---|
| Forward P/E | 6.1x vs healthcare median 15.6x → **61% discount** |
| FCF yield | **14.3%** — highest clean FCF yield on the screen |
| EV/EBITDA | 7.2x · PEG 1.05 · Dividend 2.9% |
| Analysts | 8 · Buy · median target $19 (+16.8%) · UBS upgraded Neutral→Buy, PT $18 (2026) |
| Balance sheet | current ratio 1.58, D/E 96% (elevated) |

**Thesis:** Off-patent branded + generics cash-flow machine that never gets credit. GAAP ROE is ~0 on paper because of amortization charges — which is exactly why the stock screens at 6x forward while generating real free cash. Management directs FCF to debt paydown, dividend, and tuck-in M&A. You're buying ~$2.7B of annual FCF for a ~$19B market cap.

**Risks:** $19B+ debt stack leaves little room for error; brand erosion; pipeline is shallow. This is a cash-yield position, not a compounder — size accordingly.

---

## 4. Micron Technology (MU) — $946.89 · Semis (AI memory) · Score 65 (highest)

| Metric | Value |
|---|---|
| Forward P/E | 6.1x vs tech median 19.3x → **68% discount** |
| Trailing P/E | 21.4x |
| PEG | **0.14** · ROE ~70% |
| Balance sheet | D/E 6%, current ratio 3.42 — fortress |
| Analysts | 44 · Strong Buy · median target $1,545 (+63.2%) |
| Recent actions | New Street **upgrade** Neutral→Buy, PT $1,250 (Aug 2026); Erste Group Hold→Buy, Needham Buy PT $1,550→$1,650 (Jun 2026) |
| FCF yield | 0.7% (heavy HBM capex — deliberate) |

**Thesis:** The AI memory supercycle has made Micron a ~$1T company, and yet forward earnings still price it at 6x. HBM (high-bandwidth memory) is supply-contracted years out; balance sheet is the cleanest on this list. PEG of 0.14 and 44 analysts at Strong Buy with +63% consensus target says the street sees the earnings ramp continuing.

**Risks — read this one carefully:** This is a **cyclical** cheapening, not a classic value compounder. 6x forward P/E on *peak* earnings is how memory stocks look right before cycles roll. Insider transactions −7.67% (selling into strength). FCF is being reinvested at max capex — normal at cycle peaks. Treat as tradeable value with a hard exit discipline, not a buy-and-forget.

---

## 5. Zoom Communications (ZM) — $97.32 · Software · Score 58

| Metric | Value |
|---|---|
| Trailing P/E | 9.0x vs tech median 33.0x → **73% discount** |
| Balance sheet | **D/E 1%, current ratio 3.83** — near-net-cash fortress, best balance sheet on the screen |
| FCF yield | 7.0% · EV/EBITDA 16x |
| Revenue multiple | ~6x sales, profitable, buybacks running |
| Analysts | 25 · Buy · median target $120 (+23.3%) |

**Thesis:** The market prices Zoom as a slow-decline story (hence 9x trailing). The cash-generative core keeps printing ~$2B FCF with essentially no debt. At these levels you're getting the fortress balance sheet and the cash flows for free against any AI-workplace optionality (AI Companion, Zoom Phone, Contact Center). Classic "no growth priced, modest growth delivered" setup.

**Risks:** PEG 4.2 is the honest warning — growth is scarce and Teams/Meet bundling keeps pressure on seat pricing. Insider transactions −1.0%. If revenue keeps decelerating below consensus, the multiple compresses to value-trap territory.

---

# Honorable Mentions

- **GM ($87.09, CD sector)** — 5.9x fwd, 27.8% FCF yield, PEG 0.34, Buy, +16.5% target. Near 52-wk high (87% of range) and zero book equity from buybacks (D/E 202% is a buyback artifact). Cheap truck/EV-transition hedge.
- **VICI Properties ($25.66, REIT)** — 8.6x fwd, 7.0% dividend yield, Buy, +24.7% target, sitting **1% above its 52-wk low**, 4 upgrade-headline items on Finviz. Rate-sensitive; tenant concentration (Caesars/MGM) is the trade-off. FCF-yield metric not meaningful for REITs — dividend yield is the real tell.
- **Zoetis ($76.43, Animal Health)** — 12.5x trailing, ROE ~60%, Buy, +23% target, at 6% of its 52-wk range. Quality franchise in a deep drawdown; PEG 6.7 says growth has stalled — only for patient hands.
- **Charter (CHTR, $151.41)** — 3.4x fwd P/E, but 442% D/E, Hold, target −0.9%. The deep discount is *earned*. Only for special-situation investors.
- **Allstate (ALL, $260.42)** — 5.2x trailing is catastrophe-timing distortion; forward 9.4x, Hold rating. Auto-insurance pricing cycle is past peak.

# Stocks Screened Out (distorted data, flagged for transparency)

- **GPN** — trailing 43x is Worldpay-sale accounting noise; fwd 5.7x is real but analysts see only 4% upside from here.
- **HON** — trailing 8.2x is a spin-off artifact (Solstice split); real forward multiple 21.4x. Not actually 72% cheap.
- **HPQ** — negative book value from buybacks; hold rating; excluded.
- **MKC, M, UAL, CI-adjacent names** — flagged but scored lower on balance sheet or growth.

---

## Watchlist / Next Steps

1. **Earnings calendar check** — CI and VTRS report this month; verify no pre-announcement before sizing.
2. **FIS Worldpay close** — the single biggest catalyst on the list for deleveraging math.
3. **Monitor MU insider sales** — if the −7.67% trend accelerates, that's the cycle-top tell.
4. Re-run screen next Monday (Sep 7 is Labor Day — market closed; next run effectively carries into Sep 8 open prices).

## Data Integrity Notes

- All prices/fundamentals pulled live from Yahoo Finance authenticated API and Finviz pages on 2026-08-31 (pre-market). No simulated or estimated prices anywhere in this report.
- `pegRatio`, `fcfY`, and 52-wk positions are as-reported; ROE for a few names (GM ~0) reflects buyback-shrunken equity, not operational weakness.
- Finviz "Insider Trans %" = net insider transactions over the recent period (proxy for buying/selling activity), not Form 4 verified.
- Intrinsic-value (Graham) column was blank this week because 5-year growth estimates weren't served by the API for the shortlist; PEG + EV/EBITDA substituted.

*Research for information purposes only — not investment advice. Not affiliated with any broker. Verify before acting.*

— Spock 🖖 · financial-advisor agent · run 2026-08-31 09:00 CDT