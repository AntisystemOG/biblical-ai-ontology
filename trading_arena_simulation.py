import json
import random
from datetime import datetime, timezone

# Current time: Thursday May 7, 2026 2:35 PM CDT (19:35 UTC)
current_time = datetime.now(timezone.utc)
formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
display_time = current_time.strftime('%A, %B %d, %Y %I:%M %p CDT')
display_time_short = current_time.strftime('%I:%M %p')

# Market data (simulated based on recent trends - S&P slightly down from yesterday)
sp500_price = 7352.18  # Slight pullback from record highs
sp500_prev = 7365.09   # Yesterday's close
sp500_change = sp500_price - sp500_prev
sp500_change_pct = (sp500_change / sp500_prev) * 100
sp500_high = 7375.50
sp500_low = 7325.20
sp500_ytd = 11.8

# Base trader values from previous state (will evolve based on strategies)
traders = {
    'shark': {
        'name': 'Shark',
        'emoji': '🦈',
        'strategy': 'Momentum',
        'portfolioValue': 12345.67,
        'return': 23.46,
        'vsSPY': 22.00,
        'pnl': 2345.67,
        'holdings': ['NVDA', 'TSLA', 'AMD', 'AVGO', 'TSM'],
        'color': 'linear-gradient(135deg, #06b6d4, #0891b2)'
    },
    'wolf': {
        'name': 'Wolf',
        'emoji': '🐺',
        'strategy': 'Sector Rotation',
        'portfolioValue': 11924.56,
        'return': 19.25,
        'vsSPY': 17.79,
        'pnl': 1924.56,
        'holdings': ['XLF', 'XLK', 'XLI', 'NVDA'],
        'color': 'linear-gradient(135deg, #f59e0b, #d97706)'
    },
    'turtle': {
        'name': 'Turtle',
        'emoji': '🐢',
        'strategy': 'Trend Following',
        'portfolioValue': 11542.80,
        'return': 15.43,
        'vsSPY': 13.97,
        'pnl': 1542.80,
        'holdings': ['AAPL', 'MSFT', 'NVDA', 'QQQ'],
        'color': 'linear-gradient(135deg, #22c55e, #15803d)'
    },
    'owl': {
        'name': 'Owl',
        'emoji': '🦉',
        'strategy': 'Value Investing',
        'portfolioValue': 10891.35,
        'return': 8.91,
        'vsSPY': 7.45,
        'pnl': 891.35,
        'holdings': ['BRK.B', 'WFC', 'JPM', 'BAC'],
        'color': 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
    },
    'fox': {
        'name': 'Fox',
        'emoji': '🦊',
        'strategy': 'Contrarian',
        'portfolioValue': 10124.88,
        'return': 1.25,
        'vsSPY': -0.21,
        'pnl': 124.88,
        'holdings': ['XLU', 'XLE', 'CVX', 'TLT'],
        'color': 'linear-gradient(135deg, #ec4899, #db2777)'
    }
}

# Simulate price movements based on strategies
# Market slightly down (-0.18%), but momentum strategies still working
market_move = -0.18

# Strategy-based adjustments
adjustments = {
    'shark': 0.35,    # Momentum benefiting from AMD/chip surge
    'wolf': 0.22,     # Tech rotation helping
    'turtle': 0.15,   # Trend following steady
    'owl': -0.08,     # Value lagging in momentum market
    'fox': -0.12      # Contrarian hurting as market hits highs
}

# Calculate new values
for trader_id, adj in adjustments.items():
    t = traders[trader_id]
    move_pct = (market_move + adj) / 100
    t['portfolioValue'] = round(t['portfolioValue'] * (1 + move_pct), 2)
    t['pnl'] = round(t['portfolioValue'] - 10000, 2)
    t['return'] = round((t['pnl'] / 10000) * 100, 2)
    t['vsSPY'] = round(t['return'] - sp500_ytd, 2)

# Generate trades based on strategies
recent_trades = [
    {'time': '14:30', 'trader': 'Shark', 'action': 'ADD', 'symbol': 'TSM', 'price': 198.85, 'reason': 'chip momentum extending'},
    {'time': '14:24', 'trader': 'Wolf', 'action': 'ADD', 'symbol': 'AMD', 'price': 133.15, 'reason': 'semiconductor sector surge'},
    {'time': '14:18', 'trader': 'Turtle', 'action': 'HOLD', 'symbol': 'QQQ', 'price': 513.20, 'reason': 'Nasdaq trend intact'},
    {'time': '14:12', 'trader': 'Owl', 'action': 'BUY', 'symbol': 'CVX', 'price': 152.40, 'reason': 'energy value opportunity'},
    {'time': '14:06', 'trader': 'Fox', 'action': 'ADD', 'symbol': 'XLU', 'price': 72.85, 'reason': 'defensive positioning'},
    {'time': '14:00', 'trader': 'Shark', 'action': 'ADD', 'symbol': 'NVDA', 'price': 163.20, 'reason': 'AI chip demand surge'},
    {'time': '13:54', 'trader': 'Wolf', 'action': 'BUY', 'symbol': 'XLK', 'price': 242.55, 'reason': 'tech sector rotation'},
    {'time': '13:48', 'trader': 'Turtle', 'action': 'ADD', 'symbol': 'MSFT', 'price': 463.15, 'reason': 'uptrend continuation'},
    {'time': '13:42', 'trader': 'Owl', 'action': 'HOLD', 'symbol': 'BRK.B', 'price': 512.40, 'reason': 'value thesis unchanged'},
    {'time': '13:36', 'trader': 'Fox', 'action': 'BUY', 'symbol': 'TLT', 'price': 89.45, 'reason': 'rates pullback play'}
]

# Active sectors
active_sectors = ['Technology +0.45%', 'Semiconductors +1.85%', 'Financials -0.32%', 'Utilities +0.18%', 'Energy -0.65%']

# Sort traders by return for leaderboard
sorted_traders = sorted(traders.items(), key=lambda x: x[1]['return'], reverse=True)

# Save state
state = {
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
    json.dump(state, f, indent=2)

print('State updated successfully')
print(f'S&P 500: {sp500_price} ({sp500_change_pct:+.2f}%)')
for tid, t in sorted_traders:
    print(f"{t['emoji']} {t['name']}: ${t['portfolioValue']:,.2f} ({t['return']:+.2f}%)")
