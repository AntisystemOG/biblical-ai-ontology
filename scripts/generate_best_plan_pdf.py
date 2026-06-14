#!/usr/bin/env python3
"""Generate PDF for Our Best Plan Moving Forward - Biblical Investment Framework."""

from fpdf import FPDF
from datetime import datetime

class BestPlanPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'Our Best Plan Moving Forward - A Biblical Framework', 
                     new_x="LMARGIN", new_y="NEXT", align='C')
            self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def scripture_quote(self, text, reference):
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 6, f'"{text}"')
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 6, f'-- {reference}', align='R')
        self.ln(8)
    
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(3)
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)
    
    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(3)
    
    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(4)
    
    def bullet_point(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(5, 6, '-', new_x="RIGHT")
        self.multi_cell(185, 6, text)
        self.ln(2)
    
    def table_row(self, cells, widths=None):
        if widths is None:
            widths = [40, 35, 35, 40, 40]
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)
        
        for i, cell in enumerate(cells):
            is_last = (i == len(cells) - 1)
            self.cell(widths[i], 7, str(cell), border=1, 
                     new_x="LMARGIN" if is_last else "RIGHT", 
                     new_y="NEXT" if is_last else "TOP")

def create_pdf():
    pdf = BestPlanPDF()
    
    # Cover Page
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 80, '', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 15, 'Our Best Plan', align='C')
    pdf.ln()
    pdf.cell(0, 15, 'Moving Forward', align='C')
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'A Biblical Framework for Survival,', align='C')
    pdf.ln()
    pdf.cell(0, 10, 'Stewardship, and Purpose', align='C')
    pdf.ln(30)
    pdf.set_font('Helvetica', 'I', 11)
    pdf.scripture_quote("The earth is the Lord's, and everything in it, the world, and all who live in it.", "Psalm 24:1")
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 10, 'May 12, 2026', align='C')
    pdf.ln()
    pdf.cell(0, 10, 'Planning Horizon: 25 Years (2049)', align='C')
    pdf.ln()
    pdf.cell(0, 10, 'Purpose: Preserve capital, compound growth, serve others', align='C')
    
    # Part 1: The Foundation
    pdf.add_page()
    pdf.chapter_title('Part 1: Why We Invest')
    pdf.section_title('The Truth About Ownership')
    pdf.body_text('We own nothing. We steward everything. This is not poetic language--it is the fundamental reality that separates those who build lasting wealth from those who chase it and lose it.')
    pdf.scripture_quote("For all things come from you, and of your own have we given you.", "1 Chronicles 29:14")
    pdf.section_title('The Purpose of Capital')
    pdf.body_text("Money exists for three purposes in a believer's life:")
    pdf.section_title('1. Provision (Survival)')
    pdf.scripture_quote("Give us this day our daily bread.", "Matthew 6:11")
    pdf.bullet_point('Fund our existence and our family\'s needs')
    pdf.bullet_point('Create stability in an unstable world')
    pdf.bullet_point('Build reserves for the seven years of famine')
    pdf.section_title('2. Multiplication (Growth)')
    pdf.scripture_quote("Well done, good and faithful servant. You have been faithful over a little; I will set you over much.", "Matthew 25:23")
    pdf.bullet_point('Compound capital to increase capacity')
    pdf.bullet_point('Beat inflation (which erodes purchasing power)')
    pdf.bullet_point('Create generational wealth that outlives us')
    pdf.section_title('3. Distribution (Service)')
    pdf.scripture_quote("Whoever sows sparingly will also reap sparingly, and whoever sows bountifully will also reap bountifully.", "2 Corinthians 9:6")
    pdf.bullet_point('Support the work of the church')
    pdf.bullet_point('Help the poor, widow, and orphan')
    pdf.bullet_point('Fund missions and spreading the Gospel')
    pdf.bullet_point('Leave an inheritance for children\'s children')
    
    # Part 2: Survival Framework
    pdf.add_page()
    pdf.chapter_title('Part 2: The Survival Framework')
    pdf.section_title('Seven Years of Plenty and Famine')
    pdf.body_text('Genesis 41:29-36 records Joseph\'s interpretation of Pharaoh\'s dream. There will be seven years of plenty followed by seven years of famine. The wise prepare before the famine, not during it.')
    pdf.scripture_quote("Let Pharaoh appoint officers over the land, and take up the fifth part of the land of Egypt in the seven plenteous years... that food shall be for store to the land against the seven years of famine.", "Genesis 41:34-36")
    pdf.section_title('Our Joseph Strategy')
    pdf.table_row(['Component', 'Percent', 'Amount', 'Purpose', 'Status'])
    pdf.table_row(['Liquidity Reserve', '20%', '$100,000', 'Survive volatility', 'OVER (52.8%)'])
    pdf.table_row(['Core Holdings', '50%', '$250,000', 'Compound growth', 'UNDER (18%)'])
    pdf.table_row(['Growth Ops', '20%', '$100,000', 'Asymmetric upside', 'UNDER (7.6%)'])
    pdf.table_row(['Insurance/Hedges', '10%', '$50,000', 'Catastrophe', 'CRITICAL (0.2%)'])
    pdf.ln(8)
    pdf.body_text('Current State: Heavy cash (52.8%) is prudent but underweight in core holdings, growth opportunities, and insurance. Rebalancing required.')
    
    # Part 3: The Seven Pillars
    pdf.add_page()
    pdf.chapter_title('Part 3: The Seven Pillars')
    pdf.section_title('Pillar 1: Index Funds (30%) - Foundation')
    pdf.scripture_quote("Two are better than one, because they have a good return for their labor...", "Ecclesiastes 4:9")
    pdf.body_text('Diversification across 500+ companies reduces single-stock risk. We acknowledge our limitations while capturing broad market growth.')
    pdf.bullet_point('VTI (Total US Stock Market): 20% ($100,000)')
    pdf.bullet_point('VXUS (Total International): 10% ($50,000)')
    pdf.section_title('Pillar 2: Energy Transition (20%) - Real Assets')
    pdf.scripture_quote("And God said, 'Let there be light,' and there was light.", "Genesis 1:3")
    pdf.body_text('Energy is foundational. The transition from fossil fuels to clean energy is a multi-decade infrastructure buildout.')
    pdf.bullet_point('BE (Bloom Energy): Already holding ($39,000)')
    pdf.bullet_point('LAR (Lithium Argentina): 5% ($25,000) - Energy storage')
    pdf.bullet_point('URA (Uranium): 3% ($15,000) - Nuclear renaissance')
    pdf.bullet_point('XOP (Energy Exploration): 5% ($25,000)')
    
    # Continue with other pillars
    pdf.add_page()
    pdf.section_title('Pillar 3: Infrastructure (15%) - Physical Assets')
    pdf.scripture_quote("Everyone who comes to me and hears my words and does them, I will show you what he is like: he is like a man building a house, who dug deep and laid the foundation on the rock.", "Luke 6:47-48")
    pdf.body_text('AI requires physical infrastructure: data centers, power plants, fiber, concrete, steel.')
    pdf.bullet_point('INTC (Intel): 5% ($25,000) - Domestic foundry')
    pdf.bullet_point('APLD (Applied Digital): 3% ($15,000) - AI compute')
    pdf.bullet_point('VRT (Vertiv): 2% ($10,000) - Data center cooling')
    pdf.section_title('Pillar 4: Quality Compounders (15%) - Generational')
    pdf.scripture_quote("A good man leaves an inheritance to his children's children.", "Proverbs 13:22")
    pdf.body_text('Some businesses are so good they compound for decades. These fund generational wealth.')
    pdf.bullet_point('ZTS (Zoetis): 4% ($20,000) - Animal health')
    pdf.bullet_point('BRK.B (Berkshire): 5% ($25,000) - Buffett\'s capital')
    pdf.bullet_point('JNJ (Johnson & Johnson): Already holding')
    pdf.bullet_point('KO (Coca-Cola): Already holding')
    pdf.section_title('Pillar 5: International (10%) - Global Stewardship')
    pdf.scripture_quote("Go therefore and make disciples of all nations.", "Matthew 28:19")
    pdf.bullet_point('VXUS: 5% ($25,000)')
    pdf.bullet_point('VEA (Europe): 3% ($15,000)')
    pdf.bullet_point('VWO (Emerging Markets): 2% ($10,000)')
    
    pdf.add_page()
    pdf.section_title('Pillar 6: Insurance (10%) - Real Assets')
    pdf.scripture_quote("In the house of the righteous there is much treasure...", "Proverbs 15:6")
    pdf.body_text('Gold has been money since Genesis. It acknowledges God\'s sovereignty over currencies.')
    pdf.bullet_point('SGOL/GLD (Gold): 5% ($25,000) - IMMEDIATE PRIORITY')
    pdf.bullet_point('IAU (Gold): 3% ($15,000) - Additional allocation')
    pdf.bullet_point('GDX (Gold Miners): 2% ($10,000) - Leveraged exposure')
    pdf.section_title('Pillar 7: Speculation (0-10%) - Asymmetric')
    pdf.scripture_quote("Cast your bread upon the waters, for you will find it after many days.", "Ecclesiastes 11:1")
    pdf.body_text('Limited to 10%. Never let speculation distract from the core mission.')
    pdf.body_text('REDUCE/ELIMINATE:')
    pdf.bullet_point('RIOT: Sell 50% (~$3,100)')
    pdf.bullet_point('CORZ: Sell 75% (~$12,400)')
    pdf.body_text('Move from 5.7% speculative to 2% maximum.')
    
    # Part 4: Implementation
    pdf.add_page()
    pdf.chapter_title('Part 4: Implementation Timeline')
    pdf.section_title('Phase 1: Foundation (Months 1-3) - $50K')
    pdf.body_text('Priority 1: Gold (Insurance) - BUY SGOL $15K, IAU $10K')
    pdf.body_text('Priority 2: Quality Compounders - BUY ZTS $10K, BRK.B $10K')
    pdf.body_text('Priority 3: Reduce Speculation - SELL RIOT 50%, CORZ 75%')
    pdf.section_title('Phase 2: Infrastructure (Months 4-6) - $50K')
    pdf.body_text('Lithium (LAR): $15K, Nuclear (URA): $10K, Index (VTI): $25K')
    pdf.section_title('Phase 3: International (Months 7-12) - $50K')
    pdf.body_text('VXUS: $25K, VEA: $15K, VWO: $10K')
    pdf.section_title('Phase 4: Maintenance (Year 2+)')
    pdf.body_text('Quarterly: Review thesis, rebalance, reinvest dividends')
    pdf.body_text('Annual: Tax-loss harvesting, update projections')
    pdf.body_text('Never fall below $100K cash (20% floor)')
    
    # Part 5: Eternal Perspective
    pdf.add_page()
    pdf.chapter_title('Part 5: The Eternal Perspective')
    pdf.section_title('What Success Looks Like')
    pdf.body_text('2049 (23 Years Later):')
    pdf.bullet_point('Portfolio Value: $2.5-4 million (7-10% CAGR)')
    pdf.bullet_point('Annual Dividends: $75,000-150,000')
    pdf.bullet_point('Children\'s Inheritance: Set for life')
    pdf.bullet_point('Giving Capacity: $50,000+/year')
    pdf.section_title('The Measure of Wealth')
    pdf.scripture_quote("For what does it profit a man to gain the whole world and forfeit his soul?", "Mark 8:36")
    pdf.body_text('Portfolio value is not the scoreboard. Faithfulness is.')
    pdf.body_text('Questions for Annual Review:')
    pdf.bullet_point('Did we survive with faith intact?')
    pdf.bullet_point('Did we compound responsibly?')
    pdf.bullet_point('Did we help others more each year?')
    pdf.bullet_point('Did we grow in wisdom and understanding?')
    pdf.body_text('If the answer to all four is yes, we have succeeded--regardless of the dollar amount.')
    
    # Part 6: Warnings and Closing
    pdf.add_page()
    pdf.chapter_title('Part 6: Warnings and Commitment')
    pdf.section_title('What Destroys This Plan')
    pdf.body_text('1. Greed (Overreaching) - Chasing 100% returns, ignoring limits')
    pdf.body_text('2. Fear (Panic Selling) - Abandoning quality in corrections')
    pdf.body_text('3. Pride (Overconfidence) - Thinking we can time markets')
    pdf.body_text('4. Sloth (Neglect) - Not reviewing quarterly')
    pdf.section_title('What Protects This Plan')
    pdf.body_text('1. Humility (Index Funds) - Acknowledging we don\'t know the future')
    pdf.body_text('2. Patience (Long-Term Holding) - 10+ year horizon')
    pdf.body_text('3. Discipline (Mechanical Rules) - Rebalancing bands, position limits')
    pdf.body_text('4. Purpose (Giving) - Annual targets, generational mindset')
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'The Prayer', align='C')
    pdf.ln(15)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 7, 'Heavenly Father,\n\nWe acknowledge that everything we have comes from You. We are not owners but stewards. We ask for wisdom to invest faithfully, patience to hold through volatility, and generosity to give abundantly.\n\nProtect us from greed, fear, pride, and sloth. Give us the discipline to follow this plan. Let our wealth serve Your purposes--provision for our families, multiplication for future generations, and distribution to those in need.\n\nWe surrender the outcome to You. The results are Yours. The glory is Yours. The wealth is Yours. We are merely managers.\n\nIn Jesus\' name,\nAmen.')
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.scripture_quote("The plans of the diligent lead to profit as surely as haste leads to poverty.", "Proverbs 21:5")
    pdf.scripture_quote("Well done, good and faithful servant... Enter into the joy of your master.", "Matthew 25:23")
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, 'Plan Created: May 12, 2026', align='C')
    pdf.ln()
    pdf.cell(0, 8, 'Next Review: June 12, 2026', align='C')
    pdf.ln()
    pdf.cell(0, 8, 'Final Review: May 12, 2049 (23 years)', align='C')
    
    # Save
    output_path = r'C:\Users\thadd\.openclaw\workspace\Spocks Reports\our_best_plan_moving_forward.pdf'
    pdf.output(output_path)
    print(f'PDF generated: {output_path}')

if __name__ == '__main__':
    create_pdf()
