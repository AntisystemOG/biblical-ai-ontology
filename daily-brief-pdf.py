from fpdf import FPDF
import fpdf
fpdf.set_global("FPDF_FONT_DIR", "C:\\Windows\\Fonts")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Daily Brief - May 8, 2026', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

pdf = PDF()
pdf.add_page()
pdf.set_font('Arial', '', 11)

lines = [
    'Good Morning, Thad.',
    '',
    'Compiled: Friday, May 8, 2026 - 8:00 AM CDT',
    '',
    'EXECUTIVE SUMMARY',
    '',
    'Markets opened higher this morning following a stronger-than-expected April jobs report.',
    'Nasdaq 100 futures lead gains at +0.6%, while S&P 500 futures rose 0.4%.',
    '',
    'MARKET OUTLOOK',
    '',
    'Index:              Futures Change',
    '--------------------------------',
    'Nasdaq 100          +0.6%',
    "S&P 500             +0.4%",
    'Dow Jones           +0.23%',
    '',
    'Yesterday: S&P 500 and Nasdaq hit fresh record highs.',
    '',
    'APRIL JOBS REPORT (Released 8:30 AM ET)',
    '',
    '- Nonfarm Payrolls: +115,000 jobs (beat consensus of 55,000)',
    '- Unemployment Rate: 4.3% (unchanged)',
    '- Assessment: Labor market remains resilient',
    '',
    'GEOPOLITICAL: US-IRAN',
    '',
    '- Iran reviewing US proposals via Pakistani mediators',
    '- Trump: "War will end soon"',
    '- Brent crude below $98/barrel on deal optimism',
    '',
    'EARNINGS (May 7)',
    '',
    '- Olin Corp (OLN): Q1 net loss ($0.73)/share',
    '- Viatris (VTRS): Q1 revenues $3.5B',
    '- Wynn Resorts (WYNN): Q1 results reported',
    '- Vistra Energy (VST): Q1 GAAP Net Income $1,029M',
    '- ACM Research (ACMR): Beat EPS estimates',
    '',
    'KEY THEMES TO WATCH',
    '',
    '1. Labor Market Resilience - Economy is not cracking',
    '2. Geopolitical Risk - Iran deal could ease oil prices',
    '3. Earnings Season - Corporate guidance shapes Q2 expectations',
    '',
    'Stay sharp. The market rewards preparation.',
    '',
    '- Spock'
]

for line in lines:
    if line.isupper() and len(line) > 5 and not line.startswith('-'):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, line, 0, 1)
        pdf.set_font('Arial', '', 11)
    else:
        pdf.multi_cell(0, 6, line)

output_path = r'C:\Users\thadd\OneDrive\Desktop\Spocks Reports\Daily Brief - May 8 2026.pdf'
pdf.output(output_path)
print(f'PDF saved to: {output_path}')
print('PDF generated successfully!')
