"""Convert markdown reports to PDF using fpdf2."""
from fpdf import FPDF
from pathlib import Path
import re

REPORTS = Path.home() / "OneDrive" / "Desktop" / "Spocks Reports"

class MD2PDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(True, 20)
        self.add_font("Segoe", "", r"C:\Windows\Fonts\segoeui.ttf")
        self.add_font("Segoe", "B", r"C:\Windows\Fonts\segoeuib.ttf")
        self.add_font("Segoe", "I", r"C:\Windows\Fonts\segoeuii.ttf")
        self.add_font("Consolas", "", r"C:\Windows\Fonts\consola.ttf")
        
    def render(self, md_text: str):
        lines = md_text.split('\n')
        in_code = False
        in_table = False
        table_data = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Code blocks
            if line.strip().startswith('```'):
                if in_code:
                    in_code = False
                    i += 1
                    continue
                else:
                    in_code = True
                    i += 1
                    continue
                    
            if in_code:
                self.set_font("Consolas", "", 8)
                self.set_fill_color(240, 240, 240)
                self.set_x(15)
                self.cell(180, 4.5, line[:100], fill=True)
                self.ln()
                i += 1
                continue
            
            # Separator
            if line.strip() == '---':
                self.set_draw_color(52, 152, 219)
                self.set_line_width(0.5)
                y = self.get_y()
                self.line(15, y, 195, y)
                self.ln(6)
                i += 1
                continue
            
            # Headers
            if line.startswith('# '):
                self.set_font("Segoe", "B", 18)
                self.set_text_color(44, 62, 80)
                self.set_x(15)
                self.multi_cell(180, 8, line[2:].strip())
                self.set_draw_color(52, 152, 219)
                self.set_line_width(0.8)
                y = self.get_y()
                self.line(15, y + 1, 80, y + 1)
                self.ln(4)
                i += 1
                continue
            if line.startswith('## '):
                self.set_font("Segoe", "B", 13)
                self.set_text_color(44, 62, 80)
                self.set_x(15)
                self.multi_cell(180, 7, line[3:].strip())
                self.ln(2)
                i += 1
                continue
            if line.startswith('### '):
                self.set_font("Segoe", "B", 11)
                self.set_text_color(52, 73, 94)
                self.set_x(15)
                self.multi_cell(180, 6, line[4:].strip())
                self.ln(1)
                i += 1
                continue
            
            # Tables (simple pipe tables)
            if '|' in line and line.strip().startswith('|'):
                if not in_table:
                    in_table = True
                    table_data = []
                # Skip separator lines like |---|----|
                if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                    i += 1
                    continue
                cells = [c.strip() for c in line.split('|')[1:-1]]
                table_data.append(cells)
                i += 1
                # Check if next line ends table
                if i >= len(lines) or '|' not in lines[i]:
                    in_table = False
                    if table_data:
                        self._draw_table(table_data)
                    table_data = []
                    self.ln(4)
                continue
            
            if in_table and '|' not in line and line.strip():
                in_table = False
                if table_data:
                    self._draw_table(table_data)
                table_data = []
                self.ln(4)
            
            # Blockquote
            if line.strip().startswith('>'):
                self.set_font("Segoe", "I", 9)
                self.set_text_color(100, 100, 100)
                self.set_draw_color(52, 152, 219)
                self.set_line_width(0.6)
                self.set_x(18)
                y = self.get_y()
                self.line(15, y, 15, y + 5)
                self.set_x(18)
                self.multi_cell(177, 5, line.strip()[1:].strip())
                i += 1
                continue
            
            # Bold/inline formatting - strip ** markers for now
            clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
            clean = clean.replace('`', "'")
            
            # Horizontal rule
            if line.strip() in ('---', '***', '___'):
                self.set_draw_color(180, 180, 180)
                y = self.get_y()
                self.line(15, y, 195, y)
                self.ln(4)
                i += 1
                continue

            # Normal paragraph
            if clean.strip():
                self.set_font("Segoe", "", 9.5)
                self.set_text_color(30, 30, 30)
                self.set_x(15)
                self.multi_cell(180, 5.5, clean.strip())
            else:
                self.ln(3)
            i += 1
            
        # Close any open table
        if in_table and table_data:
            self._draw_table(table_data)
    
    def _draw_table(self, rows):
        if not rows:
            return
        self.set_font("Segoe", "", 8)
        ncols = len(rows[0])
        widths = [180 / ncols] * ncols
        col_widths = []
        for c in range(ncols):
            max_w = max(len(str(row[c])) for row in rows if c < len(row)) * 2.2
            col_widths.append(max(25, min(max_w, 90)))
        # Scale to fit
        total = sum(col_widths)
        if total > 180:
            scale = 180 / total
            col_widths = [w * scale for w in col_widths]
        
        self.set_x(15)
        for c, cell in enumerate(rows[0]):
            self.set_font("Segoe", "B", 8)
            self.set_fill_color(52, 152, 219)
            self.set_text_color(255, 255, 255)
            x = self.get_x()
            self.cell(col_widths[c], 6, str(cell), border=0, fill=True)
            self.set_x(x + col_widths[c])
        self.ln()
        
        for row in rows[1:]:
            self.set_x(15)
            fill = rows.index(row) % 2 == 0
            for c, cell in enumerate(row):
                self.set_font("Segoe", "", 8)
                self.set_text_color(30, 30, 30)
                if fill:
                    self.set_fill_color(248, 249, 250)
                else:
                    self.set_fill_color(255, 255, 255)
                self.cell(col_widths[c], 5.5, str(cell), fill=True)
            self.ln()

for report_name, folder in [
    ("2026-05-06_whale_watch", "whale_watch"),
    ("2026-05-06_history_rhymes", "history_rhymes"),
    ("2026-05-06_dream", "memory_dreaming"),
]:
    md_file = REPORTS / folder / f"{report_name}.md"
    pdf_file = REPORTS / folder / f"{report_name}.pdf"
    if not md_file.exists():
        print(f"SKIP {md_file}")
        continue
    
    pdf = MD2PDF()
    pdf.add_page()
    pdf.render(md_file.read_text(encoding="utf-8"))
    pdf.output(str(pdf_file))
    size = pdf_file.stat().st_size
    print(f"OK  {pdf_file.name} ({size:,} bytes, {size/1024:.0f} KB)")
