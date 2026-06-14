#!/usr/bin/env python3
"""Generate Daily Brief PDF"""

from fpdf import FPDF
from datetime import datetime
import re

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(45, 55, 72)
        self.cell(0, 10, 'Daily Brief - Ground News Cross-Spectrum Analysis', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'May 14, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def clean_text(text):
    """Clean text for PDF - ASCII only"""
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    # Remove HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    # Replace em-dash and other unicode with ascii
    text = text.replace('\u2014', '-')  # em-dash
    text = text.replace('\u2013', '-')  # en-dash
    text = text.replace('\u2018', "'")  # left single quote
    text = text.replace('\u2019', "'")  # right single quote
    text = text.replace('\u201C', '"')  # left double quote
    text = text.replace('\u201D', '"')  # right double quote
    text = text.replace('\u2022', '*')  # bullet
    text = text.replace('\u2026', '...')  # ellipsis
    text = text.replace('\u2190', '<-')  # left arrow
    text = text.replace('\u2192', '->')  # right arrow
    return text

def add_section_title(pdf, title, level=1):
    """Add section title"""
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
    """Add paragraph text"""
    pdf.set_font('Helvetica', '', 10)
    if indent:
        pdf.set_x(20)
    else:
        pdf.set_x(10)
    # Split long text
    text = clean_text(text)
    pdf.multi_cell(190, 5, text)
    pdf.ln(2)

def add_bullet(pdf, text):
    """Add bullet point"""
    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(15)
    pdf.cell(5, 5, '*', new_x="RIGHT")
    text = clean_text(text)
    pdf.multi_cell(175, 5, text)

def add_highlight(pdf, label, text, color_type='neutral'):
    """Add a highlighted fact box"""
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
    pdf.cell(0, 10, 'May 14, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 12)
    pdf.cell(0, 8, 'Ground News Cross-Spectrum Analysis', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Portfolio Holdings \u0026 Market Intelligence', new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.add_page()

    # Market Overview
    add_section_title(pdf, 'Market Overview', 1)
    add_highlight(pdf, 'Market Status', 'S\u0026P 500 and Nasdaq futures rising, Dow reclaimed 50,000')
    add_highlight(pdf, 'CPI Inflation', '3.8% annually (highest since May 2023)', 'bearish')
    add_highlight(pdf, 'Bitcoin ETFs', '$630M outflow - largest since January', 'bearish')
    add_paragraph(pdf, 'Key themes: AI infrastructure boom continues, energy prices elevated due to Iran conflict, Fed policy uncertainty persists.')

    # Major Story
    pdf.add_page()
    add_section_title(pdf, 'Major Story: CPI Inflation Surges to 3.8%', 1)
    add_section_title(pdf, 'Bias Spectrum', 2)
    add_paragraph(pdf, 'Left (CNN) - Center (Reuters/BLS) - Right (Fox/WSJ)')

    add_section_title(pdf, 'Where They Agree (Convergent Facts)', 2)
    add_bullet(pdf, 'CPI rose 3.8% year-over-year in April 2026 (up from 3.3% in March)')
    add_bullet(pdf, 'Monthly increase: 0.6% (seasonally adjusted)')
    add_bullet(pdf, 'Core CPI (excluding food and energy): 2.8% annually')
    add_bullet(pdf, 'Energy costs drove increase due to Iran conflict')
    add_bullet(pdf, 'Highest inflation rate since May 2023')
    pdf.ln(3)

    add_section_title(pdf, 'Where They Differ', 2)
    add_paragraph(pdf, 'LEFT SOURCES: Focus on eroding paychecks, cost-of-living pressures, wage stagnation.')
    add_paragraph(pdf, 'CENTER SOURCES: Fact-based reporting on components, technical analysis, Fed policy presented neutrally.')
    add_paragraph(pdf, 'RIGHT SOURCES: Emphasis on negative real rates, criticism of sustained inflation.')

    add_section_title(pdf, 'Likely Reality', 2)
    add_paragraph(pdf, 'The 3.8% CPI reading is genuinely concerning and driven primarily by energy costs from geopolitical conflict. The Fed faces a dilemma: inflation is above target, but hiking rates further risks recession.')
    add_highlight(pdf, 'Implication', 'NEUTRAL-BEARISH - Rate cut expectations pushed back', 'bearish')

    # Portfolio News
    pdf.add_page()
    add_section_title(pdf, 'Portfolio News Analysis', 1)

    # INTC
    add_section_title(pdf, 'INTC - Intel Corp', 2)
    add_highlight(pdf, 'Current Price', '$113.61 | Daily: -$6.68 (-5.55%)', 'bearish')
    add_paragraph(pdf, 'Intel experiencing significant volatility. Faces ongoing challenges in semiconductor landscape against NVIDIA and AMD dominance in AI chips.')
    add_paragraph(pdf, 'Left sources focus on turnaround struggles. Center sources report on earnings. Right sources emphasize competition from AMD/NVIDIA.')
    add_highlight(pdf, 'Implication', 'BEARISH short-term', 'bearish')

    # BE
    add_section_title(pdf, 'BE - Bloom Energy', 2)
    add_highlight(pdf, 'Current Price', '$284.03 | Daily: -$5.73 (-1.98%)', 'neutral')
    add_paragraph(pdf, 'Bloom Energy has been a standout performer with stock surging over 1,500% from lows. Recent developments:')
    add_bullet(pdf, 'Record Q1 2026 results reported')
    add_bullet(pdf, 'Full-year revenue outlook raised')
    add_bullet(pdf, 'Major Oracle fuel cell deal for AI data centers secured')
    add_bullet(pdf, 'Benefits from AI power demand narrative')
    add_paragraph(pdf, 'Left sources highlight environmental angle. Center sources focus on business fundamentals. Right sources emphasize market opportunity.')
    add_highlight(pdf, 'Implication', 'BULLISH - AI infrastructure tailwinds', 'bullish')

    pdf.add_page()

    # FBTC
    add_section_title(pdf, 'FBTC - Fidelity Bitcoin Fund', 2)
    add_highlight(pdf, 'Current Price', '$69.57 | Daily: +$0.27 (+0.38%)', 'neutral')
    add_paragraph(pdf, 'Bitcoin/Crypto Sector Summary:')
    add_bullet(pdf, 'Bitcoin ETFs saw $630M outflows yesterday (largest since January)')
    add_bullet(pdf, 'Bitcoin price around $80,000, facing headwinds')
    add_bullet(pdf, 'Senate Banking Committee considering crypto legislation')
    add_bullet(pdf, 'CME Group launching Nasdaq crypto index futures')
    add_paragraph(pdf, 'ETF outflows indicate institutional profit-taking. $80K level proving to be resistance. Macro environment pressuring crypto.')
    add_highlight(pdf, 'Implication', 'NEUTRAL - Choppy conditions', 'neutral')

    # Crypto Miners
    add_section_title(pdf, 'Crypto Mining Holdings', 2)
    add_paragraph(pdf, 'HUT, RIOT, CORZ, CLSK, CIFR - Sector pivoting to AI infrastructure')
    add_paragraph(pdf, 'Key Developments:')
    add_bullet(pdf, 'Hut 8 (HUT): $9.8B, 15-year AI data center lease; stock surged 35%')
    add_bullet(pdf, 'CleanSpark (CLSK): Doubled MW under contract YoY')
    add_bullet(pdf, 'Core Scientific (CORZ): AMD exercise of option for additional 25 MW')
    add_bullet(pdf, 'Riot Platforms (RIOT): Q1 revenue $167.2M, data center revenue $33.2M')
    add_paragraph(pdf, 'AI data center demand driving infrastructure valuations. Hut 8 deal is transformational.')
    add_highlight(pdf, 'Implication', 'BULLISH - AI narrative tailwinds', 'bullish')

    pdf.add_page()

    # Energy Holdings
    add_section_title(pdf, 'Energy Holdings', 2)
    add_paragraph(pdf, 'VDE (Vanguard Energy ETF): $163.86 | +$0.25 (+0.15%)')
    add_paragraph(pdf, 'XOP (Oil \u0026 Gas Exploration): $167.96 | -$0.38 (-0.23%)')
    add_paragraph(pdf, 'Sector Summary: Energy prices elevated due to Iran conflict. XOP outperformed VDE over past 3 months (+27.66% vs +15.45%).')
    add_highlight(pdf, 'Implication', 'BULLISH - Geopolitical tailwinds', 'bullish')

    # Tech Holdings
    add_section_title(pdf, 'Tech Holdings Summary', 2)
    add_bullet(pdf, 'NVIDIA (NVDA): $231.48 | +5.65% - Rebounding on AI optimism')
    add_bullet(pdf, 'Micron (MU): $786.66 | -2.12% - Memory sector pressure')
    add_bullet(pdf, 'Tesla (TSLA): $444.05 | -0.27% - EV demand questions')
    add_bullet(pdf, 'Alphabet (GOOGL): $398.55 | -1.02% - Search/AI competition')
    add_bullet(pdf, 'Amazon (AMZN): $269.83 | -0.04% - Stable, cloud growth')
    add_highlight(pdf, 'Implication', 'MIXED - NVDA leading, others mixed', 'neutral')

    pdf.add_page()

    # Blindspot Report
    add_section_title(pdf, 'Blindspot Report', 1)
    add_paragraph(pdf, 'Stories Underreported by One Side:')
    add_bullet(pdf, 'Fed Real Rate Calculation: Right sources highlight negative real rates; left sources rarely mention')
    add_bullet(pdf, 'Crypto Miner AI Pivot: Center sources covering extensively; left sources focus on environmental concerns')
    add_bullet(pdf, 'Energy Transition Pace: Left pushing transition; center/right emphasizing energy security')
    add_bullet(pdf, 'Intel Foundry Strategy: Limited cross-spectrum coverage vs TSMC dominance')

    pdf.ln(10)

    # Pre-Market Outlook
    add_section_title(pdf, 'Pre-Market Outlook', 1)
    add_highlight(pdf, 'Overall Sentiment', 'CAUTIOUSLY BULLISH with INFLATION HEADWINDS', 'neutral')

    add_section_title(pdf, 'Key Factors', 2)
    add_paragraph(pdf, 'POSITIVE: AI infrastructure boom, Tech rebound, Energy sector strength')
    add_paragraph(pdf, 'NEGATIVE: Elevated inflation (3.8%), Fed policy uncertainty, Bitcoin ETF outflows')

    add_section_title(pdf, 'Portfolio Positioning Notes', 2)
    add_bullet(pdf, 'Bloom Energy (BE) has become top performer - consider trimming')
    add_bullet(pdf, 'Crypto miners benefitting from AI pivot - monitor Bitcoin correlation')
    add_bullet(pdf, 'Intel (INTC) showing weakness - reassess thesis')
    add_bullet(pdf, 'Energy holdings (VDE, XOP) well-positioned for inflation')
    add_bullet(pdf, 'Bitcoin exposure via FBTC facing near-term headwinds')

    add_section_title(pdf, 'Risk Management', 2)
    add_bullet(pdf, 'Inflation could force Fed to hold rates higher for longer')
    add_bullet(pdf, 'Geopolitical risks (Iran) could spike energy prices')
    add_bullet(pdf, 'AI bubble concerns could pressure high-flyers')

    # Footer page
    pdf.add_page()
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(128, 128, 128)
    pdf.ln(20)
    pdf.cell(0, 8, 'Report generated: May 14, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Data source: Portfolio Positions CSV (May 14, 2026 9:48 AM ET)', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Methodology: Ground News cross-spectrum analysis', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 9)
    pdf.multi_cell(0, 5, 'Disclaimer: This report is for informational purposes only and does not constitute financial advice. Past performance does not guarantee future results.')

    # Save
    output_path = 'C:\\Users\\thadd\\.openclaw\\workspace\\Spocks Reports\\daily-brief\\2026-05-14_daily_brief.pdf'
    pdf.output(output_path)
    print(f'PDF generated: {output_path}')

if __name__ == '__main__':
    main()
