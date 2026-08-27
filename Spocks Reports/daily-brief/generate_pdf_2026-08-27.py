#!/usr/bin/env python3
"""Generate Daily Brief PDF - August 27, 2026"""

from fpdf import FPDF
import re

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(45, 55, 72)
        self.cell(0, 10, 'Daily Brief - Ground News Cross-Spectrum Analysis', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Thursday, August 27, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def clean_text(text):
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('\u2014', '-')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2018', "'")
    text = text.replace('\u2019', "'")
    text = text.replace('\u201C', '"')
    text = text.replace('\u201D', '"')
    text = text.replace('\u2022', '*')
    text = text.replace('\u2026', '...')
    text = text.replace('\u2190', '<-')
    text = text.replace('\u2192', '->')
    return text

def add_section_title(pdf, title, level=1):
    if level == 1:
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(45, 55, 72)
        pdf.ln(8)
    elif level == 2:
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(66, 83, 105)
        pdf.ln(6)
    else:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(80, 100, 130)
        pdf.ln(4)
    pdf.cell(0, 8, clean_text(title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

def add_paragraph(pdf, text, indent=False):
    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(20 if indent else 10)
    pdf.multi_cell(190, 5, clean_text(text))
    pdf.ln(2)

def add_bullet(pdf, text):
    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(15)
    pdf.cell(5, 5, '*', new_x="RIGHT")
    pdf.multi_cell(175, 5, clean_text(text))

def add_highlight(pdf, label, text, color_type='neutral'):
    if color_type == 'bullish':
        pdf.set_text_color(0, 128, 0)
    elif color_type == 'bearish':
        pdf.set_text_color(200, 0, 0)
    else:
        pdf.set_text_color(0, 0, 128)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_x(10)
    pdf.cell(35, 6, label + ':', new_x="RIGHT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(155, 6, clean_text(text))

def main():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title Page
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(45, 55, 72)
    pdf.ln(40)
    pdf.cell(0, 15, 'DAILY BRIEF', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Thursday, August 27, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 12)
    pdf.cell(0, 8, 'Ground News Cross-Spectrum Analysis', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Portfolio Holdings & Market Intelligence', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(15)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(160, 60, 60)
    pdf.cell(0, 8, 'NOTE: Portfolio positions CSV is dated Jul 31, 2026 (latest available).', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Holdings list is current; prices shown are 4 weeks stale.', new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.add_page()

    # ============ MARKET OVERVIEW ============
    add_section_title(pdf, 'Market Overview', 1)
    add_highlight(pdf, 'Overnight', 'Nvidia beat Q2 and guided to ~70% growth; NVDA +4% after hours, +7.6% premarket Thursday. Nasdaq futures jumped, chip stocks firm', 'bullish')
    add_highlight(pdf, 'Indexes', 'S&P 500 ~7,700 | Dow ~53,500 | Nasdaq 100 ~29,450 (Tue/Wed closes, mixed)', 'neutral')
    add_highlight(pdf, 'Macro', 'Gold record $4,620, silver $66; BTC best week in 3 yrs (+23%), still ~$80K. Dollar weak on Treasury buyback expansion', 'neutral')
    add_highlight(pdf, 'Energy', 'Oil -6% in two sessions on Iran-Oman diplomacy; near one-month low', 'bearish')
    add_paragraph(pdf, 'Key themes: (1) Nvidia re-ignited the AI trade overnight; (2) the "debasement trade" - gold, silver, bitcoin up on Bessent Treasury buybacks - is the dominant macro story; (3) Fed Chair Kevin Warsh delivers his first Jackson Hole keynote this week amid sticky inflation and elevated Treasury yields; (4) consumer cracks (Walmart worst day since 2022); (5) new reported Trump tariff plans could broaden the trade fight and dent the chip rally.')

    # ============ KEY STORY 1: NVIDIA ============
    pdf.add_page()
    add_section_title(pdf, 'Story 1: Nvidia Blowout Reignites AI Trade', 1)
    add_section_title(pdf, 'Bias Spectrum', 2)
    add_paragraph(pdf, 'Left/Center-left (CNBC, Bloomberg) - Center (Reuters, AP) - Right (Fox Business, NY Post)')

    add_section_title(pdf, 'Where They Agree (Convergent Facts)', 2)
    add_bullet(pdf, 'Nvidia reported better-than-expected fiscal Q2 2027 results Wednesday after close; guidance topped estimates')
    add_bullet(pdf, 'Stock jumped ~4% after hours on next-fiscal-year forecast; +7.6% in Thursday premarket')
    add_bullet(pdf, 'CNBC: ~70% growth forecast puts Nvidia on track to be the No. 2 tech company by market cap')
    add_bullet(pdf, 'Chip stocks rallied in sympathy: AMD, Intel, Micron firmed; Nasdaq futures jumped Thursday morning')
    add_bullet(pdf, 'AWS + Nvidia announced 2 million additional GPUs for Amazon data centers (Aug 26 evening)')
    pdf.ln(3)

    add_section_title(pdf, 'Where They Differ', 2)
    add_paragraph(pdf, 'LEFT/CENTER-LEFT: Focus on AI momentum, hyperscaler capex, record-setting scale. Little mention of tariffs.')
    add_paragraph(pdf, 'CENTER: Notes Nvidia\'s dependence on a handful of hyperscalers whose free cash flow is being erased by capex; depreciation bill arrives 2027-28.')
    add_paragraph(pdf, 'RIGHT: Charles Payne warns of "anxiety" in the US economy; Fox segment asks if Wall Street is overreacting to China\'s Kimi K3 AI launch; StockTwits flags reported new Trump tariff plans that could broaden the trade fight.')

    add_section_title(pdf, 'Blindspots', 2)
    add_bullet(pdf, 'Bullish coverage omits: customer concentration, GPU depreciation overhang, tariff risk to supply chains')
    add_bullet(pdf, 'Bearish/right coverage omits: actual results were strong and bookings are real (AWS backlog $496B)')
    add_section_title(pdf, 'Likely Reality', 2)
    add_paragraph(pdf, 'The AI trade is real but increasingly financed by balance-sheet-stretched hyperscalers. Near term, momentum favors chip/AI names; the tariff headline and Warsh speech are the two catalysts that could reverse it this week.')

    # ============ KEY STORY 2: DEBASEMENT TRADE ============
    pdf.add_page()
    add_section_title(pdf, 'Story 2: The "Debasement Trade" - Gold Record, BTC Surge, Dollar Weak', 1)
    add_section_title(pdf, 'Where They Agree (Convergent Facts)', 2)
    add_bullet(pdf, 'Treasury Secretary Bessent announced (Aug 19) Treasury will "at least double" long-dated bond buybacks')
    add_bullet(pdf, 'Gold hit a record ~$4,620/oz; silver ~$66; bitcoin ripped ~23% in week ending Aug 21 - best week in 3+ years')
    add_bullet(pdf, 'US dollar weakened against peers amid government-debt alarm')
    pdf.ln(3)
    add_section_title(pdf, 'Where They Differ', 2)
    add_paragraph(pdf, 'CENTER-LEFT (CNBC, Bloomberg, FT): Frames it as debt-alarm + "Bessent Put" - bond-market intervention reviving the debasement trade.')
    add_paragraph(pdf, 'RIGHT (NY Post): Focuses on the trade itself - why crypto and gold are surging; skepticism of fiscal path.')
    add_paragraph(pdf, 'CRYPTO MEDIA: Celebrates the BTC bounce; less emphasis that BTC remains in a deep "crypto winter" near $80K, far below prior highs.')
    add_section_title(pdf, 'Likely Reality', 2)
    add_paragraph(pdf, 'Markets are pricing fiscal dominance: Treasury is cushioning long-end yields while deficits balloon. Hard assets (gold, silver, BTC) and miners benefit; the dollar and long bonds are the funding leg. This is a genuine regime signal, not noise.')
    add_highlight(pdf, 'Implication', 'Supports NEM, PSLV, RIOT/HUT/WULF; headwind for VBND/BND/long Treasuries', 'bullish')

    # ============ KEY STORY 3: JACKSON HOLE / FED ============
    pdf.add_page()
    add_section_title(pdf, 'Story 3: Warsh\'s First Jackson Hole - The Crucial Test', 1)
    add_section_title(pdf, 'Where They Agree (Convergent Facts)', 2)
    add_bullet(pdf, 'Kevin Warsh is Fed Chairman (second FOMC under his chair was July 29, 2026); his first Jackson Hole keynote is this week')
    add_bullet(pdf, 'Inflation remains sticky; cooler data may force his "divided Fed" to hold the line on rates (Aug 14 reporting)')
    add_bullet(pdf, 'Treasury yields remain high even as Treasury executes large buybacks - policy now has two hands (Fed + Treasury) pulling opposite ways')
    pdf.ln(3)
    add_section_title(pdf, 'Where They Differ', 2)
    add_paragraph(pdf, 'CENTER (AP, Euronews, IBTimes): "Crucial test" - markets crave clarity from a "cryptic" chair; bond yields + Treasury rescue + sticky inflation framing.')
    add_paragraph(pdf, 'RIGHT (Fox/Charles Payne, Aug 27): "Some anxiety" in the US economy ahead of Jackson Hole; skepticism of Fed engineering.')
    add_paragraph(pdf, 'MARKET FOCUS: Any hint Warsh tolerates higher-for-longer while Treasury buybacks ease long-end stress = mixed policy signal.')
    add_section_title(pdf, 'Likely Reality', 2)
    add_paragraph(pdf, 'Expect volatility around the keynote. Sticky inflation makes near-term cuts unlikely; fiscal dominance (Treasury buybacks) is quietly doing the easing. Rate-cut hopes should stay parked until inflation data cools decisively.')

    # ============ KEY STORY 4: OIL ============
    add_section_title(pdf, 'Story 4: Oil Slides on Iran-Oman Detente', 1)
    add_section_title(pdf, 'Where They Agree (Convergent Facts)', 2)
    add_bullet(pdf, 'Oil dropped ~6% in two sessions; near a one-month low')
    add_bullet(pdf, 'Iran-Oman (Muscat) talks described as "constructive"; US strikes halted; Hormuz risk premium unwinding')
    pdf.ln(3)
    add_section_title(pdf, 'Where They Differ', 2)
    add_paragraph(pdf, 'CENTER: Diplomacy rewriting the risk premium; supply woes easing (Business Standard: losses extend).')
    add_paragraph(pdf, 'CAUTION FLAGS: NBC notes Putin plan to escalate in Ukraine; new Russia fears could return the premium quickly.')
    add_section_title(pdf, 'Likely Reality', 2)
    add_paragraph(pdf, 'Genuine near-term bearish for crude while talks hold - a drag on SHEL, VDE, XOP. Fragile: one headline can restore $10-15 of risk premium. Treat weakness as geopolitical, not structural.')

    # ============ KEY STORY 5: CONSUMER ============
    pdf.add_page()
    add_section_title(pdf, 'Story 5: Consumer Cracks - Walmart\'s Worst Day Since 2022', 1)
    add_section_title(pdf, 'Where They Agree (Convergent Facts)', 2)
    add_bullet(pdf, 'Walmart Q2 FY27 (Aug 20): sales growth slowed - partly federal drug-pricing rules cutting pharmacy prices')
    add_bullet(pdf, 'Stock slumped 9%+ - worst day since 2022 despite an earnings beat; strong online sales, weak store results')
    add_bullet(pdf, 'Walmart received billions in tariff refunds; US consumer spending retreat is a cross-spectrum talking point')
    pdf.ln(3)
    add_section_title(title=None, pdf=None) if False else None
    add_section_title(pdf, 'Where They Differ', 2)
    add_paragraph(pdf, 'CENTER (AP, NBC): Cautious guidance, tariff refunds, drug-pricing mechanics - factual.')
    add_paragraph(pdf, 'LEFT (Al Jazeera): "US consumer spending retreats" - affordability crisis framing.')
    add_paragraph(pdf, 'RIGHT: Emphasizes consumer weakness as indictment of economy management; 24/7 Wall St: "three cracks in consumer spending."')
    add_section_title(pdf, 'Likely Reality', 2)
    add_paragraph(pdf, 'The consumer is softening at the margins (tariff pass-through, drug pricing, pullback). Not a recession signal yet, but it contradicts "strong economy" narratives and supports the Fed-holds view.')

    # ============ PORTFOLIO NEWS ============
    pdf.add_page()
    add_section_title(pdf, 'Portfolio News', 1)

    add_section_title(pdf, 'INTC - Intel (5.6% of account; +99.6% since Jul 31 CSV)', 2)
    add_bullet(pdf, 'Aug 25: "Intel draws Nvidia\'s backing as $20B deal fuels AI push" (aggregator; verify size vs the known $5B Nvidia investment)')
    add_bullet(pdf, 'Aug 26: Intel, AMD, Micron surged on report of government cash support (CHIPS-era funding)')
    add_bullet(pdf, 'Government 9.9% stake saga continues: Lutnick moved to toss lawsuit over the stake (Aug 24)')
    add_bullet(pdf, 'Comeback narrative: 20,000 layoffs, 14A node to rival TSMC; premarket strength with chip rally')
    add_highlight(pdf, 'Implication', 'BULLISH near-term - chip rally + government support; still a turnaround with execution risk', 'bullish')

    add_section_title(pdf, 'MU - Micron (3.1%)', 2)
    add_bullet(pdf, 'Memory shortage worst since 2017 (Goldman); data centers want 50% more memory than Micron can ship (CEO, Aug 24)')
    add_bullet(pdf, 'Customers putting up $22B (prepayments); HBM uses 3x the silicon of DDR5 - "memory wall" worsening, prices rising')
    add_bullet(pdf, 'Analysts: 2027 HBM contract prices may rise up to 140%; memory to be ~68% of cloud capex')
    add_highlight(pdf, 'Implication', 'STRONGLY BULLISH - pricing power intact; cyclical top is the only real risk', 'bullish')

    add_section_title(pdf, 'BE - Bloom Energy (1.8%)', 2)
    add_bullet(pdf, 'Nebius picked Bloom fuel cells for AI data centers - 328 MW deal, stock jumped 12-13% (Aug 12-17)')
    add_bullet(pdf, 'Brookfield expanded partnership for fuel-cell deployment across AI data centers (Aug 19); MiTAC campus expansion')
    add_bullet(pdf, 'Key angle: fuel cells beat gas turbines on permitting speed; valuation stretched at ~17x sales')
    add_highlight(pdf, 'Implication', 'BULLISH - AI onsite power demand is real; trim-worthy on valuation spikes', 'bullish')

    pdf.add_page()
    add_section_title(pdf, 'RIOT - Riot Platforms (2.5%)', 2)
    add_bullet(pdf, 'Aug 11: Signed 20-year, $9.1B data-center lease with Anthropic - miners re-rated as AI infrastructure')
    add_bullet(pdf, 'Q2 2026 (Aug 10): executed the frontier-AI lease; sold 4,300 BTC (~27% of treasury) to fund the pivot')
    add_bullet(pdf, 'RISK (CryptoSlate): $573M bridge loan for Rockdale matures BEFORE Anthropic rent starts - refinancing gap')
    add_highlight(pdf, 'Implication', 'BULLISH story / FINANCING risk - watch the bridge loan; AI pivot real but pre-revenue', 'neutral')

    add_section_title(pdf, 'CORZ - Core Scientific (3.2%)', 2)
    add_bullet(pdf, 'Pivoted to AMD with a 2.5 GW AI data-center pact months after shareholders torpedoed the ~$9B CoreWeave takeover')
    add_bullet(pdf, 'CoreWeave remains a customer: $1.2B Denton expansion (Aug 21) takes contracted HPC to ~590 MW; 440 MW live ahead of schedule')
    add_bullet(pdf, 'Aug 14: closed Polaris DS acquisition; Muskogee expansion to 1.5 GW gross power; $24B comeback faces debt test')
    add_highlight(pdf, 'Implication', 'BULLISH - contracted growth is real; leverage is the watch item', 'bullish')

    add_section_title(pdf, 'HUT - Hut 8 (0.9%)', 2)
    add_bullet(pdf, 'Aug 19: signed 352 MW lease with unnamed hyperscaler in Texas; Beacon Point expansion (possibly Nvidia-linked) doubles capacity to 704 MW; backlog $26.6B; SA target $140-150')
    add_bullet(pdf, 'CAUTION: Q2 net loss $177.1M on $74.9M revenue; of ~$7B cash, only $233.6M unrestricted (rest restricted for River Bend/Beacon Point)')
    add_highlight(pdf, 'Implication', 'BULLISH pipeline / CASH-thin execution - highest-risk, highest-reward name in the cluster', 'neutral')

    add_section_title(pdf, 'APLD / WULF (0.9% / 1.0%)', 2)
    add_bullet(pdf, 'Aug 25: APLD +6%, WULF +5% as the digital-infrastructure bid broadens past bitcoin (BTC ~$80K, "crypto winter")')
    add_bullet(pdf, 'Comparisons favor APLD\'s power access; WULF rides the same AI-datacenter re-rating')
    add_highlight(pdf, 'Implication', 'BULLISH sector beta - these trade with the AI-infra complex more than BTC now', 'bullish')

    pdf.add_page()
    add_section_title(pdf, 'AMZN - Amazon (10.0% - largest single-stock position)', 2)
    add_bullet(pdf, 'AWS backlog reached $496B (Aug 24); AWS grew 37% - fastest in 18 quarters; led the Mag-7 post-earnings rally')
    add_bullet(pdf, 'Aug 26 evening: AWS + Nvidia announced 2M additional GPUs for AWS data centers')
    add_bullet(pdf, 'Caution angle (ainvest): the depreciation bill for this capex arrives 2027-28')
    add_highlight(pdf, 'Implication', 'BULLISH - strongest fundamental story in the portfolio', 'bullish')

    add_section_title(pdf, 'STX - Seagate (1.8%)', 2)
    add_bullet(pdf, 'AI storage boom: cloud = 90% of exabyte shipments; capacity commitments now extend to 2028; hard-drive shortage widening (analyst, Benzinga)')
    add_bullet(pdf, '10-K filed Aug 4 (FY ended Jul 3, 2026); FXEmpire notes the 209% AI-driven rally')
    add_highlight(pdf, 'Implication', 'BULLISH - shortage economics; extended chart, size accordingly', 'bullish')

    add_section_title(pdf, 'GEV - GE Vernova (0.5%) / CEG - Constellation (1.0%)', 2)
    add_bullet(pdf, 'GEV: Blue Energy + GE Vernova Hitachi 2.5-GW Texas gas+nuclear project advanced to engineering/licensing (BWRX-300 SMR)')
    add_bullet(pdf, 'CEG: "riding the data center power crunch" (Fool); nuclear-power theme intact')
    add_highlight(pdf, 'Implication', 'BULLISH theme - power is the AI bottleneck; positions are small', 'bullish')

    add_section_title(pdf, 'Energy: SHEL / VDE / XOP (1.3% / 3.4% / 2.8%)', 2)
    add_bullet(pdf, 'Oil -6% in two sessions on Iran-Oman talks + halt to US strikes; Shell/BP weighed on FTSE; losses extending Aug 27')
    add_highlight(pdf, 'Implication', 'BEARISH near-term on geopolitics unwinding; structural thesis intact if talks collapse', 'bearish')

    add_section_title(pdf, 'BFLY - Butterfly Network (1.8%)', 2)
    add_bullet(pdf, 'Q2: record revenue $32.6M, raised 2026 guidance, narrowed losses; initially sank 13% on margin-durability doubts, then recovered (+24% overall)')
    add_bullet(pdf, 'Director Phanstiel bought $1.0M of stock (Aug 21) - insider signal')
    add_highlight(pdf, 'Implication', 'NEUTRAL-BULLISH - guidance raised, insider buying; still unprofitable', 'bullish')

    pdf.add_page()
    add_section_title(pdf, 'WMT - Walmart (2.8%)', 2)
    add_bullet(pdf, 'Aug 20: Q2 FY27 - slowest sales growth in years (drug-pricing rules drag), billions in tariff refunds, stock -9% (worst day since 2022)')
    add_bullet(pdf, 'Consumer spending retreat is the underlying worry; online strong, stores weak')
    add_highlight(pdf, 'Implication', 'BEARISH near-term sentiment; defensive holding, but consumer cracks matter portfolio-wide', 'bearish')

    add_section_title(pdf, 'GOOGL / NFLX / Media & Other Tech', 2)
    add_bullet(pdf, 'GOOGL: Berkshire and David Tepper piling in; stock dipped Aug 26 on AI-competition noise; Citizens analyst sets bullish target')
    add_bullet(pdf, 'NFLX: reportedly letting rivals (streaming apps) into its app - stock climbed on the idea; Wolfe raised PT to $95 (post-split)')
    add_bullet(pdf, 'AAPL/MSFT/others: chip rally tailwind; NBIG (2x NDX) gets amplified exposure to the NVDA-led move today')
    add_highlight(pdf, 'Implication', 'NEUTRAL-BULLISH', 'neutral')

    add_section_title(pdf, 'NEM / PSLV - Gold & Silver (0.4% / 0.1%)', 2)
    add_bullet(pdf, 'Gold record ~$4,620; silver ~$66 on the debasement trade - direct tailwind')
    add_highlight(pdf, 'Implication', 'BULLISH - consider adding on the fiscal-dominance theme', 'bullish')

    # ============ BLINDSPOTS ============
    pdf.add_page()
    add_section_title(pdf, 'Blindspot Report', 1)
    add_bullet(pdf, 'LEFT omits: the fiscal-debt alarm driving the debasement trade gets less airtime; "Bessent Put" framed as stability, not monetization')
    add_bullet(pdf, 'RIGHT omits: reported new Trump tariff plans threatening the very chip rally celebrated on right-leaning business TV')
    add_bullet(pdf, 'CENTER omits: who ultimately pays for Treasury buybacks; hyperscaler depreciation cliff (2027-28); miner financing gaps (Riot bridge loan, HUT restricted cash)')
    add_bullet(pdf, 'ALL underplay: divergence between BTC in a crypto winter (~$80K) vs miners re-rated on AI - if AI sentiment cracks, miners lose their new story AND their old one')
    add_bullet(pdf, 'Walmart\'s consumer warning vs AI euphoria - a divergence few are connecting')

    # ============ OUTLOOK ============
    add_section_title(pdf, 'Pre-Market Outlook (Thursday, Aug 27)', 1)
    add_highlight(pdf, 'Overall', 'BULLISH AI/CORE, CAUTIOUS MACRO - NVDA-led risk-on today; two catalysts could flip the week', 'bullish')

    add_section_title(pdf, 'Today\'s Catalysts', 2)
    add_bullet(pdf, 'NVDA +7.6% premarket after blowout quarter - lifts INTC, MU, AMD, AMZN, NBIG, and the AI-infra cluster (CORZ, HUT, APLD, WULF, RIOT, BE, GEV, VRT)')
    add_bullet(pdf, 'Warsh\'s first Jackson Hole keynote - watch for rates path clarity or "cryptic" ambiguity')
    add_bullet(pdf, 'Reported new Trump tariff plans - could broaden the trade fight and cap the chip rally')
    add_bullet(pdf, 'Oil sliding on Iran-Oman - SHEL/VDE/XOP headwind; watch for reversal headlines')

    add_section_title(pdf, 'Positioning Notes', 2)
    add_bullet(pdf, 'Concentration check: AMZN 10% + INTC 5.6% + MU 3.1% + CORZ/RIOT/HUT/APLD/WULF ~7.5% + BE/STX/BFLY ~5.5% = heavy AI-infrastructure loading. Consider trimming into strength if NVDA pop fades')
    add_bullet(pdf, 'The Jul-31 CSV is stale - refresh positions file for accurate weights (several names up 20-100%+ since)')
    add_bullet(pdf, 'Gold/silver (NEM, PSLV) remain tiny vs the debasement signal - potential diversifier')
    add_bullet(pdf, 'Energy (VDE/XOP/SHEL ~7.5% combined) faces near-term geopolitical headwind; not a structural problem yet')
    add_bullet(pdf, 'Defensives (KO, PM, JNJ, PG, WMT, HD) did their job during WMT-led consumer wobble')

    add_section_title(pdf, 'Sentiment', 2)
    add_highlight(pdf, 'Overall', 'BULLISH with a hedge plan - AI earnings beat + debasement tailwind vs Warsh + tariffs + consumer cracks', 'bullish')

    # Footer
    pdf.add_page()
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(128, 128, 128)
    pdf.ln(20)
    pdf.cell(0, 8, 'Report generated: Thursday, August 27, 2026 - 9:07 AM CDT', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Data source: Portfolio Positions CSV (Jul 31, 2026 - latest available) + multi-source web search', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Methodology: Ground News cross-spectrum analysis (Left / Center / Right)', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 9)
    pdf.multi_cell(0, 5, 'Disclaimer: This report is for informational purposes only and does not constitute financial advice. Past performance does not guarantee future results.')

    output_path = 'C:\\Users\\thadd\\.openclaw\\workspace\\Spocks Reports\\daily-brief\\2026-08-27_daily-brief.pdf'
    pdf.output(output_path)
    print(f'PDF generated: {output_path}')

if __name__ == '__main__':
    main()