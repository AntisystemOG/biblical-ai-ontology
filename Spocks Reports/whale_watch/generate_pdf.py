#!/usr/bin/env python3
"""Generate Whale Watch PDF Report using ReportLab"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

def generate_whale_watch_pdf():
    output_path = r"C:\Users\thadd\.openclaw\workspace\Spocks Reports\whale_watch\2026-05-14_whale_watch.pdf"
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5282'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#3182ce'),
        spaceBefore=10,
        spaceAfter=5
    )
    
    whale_header_style = ParagraphStyle(
        'WhaleHeader',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2c5282'),
        spaceBefore=15,
        spaceAfter=3,
        backColor=colors.HexColor('#ebf8ff'),
        borderPadding=8
    )
    
    # Title
    elements.append(Paragraph("🐋 Whale Watch Report", title_style))
    elements.append(Paragraph("Q1 2025 13F Holdings Analysis | Generated: May 14, 2026", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", h2_style))
    summary_text = """This report analyzes Q1 2025 13F filings from five major hedge fund managers and identifies 
    overlaps with your portfolio holdings. Key themes include strong positions in AI/semiconductors, 
    energy infrastructure, and strategic additions to portfolio companies."""
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Summary stats table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Portfolio Value', '$238,642.89'],
        ['Unique Holdings Analyzed', '5 Whales'],
        ['Direct Overlaps Found', '11 stocks']
    ]
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9ae6b4')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Portfolio Overlap Analysis
    elements.append(Paragraph("📊 Portfolio Overlap Analysis", h2_style))
    
    overlap_data = [
        ['Ticker', 'Company', 'Your Position', 'Whale Owner', 'Activity', 'Conviction'],
        ['INTC', 'Intel Corp', '$24,879.85', 'Aschenbrenner (45.7%)', 'NEW MAJOR', 'Very High'],
        ['NVDA', 'NVIDIA Corp', '$3,883.53', 'Cohen (+38%), Laffont', 'Added/Held', 'High'],
        ['CEG', 'Constellation Energy', '$2,379.86', 'Laffont (12.5%), Aschenbrenner', 'Added', 'High'],
        ['CORZ', 'Core Scientific', '$17,341.87', 'Aschenbrenner (3.3%)', 'NEW', 'Medium'],
        ['APLD', 'Applied Digital', '$3,085.42', 'Aschenbrenner (2.3%)', 'NEW', 'Medium'],
        ['RDDT', 'Reddit Inc', '$3,563.75', 'Laffont (5%), Sundheim', 'Held', 'High'],
        ['AMZN', 'Amazon.com', '$11,211.70', 'Cohen (+69%)', 'Added', 'High'],
        ['TSLA', 'Tesla Inc', '$5,000.91', 'Laffont (4.3%)', 'Trimmed', 'Medium'],
        ['GOOGL', 'Alphabet Inc', '$3,346.22', 'Laffont (3.1%)', 'Trimmed', 'Medium'],
        ['AAPL', 'Apple Inc', '$2,088.45', 'Tepper (4.0%)', 'NEW', 'High'],
        ['PTON', 'Peloton', '$2,401.82', 'Laffont (0.2%)', 'NEW', 'Low'],
        ['TEM', 'Tempus AI', '$2,406.00', 'Laffont (0.5%)', 'NEW', 'Medium'],
        ['SMH', 'VanEck Semi ETF', '$1,376.46', 'Tepper (0.3%)', 'NEW', 'Low'],
    ]
    
    overlap_table = Table(overlap_data, colWidths=[0.8*inch, 1.5*inch, 1*inch, 1.4*inch, 1*inch, 0.7*inch])
    overlap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e6f3ff')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(overlap_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Key Insights
    elements.append(Paragraph("💡 Key Insights & Themes", h2_style))
    
    elements.append(Paragraph("High Conviction Overlaps (Multiple Whales)", h3_style))
    insights1 = """
    <b>• Reddit (RDDT):</b> Held by both Laffont (5%) and Sundheim (4.55%) - strong validation for your position<br/>
    <b>• NVIDIA (NVDA):</b> Cohen significantly added (+38%), Laffont holds 9.3% - AI leader remains core<br/>
    <b>• Constellation Energy (CEG):</b> Both Laffont (12.5%) and Aschenbrenner (3.7%) adding - nuclear for AI
    """
    elements.append(Paragraph(insights1, styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("🚨 Major Whale Position Match: Intel (INTC)", h3_style))
    insight2 = """<b>Leopold Aschenbrenner's Situational Awareness LP made Intel a MASSIVE 45.7% position 
    ($459M) - NEW in Q1 2025.</b> This is his largest holding by far. You hold $24,879 in INTC."""
    elements.append(Paragraph(insight2, styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("Thematic Concentration", h3_style))
    themes = """
    <b>• AI Infrastructure:</b> Strong overlap in semiconductors, data center plays (CORZ, APLD)<br/>
    <b>• Energy/Data Centers:</b> CEG, VST popular across multiple whales<br/>
    <b>• Consumer Tech:</b> AMZN, AAPL, TSLA remain core positions<br/>
    <b>• Special Situations:</b> PTON, TEM - new distressed/recovery plays
    """
    elements.append(Paragraph(themes, styles['Normal']))
    elements.append(PageBreak())
    
    # Whale Manager Details
    elements.append(Paragraph("🐋 Detailed Whale Positions", h2_style))
    
    # David Tepper
    elements.append(Paragraph("David Tepper - Appaloosa LP (AUM: $5.6B | 35 holdings)", whale_header_style))
    tepper_data = [
        ['Ticker', 'Company', 'Weight', 'Activity'],
        ['SPYX', 'SPDR S&P 500 Fossil Free ETF', '36.1%', 'NEW'],
        ['BABA', 'Alibaba Group', '17.5%', 'Reduced'],
        ['AAPL', 'Apple Inc', '4.0%', 'NEW ⭐'],
        ['UBER', 'Uber Technologies', '3.3%', 'Added'],
        ['MSFT', 'Microsoft', '2.7%', 'Reduced'],
        ['NVDA', 'NVIDIA Corp', '0.5%', 'Reduced'],
        ['SMH', 'VanEck Semiconductor ETF', '0.3%', 'NEW ⭐'],
    ]
    tepper_table = Table(tepper_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1.2*inch])
    tepper_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    elements.append(tepper_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Philippe Laffont
    elements.append(Paragraph("Philippe Laffont - Coatue Management (AUM: $22.7B | 70 holdings)", whale_header_style))
    laffont_data = [
        ['Ticker', 'Company', 'Weight', 'Activity'],
        ['TSM', 'Taiwan Semi', '13.3%', 'Trimmed'],
        ['CEG', 'Constellation Energy', '12.5%', 'Trimmed ⭐'],
        ['NVDA', 'NVIDIA Corp', '9.3%', 'Trimmed'],
        ['RDDT', 'Reddit Inc', '5.0%', 'Trimmed ⭐'],
        ['TSLA', 'Tesla Inc', '4.3%', 'Trimmed ⭐'],
        ['GOOGL', 'Alphabet', '3.1%', 'Trimmed ⭐'],
        ['PM', 'Philip Morris', '2.5%', 'NEW ⭐'],
        ['PTON', 'Peloton', '0.2%', 'NEW ⭐'],
        ['TEM', 'Tempus AI', '0.5%', 'NEW ⭐'],
        ['VRT', 'Vertiv Holdings', '0.0%', 'EXITED'],
    ]
    laffont_table = Table(laffont_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1.2*inch])
    laffont_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    elements.append(laffont_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Leopold Aschenbrenner
    elements.append(Paragraph("Leopold Aschenbrenner - Situational Awareness LP (AUM: $1.0B | 12 holdings)", whale_header_style))
    sit_data = [
        ['Ticker', 'Company', 'Weight', 'Activity'],
        ['INTC', 'Intel Corp', '45.7%', 'NEW MAJOR ⭐'],
        ['AVGO', 'Broadcom', '11.7%', 'NEW'],
        ['VST', 'Vistra Corp', '6.1%', 'Added'],
        ['CEG', 'Constellation Energy', '3.7%', 'Added ⭐'],
        ['CORZ', 'Core Scientific', '3.3%', 'NEW ⭐'],
        ['APLD', 'Applied Digital', '2.3%', 'NEW ⭐'],
        ['IREN', 'IREN Ltd', '2.0%', 'NEW'],
    ]
    sit_table = Table(sit_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1.2*inch])
    sit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    elements.append(sit_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Steve Cohen
    elements.append(Paragraph("Steve Cohen - Point72 Asset Management (AUM: $41.7B est.)", whale_header_style))
    cohen_data = [
        ['Ticker', 'Company', 'Weight', 'Activity'],
        ['NVDA', 'NVIDIA Corp', '2.08%', 'Added +38% ⭐'],
        ['TSM', 'Taiwan Semi', '1.59%', 'Added +158%'],
        ['AMZN', 'Amazon.com', '1.36%', 'Added +69% ⭐'],
    ]
    cohen_table = Table(cohen_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1.2*inch])
    cohen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    elements.append(cohen_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Daniel Sundheim
    elements.append(Paragraph("Daniel Sundheim - D1 Capital Partners (AUM: $10.7B est.)", whale_header_style))
    d1_data = [
        ['Ticker', 'Company', 'Weight', 'Activity'],
        ['CART', 'Maplebear (Instacart)', '9.48%', '-'],
        ['CLH', 'Clean Harbors', '6.10%', 'Added +14%'],
        ['FLS', 'Flowserve', '4.96%', 'Added +3%'],
        ['RDDT', 'Reddit Inc', '4.55%', 'Added +5% ⭐'],
    ]
    d1_table = Table(d1_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1.2*inch])
    d1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    elements.append(d1_table)
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_text = """<font size="8" color="#718096">
    Report generated on May 14, 2026 from Q1 2025 13F filings | Data sources: SEC EDGAR<br/>
    Disclaimer: 13F data represents positions at quarter-end and may not reflect current holdings. 
    For informational purposes only. ⭐ = Overlaps with your portfolio
    </font>"""
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    print(f"PDF generated successfully: {output_path}")

if __name__ == "__main__":
    generate_whale_watch_pdf()
