#!/usr/bin/env python3
"""
Daily Brief Report Generator - May 11, 2026
Ground News Cross-Spectrum Analysis
"""

from fpdf import FPDF
from datetime import datetime
import os

class DailyBriefPDF(FPDF):
    def header(self):
        # Logo/header area
        self.set_font('Arial', 'B', 24)
        self.set_text_color(40, 40, 40)
        self.cell(0, 15, 'Daily Brief', 0, 1, 'L')
        self.set_font('Arial', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Ground News Cross-Spectrum Analysis | May 11, 2026', 0, 1, 'L')
        self.ln(5)
        # Line separator
        self.set_draw_color(200, 200, 200)
        self.line(10, 35, 200, 35)
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Daily Brief - Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')
    
    def chapter_title(self, title, subtitle=""):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(30, 60, 114)
        self.cell(0, 12, title, 0, 1, 'L')
        if subtitle:
            self.set_font('Arial', '', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 6, subtitle, 0, 1, 'L')
        self.ln(3)
    
    def section_header(self, text):
        self.set_font('Arial', 'B', 13)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, text, 0, 1, 'L')
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
    
    def subsection_header(self, text):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, text, 0, 1, 'L')
    
    def body_text(self, text, bold=False):
        self.set_font('Arial', 'B' if bold else '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)
    
    def bullet_point(self, text, indent=0):
        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)
        self.cell(indent, 5.5, '', 0, 0)
        self.cell(5, 5.5, chr(149), 0, 0)  # bullet
        # Reserve space for bullet and margin
        self.multi_cell(185 - indent - 5, 5.5, text)
    
    def spectrum_bar(self):
        # Draw spectrum visualization
        self.ln(2)
        bar_y = self.get_y()
        # Left (Blue)
        self.set_fill_color(70, 130, 180)
        self.rect(10, bar_y, 60, 6, 'F')
        # Center (Gray)
        self.set_fill_color(150, 150, 150)
        self.rect(70, bar_y, 60, 6, 'F')
        # Right (Red)
        self.set_fill_color(180, 80, 80)
        self.rect(130, bar_y, 60, 6, 'F')
        # Labels
        self.set_y(bar_y + 8)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(70, 130, 180)
        self.cell(60, 4, 'LEFT', 0, 0, 'C')
        self.set_text_color(100, 100, 100)
        self.cell(60, 4, 'CENTER', 0, 0, 'C')
        self.set_text_color(180, 80, 80)
        self.cell(60, 4, 'RIGHT', 0, 1, 'C')
        self.ln(5)
    
    def highlight_box(self, title, content, color_rgb=(240, 248, 255)):
        # Draw colored box
        self.set_fill_color(*color_rgb)
        start_y = self.get_y()
        self.set_font('Arial', 'B', 10)
        self.set_text_color(40, 40, 40)
        
        # Calculate height needed
        title_width = self.get_string_width(title)
        self.cell(5, 6, '', 0, 0)  # left margin
        self.cell(title_width + 5, 6, title, 0, 1)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)
        self.cell(5, 5, '', 0, 0)
        self.multi_cell(0, 5, content)
        end_y = self.get_y()
        
        # Draw rectangle
        self.rect(10, start_y, 190, end_y - start_y + 3, 'F')
        self.set_xy(15, start_y + 1)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, title, 0, 1)
        self.set_xy(15, start_y + 7)
        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(180, 5, content)
        self.ln(5)

def generate_report():
    pdf = DailyBriefPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # ===== EXECUTIVE SUMMARY =====
    pdf.chapter_title("Executive Summary", "Market Overview with Cross-Spectrum Analysis")
    pdf.spectrum_bar()
    
    pdf.subsection_header("WHERE THEY AGREE (Convergent Facts)")
    pdf.body_text("All sources confirm elevated geopolitical risk from the US-Iran conflict, with the Strait of Hormuz remaining a critical flashpoint. Oil prices have reacted to ceasefire negotiations and Trump's rejection of Iran's counterproposal. CPI data scheduled for May 12 is expected to show inflation acceleration due to energy costs. Semiconductor sector (NVDA, MU, INTC) continues showing strength from AI demand. Bitcoin mining stocks pivoting to AI data center contracts as a secondary revenue stream.")
    
    pdf.subsection_header("Likely Reality")
    pdf.body_text("Markets are pricing in continued volatility through Q2 2026. Energy costs from the Iran conflict are creating inflationary pressure that may delay Fed rate cuts. Tech sector strength (AI/semiconductors) remains the primary bullish counterweight. Portfolio positioning should emphasize: 1) Quality tech with pricing power, 2) Energy exposure for geopolitical hedge, 3) Reduced duration risk ahead of CPI.", bold=True)
    
    pdf.ln(5)
    
    # ===== KEY STORIES =====
    pdf.add_page()
    pdf.chapter_title("Key Stories", "Cross-Spectrum Analysis of Major Market Events")
    
    # Story 1: US-Iran Tensions
    pdf.section_header("1. US-Iran Tensions & Strait of Hormuz")
    pdf.body_text("Sources: CNN (Left) | Reuters/AP (Center) | Fox News (Right)")
    pdf.ln(2)
    
    pdf.subsection_header("WHERE THEY AGREE:")
    pdf.bullet_point("Trump rejected Iran's counterproposal to end the war, calling it 'totally unacceptable'")
    pdf.bullet_point("Military exchanges occurred in the Strait of Hormuz; US fired on Iranian forces")
    pdf.bullet_point("Oil prices remain elevated with Brent crude above $80/barrel")
    pdf.bullet_point("Strait of Hormuz closure would disrupt ~20% of global oil supply")
    pdf.ln(3)
    
    pdf.subsection_header("WHERE THEY DIFFER:")
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(70, 130, 180)
    pdf.cell(60, 5, "LEFT says:", 0, 0)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(60, 5, "CENTER says:", 0, 0)
    pdf.set_text_color(180, 80, 80)
    pdf.cell(60, 5, "RIGHT says:", 0, 1)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "CNN emphasizes humanitarian impacts and risks of escalation. Focus on Iran's new 'rules' for Hormuz as provocative. Questions administration's diplomatic approach. | Reuters/AP focus on factual military exchanges, oil price movements, and supply chain impacts. Neutral on policy implications. | Fox emphasizes Trump's strong stance, downplays escalation risk. Frames rejection as standing firm against unreasonable demands. Focus on US military superiority.")
    pdf.ln(3)
    
    pdf.subsection_header("Blindspots:")
    pdf.bullet_point("Left omits: Economic benefits of resolved conflict; US energy independence reducing vulnerability")
    pdf.bullet_point("Right omits: Long-term costs of prolonged conflict; global supply chain vulnerabilities")
    pdf.bullet_point("Center omits: Political implications and 2026 election angles")
    pdf.ln(3)
    
    pdf.subsection_header("Likely Reality:")
    pdf.body_text("The conflict will likely persist in a low-intensity state through 2026. Full Hormuz closure remains unlikely (mutually assured destruction for Iran's economy). Market impact: energy volatility continues, supporting oil/gas positions but creating inflation headwinds. Defense stocks and energy infrastructure likely beneficiaries.")
    
    pdf.ln(5)
    
    # Story 2: CPI Inflation Data
    pdf.add_page()
    pdf.section_header("2. CPI Inflation Report (May 12, 2026)")
    pdf.body_text("Sources: CNBC, Bloomberg (Left-Center) | Reuters, WSJ (Center) | Fox Business (Right)")
    pdf.ln(2)
    
    pdf.subsection_header("WHERE THEY AGREE:")
    pdf.bullet_point("April CPI release scheduled for May 12, 8:30 AM ET")
    pdf.bullet_point("Headline CPI expected ~3.7% YoY (up from 3.3% in March)")
    pdf.bullet_point("Energy-driven inflation surge from Iran conflict impact on oil prices")
    pdf.bullet_point("Core CPI may remain elevated but below headline")
    pdf.ln(3)
    
    pdf.subsection_header("WHERE THEY DIFFER:")
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "LEFT-LEANING: Focus on Fed's difficult position; potential for 'stagflation' narrative. Emphasize impact on working families. | CENTER: Data-focused analysis of CPI components. Discussion of 'transitory vs persistent' inflation. Fed policy implications. | RIGHT-LEANING: Emphasis on energy policy as root cause. Criticism of administration's Iran handling. Focus on need for domestic production.")
    pdf.ln(3)
    
    pdf.subsection_header("Likely Reality:")
    pdf.body_text("CPI will show headline inflation acceleration driven by energy costs. This is supply-shock driven, not demand-driven, which matters for Fed response. Fed likely to 'look through' energy-driven inflation but may delay rate cuts if core also rises. Bond yields likely to rise on the print. Equity markets may see volatility.")
    
    pdf.ln(5)
    
    # Story 3: Semiconductor Rally
    pdf.section_header("3. Semiconductor Sector Rally (NVDA, MU, INTC)")
    pdf.body_text("Sources: CNBC Tech (Left-Center) | Reuters/WSJ (Center) | Fox Business (Right)")
    pdf.ln(2)
    
    pdf.subsection_header("WHERE THEY AGREE:")
    pdf.bullet_point("NVDA hit new 52-week high; continues investment spree ($40B+ in equity bets)")
    pdf.bullet_point("Micron (MU) surged 38% in one week - best since 2008")
    pdf.bullet_point("Intel (INTC) up 114% in April on Apple chip deal speculation")
    pdf.bullet_point("AI demand driving unprecedented chip demand")
    pdf.bullet_point("TSMC revenue up 30% YoY in first four months of 2026")
    pdf.ln(3)
    
    pdf.subsection_header("WHERE THEY DIFFER:")
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "LEFT-LEANING: Focus on 'AI bubble' risks, concentration in mega-caps, wealth inequality from tech gains. Questions sustainability. | CENTER: Fundamental analysis of supply/demand, earnings beats, capital expenditure trends. TSMC capacity constraints. | RIGHT-LEANING: American tech leadership narrative. US vs China competition angle. Intel resurgence as domestic manufacturing win.")
    pdf.ln(3)
    
    pdf.subsection_header("Likely Reality:")
    pdf.body_text("The AI buildout is real and multi-year. Current valuations reflect genuine demand, not just speculation. NVDA's $40B investment in supply chain partners (Corning, IREN) signals deep conviction. Risk: concentration in top names. Opportunity: second-derivative plays (equipment, materials, power infrastructure). Intel's Apple deal would be transformative if confirmed.")
    
    pdf.ln(5)
    
    # ===== PORTFOLIO NEWS =====
    pdf.add_page()
    pdf.chapter_title("Portfolio News", "Cross-Spectrum Analysis of Holdings")
    
    # BE - Bloom Energy
    pdf.section_header("BE - Bloom Energy Corp")
    pdf.subsection_header("News: Record Q1 2026 Results, Oracle AI Data Center Deal")
    pdf.body_text("Stock up 109% in April. Company reported 130% YoY revenue growth and raised full-year 2026 guidance. Secured major deal with Oracle for AI data center power.")
    pdf.ln(2)
    pdf.subsection_header("Spectrum Analysis:")
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "LEFT: Focus on clean energy transition, hydrogen economy potential. Emphasis on ESG benefits. | CENTER: Financial metrics, revenue growth, AI data center demand surge. Contract economics. | RIGHT: US manufacturing, energy independence, reduced reliance on foreign energy.")
    pdf.ln(2)
    pdf.subsection_header("Blindspot Check:")
    pdf.body_text("Left sources underplaying execution risks and competition from traditional generators. Right sources underplaying regulatory tailwinds for clean energy. Center missing: valuation concerns after 109% run-up.")
    pdf.subsection_header("Market Implication:")
    pdf.body_text("BULLISH - Oracle deal validates AI data center power thesis. Raised guidance signals confidence. Risk: momentum could reverse on any execution miss.", bold=True)
    pdf.ln(5)
    
    # INTC - Intel
    pdf.section_header("INTC - Intel Corp")
    pdf.subsection_header("News: Apple Chip Deal Speculation, Q1 Earnings Beat")
    pdf.body_text("Stock climbed 114% in April on reports of preliminary agreement with Apple to manufacture chips. Q1 earnings beat expectations with 7% revenue growth.")
    pdf.ln(2)
    pdf.subsection_header("Spectrum Analysis:")
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "LEFT: Turnaround story, US manufacturing renaissance, job creation. Cautious on execution. | CENTER: Financial analysis of foundry business potential, margin impacts, competitive positioning vs TSMC. | RIGHT: US tech independence, reducing reliance on Taiwan/China, Trump-era manufacturing policy success.")
    pdf.ln(2)
    pdf.subsection_header("Blindspot Check:")
    pdf.body_text("Left underplaying geopolitical risk of Taiwan concentration that makes Intel attractive. Right underplaying how much catching up Intel must do on process technology. Center missing: Apple deal still preliminary, not confirmed.")
    pdf.subsection_header("Market Implication:")
    pdf.body_text("BULLISH - Apple deal would be transformational. Even without confirmation, sentiment shift is real. Risk: Deal falls through or terms unfavorable. Position: Hold, don't add until confirmed.", bold=True)
    pdf.ln(5)
    
    # CORZ - Core Scientific
    pdf.section_header("CORZ - Core Scientific Inc")
    pdf.subsection_header("News: 1.5 GW Expansion Plan, $3.3B Notes Offering")
    pdf.body_text("Shares hit new all-time high on expansion plan. Completed $3.3B senior secured notes offering to strengthen capital structure.")
    pdf.ln(2)
    pdf.subsection_header("Spectrum Analysis:")
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "LEFT: Crypto skepticism, environmental concerns about mining. Focus on pivot to AI data centers. | CENTER: Financial restructuring, leverage analysis, power contracts, AI hosting economics vs mining. | RIGHT: American infrastructure, domestic Bitcoin mining, reduced reliance on foreign miners.")
    pdf.ln(2)
    pdf.subsection_header("Blindspot Check:")
    pdf.body_text("Left underplaying revenue diversification success. Right underplaying debt load risks. Center missing: Bitcoin price sensitivity remaining in business model.")
    pdf.subsection_header("Market Implication:")
    pdf.body_text("BULLISH - AI pivot working. Infrastructure assets valuable. Risk: highly leveraged, dilution possible. Position: Hold with tight stops.", bold=True)
    pdf.ln(5)
    
    # Bitcoin Mining Sector
    pdf.add_page()
    pdf.section_header("Bitcoin Mining Sector (RIOT, CLSK, WULF, HUT, CIFR)")
    pdf.subsection_header("News: Sector Pivot to AI Data Centers Accelerating")
    pdf.body_text("Multiple miners reporting AI hosting deals. Terawulf locked $12.8B in AI contracts. CleanSpark reported strong April operations. Miners outperforming Bitcoin by 70% YTD.")
    pdf.ln(2)
    pdf.subsection_header("Spectrum Analysis:")
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "LEFT: Environmental concerns about both mining and AI data centers. Focus on renewable energy sourcing. | CENTER: Valuation analysis of power contracts, hosting economics, diversification strategies. | RIGHT: Infrastructure buildout, US tech leadership, capital markets functioning.")
    pdf.ln(2)
    pdf.subsection_header("Likely Reality:")
    pdf.body_text("The AI data center pivot is the dominant theme. Power access is the scarce resource; miners have it. Not all will execute successfully - differentiation by contract quality and power costs. Risk: Bitcoin price decline hurts remaining mining operations.")
    pdf.subsection_header("Market Implication:")
    pdf.body_text("BULLISH - Sector rerating based on AI infrastructure value, not just crypto. Best positioned: those with long-term power contracts and operational excellence.", bold=True)
    pdf.ln(5)
    
    # Energy Holdings
    pdf.section_header("Energy Holdings (XOP, VDE, SHEL)")
    pdf.subsection_header("News: Geopolitical Premium Supporting Oil Prices")
    pdf.body_text("Exxon and Chevron reported lower Q1 profits despite higher oil prices. Exxon warned of 750,000 bpd production loss if Hormuz closed for full Q2.")
    pdf.ln(2)
    pdf.subsection_header("Spectrum Analysis:")
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "LEFT: Climate concerns, 'stranded asset' risk, transition to renewables. Skeptical of long-term energy investment. | CENTER: Supply/demand fundamentals, capital discipline, shareholder returns, geopolitical risk premium. | RIGHT: Energy independence, domestic production importance, criticism of anti-fossil fuel policies.")
    pdf.ln(2)
    pdf.subsection_header("Likely Reality:")
    pdf.body_text("Near-term bullish due to geopolitical risk. Long-term energy transition continues but timelines extended by energy security concerns. Integrated oils (XOM, CVX) best positioned; pure-play E&P (XOP constituents) more volatile.")
    pdf.subsection_header("Market Implication:")
    pdf.body_text("NEUTRAL-BULLISH - Geopolitical hedge valuable. But sector faces production headwinds if Hormuz disruption materializes. Position: Maintain allocation for diversification.", bold=True)
    pdf.ln(5)
    
    # Semiconductors
    pdf.section_header("Semiconductors (NVDA, MU, SMH, TSM)")
    pdf.subsection_header("News: AI Demand Continues Driving Record Results")
    pdf.body_text("NVDA investing up to $40B in AI-related equity bets. Micron posted best week since 2008 (+38%). TSMC revenue surging on AI chip demand.")
    pdf.ln(2)
    pdf.subsection_header("Likely Reality:")
    pdf.body_text("The AI buildout has years to run. Current strength is fundamental, not speculative. But valuations are pricing in continued perfection. NVDA's supply chain investments indicate they see demand lasting. Risk: China-Taiwan tensions, potential US-China tech restrictions.")
    pdf.subsection_header("Market Implication:")
    pdf.body_text("BULLISH - Maintain positions. NVDA anchor position justified. MU momentum strong. TSM geopolitical risk underappreciated by some.", bold=True)
    pdf.ln(5)
    
    # ===== BLINDSPOT REPORT =====
    pdf.add_page()
    pdf.chapter_title("Blindspot Report", "Stories One Side Is Ignoring")
    
    pdf.section_header("1. Taiwan Geopolitical Risk (Underreported by ALL)")
    pdf.body_text("While Iran gets headlines, the Taiwan Strait risk remains the largest potential market disruption. TSMC produces 90%+ of advanced semiconductors. Any China-Taiwan escalation would make current semiconductor shortages look minor. Neither left nor right sources adequately cover this tail risk.")
    pdf.ln(3)
    
    pdf.section_header("2. Commercial Real Estate (Ignored by Tech-Focused Sources)")
    pdf.body_text("Office vacancy rates remain elevated. $1.5T in CRE debt maturing 2025-2026. Regional bank exposure significant. This is a slow-burning issue that doesn't fit tech/crypto narratives but matters for financial stability.")
    pdf.ln(3)
    
    pdf.section_header("3. Dollar Strength Impact (Underreported)")
    pdf.body_text("Dollar gaining as Iran tensions increase safe-haven flows. Impacts: Emerging market stress, US multinational earnings headwinds, commodity prices. Not fitting neatly into current narratives so undercovered.")
    pdf.ln(3)
    
    pdf.section_header("4. Bond Market Signals (Center-Right Only)")
    pdf.body_text("Yield curve dynamics and credit spreads only covered in depth by financial specialists. Mainstream sources focus on equity moves. Bond market often leads; worth monitoring separately.")
    pdf.ln(5)
    
    # ===== PRE-MARKET OUTLOOK =====
    pdf.add_page()
    pdf.chapter_title("Pre-Market Outlook", "Synthesis & Positioning")
    
    pdf.section_header("Market Sentiment: CAUTIOUSLY BULLISH")
    pdf.ln(3)
    
    pdf.subsection_header("Key Drivers This Week:")
    pdf.bullet_point("CPI Release (May 12): Headline inflation acceleration expected. Market reaction depends on core reading.")
    pdf.bullet_point("Iran Developments: Ceasefire status uncertain. Any Hormuz closure threat would spike oil.")
    pdf.bullet_point("Tech Earnings Momentum: NVDA, semiconductor strength likely to continue.")
    pdf.ln(5)
    
    pdf.subsection_header("Portfolio Positioning Recommendations:")
    pdf.ln(2)
    
    # Create a table
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, 'Position', 1, 0, 'C', True)
    pdf.cell(50, 8, 'Ticker/Asset', 1, 0, 'C', True)
    pdf.cell(100, 8, 'Rationale', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 9)
    pdf.set_fill_color(240, 255, 240)
    pdf.cell(40, 12, 'HOLD', 1, 0, 'C', True)
    pdf.cell(50, 12, 'BE, INTC, NVDA', 1, 0, 'C')
    pdf.cell(100, 12, 'Strong momentum, positive news flow. Use stops.', 1, 1, 'L')
    
    pdf.set_fill_color(255, 255, 240)
    pdf.cell(40, 10, 'HOLD', 1, 0, 'C', True)
    pdf.cell(50, 10, 'CORZ, RIOT, CLSK', 1, 0, 'C')
    pdf.cell(100, 10, 'AI pivot working but volatile. Tight stops.', 1, 1, 'L')
    
    pdf.set_fill_color(240, 240, 255)
    pdf.cell(40, 10, 'HOLD', 1, 0, 'C', True)
    pdf.cell(50, 10, 'XOP, VDE, SHEL', 1, 0, 'C')
    pdf.cell(100, 10, 'Geopolitical hedge. Maintain allocation.', 1, 1, 'L')
    
    pdf.set_fill_color(255, 240, 240)
    pdf.cell(40, 10, 'WATCH', 1, 0, 'C', True)
    pdf.cell(50, 10, 'TEM, SPOT, RDDT', 1, 0, 'C')
    pdf.cell(100, 10, 'Speculative positions. CPI reaction risk.', 1, 1, 'L')
    
    pdf.ln(8)
    
    pdf.section_header("Risk Factors to Monitor:")
    pdf.bullet_point("CPI surprise to upside (core above 0.4% m/m)")
    pdf.bullet_point("Strait of Hormuz closure threat or actual closure")
    pdf.bullet_point("Apple-Intel deal confirmation or denial")
    pdf.bullet_point("Fed officials' commentary post-CPI")
    pdf.ln(5)
    
    pdf.section_header("Overall Assessment:")
    pdf.body_text("Portfolio well-positioned for current environment. Tech momentum (BE, INTC, NVDA) driving gains. Energy exposure provides geopolitical hedge. Bitcoin miners transitioning to AI infrastructure plays. Main risk is CPI reaction and any Hormuz disruption. Recommend holding current positions with trailing stops on high-beta names.", bold=True)
    
    # Save the PDF
    output_dir = "C:\\Users\\thadd\\OneDrive\\Desktop\\Spocks Reports\\daily-brief"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "2026-05-11_daily_brief.pdf")
    pdf.output(output_path)
    
    return output_path

if __name__ == "__main__":
    path = generate_report()
    print(f"PDF generated: {path}")
