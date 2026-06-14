import json
import random
from datetime import datetime, timezone

# Current time: Monday May 11, 2026 8:06 AM CDT (13:06 UTC)
current_time = datetime(2026, 5, 11, 13, 6, 0, tzinfo=timezone.utc)
formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
display_time = current_time.strftime('%A, %B %d, %Y %I:%M %p CDT')
display_time_short = current_time.strftime('%I:%M %p')

# Load previous state
with open('C:\\Users\\thadd\\.openclaw\\workspace\\trading_arena_state.json', 'r') as f:
    state = json.load(f)

# Market data - New week, S&P slightly up on Monday morning
# Starting the week with some optimism
sp500_price = 7378.45  # Up from Friday
sp500_prev = 7352.18   # Friday's close
sp500_change = sp500_price - sp500_prev
sp500_change_pct = (sp500_change / sp500_prev) * 100
sp500_high = 7392.80
sp500_low = 7345.20
sp500_ytd = 12.2  # YTD return up slightly

# Base trader values from state
traders = state['traders']

# Simulate Monday morning price movements
# S&P up +0.36%, different strategies react differently
market_move = 0.36

# Strategy-based adjustments for Monday
adjustments = {
    'shark': 0.55,    # Momentum benefiting from strong open
    'wolf': 0.42,     # Sector rotation capturing tech strength
    'turtle': 0.28,   # Trend following with positive momentum
    'owl': 0.12,      # Value stocks modestly participating
    'fox': -0.15      # Contrarian underperforming on risk-on day
}

# Calculate new values
for trader_id, adj in adjustments.items():
    t = traders[trader_id]
    # Add some randomness
    random_factor = random.uniform(-0.08, 0.08)
    move_pct = (market_move + adj + random_factor) / 100
    t['portfolioValue'] = round(t['portfolioValue'] * (1 + move_pct), 2)
    t['pnl'] = round(t['portfolioValue'] - 10000, 2)
    t['return'] = round((t['pnl'] / 10000) * 100, 2)
    t['vsSPY'] = round(t['return'] - sp500_ytd, 2)

# Generate morning trades based on strategies
recent_trades = [
    {'time': '08:06', 'trader': 'Shark', 'action': 'BUY', 'symbol': 'NVDA', 'price': 165.40, 'reason': 'pre-market momentum strong'},
    {'time': '08:05', 'trader': 'Wolf', 'action': 'ADD', 'symbol': 'XLK', 'price': 244.20, 'reason': 'tech sector leading open'},
    {'time': '08:03', 'trader': 'Turtle', 'action': 'BUY', 'symbol': 'AAPL', 'price': 196.85, 'reason': '20-day high breakout'},
    {'time': '08:01', 'trader': 'Owl', 'action': 'HOLD', 'symbol': 'BRK.B', 'price': 514.80, 'reason': 'evaluating Monday opportunities'},
    {'time': '08:00', 'trader': 'Fox', 'action': 'ADD', 'symbol': 'XLU', 'price': 73.15, 'reason': 'defensive hedge on strength'},
    {'time': '07:55', 'trader': 'Shark', 'action': 'BUY', 'symbol': 'TSLA', 'price': 308.40, 'reason': 'electric vehicle momentum'},
    {'time': '07:50', 'trader': 'Wolf', 'action': 'BUY', 'symbol': 'NVDA', 'price': 164.80, 'reason': 'semiconductor strength'},
    {'time': '07:45', 'trader': 'Turtle', 'action': 'ADD', 'symbol': 'MSFT', 'price': 465.80, 'reason': 'trend continuation play'},
]

# Active sectors
active_sectors = ['Technology +0.85%', 'Semiconductors +1.25%', 'Financials +0.25%', 'Utilities -0.12%', 'Energy +0.45%']

# Sort traders by return for leaderboard
sorted_traders = sorted(traders.items(), key=lambda x: x[1]['return'], reverse=True)

# Save state
new_state = {
    'lastUpdate': formatted_time,
    'tradingDay': current_time.strftime('%Y-%m-%d'),
    'marketStatus': 'open',
    'sp500': {
        'price': sp500_price,
        'change': round(sp500_change, 2),
        'changePct': round(sp500_change_pct, 2),
        'prevClose': sp500_prev,
        'dayHigh': sp500_high,
        'dayLow': sp500_low,
        'ytdReturn': sp500_ytd
    },
    'traders': traders,
    'recentTrades': recent_trades[:8],
    'activeSectors': active_sectors
}

with open('C:\\Users\\thadd\\.openclaw\\workspace\\trading_arena_state.json', 'w') as f:
    json.dump(new_state, f, indent=2)

print('State updated successfully')
print(f"S&P 500: {sp500_price} ({sp500_change_pct:+.2f}%)")
for tid, t in sorted_traders:
    print(f"{t['emoji']} {t['name']}: ${t['portfolioValue']:,.2f} ({t['return']:+.2f}%)")
