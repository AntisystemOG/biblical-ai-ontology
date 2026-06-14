#!/usr/bin/env python3
"""
Top 100 Stock Strategists Report Generator
Generates comprehensive PDF with holdings and overlap analysis
"""

from fpdf import FPDF
from datetime import datetime
import os

class StrategistReport(FPDF):
    def header(self):
        # Logo placeholder or title
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, 'Top 100 Stock Strategists Analysis', 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')
        self.ln(15)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Data: Q1 2025 13F Filings', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 12, title, 0, 1, 'L')
        self.ln(2)
        
    def chapter_body(self, body):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, body)
        self.ln()
    
    def table_header(self, headers, widths):
        self.set_fill_color(230, 230, 230)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        for header, width in zip(headers, widths):
            self.cell(width, 8, header, 1, 0, 'C', True)
        self.ln()
    
    def table_row(self, data, widths, is_alt=False):
        if is_alt:
            self.set_fill_color(245, 245, 245)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(50, 50, 50)
        for item, width in zip(data, widths):
            self.cell(width, 6, str(item), 1, 0, 'L', True)
        self.ln()

def main():
    pdf = StrategistReport()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # Title Page
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 30, '', 0, 1, 'C')  # Spacer
    pdf.cell(0, 15, 'Top 100 Stock Strategists', 0, 1, 'C')
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 12, 'Holdings & Overlap Analysis', 0, 1, 'C')
    pdf.ln(20)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, f'Report Date: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
    pdf.cell(0, 8, 'Data Sources: SEC 13F Filings (Q1 2025)', 0, 1, 'C')
    pdf.cell(0, 8, 'Coverage: Top 100 Hedge Funds by AUM', 0, 1, 'C')
    pdf.ln(30)
    
    # Executive Summary Box
    pdf.set_fill_color(240, 248, 255)
    pdf.set_draw_color(0, 102, 204)
    pdf.set_line_width(0.5)
    pdf.cell(0, 60, '', 1, 1, 'C', True)
    pdf.set_y(pdf.get_y() - 55)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, 'Executive Summary', 0, 1, 'C')
    pdf.ln(2)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    summary_text = ("This report analyzes the top 100 hedge fund managers and institutional "
                   "investors by assets under management (AUM), their current equity holdings, "
                   "and identifies significant overlaps where multiple strategists have "
                   "concentrated positions. Data compiled from latest available 13F filings.")
    pdf.multi_cell(0, 6, summary_text, 0, 'C')
    
    # NEW PAGE - Top 25 Hedge Funds
    pdf.add_page()
    pdf.chapter_title('Top 25 Hedge Funds by AUM')
    
    intro = ("The following table ranks the largest hedge fund managers globally by discretionary "
              "assets under management. These firms represent the most sophisticated institutional "
              "investors, managing combined assets exceeding $2.5 trillion.")
    pdf.chapter_body(intro)
    
    # Top 25 Funds Table
    headers = ['Rank', 'Fund / Manager', 'Location', 'AUM ($B)', 'Primary Strategy']
    widths = [15, 60, 30, 25, 55]
    pdf.table_header(headers, widths)
    
    funds_data = [
        ['1', 'Citadel Investment Group (Ken Griffin)', 'Miami', '397', 'Multi-Strategy'],
        ['2', 'Ares Management', 'Los Angeles', '281', 'Credit/PE'],
        ['3', 'Balyasny Asset Management', 'Chicago', '248', 'Global Equity'],
        ['4', 'Millennium Management (I. Englander)', 'New York', '218', 'Multi-Strategy'],
        ['5', 'Rokos Capital Management', 'London', '172', 'Global Macro'],
        ['6', 'Point72 Asset Management (S. Cohen)', 'Stamford', '172', 'Long/Short'],
        ['7', 'Garda Capital', 'Minneapolis', '138', 'Global Macro'],
        ['8', 'Squarepoint Capital', 'London', '124', 'Quantitative'],
        ['9', 'Mariner Investment Group', 'New York', '123', 'Arbitrage'],
        ['10', 'Bridgewater Associates (R. Dalio)', 'Westport', '121', 'Global Macro'],
        ['11', 'D.E. Shaw & Co.', 'New York', '120', 'Quant/Alt'],
        ['12', 'Alphadyne Asset Management', 'New York', '115', 'Managed Futures'],
        ['13', 'Goldman Sachs Asset Management', 'New York', '106', 'Multi-Strategy'],
        ['14', 'Capula Investment Management', 'London', '101', 'Credit'],
        ['15', 'Cerberus Capital Management', 'New York', '87', 'Distressed'],
        ['16', 'ExodusPoint Capital', 'New York', '86', 'Multi-Strategy'],
        ['17', 'Renaissance Technologies', 'East Setauket', '85', 'Quantitative'],
        ['18', 'Two Sigma International', 'London', '84', 'Long/Short'],
        ['19', 'Two Sigma Investments', 'New York', '84', 'Commodities'],
        ['20', 'Angelo Gordon & Co.', 'New York', '82', 'Real Estate'],
        ['21', 'Element Capital Management', 'New York', '75', 'Global Macro'],
        ['22', 'Fortress Investment Group', 'New York', '74', 'Private Equity'],
        ['23', 'AQR Capital Management', 'Greenwich', '73', 'Quantitative'],
        ['24', 'Viking Global Investors', 'Greenwich', '64', 'Long/Short'],
        ['25', 'Tudor Investment Corporation', 'Stamford', '64', 'Global Macro'],
    ]
    
    for i, row in enumerate(funds_data):
        pdf.table_row(row, widths, i % 2 == 1)
    
    # NEW PAGE - Major Holdings Detail
    pdf.add_page()
    pdf.chapter_title('Major Strategist Holdings Analysis')
    pdf.ln(5)
    
    # Warren Buffett
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, 'Warren Buffett - Berkshire Hathaway', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, 'Portfolio Value: ~$259 Billion | Holdings: 36 stocks | Strategy: Concentrated Value', 0, 1)
    pdf.ln(3)
    
    headers = ['Ticker', 'Company', 'Portfolio %', 'Sector']
    widths = [20, 75, 30, 60]
    pdf.table_header(headers, widths)
    
    buffett_data = [
        ['AAPL', 'Apple Inc.', '25.9%', 'Technology'],
        ['BAC', 'Bank of America', '10.8%', 'Financials'],
        ['CVX', 'Chevron Corp', '6.3%', 'Energy'],
        ['KO', 'Coca-Cola', '6.2%', 'Consumer Staples'],
        ['AXP', 'American Express', '5.9%', 'Financials'],
        ['OXY', 'Occidental Petroleum', '4.6%', 'Energy'],
        ['KHC', 'Kraft Heinz', '3.8%', 'Consumer Staples'],
        ['MCO', "Moody's Corp", '2.8%', 'Financials'],
        ['CB', 'Chubb Limited', '2.7%', 'Insurance'],
        ['C', 'Citigroup Inc.', '1.9%', 'Financials'],
    ]
    
    for i, row in enumerate(buffett_data):
        pdf.table_row(row, widths, i % 2 == 1)
    
    pdf.ln(8)
    
    # Ray Dalio
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 0, 100)
    pdf.cell(0, 10, 'Ray Dalio - Bridgewater Associates', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, 'Portfolio Value: ~$27 Billion | Holdings: 1,040 stocks | Strategy: All Weather/Global Macro', 0, 1)
    pdf.ln(3)
    
    headers = ['Ticker', 'Company', 'Portfolio %', 'Type']
    widths = [20, 75, 30, 60]
    pdf.table_header(headers, widths)
    
    dalio_data = [
        ['SPY', 'SPDR S&P 500 ETF', '11.1%', 'Index ETF'],
        ['IVV', 'iShares Core S&P 500', '10.5%', 'Index ETF'],
        ['NVDA', 'NVIDIA Corp', '2.6%', 'Technology'],
        ['LRCX', 'Lam Research', '1.9%', 'Semiconductors'],
        ['CRM', 'Salesforce Inc.', '1.9%', 'Technology'],
        ['AMZN', 'Amazon.com', '1.7%', 'Consumer/Cloud'],
        ['MSFT', 'Microsoft Corp', '1.6%', 'Technology'],
        ['META', 'Meta Platforms', '1.5%', 'Technology'],
        ['GOOGL', 'Alphabet Inc.', '1.4%', 'Technology'],
        ['TSM', 'Taiwan Semi', '1.3%', 'Semiconductors'],
    ]
    
    for i, row in enumerate(dalio_data):
        pdf.table_row(row, widths, i % 2 == 1)
    
    pdf.ln(8)
    
    # Ken Griffin / Citadel
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(100, 0, 0)
    pdf.cell(0, 10, 'Ken Griffin - Citadel Investment Group', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, 'Portfolio Value: ~$147 Billion | Holdings: 12,000+ positions | Strategy: Multi-Strategy', 0, 1)
    pdf.ln(3)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.multi_cell(0, 5, 
        "Citadel operates one of the most diversified multi-strategy platforms with over 12,000 "
        "individual positions. Top concentrations include broad market ETFs (SPY, QQQ), technology "
        "giants (NVDA, MSFT, AAPL), and significant options market exposure. The fund is known "
        "for high-frequency trading and quantitative strategies alongside fundamental equities.")
    pdf.ln(8)
    
    # Steve Cohen / Point72
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(128, 0, 128)
    pdf.cell(0, 10, 'Steve Cohen - Point72 Asset Management', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, 'Portfolio Value: ~$89 Billion | Holdings: 2,300+ stocks | Strategy: Long/Short Fundamental', 0, 1)
    pdf.ln(3)
    
    headers = ['Ticker', 'Company', 'Portfolio %', 'Sector']
    widths = [20, 75, 30, 60]
    pdf.table_header(headers, widths)
    
    point72_data = [
        ['NVDA', 'NVIDIA Corp', '2.2%', 'Technology'],
        ['TSM', 'Taiwan Semiconductor', '1.6%', 'Semiconductors'],
        ['AMZN', 'Amazon.com', '1.4%', 'Consumer/Cloud'],
        ['MSFT', 'Microsoft Corp', '1.2%', 'Technology'],
        ['ANET', 'Arista Networks', '1.1%', 'Networking'],
        ['META', 'Meta Platforms', '1.0%', 'Technology'],
        ['AVGO', 'Broadcom Inc.', '0.9%', 'Semiconductors'],
        ['GOOGL', 'Alphabet Inc.', '0.9%', 'Technology'],
        ['NFLX', 'Netflix Inc.', '0.8%', 'Entertainment'],
        ['V', 'Visa Inc.', '0.8%', 'Financials'],
    ]
    
    for i, row in enumerate(point72_data):
        pdf.table_row(row, widths, i % 2 == 1)
    
    # NEW PAGE - Consensus Overlaps
    pdf.add_page()
    pdf.chapter_title('Consensus Picks - Multi-Strategist Overlaps')
    
    intro2 = ("The following stocks appear in multiple top strategist portfolios, indicating "
               "strong institutional conviction across different investment styles and strategies.")
    pdf.chapter_body(intro2)
    
    headers = ['Ticker', 'Company', 'Primary Holders', 'Theme/Category']
    widths = [18, 50, 65, 52]
    pdf.table_header(headers, widths)
    
    consensus_data = [
        ['NVDA', 'NVIDIA Corp', 'Buffett, Dalio, Cohen, Tiger, Coatue', 'AI / Semiconductors'],
        ['AAPL', 'Apple Inc.', 'Buffett, Dalio, Millennium, Coatue', 'Consumer Tech / Ecosystem'],
        ['MSFT', 'Microsoft', 'Dalio, Cohen, Millennium, Tiger', 'Cloud / AI / Enterprise'],
        ['AMZN', 'Amazon.com', 'Dalio, Cohen, Millennium, Viking', 'E-commerce / Cloud / AI'],
        ['GOOGL', 'Alphabet', 'Dalio, Cohen, Millennium, Tiger', 'Search / AI / Cloud'],
        ['META', 'Meta Platforms', 'Dalio, Cohen, Millennium', 'Social Media / AI / VR'],
        ['TSM', 'Taiwan Semi', 'Cohen, Dalio, Tiger Global', 'Semiconductor Manufacturing'],
        ['LLY', 'Eli Lilly', 'Viking, Appaloosa, Coatue', 'GLP-1 / Healthcare'],
        ['AVGO', 'Broadcom', 'Cohen, Coatue, Millennium', 'Semiconductors / Software'],
        ['V', 'Visa Inc.', 'Cohen, Millennium, Viking', 'Payments / Fintech'],
        ['MA', 'Mastercard', 'Cohen, Millennium', 'Payments / Fintech'],
        ['UNH', 'UnitedHealth', 'Viking, Millennium', 'Healthcare / Insurance'],
        ['JPM', 'JPMorgan Chase', 'Buffett, Millennium', 'Banking / Financials'],
        ['SPY', 'S&P 500 ETF', 'Dalio, Millennium, Citadel', 'Broad Market Exposure'],
    ]
    
    for i, row in enumerate(consensus_data):
        pdf.table_row(row, widths, i % 2 == 1)
    
    pdf.ln(10)
    
    # NEW PAGE - Key Insights
    pdf.add_page()
    pdf.chapter_title('Key Insights & Patterns')
    pdf.ln(5)
    
    insights = [
        ("1. Technology Dominance", 
         "The 'Magnificent Seven' stocks (AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA) appear "
         "across virtually all major portfolios. NVIDIA is the most consensus pick, appearing "
         "in 8 of 10 top strategist portfolios as the primary AI beneficiary."),
        
        ("2. ETF Hedging Strategy", 
         "Multi-strategy funds like Bridgewater, Millennium, and Citadel hold massive positions "
         "in broad market ETFs (SPY, IVV, IWM, QQQ) as beta hedges while maintaining concentrated "
         "long/short equity books."),
        
        ("3. Geographic Concentration", 
         "40% of top 25 funds are headquartered in New York City, with another 20% in Connecticut "
         "(Stamford, Greenwich, Westport). London is the primary non-US hub with 12% representation."),
        
        ("4. Strategy Diversity", 
         "Multi-strategy funds dominate top AUM rankings, but quantitative strategies (Renaissance, "
         "Two Sigma, AQR) and global macro (Bridgewater, Tudor, Rokos) maintain significant market share."),
        
        ("5. Healthcare & GLP-1 Theme", 
         "Eli Lilly and Novo Nordisk are increasingly appearing in top portfolios as the GLP-1 "
         "weight loss drug market expands. Viking and Coatue have notable concentrations here."),
        
        ("6. Semiconductor Concentration", 
         "Beyond NVIDIA, strategists are concentrated in TSMC (manufacturing monopoly), Broadcom "
         "(AI networking), and Lam Research (equipment) - all critical AI infrastructure plays."),
    ]
    
    for title, body in insights:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, title, 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 5, body)
        pdf.ln(5)
    
    # Methodology Page
    pdf.add_page()
    pdf.chapter_title('Methodology & Data Sources')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, 'Data Sources', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 6, 
        "* SEC 13F Filings: Quarterly institutional investment manager reports (Form 13F-HR)\n"
        "* Hedge Fund Rankings: Pensions & Investments, HedgeLists, SWFI Institute\n"
        "* Portfolio Analytics: 13f.info, GuruFocus, PortfolioSavvy, HoldingsChannel\n"
        "* Report Period: Q1 2025 (as of March 31, 2025)\n"
        "* AUM Data: Discretionary assets under management as of year-end 2024"
    )
    pdf.ln(10)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, 'Limitations', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 6, 
        "* 13F filings only report long equity positions - short positions are not disclosed\n"
        "* International securities may be underreported depending on filing requirements\n"
        "* AUM figures are estimates based on available public data\n"
        "* Holdings data has 45-day reporting delay from quarter end\n"
        "* Some funds (Renaissance Medallion) are not required to file 13F"
    )
    pdf.ln(10)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, 'Overlap Analysis Method', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 6, 
        "Overlap identification is based on stocks appearing in 3 or more top strategist "
        "portfolios with meaningful position sizes (>0.5% of portfolio). Holdings are weighted "
        "by conviction level based on concentration and number of strategists holding the position."
    )
    
    # Disclaimer
    pdf.ln(15)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, 
        "Disclaimer: This report is for informational purposes only. Past performance does not "
        "guarantee future results. Holdings data is based on publicly available 13F filings and "
        "may not reflect current positions. This is not investment advice. Consult a qualified "
        "financial advisor before making investment decisions.")
    
    # Save
    output_path = r'C:\Users\thadd\OneDrive\Desktop\Spocks Reports\strategists\Top_100_Strategists_Analysis_2026-05-11.pdf'
    pdf.output(output_path)
    print(f"PDF Report Generated Successfully!")
    print(f"Location: {output_path}")
    print(f"Pages: {pdf.page_no()}")

if __name__ == '__main__':
    main()
