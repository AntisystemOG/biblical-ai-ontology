import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
STARTING_CAPITAL = 10000
TRADERS = {
    "Turtle": {"strategy": "Trend", "color": "#4CAF50"},
    "Shark": {"strategy": "Momentum", "color": "#2196F3"},
    "Owl": {"strategy": "Value", "color": "#9C27B0"},
    "Wolf": {"strategy": "Sector Rotation", "color": "#F44336"},
    "Fox": {"strategy": "Contrarian", "color": "#FF9800"},
}
ASSETS = ["SPY", "QQQ", "GLD", "TLT", "VIX"]
DATE = datetime(2026, 8, 12)

def generate_market_data(days=30):
    """Generates mock market data leading up to and including Aug 12, 2026."""
    data = {}
    for asset in ASSETS:
        start_price = {"SPY": 500, "QQQ": 400, "GLD": 200, "TLT": 100, "VIX": 20}[asset]
        prices = []
        current = start_price
        for _ in range(days):
            # Random walk with slight drift
            drift = 0.0002 if asset != "VIX" else -0.0001
            vol = 0.015 if asset != "VIX" else 0.05
            change = current * (drift + random.gauss(0, vol))
            current += change
            prices.append(current)
        data[asset] = prices
    
    dates = [DATE - timedelta(days=days-i-1) for i in range(days)]
    return pd.DataFrame(data, index=dates)

class AITrader:
    def __init__(self, name, strategy, color):
        self.name = name
        self.strategy = strategy
        self.color = color
        self.capital = STARTING_CAPITAL
        self.portfolio = {asset: 0 for asset in ASSETS}
        self.pnl_history = []

    def decide(self, current_date, market_df):
        """Trading logic based on strategy."""
        # Get recent window for indicators
        idx = market_df.index.get_loc(current_date)
        if idx < 5: return # Need history
        
        prices = market_df.iloc[idx]
        prev_prices = market_df.iloc[idx-5:idx]
        
        # Mock signals based on strategy
        signal = 0 # -1 Sell, 0 Hold, 1 Buy
        asset_to_trade = "SPY"

        if self.strategy == "Trend":
            # Simple moving average crossover logic (mock)
            if prices["SPY"] > prev_prices["SPY"].mean(): signal = 1
            else: signal = -1
        elif self.strategy == "Momentum":
            # Buy what is going up fastest
            asset_to_trade = prev_prices.pct_change().iloc[-1].idxmax()
            signal = 1 if prev_prices[asset_to_trade].iloc[-1] > prev_prices[asset_to_trade].iloc[0] else -1
        elif self.strategy == "Value":
            # Buy what is 'undervalued' (relative to its own mean)
            asset_to_trade = prev_prices.mean().idxmin() 
            signal = 1 if prices[asset_to_trade] < prev_prices[asset_to_trade].mean() else -1
        elif self.strategy == "Sector Rotation":
            # Switch assets based on relative strength
            asset_to_trade = random.choice(["QQQ", "GLD", "TLT"])
            signal = 1 if random.random() > 0.5 else -1
        elif self.strategy == "Contrarian":
            # Buy the dip, sell the rip
            if prices["SPY"] < prev_prices["SPY"].min(): signal = 1
            elif prices["SPY"] > prev_prices["SPY"].max(): signal = -1

        self.execute_trade(asset_to_trade, signal, prices[asset_to_trade])

    def execute_trade(self, asset, signal, price):
        # Simple fixed-size trading for simulation
        trade_amount = 1000 # $1000 per trade
        if signal == 1 and self.capital >= trade_amount:
            shares = trade_amount / price
            self.portfolio[asset] += shares
            self.capital -= trade_amount
        elif signal == -1 and self.portfolio[asset] > 0:
            shares = self.portfolio[asset]
            self.capital += shares * price
            self.portfolio[asset] = 0

    def get_total_value(self, current_prices):
        asset_value = sum(self.portfolio[asset] * current_prices[asset] for asset in ASSETS)
        return self.capital + asset_value

def run_simulation():
    market_df = generate_market_data(30)
    traders = [AITrader(name, info["strategy"], info["color"]) for name, info in TRADERS.items()]
    
    # Simulation loop
    for date in market_df.index:
        for trader in traders:
            trader.decide(date, market_df)
            trader.pnl_history.append(trader.get_total_value(market_df.loc[date]))
    
    # Benchmarking (Buy and Hold SPY)
    spy_start = market_df["SPY"].iloc[0]
    spy_end = market_df["SPY"].iloc[-1]
    benchmark_return = (spy_end / spy_start) - 1
    benchmark_final = STARTING_CAPITAL * (1 + benchmark_return)

    # Final Standings
    results = []
    for t in traders:
        final_val = t.get_total_value(market_df.iloc[-1])
        results.append({
            "Name": t.name,
            "Strategy": t.strategy,
            "FinalValue": final_val,
            "PnL": final_val - STARTING_CAPITAL,
            "Return": (final_val / STARTING_CAPITAL - 1) * 100,
            "Color": t.color,
            "History": t.pnl_history
        })
    
    return results, benchmark_final, market_df

def generate_html(results, benchmark_final):
    # Sort by PnL
    sorted_results = sorted(results, key=lambda x: x["FinalValue"], reverse=True)
    
    rows = ""
    for i, r in enumerate(sorted_results):
        rows += f'''
        <tr>
            <td>{i+1}</td>
            <td><span style="color:{r['Color']}; font-weight:bold;">{r['Name']}</span></td>
            <td>{r['Strategy']}</td>
            <td>${r['FinalValue']:,.2f}</td>
            <td style="color:{'green' if r['PnL'] >= 0 else 'red'}">${r['PnL']:,.2f}</td>
            <td style="color:{'green' if r['Return'] >= 0 else 'red'}">{r['Return']:.2f}%</td>
        </tr>
        '''

    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading Arena - Aug 12, 2026</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 40px; }}
            .container {{ max-width: 1000px; margin: auto; background: #1e1e1e; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            h1 {{ text-align: center; color: #fff; margin-bottom: 10px; }}
            .date {{ text-align: center; color: #888; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ background-color: #252525; color: #aaa; text-transform: uppercase; font-size: 12px; }}
            .benchmark {{ margin-top: 30px; padding: 20px; background: #252525; border-left: 5px solid #aaa; font-size: 18px; }}
            .highlight {{ color: #ffd700; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏆 Trading Arena Simulation</h1>
            <div class="date">Market Report: August 12, 2026</div>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Trader</th>
                        <th>Strategy</th>
                        <th>Final Capital</th>
                        <th>PnL</th>
                        <th>Return</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <div class="benchmark">
                S&P 500 Benchmark (Buy & Hold): <span class="highlight">${benchmark_final:,.2f}</span>
            </div>
        </div>
    </body>
    </html>
    '''
    return html_content

if __name__ == "__main__":
    results, benchmark, market_df = run_simulation()
    html = generate_html(results, benchmark)
    
    output_path = r"C:\Users\thadd\OneDrive\Desktop\Spocks Reports\market\trading_arena.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Simulation complete. Dashboard saved to: {output_path}")
