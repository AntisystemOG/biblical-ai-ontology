#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Arena Simulation
5 AI traders compete with different strategies vs S&P 500 benchmark
"""

import json
import random
import datetime
import sys
from pathlib import Path

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
TRADERS = {
    "Turtle": {"strategy": "Trend Following", "emoji": "🐢", "color": "#22c55e"},
    "Shark": {"strategy": "Momentum", "emoji": "🦈", "color": "#ef4444"},
    "Owl": {"strategy": "Value", "emoji": "🦉", "color": "#3b82f6"},
    "Wolf": {"strategy": "Sector Rotation", "emoji": "🐺", "color": "#f59e0b"},
    "Fox": {"strategy": "Contrarian", "emoji": "🦊", "color": "#a855f7"},
}

STARTING_CAPITAL = 10000.0
DATA_FILE = Path("C:/Users/thadd/.openclaw/workspace/trading_arena_data.json")
HTML_OUTPUT = Path("C:/Users/thadd/OneDrive/Desktop/Spocks Reports/market/trading_arena.html")

def load_data():
    """Load existing trading data or initialize"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return initialize_data()

def initialize_data():
    """Initialize fresh trading data"""
    now = datetime.datetime.now()
    return {
        "start_date": now.isoformat(),
        "last_update": now.isoformat(),
        "traders": {name: {"cash": STARTING_CAPITAL, "positions": {}, "history": [{"date": now.isoformat(), "value": STARTING_CAPITAL}]} for name in TRADERS},
        "sp500_benchmark": {"value": STARTING_CAPITAL, "history": [{"date": now.isoformat(), "value": STARTING_CAPITAL}]},
        "trades": []
    }

def save_data(data):
    """Save trading data to file"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def simulate_market_movement():
    """Simulate market movements with realistic volatility"""
    # S&P 500 daily movement (roughly -2% to +2% with occasional larger moves)
    sp500_change = random.gauss(0.0005, 0.012)  # Mean slightly positive, 1.2% std dev
    
    # Individual stock movements
    stock_moves = {}
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "BAC"]
    for ticker in tickers:
        # Individual stocks more volatile than market
        stock_moves[ticker] = random.gauss(sp500_change, 0.025)
    
    return sp500_change, stock_moves, tickers

def execute_trader_strategy(name, trader_data, stock_moves, tickers, sp500_change):
    """Execute trading strategy based on trader type"""
    cash = trader_data["cash"]
    positions = trader_data["positions"]
    
    new_trades = []
    
    if name == "Turtle":  # Trend Following
        # Buy stocks that are moving up, sell if going down
        for ticker, change in stock_moves.items():
            if change > 0.015 and cash > 1000:  # Strong uptrend
                buy_amount = min(1000, cash * 0.2)
                shares = buy_amount / 100  # Simulated price
                positions[ticker] = positions.get(ticker, 0) + shares
                cash -= buy_amount
                new_trades.append({"type": "BUY", "ticker": ticker, "amount": buy_amount, "reason": "Uptrend detected"})
            elif change < -0.02 and ticker in positions and positions[ticker] > 0:  # Stop loss
                shares = positions[ticker]
                sell_amount = shares * 100 * (1 + change)
                cash += sell_amount
                del positions[ticker]
                new_trades.append({"type": "SELL", "ticker": ticker, "amount": sell_amount, "reason": "Stop loss triggered"})
    
    elif name == "Shark":  # Momentum
        # Buy highest momentum stocks
        sorted_moves = sorted(stock_moves.items(), key=lambda x: x[1], reverse=True)
        for ticker, change in sorted_moves[:3]:
            if change > 0.01 and cash > 500:
                buy_amount = min(500, cash * 0.15)
                shares = buy_amount / 100
                positions[ticker] = positions.get(ticker, 0) + shares
                cash -= buy_amount
                new_trades.append({"type": "BUY", "ticker": ticker, "amount": buy_amount, "reason": "High momentum"})
    
    elif name == "Owl":  # Value
        # Buy on dips, sell on peaks
        sorted_moves = sorted(stock_moves.items(), key=lambda x: x[1])
        for ticker, change in sorted_moves[:3]:
            if change < -0.01 and cash > 500:  # Buy the dips
                buy_amount = min(500, cash * 0.15)
                shares = buy_amount / 100
                positions[ticker] = positions.get(ticker, 0) + shares
                cash -= buy_amount
                new_trades.append({"type": "BUY", "ticker": ticker, "amount": buy_amount, "reason": "Value opportunity"})
        # Sell winners
        for ticker in list(positions.keys()):
            if stock_moves.get(ticker, 0) > 0.025:
                shares = positions[ticker]
                sell_amount = shares * 100 * (1 + stock_moves[ticker])
                cash += sell_amount
                del positions[ticker]
                new_trades.append({"type": "SELL", "ticker": ticker, "amount": sell_amount, "reason": "Take profits"})
    
    elif name == "Wolf":  # Sector Rotation
        # Rotate between sectors based on market conditions
        sectors = {"TECH": ["AAPL", "MSFT", "GOOGL", "NVDA"], "FINANCE": ["JPM", "BAC", "MA", "V"], "HEALTH": ["JNJ", "UNH", "PG"]}
        sector_performance = {}
        for sector, tickers_list in sectors.items():
            avg_change = sum(stock_moves.get(t, 0) for t in tickers_list) / len(tickers_list)
            sector_performance[sector] = avg_change
        
        best_sector = max(sector_performance, key=sector_performance.get)
        if sector_performance[best_sector] > 0.005:
            for ticker in sectors[best_sector]:
                if cash > 300 and stock_moves.get(ticker, 0) > 0:
                    buy_amount = min(300, cash * 0.1)
                    shares = buy_amount / 100
                    positions[ticker] = positions.get(ticker, 0) + shares
                    cash -= buy_amount
                    new_trades.append({"type": "BUY", "ticker": ticker, "amount": buy_amount, "reason": f"{best_sector} sector strength"})
    
    elif name == "Fox":  # Contrarian
        # Do the opposite - buy what's down, sell what's up
        sorted_moves = sorted(stock_moves.items(), key=lambda x: x[1])
        for ticker, change in sorted_moves[:2]:
            if change < -0.015 and cash > 400:  # Buy when others panic
                buy_amount = min(400, cash * 0.15)
                shares = buy_amount / 100
                positions[ticker] = positions.get(ticker, 0) + shares
                cash -= buy_amount
                new_trades.append({"type": "BUY", "ticker": ticker, "amount": buy_amount, "reason": "Contrarian play"})
        # Sell when euphoric
        for ticker in list(positions.keys()):
            if stock_moves.get(ticker, 0) > 0.03:
                shares = positions[ticker]
                sell_amount = shares * 100 * (1 + stock_moves[ticker])
                cash += sell_amount
                del positions[ticker]
                new_trades.append({"type": "SELL", "ticker": ticker, "amount": sell_amount, "reason": "Contrarian exit"})
    
    return {"cash": cash, "positions": positions}, new_trades

def calculate_portfolio_value(trader_data, stock_moves):
    """Calculate total portfolio value"""
    cash = trader_data.get("cash", 0)
    positions = trader_data.get("positions", {})
    stock_value = 0
    for ticker, shares in positions.items():
        price = 100 * (1 + stock_moves.get(ticker, 0))
        stock_value += shares * price
    return cash + stock_value

def run_simulation():
    """Run one iteration of the trading simulation"""
    data = load_data()
    sp500_change, stock_moves, tickers = simulate_market_movement()
    
    now = datetime.datetime.now()
    
    # Update each trader
    for name in TRADERS:
        trader_data = data["traders"][name]
        updated_data, trades = execute_trader_strategy(name, trader_data, stock_moves, tickers, sp500_change)
        data["traders"][name].update(updated_data)
        
        # Ensure history exists
        if "history" not in data["traders"][name]:
            data["traders"][name]["history"] = [{"date": now.isoformat(), "value": STARTING_CAPITAL}]
        
        # Calculate new value
        new_value = calculate_portfolio_value(updated_data, stock_moves)
        data["traders"][name]["current_value"] = round(new_value, 2)
        data["traders"][name]["history"].append({"date": now.isoformat(), "value": round(new_value, 2)})
        
        # Record trades
        for trade in trades:
            trade["trader"] = name
            trade["time"] = now.isoformat()
            data["trades"].append(trade)
    
    # Update S&P 500 benchmark
    sp500_value = data["sp500_benchmark"]["value"] * (1 + sp500_change)
    data["sp500_benchmark"]["value"] = round(sp500_value, 2)
    data["sp500_benchmark"]["history"].append({"date": now.isoformat(), "value": round(sp500_value, 2)})
    
    data["last_update"] = now.isoformat()
    
    save_data(data)
    return data

def generate_html(data):
    """Generate HTML dashboard"""
    now = datetime.datetime.now()
    
    # Calculate rankings
    rankings = []
    for name, info in TRADERS.items():
        value = data["traders"][name].get("current_value", STARTING_CAPITAL)
        pnl = value - STARTING_CAPITAL
        pnl_pct = (pnl / STARTING_CAPITAL) * 100
        rankings.append({
            "name": name,
            "emoji": info["emoji"],
            "strategy": info["strategy"],
            "color": info["color"],
            "value": value,
            "pnl": pnl,
            "pnl_pct": pnl_pct
        })
    
    rankings.sort(key=lambda x: x["value"], reverse=True)
    
    # Benchmark data
    sp500_value = data["sp500_benchmark"]["value"]
    sp500_pnl = sp500_value - STARTING_CAPITAL
    sp500_pnl_pct = (sp500_pnl / STARTING_CAPITAL) * 100
    
    # Recent trades (last 10)
    recent_trades = data["trades"][-10:][::-1] if data["trades"] else []
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Arena - Live Simulation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid #334155;
            margin-bottom: 30px;
        }}
        h1 {{ font-size: 2.5rem; background: linear-gradient(90deg, #22d3ee, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }}
        .subtitle {{ color: #94a3b8; font-size: 1.1rem; }}
        .last-update {{ color: #64748b; font-size: 0.9rem; margin-top: 10px; }}
        
        .standings-grid {{
            display: grid;
            gap: 15px;
            margin-bottom: 40px;
        }}
        
        .trader-card {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 12px;
            padding: 20px;
            display: grid;
            grid-template-columns: auto 1fr auto auto;
            align-items: center;
            gap: 20px;
            border: 1px solid #334155;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .trader-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 40px rgba(0,0,0,0.3); }}
        .trader-card.rank-1 {{ border-color: #fbbf24; background: linear-gradient(135deg, #1e293b 0%, #292208 100%); }}
        .trader-card.rank-2 {{ border-color: #94a3b8; }}
        .trader-card.rank-3 {{ border-color: #b45309; }}
        
        .rank {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #64748b;
            width: 40px;
            text-align: center;
        }}
        .rank-1 .rank {{ color: #fbbf24; }}
        .rank-2 .rank {{ color: #94a3b8; }}
        .rank-3 .rank {{ color: #b45309; }}
        
        .trader-info {{ display: flex; flex-direction: column; }}
        .trader-name {{ font-size: 1.3rem; font-weight: bold; display: flex; align-items: center; gap: 8px; }}
        .trader-strategy {{ color: #94a3b8; font-size: 0.9rem; margin-top: 2px; }}
        
        .portfolio-value {{ text-align: right; }}
        .value-amount {{ font-size: 1.4rem; font-weight: bold; color: #22d3ee; }}
        .pnl {{ font-size: 0.95rem; margin-top: 4px; }}
        .pnl.positive {{ color: #22c55e; }}
        .pnl.negative {{ color: #ef4444; }}
        
        .benchmark {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 12px;
            padding: 25px;
            border: 2px solid #3b82f6;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .benchmark-label {{ color: #94a3b8; font-size: 0.9rem; }}
        .benchmark-value {{ font-size: 2rem; font-weight: bold; color: #3b82f6; }}
        
        .trades-section {{
            background: #1e293b;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #334155;
        }}
        .section-title {{ font-size: 1.3rem; margin-bottom: 15px; color: #e2e8f0; }}
        
        .trade-row {{
            display: grid;
            grid-template-columns: 60px 1fr 100px 120px auto;
            gap: 15px;
            padding: 12px 0;
            border-bottom: 1px solid #334155;
            align-items: center;
            font-size: 0.95rem;
        }}
        .trade-row:last-child {{ border-bottom: none; }}
        .trade-type {{ font-weight: bold; padding: 4px 10px; border-radius: 4px; text-align: center; font-size: 0.8rem; }}
        .trade-type.BUY {{ background: rgba(34, 197, 94, 0.2); color: #22c55e; }}
        .trade-type.SELL {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; }}
        .trade-reason {{ color: #94a3b8; font-size: 0.85rem; }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
            padding: 20px;
            background: #1e293b;
            border-radius: 8px;
            flex-wrap: wrap;
        }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; color: #94a3b8; }}
        .legend-color {{ width: 12px; height: 12px; border-radius: 50%; }}
        
        @media (max-width: 768px) {{
            .trader-card {{ grid-template-columns: 1fr; text-align: center; }}
            .trade-row {{ grid-template-columns: 1fr; gap: 5px; }}
            .benchmark {{ flex-direction: column; text-align: center; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎪 Trading Arena</h1>
            <p class="subtitle">5 AI Traders Compete with $10,000 Each</p>
            <p class="last-update">Last Updated: {now.strftime('%Y-%m-%d %H:%M:%S CDT')}</p>
        </header>
        
        <div class="standings-grid">
"""
    
    # Add trader cards
    for i, trader in enumerate(rankings, 1):
        pnl_class = "positive" if trader["pnl"] >= 0 else "negative"
        pnl_sign = "+" if trader["pnl"] >= 0 else ""
        
        html += f"""
            <div class="trader-card rank-{i}">
                <div class="rank">#{i}</div>
                <div class="trader-info">
                    <div class="trader-name">
                        <span>{trader["emoji"]}</span>
                        <span style="color: {trader['color']}">{trader['name']}</span>
                    </div>
                    <div class="trader-strategy">{trader['strategy']} Strategy</div>
                </div>
                <div class="portfolio-value">
                    <div class="value-amount">${trader['value']:,.2f}</div>
                    <div class="pnl {pnl_class}">{pnl_sign}${trader['pnl']:,.2f} ({pnl_sign}{trader['pnl_pct']:.2f}%)</div>
                </div>
            </div>
"""
    
    # Add benchmark
    sp500_pnl_class = "positive" if sp500_pnl >= 0 else "negative"
    sp500_pnl_sign = "+" if sp500_pnl >= 0 else ""
    
    html += f"""
        </div>
        
        <div class="benchmark">
            <div>
                <div class="benchmark-label">S&P 500 Benchmark</div>
                <div style="color: #64748b; font-size: 0.85rem;">Buy & Hold Strategy</div>
            </div>
            <div style="text-align: right;">
                <div class="benchmark-value">${sp500_value:,.2f}</div>
                <div class="pnl {sp500_pnl_class}">{sp500_pnl_sign}${sp500_pnl:,.2f} ({sp500_pnl_sign}{sp500_pnl_pct:.2f}%)</div>
            </div>
        </div>
        
        <div class="trades-section">
            <h2 class="section-title">📊 Recent Trades</h2>
"""
    
    if recent_trades:
        for trade in recent_trades:
            trader_info = TRADERS.get(trade.get('trader', ''), {})
            html += f"""
            <div class="trade-row">
                <div class="trade-type {trade.get('type', 'BUY')}">{trade.get('type', 'BUY')}</div>
                <div><strong>{trade.get('ticker', 'N/A')}</strong> <span class="trade-reason">- {trade.get('reason', 'N/A')}</span></div>
                <div style="text-align: right;">${trade.get('amount', 0):,.0f}</div>
                <div style="color: {trader_info.get('color', '#888')}; text-align: right;">{trader_info.get('emoji', '🤖')} {trade.get('trader', 'Unknown')}</div>
                <div style="color: #64748b; font-size: 0.8rem;">{trade.get('time', '')[11:16] if trade.get('time') else 'N/A'}</div>
            </div>
"""
    else:
        html += '<p style="color: #64748b; text-align: center; padding: 20px;">No trades yet today</p>'
    
    html += f"""
        </div>
        
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background: #22c55e;"></div> 🐢 Turtle - Trend Following</div>
            <div class="legend-item"><div class="legend-color" style="background: #ef4444;"></div> 🦈 Shark - Momentum</div>
            <div class="legend-item"><div class="legend-color" style="background: #3b82f6;"></div> 🦉 Owl - Value</div>
            <div class="legend-item"><div class="legend-color" style="background: #f59e0b;"></div> 🐺 Wolf - Sector Rotation</div>
            <div class="legend-item"><div class="legend-color" style="background: #a855f7;"></div> 🦊 Fox - Contrarian</div>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Main entry point"""
    print("Trading Arena Simulation")
    print("=" * 40)
    
    # Ensure output directory exists
    HTML_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    # Run simulation
    data = run_simulation()
    
    # Generate HTML
    html = generate_html(data)
    
    # Write HTML file
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nSimulation complete!")
    print(f"Dashboard updated: {HTML_OUTPUT}")
    print(f"Data saved: {DATA_FILE}")
    
    # Print standings
    print("\nCurrent Standings:")
    print("-" * 40)
    rankings = [(name, data["traders"][name].get("current_value", STARTING_CAPITAL)) for name in TRADERS]
    rankings.sort(key=lambda x: x[1], reverse=True)
    for i, (name, value) in enumerate(rankings, 1):
        pnl = value - STARTING_CAPITAL
        pnl_pct = (pnl / STARTING_CAPITAL) * 100
        emoji = TRADERS[name]["emoji"]
        print(f"  #{i} {emoji} {name}: ${value:,.2f} ({pnl:+.2f}, {pnl_pct:+.2f}%)")
    
    sp500_val = data["sp500_benchmark"]["value"]
    sp500_pnl = sp500_val - STARTING_CAPITAL
    sp500_pct = (sp500_pnl / STARTING_CAPITAL) * 100
    print(f"  S&P 500: ${sp500_val:,.2f} ({sp500_pnl:+.2f}, {sp500_pct:+.2f}%)")
    
    return True

if __name__ == "__main__":
    main()
