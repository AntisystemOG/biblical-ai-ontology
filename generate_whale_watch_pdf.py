from fpdf import FPDF
from datetime import datetime

class WhaleWatchPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(44, 62, 80)
        self.cell(0, 15, 'WHALE WATCH REPORT', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_font('Helvetica', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Q4 2025 Hedge Fund Holdings Analysis', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Whale Watch Report | May 12, 2026', align='C')
        
    def chapter_title(self, title, size=14):
        self.set_font('Helvetica', 'B', size)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(44, 62, 80)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)
        
    def chapter_body(self, body):
        # Replace Unicode bullets with simple dashes
        body_clean = body.replace('\u2022', '-').replace('\u2026', '...').replace('\u2019', "'")
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, body_clean)
        self.ln()

# Create PDF
pdf = WhaleWatchPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Executive Summary
pdf.chapter_title('Executive Summary', 14)
pdf.chapter_body("""This report analyzes Q4 2025 13F filings from five major hedge fund managers. The quarter saw significant positioning in AI infrastructure plays, mega-cap technology, and strategic rotations out of certain Chinese tech names. Point72 leads with $75.2B in disclosed equity positions, while Situational Awareness LP posted exceptional +47% returns in H1 2025.

Key Themes:
- AI infrastructure dominance (NVDA, TSM, semiconductors)
- Mega-cap tech consolidation (GOOGL, META, AMZN, MSFT)
- China tech rotation (BABA trimming across funds)
- Semiconductor equipment focus (AMAT, MU)
- Diverse strategies from extreme diversification to concentrated bets""")

# Manager Holdings Overview
pdf.chapter_title('Manager Holdings Overview', 14)

# Point72
pdf.chapter_title('Point72 Asset Management (Steven Cohen)', 12)
pdf.chapter_body("""AUM (13F): $75.16B | Holdings: 2,115 positions | Performance Q4: +7.55%

Strategy: Multi-strategy with significant options activity (~28% of portfolio). Maintains highly diversified book across 2,100+ positions.

Key Activity: Point72 continues broad diversification with heavy options use for hedging. NVDA, TSM, and AMZN remain core long positions.""")

# D1 Capital
pdf.chapter_title('D1 Capital Partners (Daniel Sundheim)', 12)
pdf.chapter_body("""AUM (13F): $10.70B | Holdings: 42 positions | Performance Q4: +2.17%

Strategy: Concentrated long/short equity. 100% stock allocation with no options exposure.

Notable Holdings: CART (Instacart), APP (AppLovin), SE (Sea Ltd), CLH (Clean Harbors), META

Quarter saw +22.9% AUM growth ($8.7B to $10.7B) through concentrated positioning.""")

# Appaloosa
pdf.chapter_title('Appaloosa LP (David Tepper)', 12)
pdf.chapter_body("""AUM (13F): $6.93B | Holdings: 39 positions | Top 5: 39% of portfolio

Strategy: Concentrated value with high conviction bets. Active trading characterized the quarter.

Key Activity: Trimmed BABA ~20% despite remaining largest position (~11%). Added to GOOGL, MU, META, TSM. New positions in EWY (South Korea ETF) and Ball Corp.

Top Holdings: BABA (~11%), GOOGL, AMZN, MU, META""")

# Coatue
pdf.chapter_title('Coatue Management (Philippe Laffont)', 12)
pdf.chapter_body("""AUM (13F): $39.96B | Holdings: 52 positions | Top 5: ~32% of portfolio

Strategy: Tech/Growth focused with significant semiconductor concentration.

Key Activity: Major stake increases in AMAT (+80%), SPOT (+35%), NFLX (+60%), DASH (+80%). New position in NTRA (2.55%). Complete disposal of BABA, CRWV, KKR, TEAM, HNGE, INTU.

Top Holdings: GOOGL, TSM, MSFT, META, AMZN""")

# Aschenbrenner
pdf.chapter_title('Situational Awareness LP (Leopold Aschenbrenner)', 12)
pdf.chapter_body("""AUM (13F): ~$3.91B | Holdings: 24 positions | Performance H1 2025: +47%

Strategy: AI-focused global macro long/short equity. Heavy concentration on AI infrastructure, semiconductors, power generation, data centers, and Bitcoin miners.

Background: Founded 2024 by former OpenAI researcher. Backed by Stripe founders, Nat Friedman, Daniel Gross. Grew from $383M to over $5B in under a year.""")

# High-Conviction Overlaps
pdf.add_page()
pdf.chapter_title('High-Conviction Overlaps', 14)
pdf.chapter_body("""Positions held by multiple whale managers indicate strong consensus themes.

VERY HIGH CONVICTION (3+ Whales):

NVDA (NVIDIA Corp)
- Whales: Cohen, Tepper, Laffont
- Theme: AI Infrastructure
- Status: Clear consensus on AI chip leadership

GOOGL (Alphabet Inc)
- Whales: Cohen, Tepper, Laffont
- Theme: AI/Search/Cloud
- Activity: Tepper increased, Laffont trimmed slightly

META (Meta Platforms)
- Whales: Sundheim, Tepper, Laffont
- Theme: AI/Social Media
- Activity: All showing strong interest

AMZN (Amazon.com)
- Whales: Cohen, Tepper, Laffont
- Theme: Cloud/AWS/AI
- Note: Tepper reduced while others maintained

HIGH CONVICTION (2+ Whales):

TSM (Taiwan Semiconductor)
- Whales: Cohen, Tepper, Laffont
- Theme: Semiconductors/Foundry
- Critical link in AI supply chain

MSFT (Microsoft)
- Whales: Cohen, Laffont
- Theme: Cloud/AI
- Stable core holding

MU (Micron Technology)
- Whales: Tepper (increased significantly)
- Theme: Memory/Semis
- Benefiting from AI memory demand

SPOT (Spotify)
- Whales: Laffont (+35%)
- Theme: Streaming
- Growing position""")

# Key Themes
pdf.chapter_title('Key Themes & Insights', 14)

pdf.chapter_title('1. AI Infrastructure Dominance', 11)
pdf.chapter_body("""NVIDIA (NVDA) remains the most-held stock across whale portfolios - clear consensus on AI chip leadership.

TSM appears in all major tech-focused portfolios as the critical foundry partner for AI chips.

Aschenbrenner's fund explicitly targets AI infrastructure with exceptional returns (+47% H1 2025).""")

pdf.chapter_title('2. Mega-Cap Tech Consolidation', 11)
pdf.chapter_body("""GOOGL, META, AMZN, MSFT - the 'Magnificent Seven' continue to dominate whale thinking.

Coatue and Appaloosa both rotating into these names while trimming smaller positions.""")

pdf.chapter_title('3. China Tech Rotation', 11)
pdf.chapter_body("""Tepper continued trimming BABA (~20% reduction) despite it remaining his largest position.

Coatue completely exited BABA in Q4 2025.

Rotation appears to be from China tech toward US mega-caps and semiconductors.""")

pdf.chapter_title('4. Semiconductor Focus', 11)
pdf.chapter_body("""Micron (MU) - Tepper significantly increased his stake.

Applied Materials (AMAT) - Coatue increased +80%.

Semiconductor equipment and memory names seeing increased attention across funds.""")

pdf.chapter_title('5. Concentration vs. Diversification', 11)
pdf.chapter_body("""Point72: Extreme diversification (2,115 positions) with options overlay

D1 Capital: Concentrated (42 positions), pure equity, high conviction

Appaloosa: Highly concentrated (39 positions, 39% in top 5)

Coatue: Moderate concentration (52 positions, 32% in top 5)

Situational Awareness: Focused (24 positions, thematic)""")

# Notable Activity
pdf.chapter_title('Notable Q4 2025 Activity', 14)
pdf.chapter_body("""TEPPER (Appaloosa):
- MAJOR BUYS: GOOGL (+), MU (+), META (+), TSM (+), EWY (new)
- MAJOR SELLS: BABA (~20% trim), AMZN (-), NVDA (-)

LAFFONT (Coatue):
- MAJOR BUYS: AMAT (+80%), SPOT (+35%), NFLX (+60%), DASH (+80%)
- MAJOR SELLS: BABA (exit), INTU (trim), CRWV (exit), KKR (exit)

ASCHENBRENNER (Situational Awareness):
- THEME BUYS: AI infrastructure, power generation, data centers, BTC miners
- STATUS: New fund with exceptional H1 performance""")

# Performance Table
pdf.chapter_title('Performance Comparison', 14)
pdf.chapter_body("""Manager              | Fund                  | Q4 Return    | AUM
---------------------|-----------------------|--------------|-------------
Steven Cohen         | Point72               | +7.55%       | $75.16B
Daniel Sundheim      | D1 Capital            | +2.17%       | $10.70B
David Tepper         | Appaloosa             | Active       | $6.93B
Philippe Laffont     | Coatue                | Active       | $39.96B
Leopold Aschenbrenner| Situational Awareness | +47%* (H1)   | ~$3.91B

*H1 2025 annualized, not Q4 specific""")

# Disclaimers
pdf.add_page()
pdf.chapter_title('Important Disclaimers', 14)
pdf.chapter_body("""- Data sourced from SEC 13F filings as of Q4 2025 (filed February 2026)

- 13F filings have a 45-day delay and may not reflect current positions

- Short positions, international equities, and options are not fully disclosed on 13F forms

- This report is for informational purposes only - not investment advice

- Past performance does not guarantee future results

- Data integrity sourced from SEC EDGAR database and third-party aggregation services

Report Generated: May 12, 2026
Data: SEC EDGAR | whale_watch | Spock
""")

# Save PDF
output_path = "C:\\Users\\thadd\\OneDrive\\Desktop\\Spocks Reports\\whale_watch\\2026-05-12_whale_watch.pdf"
pdf.output(output_path)
print(f"PDF generated successfully: {output_path}")
