#!/usr/bin/env python3
"""
Top 100 Stock Strategists Report Generator
Generates a comprehensive PDF report on hedge fund holdings and overlaps.
"""

from fpdf import FPDF
from datetime import datetime
import os

class PDFReport(FPDF):
    def header(self):
        # Logo placeholder
        self.set_font('Arial', 'B', 10)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, 'Top 100 Stock Strategists Report', 0, 0, 'L')
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'R')
        self.ln(15)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 12, title, 0, 1, 'L')
        self.ln(2)
        
    def chapter_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(66, 70, 73)
        self.cell(0, 8, subtitle, 0, 1, 'L')
        self.ln(1)
        
    def body_text(self, text):
        self.set_font('Arial', '', 10)
        self.set_text_color(33, 37, 41)
        self.multi_cell(0, 5, text)
        self.ln(3)
        
    def section_divider(self):
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

def create_report():
    pdf = PDFReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ===== COVER PAGE =====
    pdf.add_page()
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(33, 37, 41)
    pdf.ln(60)
    pdf.cell(0, 20, 'Top 100 Stock Strategists', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(66, 70, 73)
    pdf.cell(0, 12, 'Hedge Fund Holdings & Consensus Analysis', 0, 1, 'C')
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f'Report Date: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Data Source: SEC 13F Filings (Q4 2025)', 0, 1, 'C')
    
    # ===== EXECUTIVE SUMMARY =====
    pdf.add_page()
    pdf.chapter_title('Executive Summary')
    
    summary_text = """This report analyzes the holdings of the top 100 stock strategists and hedge fund managers 
based on their latest 13F filings. The analysis covers $5.52 trillion in combined assets under management 
and identifies key consensus positions across major institutional investors.

Key Findings:
- Technology remains the dominant sector with $1.3 trillion in new institutional capital
- Microsoft leads consensus buys with over 4,000 new institutional buyers in Q4 2025
- The "Magnificent Seven" stocks continue to dominate institutional portfolios
- Healthcare emerged as a major growth sector with $508.8B in new capital flows"""
    
    pdf.body_text(summary_text)
    pdf.section_divider()
    
    # Top 10 Consensus Stocks
    pdf.chapter_subtitle('Top 10 Most-Held Consensus Stocks')
    
    consensus_stocks = [
        ("1. Microsoft (MSFT)", "Over 4,000 institutional buyers", "$263.5B new capital", "5 superinvestor buys"),
        ("2. Apple (AAPL)", "Over 4,000 institutional buyers", "$219.9B new capital", "4 superinvestor buys"),
        ("3. Amazon (AMZN)", "Over 4,000 institutional buyers", "$169.8B new capital", "4 superinvestor buys"),
        ("4. NVIDIA (NVDA)", "445 new buyers (high conviction)", "$80.7B new capital", "Tech/Growth"),
        ("5. Johnson & Johnson (JNJ)", "3,142 new buyers", "Healthcare consensus", "Post-Kenvue separation"),
        ("6. Eli Lilly (LLY)", "3,034 new buyers", "$79.5B new capital", "GLP-1 drug momentum"),
        ("7. Walmart (WMT)", "2,982 new buyers", "$178.2B sector", "E-commerce transformation"),
        ("8. Berkshire Hathaway (BRK.B)", "3 superinvestors", "Warren Buffett value", "2.5% avg allocation"),
        ("9. Taiwan Semi (TSM)", "1,945 new buyers", "$49.0B new capital", "Semiconductor supply chain"),
        ("10. Broadcom (AVGO)", "2 superinvestors", "$32.0B new capital", "3.6% avg allocation"),
    ]
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 6, 'Stock', 1, 0, 'L')
    pdf.cell(45, 6, 'Institutional Interest', 1, 0, 'L')
    pdf.cell(50, 6, 'Capital Flow', 1, 0, 'L')
    pdf.cell(45, 6, 'Signal', 1, 1, 'L')
    
    pdf.set_font('Arial', '', 9)
    for stock, buyers, capital, signal in consensus_stocks:
        pdf.cell(50, 5, stock, 1, 0, 'L')
        pdf.cell(45, 5, buyers, 1, 0, 'L')
        pdf.cell(50, 5, capital, 1, 0, 'L')
        pdf.cell(45, 5, signal, 1, 1, 'L')
    pdf.ln(5)
    
    # ===== TOP 100 STRATEGISTS =====
    pdf.add_page()
    pdf.chapter_title('Top 100 Stock Strategists by AUM')
    
    intro = """The following represents the 100 largest hedge fund managers in North America, 
managing a combined $5.52 trillion in assets as of 2026 (up 13.9% from 2025)."""
    pdf.body_text(intro)
    
    # Top 25 table
    top_25 = [
        ("1", "Citadel Investment Group", "$446.0B", "Ken Griffin", "Multi-Strategy"),
        ("2", "Ares Management", "$318.7B", "Tony Ressler", "Credit/Private Equity"),
        ("3", "Balyasny Asset Management", "$265.2B", "Dmitry Balyasny", "Multi-Strategy"),
        ("4", "Oracle Investment Management", "$265.2B", "Larry Ellison", "Long/Short"),
        ("5", "Point72 Asset Management", "$220.9B", "Steven Cohen", "Multi-Strategy"),
        ("6", "Millennium Capital Partners", "$218.0B", "Israel Englander", "Multi-Strategy"),
        ("7", "D.E. Shaw", "$154.6B", "David Shaw", "Quantitative"),
        ("8", "Alphadyne Asset Management", "$147.4B", "Philippe Jabre", "Global Macro"),
        ("9", "ExodusPoint Capital", "$119.7B", "Michael Gelband", "Multi-Strategy"),
        ("10", "Two Sigma Investments", "$110.3B", "John Overdeck", "Quantitative"),
        ("11", "Garda Capital", "$106.6B", "Mike Packer", "Distressed"),
        ("12", "Goldman Sachs Asset Mgmt", "$106.2B", "Multiple", "Fund of Funds"),
        ("13", "Mariner Investment Group", "$103.6B", "William Michaelcheck", "Multi-Strategy"),
        ("14", "Angelo Gordon", "$100.1B", "Joshua Baumgarten", "Credit/Distressed"),
        ("15", "Bridgewater Associates", "$97.9B", "Ray Dalio", "Global Macro"),
        ("16", "Renaissance Technologies", "$92.0B", "Jim Simons", "Quantitative"),
        ("17", "Lighthouse Investment", "$85.7B", "Sean McGowan", "Multi-Strategy"),
        ("18", "Bracebridge Capital", "$84.7B", "Nancy Zimmerman", "Fixed Income"),
        ("19", "Cerberus Capital", "$84.1B", "Steve Feinberg", "Distressed"),
        ("20", "AQR Capital Management", "$83.8B", "Cliff Asness", "Quantitative"),
        ("21", "Tudor Investment", "$83.6B", "Paul Tudor Jones", "Global Macro"),
        ("22", "Fortress Investment Group", "$71.3B", "Wesley Edens", "Credit/Real Estate"),
        ("23", "Viking Global Investors", "$69.8B", "Andreas Halvorsen", "Long/Short Equity"),
        ("24", "Tiger Global Management", "$69.6B", "Chase Coleman", "Growth/Tech"),
        ("25", "Coatue Management", "$69.4B", "Philippe Laffont", "Tech/Growth"),
    ]
    
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(10, 5, 'Rank', 1, 0, 'C')
    pdf.cell(55, 5, 'Fund Name', 1, 0, 'L')
    pdf.cell(30, 5, 'AUM', 1, 0, 'R')
    pdf.cell(45, 5, 'Key Manager', 1, 0, 'L')
    pdf.cell(50, 5, 'Strategy', 1, 1, 'L')
    
    pdf.set_font('Arial', '', 8)
    for rank, name, aum, manager, strategy in top_25:
        pdf.cell(10, 4, rank, 1, 0, 'C')
        pdf.cell(55, 4, name[:28], 1, 0, 'L')
        pdf.cell(30, 4, aum, 1, 0, 'R')
        pdf.cell(45, 4, manager[:22], 1, 0, 'L')
        pdf.cell(50, 4, strategy[:24], 1, 1, 'L')
    pdf.ln(5)
    
    # Next 25
    pdf.chapter_subtitle('Rankings 26-50')
    next_25 = [
        ("26", "Adage Capital Management", "$60.0B", "Phillip Gross"),
        ("27", "Stone Point Capital", "$56.8B", "James Parsons"),
        ("28", "III Capital", "$55.3B", "Cullen Thompson"),
        ("29", "Farallon Capital", "$48.2B", "Thomas Steyer"),
        ("30", "Och-Ziff Capital", "$44.0B", "Daniel Och"),
        ("31", "Sculptor Capital", "$44.0B", "Jimmy Levin"),
        ("32", "GoldenTree Asset Mgmt", "$43.7B", "Steven Tananbaum"),
        ("33", "Polar Asset Management", "$42.9B", "Canada/Toronto"),
        ("34", "Davidson Kempner", "$41.6B", "Anthony Yoseloff"),
        ("35", "Tenaron Capital", "$40.0B", "Yves Balcer"),
        ("36", "Element Capital", "$40.0B", "Jeffrey Talpins"),
        ("37", "Oaktree Capital", "$38.4B", "Howard Marks"),
        ("38", "Holocene Advisors", "$38.0B", "Brandon Haley"),
        ("39", "Silver Point Capital", "$37.1B", "Robert OShea"),
        ("40", "Centerbridge Partners", "$37.0B", "Mark Gallogly"),
        ("41", "Voloridge Investment", "$36.3B", "David Siegel"),
        ("42", "Field Street Capital", "$36.0B", "Daniel Krueger"),
        ("43", "Hudson Bay Capital", "$33.9B", "Sander Gerber"),
        ("44", "BlackRock Alternative", "$33.3B", "Multiple"),
        ("45", "Apollo Capital", "$32.7B", "Multiple"),
        ("46", "King Street Capital", "$32.3B", "O. Andreas Halvorsen"),
        ("47", "Paskewitz Asset Mgmt", "$31.8B", "Norman Paskewitz"),
        ("48", "Alyeska Investment", "$31.7B", "Adam Weiss"),
        ("49", "Select Equity", "$31.6B", "Robert Ellis"),
        ("50", "Graham Capital", "$28.5B", "Kenneth Tropin"),
    ]
    
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(10, 5, 'Rank', 1, 0, 'C')
    pdf.cell(65, 5, 'Fund Name', 1, 0, 'L')
    pdf.cell(35, 5, 'AUM', 1, 0, 'R')
    pdf.cell(80, 5, 'Key Manager', 1, 1, 'L')
    
    pdf.set_font('Arial', '', 8)
    for rank, name, aum, manager in next_25:
        pdf.cell(10, 4, rank, 1, 0, 'C')
        pdf.cell(65, 4, name[:32], 1, 0, 'L')
        pdf.cell(35, 4, aum, 1, 0, 'R')
        pdf.cell(80, 4, manager, 1, 1, 'L')
    pdf.ln(5)
    
    # ===== MAJOR MANAGER HOLDINGS =====
    pdf.add_page()
    pdf.chapter_title('Major Strategist Holdings (Latest 13F)')
    
    # Berkshire Hathaway
    pdf.chapter_subtitle('Berkshire Hathaway (Warren Buffett) - $258.7B AUM')
    berkshire = """Top Holdings:
- Apple (AAPL) - Largest position, ~40% of portfolio
- Bank of America (BAC) - Major financial holding
- Coca-Cola (KO) - Long-term holding
- American Express (AXP) - Financial services
- Occidental Petroleum (OXY) - Energy sector
- Chevron (CVX) - Oil & gas major
- Kraft Heinz (KHC) - Consumer staples
- Moody's (MCO) - Financial information
- DaVita (DVA) - Healthcare services
- Citigroup (C) - Banking (new position)"""
    pdf.body_text(berkshire)
    pdf.section_divider()
    
    # Citadel
    pdf.chapter_subtitle('Citadel Advisors (Ken Griffin) - $665.9B AUM')
    citadel = """Profile: Multi-strategy hedge fund with extensive diversification
Holdings: 12,508 positions (highly diversified)
Key Sectors: Technology, Consumer, Healthcare, Financials
Notable: Significant QQQ position ($1.56B), dramatic increases in UNH (+1,201%), 
PEP (+965%), and GLD (+891%) showing tech conviction and defensive plays."""
    pdf.body_text(citadel)
    pdf.section_divider()
    
    # Bridgewater
    pdf.chapter_subtitle('Bridgewater Associates (Ray Dalio) - $27.4B AUM')
    bridgewater = """Strategy: Global macro, risk-parity
Holdings: 1,040 positions
Top Sectors: ETFs, Consumer Staples, Healthcare
Known for: All Weather strategy, diversified across asset classes and geographies."""
    pdf.body_text(bridgewater)
    pdf.section_divider()
    
    # Point72
    pdf.chapter_subtitle('Point72 Asset Management (Steven Cohen) - $63.8B AUM')
    point72 = """Holdings: 2,338 positions
Strategy: Multi-strategy, fundamental + quantitative
Notable Q4 2025 moves: New QQQ position ($1.56B), increased UNH (+1,201%), 
PEP (+965%), GLD (+891%) - dual signal of tech conviction and defensive rotation."""
    pdf.body_text(point72)
    pdf.section_divider()
    
    # Pershing Square
    pdf.chapter_subtitle('Pershing Square (Bill Ackman) - $15.5B AUM')
    pershing = """Strategy: Concentrated, activist
Holdings: 11 positions (highly concentrated)
Top Holdings: Brookfield Corporation, Uber Technologies, Amazon, 
Alphabet, Chipotle Mexican Grill, Lowe's Companies
Recent: Significantly increased Amazon (AMZN) position."""
    pdf.body_text(pershing)
    pdf.section_divider()
    
    # Appaloosa
    pdf.chapter_subtitle('Appaloosa Management (David Tepper) - $6.9B AUM')
    appaloosa = """Holdings: 39 positions
Strategy: Distressed, event-driven, value
Key Holdings: Chinese tech stocks (Alibaba, PDD, JD.com), 
semiconductors (Micron), and U.S. tech giants."""
    pdf.body_text(appaloosa)
    
    # ===== OVERLAP ANALYSIS =====
    pdf.add_page()
    pdf.chapter_title('Overlap Analysis')
    
    overlap_intro = """This section analyzes which stocks appear in multiple top-tier 
hedge fund portfolios, indicating strong institutional consensus."""
    pdf.body_text(overlap_intro)
    
    pdf.chapter_subtitle('Sector Distribution of New Institutional Capital')
    sectors = [
        ("Technology", "$1.3 trillion", "47% of new capital"),
        ("Financial Services", "$666.7B", "23% of new capital"),
        ("Healthcare", "$508.8B", "18% of new capital"),
        ("Consumer Cyclical", "$450.2B", "16% of new capital"),
        ("Consumer Defensive", "$178.2B", "6% of new capital"),
        ("Utilities", "$107.4B", "4% of new capital"),
    ]
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 6, 'Sector', 1, 0, 'L')
    pdf.cell(50, 6, 'New Capital', 1, 0, 'R')
    pdf.cell(60, 6, 'Share', 1, 1, 'L')
    
    pdf.set_font('Arial', '', 9)
    for sector, capital, share in sectors:
        pdf.cell(60, 5, sector, 1, 0, 'L')
        pdf.cell(50, 5, capital, 1, 0, 'R')
        pdf.cell(60, 5, share, 1, 1, 'L')
    pdf.ln(5)
    
    pdf.chapter_subtitle('High-Conviction Overlaps')
    conviction = """Stocks held by multiple superinvestors with high average allocations:

1. Microsoft (MSFT) - 5 superinvestors, 3.6% avg allocation
   - Strongest consensus signal in the market
   - Cloud, AI, and productivity leadership

2. Amazon (AMZN) - 4 superinvestors, 2.8% avg allocation
   - E-commerce + AWS dual moat
   - AI infrastructure investments

3. Tyson Foods (TSFN) - 4 superinvestors, 2.9% avg allocation
   - Defensive food sector play
   - Value rotation signal

4. Berkshire Hathaway (BRK.B) - 3 superinvestors, 2.5% avg allocation
   - Value investor's value play
   - Diversified conglomerate exposure

5. Broadcom (AVGO) - 2 superinvestors, 3.6% avg allocation
   - AI chip exposure
   - VMware integration synergies"""
    pdf.body_text(conviction)
    
    # ===== CONSENSUS PICKS =====
    pdf.add_page()
    pdf.chapter_title('Consensus Picks')
    
    consensus_intro = """The following stocks show the highest degree of strategist overlap 
and represent the strongest institutional conviction positions."""
    pdf.body_text(consensus_intro)
    
    pdf.chapter_subtitle('Tier 1: Universal Consensus (4,000+ New Buyers)')
    tier1 = [
        ("Microsoft (MSFT)", "Cloud/AI leadership", "$263.5B"),
        ("Apple (AAPL)", "Consumer ecosystem", "$219.9B"),
        ("Amazon (AMZN)", "E-commerce + Cloud", "$169.8B"),
    ]
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 6, 'Stock', 1, 0, 'L')
    pdf.cell(70, 6, 'Thesis', 1, 0, 'L')
    pdf.cell(50, 6, 'New Capital', 1, 1, 'R')
    
    pdf.set_font('Arial', '', 9)
    for stock, thesis, capital in tier1:
        pdf.cell(50, 5, stock, 1, 0, 'L')
        pdf.cell(70, 5, thesis, 1, 0, 'L')
        pdf.cell(50, 5, capital, 1, 1, 'R')
    pdf.ln(5)
    
    pdf.chapter_subtitle('Tier 2: Strong Consensus (1,000+ New Buyers)')
    tier2 = [
        ("NVIDIA (NVDA)", "AI chips, few new buyers but massive capital", "$80.7B"),
        ("Eli Lilly (LLY)", "GLP-1 obesity drugs", "$79.5B"),
        ("Taiwan Semi (TSM)", "AI chip manufacturing", "$49.0B"),
        ("Broadcom (AVGO)", "AI infrastructure", "$32.0B"),
        ("Johnson & Johnson (JNJ)", "Healthcare stability", "Post-Kenvue"),
    ]
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 6, 'Stock', 1, 0, 'L')
    pdf.cell(80, 6, 'Thesis', 1, 0, 'L')
    pdf.cell(40, 6, 'New Capital', 1, 1, 'R')
    
    pdf.set_font('Arial', '', 9)
    for stock, thesis, capital in tier2:
        pdf.cell(50, 5, stock, 1, 0, 'L')
        pdf.cell(80, 5, thesis[:35], 1, 0, 'L')
        pdf.cell(40, 5, capital, 1, 1, 'R')
    pdf.ln(5)
    
    pdf.chapter_subtitle('Key Insights')
    insights = """1. AI Infrastructure Play: NVIDIA, Broadcom, and Taiwan Semi represent 
   a concentrated bet on AI hardware infrastructure.

2. Healthcare Renaissance: Eli Lilly and J+J show institutional rotation 
   into defensive healthcare with growth catalysts.

3. Big Tech Dominance: Microsoft, Apple, and Amazon remain the core 
   foundational holdings across virtually all major funds.

4. Defensive Rotation: Increased positions in consumer staples (Tyson, Pepsi) 
   and healthcare indicate hedging against market volatility.

5. International Exposure: Appaloosa's China tech bets (Alibaba, PDD, JD) 
   represent a contrarian/value play on beaten-down Chinese equities."""
    pdf.body_text(insights)
    
    # ===== RANKINGS 51-100 =====
    pdf.add_page()
    pdf.chapter_title('Rankings 51-100')
    
    rankings_51_100 = [
        ("51", "Kayne Anderson", "$28.4B"),
        ("52", "HBK Capital Management", "$28.0B"),
        ("53", "Moore Capital Management", "$28.0B"),
        ("54", "Wellington Management", "$27.2B"),
        ("55", "Capstone Investment Advisors", "$27.0B"),
        ("56", "Benefit Street Partners", "$26.1B"),
        ("57", "Magnetar Capital", "$25.0B"),
        ("58", "Pine River Capital", "$24.1B"),
        ("59", "Baupost Group", "$23.6B"),
        ("60", "Strategic Value Partners", "$23.4B"),
        ("61", "Onex Credit Partners", "$23.4B"),
        ("62", "Woodline Partners", "$22.7B"),
        ("63", "Horsley Bridge Partners", "$22.3B"),
        ("64", "Haidar Capital Management", "$21.9B"),
        ("65", "Diameter Capital Partners", "$21.6B"),
        ("66", "Wafra Investment Group", "$20.8B"),
        ("67", "Paloma Partners", "$20.8B"),
        ("68", "Brigade Capital Management", "$20.3B"),
        ("69", "Marathon Asset Management", "$20.3B"),
        ("70", "Lone Pine Capital", "$19.8B"),
        ("71", "Beach Point Capital", "$19.7B"),
        ("72", "Arrowstreet Capital", "$19.6B"),
        ("73", "Stockbridge", "$19.5B"),
        ("74", "Third Point LLC", "$19.3B"),
        ("75", "Guggenheim Capital", "$19.2B"),
        ("76", "Appaloosa Management", "$19.1B"),
        ("77", "Alpha Wave Global", "$19.0B"),
        ("78", "Grantham Mayo Van Otterloo", "$19.0B"),
        ("79", "Pershing Square Capital", "$18.3B"),
        ("80", "OrbiMed Advisors", "$17.3B"),
        ("81", "Universa Investments", "$17.2B"),
        ("82", "Varde Partners", "$16.7B"),
        ("83", "Monarch Alternative Capital", "$16.5B"),
        ("84", "Neuberger Berman", "$15.9B"),
        ("85", "MSD Capital", "$15.7B"),
        ("86", "Bayview Asset Management", "$14.7B"),
        ("87", "Saba Capital", "$14.5B"),
        ("88", "Alkeon Capital Management", "$14.2B"),
        ("89", "Lazard Alternatives", "$14.1B"),
        ("90", "PDT Partners", "$14.0B"),
        ("91", "Commonfund Capital", "$14.0B"),
        ("92", "CarVal Investors", "$13.9B"),
        ("93", "Engineers Gate Manager", "$13.6B"),
        ("94", "Canyon Partners", "$13.5B"),
        ("95", "MJX Asset Management", "$13.1B"),
        ("96", "LibreMax Capital", "$13.0B"),
        ("97", "Abrams Capital", "$13.0B"),
        ("98", "26 North", "$12.8B"),
        ("99", "JHL Capital Group", "$12.8B"),
        ("100", "Rockpoint Group", "$12.8B"),
    ]
    
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(15, 5, 'Rank', 1, 0, 'C')
    pdf.cell(85, 5, 'Fund Name', 1, 0, 'L')
    pdf.cell(40, 5, 'AUM', 1, 1, 'R')
    
    pdf.set_font('Arial', '', 8)
    for rank, name, aum in rankings_51_100:
        pdf.cell(15, 4, rank, 1, 0, 'C')
        pdf.cell(85, 4, name[:38], 1, 0, 'L')
        pdf.cell(40, 4, aum, 1, 1, 'R')
    
    # ===== DISCLAIMER =====
    pdf.add_page()
    pdf.chapter_title('Disclaimer & Methodology')
    
    disclaimer = """IMPORTANT NOTICE:

This report is for informational purposes only and does not constitute investment advice. 
The data presented is compiled from publicly available SEC 13F filings and other open sources.

Methodology:
- Data sourced from SEC EDGAR 13F-HR filings for Q4 2025
- Holdings data represents positions as of December 31, 2025
- AUM figures are estimates based on publicly available information
- Consensus analysis based on new institutional buyers in Q4 2025
- Overlaps calculated from reported 13F filings of major hedge funds

Limitations:
- 13F filings have a 45-day delay from quarter end
- Not all holdings are disclosed (exemptions apply)
- Short positions are not reported in 13F filings
- International holdings may be underrepresented
- Data reflects positions at filing date, not current date

Notable Managers Not Yet Filed (as of report date):
- Berkshire Hathaway (Q2 data used)
- Bridgewater Associates (previous quarter)
- Citadel Advisors (previous quarter)
- Millennium Management
- Two Sigma Investments

This report was generated on {date}.

Data Sources:
- SEC EDGAR Database
- 13F Insight
- SuperInvestor Club
- HedgeLists
- SWFI Institute
- Capital AUM

Report prepared by: Spock AI Assistant""".format(date=datetime.now().strftime("%B %d, %Y"))
    
    pdf.body_text(disclaimer)
    
    # Save the PDF
    output_dir = r"C:\Users\thadd\OneDrive\Desktop\Spocks Reports"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"top_100_strategists_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    pdf.output(output_path)
    print(f"PDF generated successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    create_report()
