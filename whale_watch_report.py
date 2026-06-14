#!/usr/bin/env python3
"""
Whale Watch Report Generator - Q4 2025 13F Filings Analysis
Generates PDF report tracking hedge fund holdings and overlaps
"""

from weasyprint import HTML
import datetime

# Q4 2025 13F Holdings Data
WHALE_DATA = {
    "Point72 (Steven Cohen)": {
        "aum": "$89.42B",
        "holdings": 3862,
        "top_positions": [
            ("NVDA", "NVIDIA CORP", "Long"),
            ("SPY", "SPDR S&P 500 ETF", "Put"),
            ("TSM", "TAIWAN SEMICONDUCTOR", "Long"),
            ("QQQ", "Invesco QQQ ETF", "Put"),
        ],
        "change_pct": "+49.64%",
        "allocation": {"stocks": "68.18%", "options": "28.67%", "debt": "2.99%"}
    },
    "D1 Capital (Daniel Sundheim)": {
        "aum": "$10.70B",
        "holdings": 42,
        "top_positions": [
            ("CART", "MAPLEBEAR INC (Instacart)", "Long"),
            ("APP", "APPLOVIN CORP", "Long"),
            ("SE", "SEA LTD", "Long"),
            ("APP", "CLEAN HARBORS INC", "Long"),
            ("META", "META PLATFORMS INC", "Long"),
        ],
        "change_pct": "+22.90%",
        "allocation": {"stocks": "100.00%", "options": "0.00%", "debt": "0.00%"}
    },
    "Appaloosa (David Tepper)": {
        "aum": "$6.93B",
        "holdings": 39,
        "top_positions": [
            ("BABA", "ALIBABA GROUP", "Long"),
            ("NVDA", "NVIDIA CORP", "Long"),
            ("META", "META PLATFORMS", "Long"),
            ("AMZN", "AMAZON.COM INC", "Long"),
        ],
        "change_pct": "-6.21%",
        "allocation": {"stocks": "98.97%", "options": "1.03%", "debt": "0.00%"}
    }
}

# Common positions found across multiple funds
HIGH_CONVICTION_OVERLAPS = [
    ("NVDA", "NVIDIA CORP", ["Point72", "D1 Capital", "Appaloosa"]),
    ("META", "META PLATFORMS", ["D1 Capital", "Appaloosa"]),
]

def generate_whale_watch_report():
    today = datetime.datetime.now().strftime("%B %d, %Y")
    report_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Build holdings tables
    holdings_html = ""
    for fund_name, data in WHALE_DATA.items():
        holdings_html += f'''
        <div class="fund-section">
            <h3>{fund_name}</h3>
            <table class="fund-stats">
                <tr>
                    <td><strong>AUM:</strong> {data['aum']}</td>
                    <td><strong>Holdings:</strong> {data['holdings']} positions</td>
                    <td><strong>QoQ Change:</strong> <span class="{'positive' if '+' in data['change_pct'] else 'negative'}">{data['change_pct']}</span></td>
                </tr>
            </table>
            <p><strong>Top Positions:</strong></p>
            <table class="positions">
                <tr><th>Ticker</th><th>Company</th><th>Type</th></tr>
                {''.join(f'<tr><td>{t}</td><td>{n}</td><td>{typ}</td></tr>' for t, n, typ in data['top_positions'])}
            </table>
        </div>
        '''
    
    # Build overlaps table
    overlaps_html = """
        <tr><th>Ticker</th><th>Company</th><th>Whales Holding</th><th>Conviction Score</th></tr>
    """
    for ticker, name, funds in HIGH_CONVICTION_OVERLAPS:
        score = "🔥🔥🔥 HIGH" if len(funds) >= 3 else "🔥🔥 MEDIUM" if len(funds) >= 2 else "🔥 LOW"
        overlaps_html += f"<tr><td>{ticker}</td><td>{name}</td><td>{', '.join(funds)}</td><td>{score}</td></tr>"
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Whale Watch Report - Q4 2025</title>
    <style>
        @page {{ size: letter; margin: 0.75in; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            font-size: 10pt; 
            line-height: 1.4;
            color: #333;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #1a5276;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #1a5276;
            font-size: 28pt;
            margin: 0;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 12pt;
            margin-top: 5px;
        }}
        .header .date {{
            color: #999;
            font-size: 10pt;
            margin-top: 10px;
        }}
        h2 {{
            color: #1a5276;
            border-bottom: 1px solid #3498db;
            font-size: 14pt;
            margin-top: 25px;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #2874a6;
            font-size: 12pt;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #1a5276;
            margin: 20px 0;
        }}
        .fund-section {{
            margin: 20px 0;
            padding: 15px;
            background: #fff;
            border: 1px solid #ddd;
            page-break-inside: avoid;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 9pt;
        }}
        th {{
            background: #1a5276;
            color: white;
            padding: 8px;
            text-align: left;
        }}
        td {{
            padding: 6px 8px;
            border-bottom: 1px solid #eee;
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .positions th {{ background: #5dade2; }}
        .positive {{ color: #27ae60; font-weight: bold; }}
        .negative {{ color: #e74c3c; font-weight: bold; }}
        .overlaps {{ 
            margin: 20px 0; 
            background: #fef9e7;
            padding: 15px;
            border: 1px solid #f9e79f;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            font-size: 8pt;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐋 Whale Watch Report</h1>
        <div class="subtitle">Q4 2025 13F Hedge Fund Holdings Analysis</div>
        <div class="date">Generated: {today}</div>
    </div>
    
    <div class="summary">
        <strong>Executive Summary:</strong> This report tracks Q4 2025 13F filings for major hedge funds. 
        Point72 leads with $89.4B AUM (+49.6% QoQ), followed by D1 Capital at $10.7B (+22.9% QoQ), 
        and Appaloosa at $6.9B (-6.2% QoQ). Key overlaps identified in NVDA and META represent high-conviction 
        themes across multiple managers.
    </div>
    
    <h2>📊 Manager Holdings Overview</h2>
    {holdings_html}
    
    <h2>🔥 High-Conviction Overlaps</h2>
    <p>Positions held by multiple whale managers indicate strong consensus:</p>
    <div class="overlaps">
        <table>
            {overlaps_html}
        </table>
    </div>
    
    <h2>📈 Key Insights</h2>
    <ul>
        <li><strong>NVIDIA (NVDA)</strong> appears as a top holding across multiple funds — strongest consensus play</li>
        <li><strong>Point72</strong> dramatically increased AUM by nearly 50%, indicating significant new capital deployment</li>
        <li><strong>D1 Capital</strong> shows strong growth (+22.9%) with concentrated positions in tech/growth names</li>
        <li><strong>Appaloosa</strong> reduced positions slightly (-6.2%) while maintaining core equity exposure</li>
        <li>Options activity elevated at Point72 (28.7% of portfolio) suggests hedging or tactical positioning</li>
    </ul>
    
    <h2>⚠️ Important Disclaimers</h2>
    <ul>
        <li>Data sourced from SEC 13F filings as of Q4 2025 (filed February 2026)</li>
        <li>13F filings have a 45-day delay and may not reflect current positions</li>
        <li>Short positions are not required to be disclosed on 13F forms</li>
        <li>This report is for informational purposes only — not investment advice</li>
    </ul>
    
    <div class="footer">
        Whale Watch Report | Q4 2025 13F Analysis | Data: SEC EDGAR<br>
        Generated by Spock 🖖
    </div>
</body>
</html>'''
    
    output_path = f"C:\\Users\\thadd\\OneDrive\\Desktop\\Spocks Reports\\whale_watch\\{report_date}_whale_watch.pdf"
    
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    HTML(string=html).write_pdf(output_path)
    print(f"Report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_whale_watch_report()
