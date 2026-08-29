#!/usr/bin/env python3
"""Generate Daily Brief PDF from markdown - August 29, 2026"""
import re, sys
from fpdf import FPDF

MD = r"C:\Users\thadd\.openclaw\workspace\Spocks Reports\daily-brief\2026-08-29_daily-brief.md"
OUT = r"C:\Users\thadd\.openclaw\workspace\Spocks Reports\daily-brief\2026-08-29_daily-brief.pdf"

class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(45, 55, 72)
        self.cell(0, 8, 'Daily Brief - Saturday, August 29, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def clean(text):
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = text.replace('**', '').replace('&nbsp;', ' ')
    for a, b in [('\u2212','-'),('\u2248','~'),('\u2014',' - '),('\u2013','-'),('\u2018',"'"),('\u2019',"'"),('\u201C','"'),('\u201D','"'),('\u2022','*'),('\u2026','...'),('\u2192','->'),('\u2265','>='),('\u2264','<='),('\u00d7','x'),('\u00a0',' ')]:
        text = text.replace(a, b)
    # final fallback: replace anything outside latin-1
    text = text.encode('latin-1', 'replace').decode('latin-1')
    return text

def rich_cell(pdf, text, w):
    """Render text with **bold** segments inside a multi_cell."""
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    styles = []
    for p in parts:
        if p.startswith('**') and p.endswith('**') and len(p) > 4:
            styles.append((p[2:-2], True))
        elif p != '':
            styles.append((p, False))
    # fpdf2 multi_cell doesn't support mixed styles; render line by line approximation:
    # simulate with markdown=False and just strip bold markers, bold whole first token if it starts bold
    pdf.multi_cell(w, 5, clean(text))

def main():
    with open(MD, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title block
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(45, 55, 72)
    pdf.ln(30)
    pdf.cell(0, 15, 'DAILY BRIEF', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Saturday, August 29, 2026', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(6)
    pdf.set_font('Helvetica', 'I', 12)
    pdf.cell(0, 8, 'Ground News Cross-Spectrum Analysis', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Markets - Fed Pivot Risk - Portfolio Intelligence', new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(12)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(160, 60, 60)
    pdf.multi_cell(190, 6, 'HIGHLIGHTS: Warsh put a September HIKE on the table (odds ~60%). BTC broke $77K on $488M liquidations. NVDA guided ~70% growth. Portfolio CSV dated Jul 31, 2026 - prices stale, positions current.')

    skipping = True  # skip markdown title block, we rendered our own
    for raw in lines:
        line = raw.rstrip()
        if skipping:
            # skip everything before first '### ' heading
            if line.startswith('### '):
                skipping = False
            else:
                continue
        if line.strip() == '':
            pdf.ln(2)
            continue
        if line.startswith('==='):  # page-break markers
            pdf.add_page()
            continue
        if line.startswith('# ') or line.startswith('## '):
            level = 1 if line.startswith('# ') else 2
            pdf.ln(6 if level == 2 else 0)
            pdf.set_font('Helvetica', 'B', 15 if level == 1 else 12.5)
            pdf.set_text_color(45, 55, 72) if level == 1 else pdf.set_text_color(66, 83, 105)
            pdf.multi_cell(190, 7, clean(line[2:].strip()))
            pdf.set_draw_color(120, 130, 150) if level == 1 else None
            if level == 1:
                y = pdf.get_y()
                pdf.line(10, y, 200, y)
                pdf.ln(2)
            else:
                pdf.ln(1)
            pdf.set_text_color(0, 0, 0)
        elif line.startswith('### '):
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(80, 100, 130)
            pdf.multi_cell(190, 6, clean(line[4:].strip()))
            pdf.ln(1)
            pdf.set_text_color(0, 0, 0)
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font('Helvetica', '', 10)
            pdf.set_x(14)
            pdf.set_text_color(90, 90, 90)
            pdf.cell(5, 5, '*', new_x="RIGHT")
            pdf.set_text_color(0, 0, 0)
            rich_cell(pdf, line[2:].strip(), 175)
        elif line.startswith('---'):
            pdf.ln(2)
            y = pdf.get_y()
            pdf.set_draw_color(200, 200, 200)
            pdf.line(25, y, 185, y)
            pdf.ln(2)
        elif line.startswith('*') and line.endswith('*') and not line.startswith('**'):
            pdf.set_font('Helvetica', 'I', 8.5)
            pdf.set_text_color(120, 120, 120)
            pdf.multi_cell(190, 4.5, clean(line.strip('*')))
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.set_font('Helvetica', '', 10)
            rich_cell(pdf, line, 190)

    pdf.output(OUT)
    print('PDF written:', OUT)

if __name__ == '__main__':
    main()