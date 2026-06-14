#!/usr/bin/env python3
"""
Generate PDF from profit_above_all.md using fpdf2 with core fonts (Helvetica).
This is a sensitive document showing what NOT to do - formatted with clear warnings.
Uses ASCII-only characters for maximum compatibility.
"""

from fpdf import FPDF
import re

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Skip header on first page
        if self.page_no() > 1:
            self.set_font('Helvetica', '', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, 'Profit Above All - Educational Document (What NOT to Do)', align='C')
            self.ln(5)
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def clean_text(text):
    """Remove markdown formatting and convert to ASCII from text"""
    # Remove bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove inline code
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Replace Unicode characters with ASCII equivalents
    text = text.replace('—', '--')  # Em dash
    text = text.replace('–', '-')   # En dash
    text = text.replace('"', '"')   # Left double quote
    text = text.replace('"', '"')   # Right double quote
    text = text.replace(''', "'")   # Left single quote
    text = text.replace(''', "'")   # Right single quote
    text = text.replace('…', '...') # Ellipsis
    return text

def parse_markdown(md_text):
    """Parse markdown into structured content"""
    lines = md_text.split('\n')
    content = []
    current_list = []
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            if not in_code_block and current_list:
                content.append(('list', current_list))
                current_list = []
            i += 1
            continue
        
        if in_code_block:
            content.append(('code', stripped))
            i += 1
            continue
        
        # Empty lines
        if not stripped:
            if current_list:
                content.append(('list', current_list))
                current_list = []
            i += 1
            continue
        
        # Headers
        if stripped.startswith('# '):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            content.append(('h1', stripped[2:]))
        elif stripped.startswith('## '):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            content.append(('h2', stripped[3:]))
        elif stripped.startswith('### '):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            content.append(('h3', stripped[4:]))
        elif stripped.startswith('#### '):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            content.append(('h4', stripped[5:]))
        
        # Blockquotes
        elif stripped.startswith('>'):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            content.append(('quote', stripped[1:].strip()))
        
        # Lists
        elif re.match(r'^[-*]\s', stripped):
            # Check if it's a table row (contains |)
            if '|' in stripped:
                if current_list:
                    content.append(('list', current_list))
                    current_list = []
                content.append(('table_row', stripped))
            else:
                current_list.append(stripped[2:])
        
        # Numbered lists
        elif re.match(r'^\d+\.\s', stripped):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            current_list.append(stripped)
        
        # Tables (separator line)
        elif re.match(r'^\|?[-:\|\s]+\|?$', stripped):
            i += 1
            continue
        
        # Table rows
        elif stripped.startswith('|') and stripped.endswith('|'):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            content.append(('table_row', stripped))
        
        # Horizontal rules
        elif stripped == '---':
            if current_list:
                content.append(('list', current_list))
                current_list = []
            content.append(('hr', ''))
        
        # Bold markers for section headers (check if bold text on its own line)
        elif re.match(r'^\*\*[^*]+\*\*$', stripped):
            if current_list:
                content.append(('list', current_list))
                current_list = []
            text = stripped[2:-2]
            content.append(('bold_header', text))
        
        # Regular paragraphs
        else:
            if current_list:
                content.append(('list', current_list))
                current_list = []
            # Process inline formatting
            content.append(('paragraph', stripped))
        
        i += 1
    
    if current_list:
        content.append(('list', current_list))
    
    return content

def render_table(pdf, table_data):
    """Render a table from parsed data"""
    if not table_data:
        return
    
    pdf.ln(5)
    
    # Calculate column widths based on number of columns
    num_cols = max(len(row) for row in table_data)
    col_width = 180 / num_cols
    
    # Check if this is the contrast table (Part 6)
    is_contrast_table = any('Profit Above All' in str(cell) or 'Stewardship' in str(cell) for row in table_data for cell in row)
    
    for i, row in enumerate(table_data):
        # Header row styling
        if i == 0:
            pdf.set_fill_color(180, 50, 50)  # Dark red header
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 9)
        else:
            # Alternate row colors for contrast table
            if is_contrast_table:
                if i % 2 == 0:
                    pdf.set_fill_color(245, 245, 245)
                else:
                    pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(240, 240, 240)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 9)
        
        # Print cells
        for j, cell in enumerate(row):
            cell_text = clean_text(cell)
            # First column in contrast table gets special styling
            if is_contrast_table and j == 0 and i > 0:
                pdf.set_fill_color(255, 220, 220)  # Light red
            elif is_contrast_table and j == 1 and i > 0:
                pdf.set_fill_color(220, 255, 220)  # Light green
            
            border = 1 if is_contrast_table else 'TB'
            fill = True if is_contrast_table or i == 0 else False
            
            pdf.cell(col_width, 7, cell_text, border=border, fill=fill, align='L')
        
        pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

def generate_pdf(input_file, output_file):
    # Read markdown
    with open(input_file, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    # Parse content
    content = parse_markdown(md_text)
    
    # Create PDF
    pdf = PDF()
    pdf.add_page()
    
    # Title Page
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(180, 50, 50)  # Dark red for warning
    pdf.cell(0, 20, 'Profit Above All', align='C')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'The Amoral Playbook for Maximum Extraction', align='C')
    pdf.ln(15)
    
    # Warning box on title page
    pdf.set_fill_color(255, 235, 235)
    pdf.set_draw_color(200, 50, 50)
    pdf.set_text_color(150, 30, 30)
    pdf.set_font('Helvetica', 'B', 11)
    
    warning_text = """!!! EDUCATIONAL WARNING !!!

This document simulates the worldview of those who prioritize profit without moral constraint.
It is designed as a NEGATIVE EXAMPLE -- showing what to AVOID, not what to emulate.

Purpose: Know the enemy's tactics to resist them."""
    
    pdf.multi_cell(0, 8, warning_text, border=1, fill=True, align='C')
    pdf.ln(10)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 10, 'Document Type: Deconstruction of Harmful Tactics', align='C')
    pdf.ln(8)
    pdf.cell(0, 10, 'Intended Use: Recognition and Defense Only', align='C')
    
    # Content pages
    pdf.add_page()
    
    in_table = False
    table_data = []
    
    for item_type, item_content in content:
        if item_type == 'h1':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(180, 50, 50)
            pdf.ln(5)
            pdf.cell(0, 10, clean_text(item_content))
            pdf.set_draw_color(180, 50, 50)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(8)
            pdf.set_text_color(0, 0, 0)
            
        elif item_type == 'h2':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(80, 80, 80)
            pdf.ln(5)
            pdf.cell(0, 8, clean_text(item_content))
            pdf.set_draw_color(150, 150, 150)
            pdf.line(10, pdf.get_y(), 150, pdf.get_y())
            pdf.ln(5)
            pdf.set_text_color(0, 0, 0)
            
        elif item_type == 'h3':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(60, 60, 60)
            pdf.ln(4)
            pdf.cell(0, 7, clean_text(item_content))
            pdf.ln(3)
            pdf.set_text_color(0, 0, 0)
            
        elif item_type == 'h4':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6, clean_text(item_content))
            pdf.ln(2)
            pdf.set_text_color(0, 0, 0)
            
        elif item_type == 'bold_header':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(60, 60, 60)
            pdf.ln(2)
            pdf.cell(0, 6, clean_text(item_content))
            pdf.ln(2)
            pdf.set_text_color(0, 0, 0)
            
        elif item_type == 'quote':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_left_margin(20)
            pdf.set_right_margin(20)
            pdf.multi_cell(0, 6, f'"{clean_text(item_content)}"')
            pdf.set_left_margin(10)
            pdf.set_right_margin(10)
            pdf.ln(3)
            pdf.set_text_color(0, 0, 0)
            
        elif item_type == 'paragraph':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', '', 10)
            text = clean_text(item_content)
            pdf.multi_cell(0, 6, text)
            pdf.ln(2)
            
        elif item_type == 'list':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.set_font('Helvetica', '', 10)
            for item in item_content:
                # Check if numbered list
                match = re.match(r'^(\d+)\.\s*(.+)$', item)
                if match:
                    num, text = match.groups()
                    # Calculate remaining width
                    remaining_width = pdf.w - pdf.r_margin - pdf.l_margin - 8
                    pdf.cell(8, 6, f'{num}.')
                    pdf.multi_cell(remaining_width, 6, clean_text(text))
                else:
                    remaining_width = pdf.w - pdf.r_margin - pdf.l_margin - 5
                    pdf.cell(5, 6, chr(149))  # Bullet
                    pdf.multi_cell(remaining_width, 6, clean_text(item))
            pdf.ln(3)
            
        elif item_type == 'table_row':
            in_table = True
            # Parse table row
            cells = [c.strip() for c in item_content.split('|') if c.strip()]
            if cells:
                table_data.append(cells)
        
        elif item_type == 'hr':
            if in_table:
                render_table(pdf, table_data)
                table_data = []
                in_table = False
            pdf.ln(5)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(30, pdf.get_y(), 180, pdf.get_y())
            pdf.ln(5)
    
    # Render any remaining table
    if table_data:
        render_table(pdf, table_data)
    
    # Final warning page
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(180, 50, 50)
    pdf.cell(0, 15, '!!! FINAL WARNING !!!', align='C')
    pdf.ln(10)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 8, """This document is for educational purposes only. It describes harmful behaviors to enable recognition and resistance, not emulation.

"Have nothing to do with the fruitless deeds of darkness, but rather expose them." -- Ephesians 5:11

The tactics described herein are antithetical to ethical business practices and Christian stewardship. The purpose of understanding these methods is to defend against them, not to employ them.""", align='C')
    
    # Save PDF
    pdf.output(output_file)
    print(f"PDF generated successfully: {output_file}")

if __name__ == '__main__':
    input_file = r'C:\Users\thadd\.openclaw\workspace\Spocks Reports\profit_above_all.md'
    output_file = r'C:\Users\thadd\.openclaw\workspace\Spocks Reports\profit_above_all.pdf'
    generate_pdf(input_file, output_file)
