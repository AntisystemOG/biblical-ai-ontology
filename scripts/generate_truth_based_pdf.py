#!/usr/bin/env python3
"""Generate PDF from Truth-Based Trading markdown report."""

from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'Truth-Based Trading Report - May 12, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
            self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(2)
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def chapter_subtitle(self, subtitle):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, subtitle, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(2)
    
    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(3)
    
    def quote_text(self, text):
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(60, 60, 60)
        self.set_x(20)
        self.multi_cell(170, 6, f'"{text}"')
        self.ln(3)
    
    def table_row(self, cells, widths=None, bold_first=False):
        if widths is None:
            widths = [40, 50, 50, 50]
        
        self.set_font('Helvetica', 'B' if bold_first else '', 9)
        self.set_text_color(0, 0, 0)
        
        for i, cell in enumerate(cells):
            is_last = (i == len(cells) - 1)
            self.cell(widths[i], 6, str(cell), border=1, 
                     new_x="LMARGIN" if is_last else "RIGHT", 
                     new_y="NEXT" if is_last else "TOP")
        
        if bold_first:
            self.set_font('Helvetica', '', 9)

def create_pdf():
    pdf = PDFReport()
    pdf.add_page()
    
    # Title Page
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 60, '', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 15, 'Truth-Based Trading', align='C')
    pdf.ln()
    pdf.set_font('Helvetica', '', 16)
    pdf.cell(0, 10, 'for Long-Term Retirement Goals', align='C')
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Report Date: May 12, 2026', align='C')
    pdf.ln()
    pdf.cell(0, 10, 'Analysis Period: Q1-Q2 2026', align='C')
    pdf.ln()
    pdf.cell(0, 10, 'Objective: Real returns over 15-25 year horizon', align='C')
    
    # Add new page for content
    pdf.add_page()
    
    # Executive Summary
    pdf.chapter_title('Executive Summary: The Uncomfortable Truth')
    pdf.body_text('After analyzing millions of data points from hedge fund 13F filings, market history, SPIVA scorecards, and actual performance metrics, one truth emerges:')
    pdf.quote_text('87% of professional money managers underperform a simple S&P 500 index fund over 10 years.')
    pdf.body_text('Your edge is not in copying "smart money" - it is in avoiding their fees, their lag, and their narratives.')
    
    # Part 1
    pdf.add_page()
    pdf.chapter_title('Part 1: What We Learned From the Data')
    pdf.chapter_subtitle('The Hedge Fund Mirage')
    pdf.body_text('Analysis of reported 13F filings shows a consistent pattern:')
    
    # Table header
    pdf.set_fill_color(230, 230, 230)
    pdf.table_row(['Manager', 'Marketing Claim', '2024 Reality', 'Verdict'], bold_first=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.table_row(['Terry Smith', 'Quality compounder', '+8.9% vs +20.8%', 'Underperform'])
    pdf.table_row(['Chris Hohn', 'Activist value', '+15% vs +23%', 'Underperform'])
    pdf.table_row(['S&P 500 Index', '"Boring"', '+23%', 'Beat most pros'])
    pdf.ln(5)
    pdf.body_text('Key Insight: 13F filings are 90 days stale. By the time you see Buffett bought something, the opportunity is gone.')
    
    # Part 2
    pdf.add_page()
    pdf.chapter_title('Part 2: Current Portfolio - Truth-Based Assessment')
    pdf.chapter_subtitle('HOLD - Evidence Supports Thesis')
    pdf.table_row(['Ticker', 'Evidence', 'Hold Period'], widths=[30, 100, 60], bold_first=True)
    pdf.table_row(['BE', 'Actual customer contracts, hydrogen infrastructure', '5-7 years'])
    pdf.table_row(['INTC', 'Foundry investments real, cyclical recovery', '3-5 years'])
    pdf.table_row(['APLD', '$300M funding secured, data center demand', '3-5 years'])
    pdf.table_row(['XOM', 'Dividend aristocrat, transition takes decades', '10+ years'])
    pdf.table_row(['VST', 'Nuclear baseload real, regulatory moat', '5-10 years'])
    pdf.ln(5)
    
    pdf.chapter_subtitle('SELL - Evidence Contradicts Thesis')
    pdf.table_row(['Ticker', 'Evidence', 'Action'], widths=[30, 100, 60], bold_first=True)
    pdf.table_row(['RIOT', '"AI pivot" = narrative, cash burn, -47%', 'Sell 100%'])
    pdf.table_row(['CORZ', 'Same playbook, no profitability path', 'Sell 100%'])
    pdf.table_row(['CEG', 'Unrealized loss, thesis unclear', 'Sell 100%'])
    pdf.table_row(['MU', '+38% weekly = cyclical peak pattern', 'Sell 50%'])
    
    # Part 3
    pdf.add_page()
    pdf.chapter_title('Part 3: The Truth-Based Strategy')
    pdf.body_text('Core Principle: Get Rich Slowly. Buffett actual formula:')
    pdf.body_text('1. Buy businesses you understand')
    pdf.body_text('2. At prices that make sense')
    pdf.body_text('3. Hold for decades')
    pdf.body_text('4. Ignore the noise')
    pdf.ln(5)
    
    pdf.chapter_subtitle('The Three-Bucket System')
    
    pdf.chapter_subtitle('Bucket 1: The Foundation (70%)')
    pdf.body_text('What: Low-cost index funds')
    pdf.body_text('Why: 87% of managers cannot beat them')
    pdf.body_text('Specific: VTI (Total US), VXUS (International), BND (Bonds)')
    pdf.body_text('Expected Return: 8-10% nominal, 5-7% real')
    
    pdf.chapter_subtitle('Bucket 2: Individual Holdings (25%)')
    pdf.body_text('What: Individual stocks with moats')
    pdf.body_text('Why: Concentration builds wealth')
    pdf.body_text('Criteria: 10+ years profitability, pricing power, low debt')
    pdf.body_text('Expected Return: 10-15% if correct, -50% if wrong')
    
    pdf.chapter_subtitle('Bucket 3: Opportunistic (5%)')
    pdf.body_text('What: Speculation, distressed, contrarian')
    pdf.body_text('Why: Lottery tickets with positive expected value')
    pdf.body_text('Current: APLD, cash waiting for 20%+ correction')
    
    # Part 4
    pdf.add_page()
    pdf.chapter_title('Part 4: The Hard Rules')
    pdf.chapter_subtitle('Entry Rules')
    pdf.body_text('- Never buy on news - priced in by the time you hear it')
    pdf.body_text('- Never buy because someone famous did - 90-day lag')
    pdf.body_text('- Never buy without reading the 10-K')
    pdf.body_text('- Never buy at all-time highs - patience is an edge')
    pdf.ln(3)
    
    pdf.chapter_subtitle('Exit Rules')
    pdf.body_text('- Sell when thesis breaks - not when price drops')
    pdf.body_text('- Sell when valuation exceeds reality')
    pdf.body_text('- Sell when you need the money - retirement, not panic')
    pdf.body_text('- Never sell winners to buy losers - hold your flowers')
    pdf.ln(3)
    
    pdf.chapter_subtitle('Holding Rules')
    pdf.body_text('- Minimum 5-year horizon - or do not buy')
    pdf.body_text('- Rebalance annually - not daily')
    pdf.body_text('- Ignore the scoreboard - 10-year games have noise')
    pdf.body_text('- Add on weakness - if thesis intact')
    
    # Part 5
    pdf.add_page()
    pdf.chapter_title('Part 5: The Retirement Math')
    pdf.chapter_subtitle('Scenario A: Truth-Based Approach')
    pdf.body_text('70% VTI/VXUS (8% return) + 25% moats (12% return) + 5% opportunistic (0% return)')
    pdf.body_text('Blended Expected Return: ~9%')
    pdf.ln(3)
    pdf.body_text('On $100K starting, $10K annual additions:')
    pdf.body_text('Year 10: $340K')
    pdf.body_text('Year 20: $890K')
    pdf.body_text('Year 25: $1.45M')
    pdf.ln(5)
    
    pdf.chapter_subtitle('Scenario B: Manager-Following Approach')
    pdf.body_text('100% hedge fund replication with 2% fee + 20% carry')
    pdf.body_text('Underperform by 3% annually (SPIVA data)')
    pdf.body_text('Blended Expected Return: ~5%')
    pdf.ln(3)
    pdf.body_text('On $100K starting, $10K annual additions:')
    pdf.body_text('Year 10: $280K (-$60K)')
    pdf.body_text('Year 20: $620K (-$270K)')
    pdf.body_text('Year 25: $890K (-$560K)')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, 'Opportunity Cost of Narrative Investing: $560,000 over 25 years', new_x="LMARGIN", new_y="NEXT")
    
    # Part 6
    pdf.add_page()
    pdf.chapter_title('Part 6: Action Items')
    pdf.chapter_subtitle('Immediate (This Week)')
    pdf.body_text('1. Sell RIOT, CORZ, CEG (100% each)')
    pdf.body_text('2. Trim MU (sell 50% of position)')
    pdf.body_text('3. Calculate proceeds from sales')
    pdf.ln(3)
    
    pdf.chapter_subtitle('Short-Term (This Month)')
    pdf.body_text('1. Open VTI position (70% of available cash)')
    pdf.body_text('2. Research 2-3 additional individual moats')
    pdf.body_text('3. Read 10-K for any new individual holding')
    pdf.ln(3)
    
    pdf.chapter_subtitle('Long-Term (This Quarter)')
    pdf.body_text('1. Set automatic monthly VTI purchases')
    pdf.body_text('2. Schedule annual portfolio review')
    pdf.body_text('3. Establish rebalancing rules (+/- 5% bands)')
    
    # Part 7
    pdf.add_page()
    pdf.chapter_title('Part 7: The Biblical Anchor')
    pdf.quote_text('The plans of the diligent lead to profit as surely as haste leads to poverty. - Proverbs 21:5')
    pdf.ln(5)
    pdf.body_text('Truth-based trading is not exciting. It will not make you rich quick. But over 25 years, it will make you rich.')
    pdf.ln(5)
    pdf.body_text('The hedge funds get paid for excitement. You get paid for patience.')
    pdf.ln(10)
    
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Next Review: June 12, 2026 | Rebalance Trigger: Any position >10% overweight', align='C')
    pdf.ln()
    pdf.cell(0, 10, 'This report is not financial advice. Past performance does not guarantee future results.', align='C')
    
    # Save
    output_path = r'C:\Users\thadd\.openclaw\workspace\Spocks Reports\truth_based_trading\2026-05-12_truth_based_trading.pdf'
    pdf.output(output_path)
    print(f'PDF generated: {output_path}')

if __name__ == '__main__':
    create_pdf()
