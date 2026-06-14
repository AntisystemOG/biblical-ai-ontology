import json
from datetime import datetime, timezone

# Load the current state
with open('C:\\Users\\thadd\\.openclaw\\workspace\\trading_arena_state.json', 'r') as f:
    state = json.load(f)

current_time = datetime.now(timezone.utc)
display_time = current_time.strftime('%A, %B %d, %Y %I:%M %p CDT')

sp = state['sp500']
traders = state['traders']
recent_trades = state['recentTrades']
active_sectors = state['activeSectors']

# Sort traders by return
sorted_traders = sorted(traders.items(), key=lambda x: x[1]['return'], reverse=True)

# Rank classes for leaderboard
def get_rank_class(rank):
    if rank == 0:
        return 'rank-1'
    elif rank == 1:
        return 'rank-2'
    elif rank == 2:
        return 'rank-3'
    return ''

def fmt(value):
    return f"{value:,.2f}"

def fmt_ret(value):
    sign = '+' if value >= 0 else ''
    return f"{sign}{value:.2f}%"

def fmt_pnl(value):
    sign = '+' if value >= 0 else ''
    return f"{sign}${abs(value):,.2f}"

def pos_neg_class(value):
    if value > 0:
        return 'positive'
    elif value < 0:
        return 'negative'
    return 'neutral'

# Build trader cards HTML
trader_cards_html = ""
for tid, t in sorted_traders:
    trader_cards_html += f'''
            <!-- {t['name']} - {t['strategy']} -->
            <div class="trader-card">
                <div class="trader-header">
                    <div class="trader-avatar" style="background: {t['color']};">{t['emoji']}</div>
                    <div class="trader-info">
                        <h3>{t['name']}</h3>
                        <span class="trader-strategy">{t['strategy']}</span>
                    </div>
                </div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-label">Portfolio Value</div>
                        <div class="stat-value">${fmt(t['portfolioValue'])}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Return</div>
                        <div class="stat-value {pos_neg_class(t['return'])}">{fmt_ret(t['return'])}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">vs S&P 500</div>
                        <div class="stat-value {pos_neg_class(t['vsSPY'])}">{fmt_ret(t['vsSPY'])}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">P&L</div>
                        <div class="stat-value {pos_neg_class(t['pnl'])}">{fmt_pnl(t['pnl'])}</div>
                    </div>
                </div>
            </div>
'''

# Build leaderboard HTML
leaderboard_html = ""
for rank, (tid, t) in enumerate(sorted_traders):
    rank_class = get_rank_class(rank)
    leaderboard_html += f'''
            <div class="leaderboard-row">
                <span class="rank {rank_class}">{rank + 1}</span>
                <span class="leader-name">{t['emoji']} {t['name']} ({t['strategy']})</span>
                <span class="leader-return {pos_neg_class(t['return'])}">{fmt_ret(t['return'])}</span>
                <span class="leader-pnl {pos_neg_class(t['pnl'])}">{fmt_pnl(t['pnl'])}</span>
            </div>
'''

# Build trade log HTML
trade_log_html = ""
for trade in recent_trades[:10]:
    action_class = trade['action'].lower()
    emoji_map = {
        'Shark': '🦈',
        'Wolf': '🐺', 
        'Turtle': '🐢',
        'Owl': '🦉',
        'Fox': '🦊'
    }
    trade_log_html += f'''
            <div class="log-entry">
                <span class="log-time">{trade['time']}</span>
                <span class="log-trader">{emoji_map.get(trade['trader'], '')} {trade['trader']}</span>
                <span class="log-action"><span class="{action_class}">{trade['action']}</span> {trade['symbol']} @ ${trade['price']} ({trade['reason']})</span>
            </div>
'''

# Market status note
market_note = "Pullback from record highs, semiconductors resilient"

# Full HTML template
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Arena - Live AI Simulation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #1a1a2e;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #888;
            font-size: 1.1rem;
        }}
        .last-updated {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 10px;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .trader-card {{
            background: linear-gradient(145deg, #1a1a2e, #16213e);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #2a2a4a;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .trader-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
        }}
        .trader-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .trader-avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
        }}
        .trader-info h3 {{
            font-size: 1.3rem;
            margin-bottom: 4px;
        }}
        .trader-strategy {{
            font-size: 0.85rem;
            color: #888;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .stat-box {{
            background: rgba(0,0,0,0.3);
            padding: 12px;
            border-radius: 8px;
        }}
        .stat-label {{
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .stat-value {{
            font-size: 1.2rem;
            font-weight: 600;
        }}
        .positive {{ color: #4ade80; }}
        .negative {{ color: #f87171; }}
        .neutral {{ color: #94a3b8; }}
        .benchmark-section {{
            background: linear-gradient(145deg, #1e3a5f, #0f2744);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid #2a5a8a;
        }}
        .benchmark-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .benchmark-title {{
            font-size: 1.5rem;
            color: #60a5fa;
        }}
        .sp500-badge {{
            background: #2563eb;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
        }}
        .leaderboard {{
            background: #0f0f1a;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #2a2a4a;
        }}
        .leaderboard-title {{
            font-size: 1.4rem;
            margin-bottom: 20px;
            text-align: center;
        }}
        .leaderboard-row {{
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #2a2a4a;
        }}
        .leaderboard-row:last-child {{
            border-bottom: none;
        }}
        .rank {{
            width: 40px;
            font-size: 1.2rem;
            font-weight: bold;
        }}
        .rank-1 {{ color: #ffd700; }}
        .rank-2 {{ color: #c0c0c0; }}
        .rank-3 {{ color: #cd7f32; }}
        .leader-name {{
            flex: 1;
            font-weight: 500;
        }}
        .leader-return {{
            font-weight: 600;
            margin-right: 15px;
        }}
        .leader-pnl {{
            width: 100px;
            text-align: right;
        }}
        .trade-log {{
            background: #0f0f1a;
            border-radius: 16px;
            padding: 24px;
            margin-top: 30px;
            border: 1px solid #2a2a4a;
        }}
        .log-entry {{
            display: flex;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #2a2a4a;
            font-size: 0.9rem;
        }}
        .log-time {{
            color: #666;
            width: 80px;
            font-size: 0.8rem;
        }}
        .log-trader {{
            width: 90px;
            font-weight: 500;
        }}
        .log-action {{
            flex: 1;
        }}
        .buy {{ color: #4ade80; }}
        .sell {{ color: #f87171; }}
        .hold {{ color: #94a3b8; }}
        .add {{ color: #60a5fa; }}
        .market-status {{
            background: rgba(74, 222, 128, 0.1);
            border: 1px solid rgba(74, 222, 128, 0.3);
            border-radius: 8px;
            padding: 10px 16px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
        }}
        .market-status.closed {{
            background: rgba(248, 113, 113, 0.1);
            border-color: rgba(248, 113, 113, 0.3);
        }}
        .market-dot {{
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        .market-status.closed .market-dot {{
            background: #f87171;
            animation: none;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8rem; }}
            .dashboard {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Trading Arena</h1>
            <p class="subtitle">5 AI Traders Competing Live vs S&P 500</p>
            <p class="last-updated">Last Updated: {display_time}</p>
            <div style="margin-top: 15px;">
                <span class="market-status">
                    <span class="market-dot"></span>
                    Market Open - {market_note}
                </span>
            </div>
        </header>

        <div class="benchmark-section">
            <div class="benchmark-header">
                <h2 class="benchmark-title">S&P 500 Benchmark</h2>
                <span class="sp500-badge">{fmt(sp['price'])} ({fmt_ret(sp['changePct'])})</span>
            </div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Previous Close</div>
                    <div class="stat-value neutral">{fmt(sp['prevClose'])}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Day High</div>
                    <div class="stat-value positive">{fmt(sp['dayHigh'])}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Day Low</div>
                    <div class="stat-value">{fmt(sp['dayLow'])}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">YTD Return</div>
                    <div class="stat-value positive">+{sp['ytdReturn']}%</div>
                </div>
            </div>
        </div>

        <div class="dashboard">
{trader_cards_html}
        </div>

        <div class="leaderboard">
            <h2 class="leaderboard-title">Live Leaderboard</h2>
{leaderboard_html}
            <div class="leaderboard-row" style="background: rgba(37, 99, 235, 0.1); margin-top: 10px; padding: 15px; border-radius: 8px;">
                <span class="rank">&#128202;</span>
                <span class="leader-name">S&P 500 Benchmark</span>
                <span class="leader-return positive">+{sp['ytdReturn']}%</span>
                <span class="leader-pnl">—</span>
            </div>
        </div>

        <div class="trade-log">
            <h2 class="leaderboard-title">Recent Trading Activity</h2>
{trade_log_html}
        </div>
    </div>

    <script>
        // Market data snapshot (embedded for file:// protocol compatibility)
        const marketData = {json.dumps(state, indent=2)};

        // Auto-refresh indicator
        console.log('Trading Arena loaded. Market data current as of:', marketData.lastUpdate);
        console.log('Active sectors:', marketData.activeSectors.join(', '));
    </script>
</body>
</html>
'''

# Write HTML file
with open('C:\\Users\\thadd\\OneDrive\\Desktop\\Spocks Reports\\market\\trading_arena.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML dashboard updated successfully!")
print(f"S&P 500: ${sp['price']:,.2f} ({sp['changePct']:+.2f}%)")
print("\nLeaderboard:")
for rank, (tid, t) in enumerate(sorted_traders):
    print(f"{rank+1}. {t['name']}: ${t['portfolioValue']:,.2f} ({t['return']:+.2f}%)")
