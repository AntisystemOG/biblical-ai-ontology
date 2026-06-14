#!/usr/bin/env python3
"""
Trading Arena PDF Report Generator
Uses fpdf2 for pure Python PDF generation (no system dependencies)
"""

from datetime import datetime
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("Installing fpdf2...")
    import subprocess
    subprocess.run(["pip", "install", "fpdf2"], check=True)
    from fpdf import FPDF

# Output path
OUTPUT_DIR = Path("C:/Users/thadd/.openclaw/workspace/Spocks Reports/market")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f"trading_arena_report_{datetime.now().strftime('%Y%m%d')}.pdf"

class TradingReport(FPDF):
    def header(self):
        # Logo/Title area
        self.set_fill_color(30, 58, 95)  # #1e3a5f
        self.rect(0, 0, 210, 25, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 16)
        self.set_xy(10, 8)
        self.cell(0, 10, 'Trading Arena Report', ln=True)
        
        self.set_font('Helvetica', '', 9)
        self.set_xy(10, 17)
        self.cell(0, 6, 'AI Trader Simulation Results', ln=True)
        
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def add_benchmark_box(self, price, change_pct):
        # Benchmark box
        self.set_fill_color(240, 244, 248)
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.5)
        self.rect(10, self.get_y(), 190, 22, 'FD')
        
        self.set_xy(14, self.get_y() + 4)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(30, 58, 95)
        self.cell(0, 6, 'S&P 500 Benchmark', ln=True)
        
        self.set_xy(14, self.get_y())
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Session started: May 11, 2026 | Day 7', ln=True)
        
        # Price on right
        change_color = (34, 197, 94) if change_pct >= 0 else (220, 38, 38)
        self.set_xy(130, self.get_y() - 11)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(30, 58, 95)
        self.cell(50, 8, f'${price:,.2f}', 0, 0, 'R')
        
        self.set_xy(130, self.get_y() + 8)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*change_color)
        sign = '+' if change_pct >= 0 else ''
        self.cell(50, 6, f'{sign}{change_pct:.2f}%', 0, 0, 'R')
        
        self.ln(20)
    
    def add_standings_table(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(30, 58, 95)
        self.cell(0, 8, 'Live Standings', ln=True)
        self.ln(2)
        
        # Table header
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        
        col_widths = [15, 30, 40, 35, 35, 35]
        headers = ['Rank', 'Trader', 'Strategy', 'Portfolio', 'Return', 'vs S&P']
        
        for width, header in zip(col_widths, headers):
            self.cell(width, 8, header, 1, 0, 'L', True)
        self.ln()
        
        # Data
        traders = [
            ('1', 'Shark', 'Momentum', 21104.80, 111.05, 96.27),
            ('2', 'Turtle', 'Trend Following', 17856.30, 78.56, 63.78),
            ('3', 'Wolf', 'Sector Rotation', 17345.60, 73.46, 58.68),
            ('4', 'Owl', 'Value', 11368.45, 13.68, -1.10),
            ('5', 'Fox', 'Contrarian', 9865.30, -1.35, -16.13),
        ]
        
        row_colors = [
            (255, 215, 0),    # Gold
            (229, 231, 235),  # Silver
            (205, 127, 50),   # Bronze
            (255, 255, 255),  # White
            (255, 255, 255),  # White
        ]
        
        for i, (rank, name, strategy, portfolio, ret, vs_sp) in enumerate(traders):
            # Set row background
            if i < 3:
                self.set_fill_color(*row_colors[i])
            else:
                self.set_fill_color(249, 250, 251)
            
            self.set_text_color(0, 0, 0)
            self.set_font('Helvetica', 'B' if i < 3 else '', 9)
            
            # Rank with medal emoji replacement
            rank_display = rank
            if rank == '1':
                rank_display = '#1'
            elif rank == '2':
                rank_display = '#2'
            elif rank == '3':
                rank_display = '#3'
            
            self.cell(col_widths[0], 8, rank_display, 1, 0, 'C', True)
            self.cell(col_widths[1], 8, name, 1, 0, 'L', True)
            
            self.set_font('Helvetica', '', 9)
            self.cell(col_widths[2], 8, strategy, 1, 0, 'L', True)
            self.cell(col_widths[3], 8, f'${portfolio:,.2f}', 1, 0, 'R', True)
            
            # Return with color
            ret_color = (34, 197, 94) if ret >= 0 else (220, 38, 38)
            self.set_text_color(*ret_color)
            sign = '+' if ret >= 0 else ''
            self.cell(col_widths[4], 8, f'{sign}{ret:.2f}%', 1, 0, 'R', True)
            
            # vs S&P with color
            vs_color = (34, 197, 94) if vs_sp >= 0 else (220, 38, 38)
            self.set_text_color(*vs_color)
            sign = '+' if vs_sp >= 0 else ''
            self.cell(col_widths[5], 8, f'{sign}{vs_sp:.2f}%', 1, 0, 'R', True)
            
            self.ln()
        
        self.ln(5)
    
    def add_trader_detail(self, emoji, name, strategy, rank, rank_color, portfolio, total_ret, vs_sp, cash, holdings, actions):
        # Trader box
        box_y = self.get_y()
        self.set_fill_color(250, 250, 250)
        self.set_draw_color(229, 231, 235)
        self.rect(10, box_y, 190, 42, 'FD')
        
        # Header with rank badge
        self.set_xy(14, box_y + 3)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(30, 58, 95)
        self.cell(0, 6, f'{name}', ln=True)
        
        self.set_xy(14, box_y + 10)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f'{strategy}', ln=True)
        
        # Rank badge
        self.set_xy(170, box_y + 3)
        if rank == 1:
            self.set_fill_color(255, 215, 0)
        elif rank == 2:
            self.set_fill_color(229, 231, 235)
        elif rank == 3:
            self.set_fill_color(205, 127, 50)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(107, 114, 128)
            self.set_text_color(255, 255, 255)
        
        self.cell(20, 8, f'#{rank}', 0, 0, 'C', True)
        
        # Metrics row
        self.set_text_color(0, 0, 0)
        self.set_xy(14, box_y + 18)
        
        # 4 metrics in a row
        metrics = [
            ('Portfolio', f'${portfolio:,.2f}'),
            ('Total Return', f'{total_ret:+.2f}%', (34, 197, 94) if total_ret >= 0 else (220, 38, 38)),
            ('vs S&P 500', f'{vs_sp:+.2f}%', (34, 197, 94) if vs_sp >= 0 else (220, 38, 38)),
            ('Cash', f'${cash:,.2f}'),
        ]
        
        metric_width = 44
        for label, value, *color in metrics:
            self.set_font('Helvetica', '', 7)
            self.set_text_color(100, 100, 100)
            self.cell(metric_width, 4, label, 0, 0, 'L')
            
            self.set_xy(self.get_x() - metric_width, self.get_y() + 4)
            self.set_font('Helvetica', 'B', 9)
            if color:
                self.set_text_color(*color[0])
            else:
                self.set_text_color(0, 0, 0)
            self.cell(metric_width, 5, value, 0, 0, 'L')
            self.set_xy(self.get_x(), self.get_y() - 4)
        
        self.ln(12)
        
        # Holdings
        self.set_xy(14, box_y + 32)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(18, 5, 'Holdings:', 0, 0)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, holdings, ln=True)
        
        self.ln(5)
    
    def add_activity_section(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(30, 58, 95)
        self.cell(0, 8, 'Recent Activity (2:00 PM - 2:30 PM)', ln=True)
        self.ln(2)
        
        activities = [
            ('2:05 PM', 'BUY', 'Turtle adds MSFT +5 shares @ $412.15'),
            ('2:15 PM', 'ADD', 'Shark increases NVDA +8 shares @ $235.40'),
            ('2:22 PM', 'BUY', 'Fox initiates QQQ +15 shares @ $498.20'),
            ('2:28 PM', 'HOLD', 'Wolf - no rotation signals'),
        ]
        
        self.set_font('Helvetica', '', 9)
        for time, action, desc in activities:
            self.set_text_color(100, 100, 100)
            self.set_font('Courier', '', 8)
            self.cell(25, 6, time, 0, 0)
            
            if action == 'BUY' or action == 'ADD':
                self.set_text_color(34, 197, 94)
            elif action == 'SELL':
                self.set_text_color(220, 38, 38)
            else:
                self.set_text_color(100, 100, 100)
            
            self.set_font('Helvetica', 'B', 9)
            self.cell(15, 6, action, 0, 0)
            
            self.set_text_color(0, 0, 0)
            self.set_font('Helvetica', '', 9)
            self.cell(0, 6, desc, ln=True)
        
        self.ln(5)

def generate_pdf():
    """Generate the PDF report"""
    print("Generating Trading Arena report...")
    
    pdf = TradingReport()
    pdf.add_page()
    
    # Benchmark
    pdf.add_benchmark_box(7495.20, 0.64)
    
    # Standings table
    pdf.add_standings_table()
    
    # Add new page for trader details
    pdf.add_page()
    pdf.set_y(30)
    
    # Trader details
    traders_data = [
        ('', 'Shark', 'Momentum Strategy', 1, 'gold', 21104.80, 111.05, 96.27, 5426.40, 'NVDA x46, AMD x12, TSLA x8'),
        ('', 'Turtle', 'Trend Following Strategy', 2, 'silver', 17856.30, 78.56, 63.78, 452.20, 'AAPL x22, MSFT x17, AVGO x6'),
        ('', 'Wolf', 'Sector Rotation Strategy', 3, 'bronze', 17345.60, 73.46, 58.68, 5142.50, 'XLK x30, XLE x45, XLF x25'),
        ('', 'Owl', 'Value Strategy', 4, 'gray', 11368.45, 13.68, -1.10, 1795.75, 'JPM x20, BRK.B x10, UNH x5'),
        ('', 'Fox', 'Contrarian Strategy', 5, 'gray', 9865.30, -1.35, -16.13, 2368.20, 'XLU x30, QQQ x15, TLT x12'),
    ]
    
    for data in traders_data:
        pdf.add_trader_detail(*data, [])
    
    # Activity section
    pdf.add_activity_section()
    
    # Footer note
    pdf.set_y(-25)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, 'Trading Arena Simulation | Next update: 3:00 PM CDT', 0, 0, 'C')
    pdf.ln(4)
    pdf.cell(0, 5, 'This report is for informational purposes only and does not constitute investment advice.', 0, 0, 'C')
    
    # Save
    pdf.output(OUTPUT_FILE)
    
    print(f"[OK] PDF generated: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    return OUTPUT_FILE

if __name__ == "__main__":
    generate_pdf()
