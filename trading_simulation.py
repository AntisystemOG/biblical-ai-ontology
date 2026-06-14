import json
import random
from datetime import datetime

# Load existing data
with open('trading_arena_data.json', 'r') as f:
    data = json.load(f)

# Current timestamp
current_time = "2026-05-15T18:00:00Z"

# Stock price database (simulated - base prices)
stock_prices = {
    "AAPL": 195.50, "MSFT": 450.25, "GOOGL": 175.80, "AMZN": 185.40,
    "TSLA": 175.90, "META": 505.20, "NVDA": 950.00, "JPM": 205.30,
    "JNJ": 160.25, "PG": 170.80, "UNH": 575.40, "MA": 505.90,
    "BAC": 38.75, "BRK.B": 435.20, "KO": 65.30, "VZ": 42.10,
    "PFE": 28.90, "WBA": 22.40, "T": 18.50, "XLU": 65.80,
    "XLP": 78.20, "XLK": 215.60, "XLC": 85.40, "VGT": 520.30,
    "QQQ": 490.50, "SMH": 285.70, "ARKK": 48.90, "QCLN": 24.60
}

# Apply random market movement (±2.5% for simulation)
def get_new_price(base_price):
    change = random.uniform(-0.025, 0.025)
    return round(base_price * (1 + change), 2)

# Current prices (simulated for this run)
current_prices = {ticker: get_new_price(price) for ticker, price in stock_prices.items()}

# Calculate portfolio value for each trader
def calc_portfolio_value(trader_data):
    positions = trader_data.get('positions', {})
    cash = trader_data.get('cash', 0)
    position_value = sum(
        shares * current_prices.get(ticker, 0) 
        for ticker, shares in positions.items()
    )
    return round(cash + position_value, 2)

# S&P 500 benchmark simulation
def update_sp500_benchmark():
    prev_value = data['sp500_benchmark']['value']
    change = random.uniform(-0.015, 0.015)
    new_value = round(prev_value * (1 + change), 2)
    data['sp500_benchmark']['value'] = new_value
    data['sp500_benchmark']['history'].append({
        'date': current_time,
        'value': new_value
    })
    return new_value

# Generate trades based on strategy
def generate_turtle_trade(trader_data):
    """Turtle: Trend following - buys on uptrends"""
    if random.random() < 0.4 and trader_data['cash'] > 500:
        tickers = ['MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA']
        ticker = random.choice(tickers)
        amount = min(500, trader_data['cash'] * 0.3)
        return {'type': 'BUY', 'ticker': ticker, 'amount': amount, 'reason': 'Uptrend detected'}
    return None

def generate_shark_trade(trader_data):
    """Shark: Momentum - chases high momentum stocks"""
    if random.random() < 0.45:
        if trader_data['cash'] > 400:
            tickers = ['NVDA', 'TSLA', 'META', 'AMD', 'COIN']
            ticker = random.choice(tickers)
            amount = min(400, trader_data['cash'] * 0.25)
            return {'type': 'BUY', 'ticker': ticker, 'amount': amount, 'reason': 'High momentum'}
        else:
            # Take profits on winners
            positions = trader_data.get('positions', {})
            if positions:
                ticker = random.choice(list(positions.keys()))
                shares = positions[ticker] * 0.3
                if shares > 1:
                    return {'type': 'SELL', 'ticker': ticker, 'shares': round(shares, 2), 'reason': 'Momentum fading - take profits'}
    return None

def generate_owl_trade(trader_data):
    """Owl: Value - buys undervalued, holds long"""
    if random.random() < 0.3 and trader_data['cash'] > 600:
        tickers = ['BRK.B', 'JNJ', 'PG', 'KO', 'VZ']
        ticker = random.choice(tickers)
        amount = min(600, trader_data['cash'] * 0.35)
        return {'type': 'BUY', 'ticker': ticker, 'amount': amount, 'reason': 'Value opportunity'}
    return None

def generate_wolf_trade(trader_data):
    """Wolf: Sector rotation - rotates between sectors"""
    sectors = {
        'TECH': ['XLK', 'VGT', 'QQQ'],
        'HEALTH': ['XLV', 'JNJ', 'UNH'],
        'FINANCE': ['XLF', 'JPM', 'BAC', 'MA']
    }
    if random.random() < 0.5:
        sector_name = random.choice(list(sectors.keys()))
        ticker = random.choice(sectors[sector_name])
        if trader_data['cash'] > 300:
            amount = min(300, trader_data['cash'] * 0.2)
            return {'type': 'BUY', 'ticker': ticker, 'amount': amount, 'reason': f'{sector_name} sector strength'}
    return None

def generate_fox_trade(trader_data):
    """Fox: Contrarian - buys when others sell"""
    if random.random() < 0.35 and trader_data['cash'] > 500:
        tickers = ['XLU', 'XLP', 'PFE', 'T', 'WBA']
        ticker = random.choice(tickers)
        amount = min(500, trader_data['cash'] * 0.3)
        return {'type': 'BUY', 'ticker': ticker, 'amount': amount, 'reason': 'Contrarian play'}
    return None

# Process trades for each trader
trade_generators = {
    'Turtle': generate_turtle_trade,
    'Shark': generate_shark_trade,
    'Owl': generate_owl_trade,
    'Wolf': generate_wolf_trade,
    'Fox': generate_fox_trade
}

new_trades = []

for trader_name, trader_data in data['traders'].items():
    # Generate trade
    generator = trade_generators[trader_name]
    trade = generator(trader_data)
    
    if trade:
        trade['trader'] = trader_name
        trade['time'] = current_time
        
        if trade['type'] == 'BUY':
            # Execute buy
            amount = trade['amount']
            ticker = trade['ticker']
            price = current_prices.get(ticker, 100)
            shares = round(amount / price, 4)
            
            if trader_data['cash'] >= amount:
                trader_data['cash'] = round(trader_data['cash'] - amount, 4)
                if ticker not in trader_data['positions']:
                    trader_data['positions'][ticker] = 0
                trader_data['positions'][ticker] = round(trader_data['positions'][ticker] + shares, 4)
                new_trades.append(trade)
        
        elif trade['type'] == 'SELL':
            # Execute sell
            ticker = trade['ticker']
            shares = trade.get('shares', 0)
            
            if ticker in trader_data['positions'] and trader_data['positions'][ticker] >= shares:
                price = current_prices.get(ticker, 100)
                proceeds = round(shares * price, 2)
                trader_data['cash'] = round(trader_data['cash'] + proceeds, 4)
                trader_data['positions'][ticker] = round(trader_data['positions'][ticker] - shares, 4)
                if trader_data['positions'][ticker] <= 0:
                    del trader_data['positions'][ticker]
                trade['amount'] = proceeds
                new_trades.append(trade)
    
    # Calculate new portfolio value
    new_value = calc_portfolio_value(trader_data)
    trader_data['current_value'] = new_value
    trader_data['history'].append({
        'date': current_time,
        'value': new_value
    })

# Update benchmark
sp500_value = update_sp500_benchmark()

# Update metadata
data['last_update'] = current_time

# Save updated data
with open('trading_arena_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Print summary
print("=== Trading Arena Simulation Complete ===")
print(f"\nTimestamp: {current_time}")
print(f"\nS&P 500 Benchmark: ${sp500_value:,.2f}")
print("\n--- Trader Standings ---")

# Sort traders by value
sorted_traders = sorted(data['traders'].items(), key=lambda x: x[1]['current_value'], reverse=True)
for rank, (name, t) in enumerate(sorted_traders, 1):
    start_val = 10000
    current_val = t['current_value']
    return_pct = ((current_val - start_val) / start_val) * 100
    vs_sp500 = ((current_val - start_val) / start_val - (sp500_value - 10000) / 10000) * 100
    print(f"{rank}. {name}: ${current_val:,.2f} ({return_pct:+.2f}%) vs S&P: {vs_sp500:+.2f}%")

print(f"\n--- New Trades ({len(new_trades)}) ---")
for trade in new_trades[-5:]:
    print(f"  {trade['trader']}: {trade['type']} {trade.get('ticker', 'N/A')} - {trade['reason']}")

# Generate HTML dashboard HTML
html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Arena | Live Simulation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0a0e1a;
            color: #e0e6ed;
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #1a2332;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        .subtitle {{ color: #64748b; font-size: 1.1em; }}
        .market-status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 15px;
        }}
        .market-open {{ background: rgba(34, 197, 94, 0.2); color: #22c55e; }}
        .card {{
            background: #111827;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #1f2937;
            transition: transform 0.2s, border-color 0.2s;
            margin-bottom: 20px;
        }}
        .card:hover {{ transform: translateY(-2px); border-color: #374151; }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #1f2937;
        }}
        .trader-name {{ font-size: 1.4em; font-weight: 700; display: flex; align-items: center; gap: 10px; }}
        .emoji {{ font-size: 1.2em; }}
        .rank {{
            background: #1f2937;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .rank-1 {{ background: linear-gradient(135deg, #ffd700, #ffaa00); color: #000; }}
        .rank-2 {{ background: linear-gradient(135deg, #c0c0c0, #a0a0a0); color: #000; }}
        .rank-3 {{ background: linear-gradient(135deg, #cd7f32, #b87333); color: #fff; }}
        .strategy {{ color: #64748b; font-size: 0.9em; margin-bottom: 15px; }}
        .metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .metric {{ background: #0a0e1a; padding: 12px; border-radius: 8px; }}
        .metric-label {{ color: #64748b; font-size: 0.75em; text-transform: uppercase; }}
        .metric-value {{ font-size: 1.3em; font-weight: 700; margin-top: 4px; }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
        .holdings {{ background: #0a0e1a; padding: 12px; border-radius: 8px; margin-bottom: 12px; }}
        .holdings-label {{ color: #64748b; font-size: 0.75em; text-transform: uppercase; margin-bottom: 8px; }}
        .ticker-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .ticker {{
            background: #1f2937;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }}
        .action {{
            background: #1e3a5f;
            border-left: 3px solid #00d4ff;
            padding: 10px 12px;
            border-radius: 0 8px 8px 0;
            font-size: 0.9em;
            color: #94a3b8;
        }}
        .action strong {{ color: #00d4ff; }}
        .sp500-card {{
            background: linear-gradient(135deg, #1e3a5f 0%, #0a0e1a 100%);
            border: 2px solid #3b82f6;
        }}
        .sp500-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .sp500-title {{ font-size: 1.5em; font-weight: 700; }}
        .sp500-price {{ font-size: 2em; font-weight: 700; }}
        .sp500-change {{ font-size: 1.1em; font-weight: 600; }}
        .leaderboard {{
            background: #111827;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #1f2937;
        }}
        .leaderboard-header {{ font-size: 1.3em; font-weight: 600; margin-bottom: 15px; color: #fbbf24; }}
        .leaderboard-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #1f2937;
        }}
        .leaderboard-row:last-child {{ border-bottom: none; }}
        .leader-trader {{ display: flex; align-items: center; gap: 12px; }}
        .leader-rank {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9em;
        }}
        .leader-name-text {{ font-weight: 600; }}
        .leader-return {{ font-family: 'Courier New', monospace; font-weight: 700; }}
        .progress-bar {{
            height: 4px;
            background: #1f2937;
            border-radius: 2px;
            margin-top: 8px;
            overflow: hidden;
        }}
        .progress-fill {{ height: 100%; border-radius: 2px; transition: width 0.5s ease; }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #64748b;
            border-top: 1px solid #1f2937;
            margin-top: 30px;
        }}
        .update-time {{ font-family: 'Courier New', monospace; }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Trading Arena</h1>
            <p class="subtitle">5 AI Traders Competing Live vs S&P 500</p>
            <span class="market-status market-open">● MARKET OPEN</span>
        </header>

        <div class="card sp500-card">
            <div class="sp500-header">
                <div>
                    <div class="sp500-title">📊 S&P 500 Benchmark</div>
                    <div style="color: #64748b; margin-top: 5px;">Session started: May 11, 2026</div>
                </div>
                <div style="text-align: right;">
                    <div class="sp500-price">{sp500_value:,.2f}</div>
                    <div class="sp500-change {'positive' if sp500_value >= 10000 else 'negative'}">{((sp500_value - 10000) / 100):+.2f}%</div>
                </div>
            </div>
        </div>

        <div class="leaderboard">
            <div class="leaderboard-header">🏆 Live Standings</div>'''

# Add leaderboard rows
for rank, (name, t) in enumerate(sorted_traders, 1):
    start_val = 10000
    current_val = t['current_value']
    return_pct = ((current_val - start_val) / start_val) * 100
    
    rank_class = "rank-1" if rank == 1 else "rank-2" if rank == 2 else "rank-3" if rank == 3 else ""
    rank_style = "" if rank_class else 'style="background: #374151; color: #fff;"'
    return_class = "positive" if return_pct >= 0 else "negative"
    
    emojis = {'Turtle': '🐢', 'Shark': '🦈', 'Owl': '🦉', 'Wolf': '🐺', 'Fox': '🦊'}
    strategies = {'Turtle': 'Trend Following', 'Shark': 'Momentum', 'Owl': 'Value', 'Wolf': 'Sector Rotation', 'Fox': 'Contrarian'}
    
    html_template += f'''
            <div class="leaderboard-row">
                <div class="leader-trader">
                    <div class="leader-rank {rank_class}" {rank_style}>{rank}</div>
                    <span class="leader-name-text">{emojis[name]} {name} ({strategies[name]})</span>
                </div>
                <span class="leader-return {return_class}">{return_pct:+.2f}%</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" style="width: {min(abs(return_pct) * 2, 100)}%; background: {'linear-gradient(90deg, #22c55e, #16a34a)' if return_pct >= 0 else '#ef4444'};"></div></div>'''

html_template += '''
        </div>

        <div class="dashboard-grid">'''

# Add individual trader cards
for rank, (name, t) in enumerate(sorted_traders, 1):
    start_val = 10000
    current_val = t['current_value']
    return_pct = ((current_val - start_val) / start_val) * 100
    vs_sp500 = return_pct - ((sp500_value - 10000) / 100)
    
    rank_class = "rank-1" if rank == 1 else "rank-2" if rank == 2 else "rank-3" if rank == 3 else ""
    return_class = "positive" if return_pct >= 0 else "negative"
    vs_class = "positive" if vs_sp500 >= 0 else "negative"
    
    emojis = {'Turtle': '🐢', 'Shark': '🦈', 'Owl': '🦉', 'Wolf': '🐺', 'Fox': '🦊'}
    strategies = {'Turtle': 'Trend Following', 'Shark': 'Momentum', 'Owl': 'Value', 'Wolf': 'Sector Rotation', 'Fox': 'Contrarian'}
    
    holdings_html = ''.join([f'<span class="ticker">{ticker}</span>' for ticker in t.get('positions', {}).keys()])
    
    # Get latest trade for this trader
    trader_trades = [tr for tr in new_trades if tr['trader'] == name]
    if trader_trades:
        latest = trader_trades[-1]
        action_text = f"<strong>Latest:</strong> {latest['type']} {latest.get('ticker', 'N/A')} - {latest['reason']}"
    else:
        action_text = "<strong>Latest:</strong> Holding position - awaiting signal"
    
    html_template += f'''
            <div class="card">
                <div class="card-header">
                    <div class="trader-name"><span class="emoji">{emojis[name]}</span> {name}</div>
                    <span class="rank {rank_class}">#{rank}</span>
                </div>
                <div class="strategy">{strategies[name]} Strategy</div>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Portfolio Value</div>
                        <div class="metric-value">${current_val:,.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Total Return</div>
                        <div class="metric-value {return_class}">{return_pct:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">vs S&P 500</div>
                        <div class="metric-value {vs_class}">{vs_sp500:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Cash</div>
                        <div class="metric-value">${t.get('cash', 0):,.2f}</div>
                    </div>
                </div>
                <div class="holdings">
                    <div class="holdings-label">Holdings</div>
                    <div class="ticker-list">
                        {holdings_html if holdings_html else '<span style="color: #64748b;">No positions</span>'}
                    </div>
                </div>
                <div class="action">{action_text}</div>
            </div>'''

html_template += f'''
        </div>

        <div class="footer">
            <p>Trading Arena Simulation</p>
            <p class="update-time">Last updated: Friday, May 15, 2026 at 1:00 PM CDT</p>
            <p style="margin-top: 10px; font-size: 0.85em;">Next update: 1:30 PM CDT</p>
        </div>
    </div>
</body>
</html>'''

# Save HTML
with open(r'C:\Users\thadd\OneDrive\Desktop\Spocks Reports\market\trading_arena.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("\n[OK] HTML dashboard updated successfully!")
