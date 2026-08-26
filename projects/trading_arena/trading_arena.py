#!/usr/bin/env python3
"""Trading Arena — live simulation dashboard."""
import json, os, math, random, urllib.request, urllib.error
from datetime import datetime, timezone, time
from pathlib import Path

# --- Config ---
AGENTS = ['Turtle', 'Shark', 'Owl', 'Wolf', 'Fox']
START_CAPITAL = 10_000.0
BENCHMARK = 'SPY'
UNIVERSE = {
    'trend': ['QQQ', 'SPY', 'IWM', 'XLK', 'XLF'],
    'momentum': ['NVDA', 'TSLA', 'PLTR', 'COIN', 'RBLX'],
    'value': ['JPM', 'BRK-B', 'XOM', 'UNH', 'PG'],
    'rotation': ['XLE', 'XLF', 'XLI', 'XLU', 'XLK', 'XLP', 'XBI'],
    'contrarian': ['GME', 'AMC', 'TLRY', 'HOOD', 'AAL'],
}
HISTORY_DAYS = 60
DATA_DIR = Path(__file__).with_suffix('').parent / 'data'
OUT_PATH = Path('C:/Users/thadd/OneDrive/Desktop/Spocks Reports/market/trading_arena.html')
PRICE_FILE = DATA_DIR / 'prices.json'
STATE_FILE = DATA_DIR / 'state.json'

DATA_DIR.mkdir(exist_ok=True)

# --- Market hours check ---
def _get_chicago_now():
    utc = datetime.now(timezone.utc)
    try:
        import zoneinfo
        return utc.astimezone(zoneinfo.ZoneInfo('America/Chicago'))
    except Exception:
        from datetime import timedelta
        offset = -5 if utc.month > 3 and utc.month < 11 else -6
        return utc.astimezone(timezone(timedelta(hours=offset)))

def market_open_now():
    now = _get_chicago_now()
    if now.weekday() >= 5:
        return False
    # Holidays: basic US market holidays 2026
    holidays = {
        '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03',
        '2026-05-25', '2026-07-03', '2026-09-07', '2026-11-26',
        '2026-12-25'
    }
    if now.strftime('%Y-%m-%d') in holidays:
        return False
    t = now.time()
    return time(8, 30) <= t <= time(15, 0)

# --- Data fetch ---
def fetch_chart(symbol, interval='1d', range_='3mo'):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'{symbol}: {e.code} {e.reason}')

def parse_ohlc(result):
    timestamps = result['timestamp']
    q = result['indicators']['quote'][0]
    series = []
    for i, t in enumerate(timestamps):
        if q['close'][i] is not None:
            series.append({
                'ts': t,
                'open': q['open'][i],
                'high': q['high'][i],
                'low': q['low'][i],
                'close': q['close'][i],
                'volume': q['volume'][i] if q.get('volume') else None,
            })
    return series

def fetch_prices():
    all_syms = sorted({BENCHMARK} | set(v for group in UNIVERSE.values() for v in group))
    prices = {}
    for sym in all_syms:
        try:
            data = fetch_chart(sym, interval='1d', range_='3mo')
            prices[sym] = parse_ohlc(data['chart']['result'][0])
            print(f'Fetched {sym}: {len(prices[sym])} days, last close {prices[sym][-1]["close"]}')
        except Exception as e:
            print(f'WARN: {sym} failed: {e}')
    return prices

def load_or_fetch_prices():
    if PRICE_FILE.exists():
        with open(PRICE_FILE) as f:
            prices = json.load(f)
        # Refresh if last bar older than today in Chicago
        today = _get_chicago_now().date().isoformat()
        last_date = datetime.utcfromtimestamp(prices[BENCHMARK][-1]['ts']).strftime('%Y-%m-%d')
        if last_date == today and len(prices.get(BENCHMARK, [])) > 30:
            return prices
    prices = fetch_prices()
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f)
    return prices

# --- Indicators ---
def ema(series, period):
    k = 2 / (period + 1)
    out = [None] * (period - 1) + [sum(series[:period]) / period]
    for v in series[period:]:
        out.append(v * k + out[-1] * (1 - k))
    return out

def sma(series, period):
    out = []
    for i in range(len(series)):
        if i + 1 < period:
            out.append(None)
        else:
            out.append(sum(series[i + 1 - period:i + 1]) / period)
    return out

def rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        gains.append(max(ch, 0))
        losses.append(max(-ch, 0))
    out = [None] * period
    for i in range(period, len(gains)):
        avg_g = sum(gains[i - period:i]) / period
        avg_l = sum(losses[i - period:i]) / period
        rs = avg_g / avg_l if avg_l else float('inf')
        out.append(100 - 100 / (1 + rs))
    return out

def analyze(prices):
    indicators = {}
    for sym, bars in prices.items():
        closes = [b['close'] for b in bars]
        if len(closes) < 50:
            continue
        indicators[sym] = {
            'price': closes[-1],
            'prev': closes[-2],
            'sma20': sma(closes, 20)[-1],
            'sma50': sma(closes, 50)[-1],
            'ema12': ema(closes, 12)[-1],
            'ema26': ema(closes, 26)[-1],
            'rsi': rsi(closes)[-1],
            'high20': max(closes[-20:]),
            'low20': min(closes[-20:]),
            'high50': max(closes[-50:]),
            'low50': min(closes[-50:]),
            'volatility': (max(closes[-20:]) - min(closes[-20:])) / min(closes[-20:]) if min(closes[-20:]) else 0,
            'returns_5d': (closes[-1] - closes[-6]) / closes[-6] if len(closes) >= 6 else 0,
            'returns_20d': (closes[-1] - closes[-21]) / closes[-21] if len(closes) >= 21 else 0,
        }
    return indicators

# --- Agent strategies ---
def turtle_signal(sym, ind):
    if ind['price'] >= ind['high20']:
        return 1.0
    if ind['price'] <= ind['low20'] or ind['price'] < ind['sma50']:
        return -1.0
    return 0.0

def shark_signal(sym, ind):
    if ind['rsi'] is None:
        return 0.0
    mom = ind['returns_5d']
    if ind['ema12'] and ind['ema26'] and ind['ema12'] > ind['ema26'] and ind['rsi'] < 80 and mom > 0.03:
        return 1.0
    if ind['ema12'] and ind['ema26'] and ind['ema12'] < ind['ema26'] and ind['rsi'] > 40:
        return -1.0
    return 0.0

def owl_signal(sym, ind):
    if ind['sma50'] and ind['price'] < ind['sma50'] * 0.98 and ind['rsi'] and ind['rsi'] < 45:
        return 1.0
    if ind['sma50'] and ind['price'] > ind['sma50'] * 1.05 and ind['rsi'] and ind['rsi'] > 65:
        return -1.0
    return 0.0

def wolf_signal(sym, ind):
    # sector rotation: pick sector with strongest 5-day return
    # actual scoring done externally; here just express bullish on momentum ETF
    if sym in UNIVERSE['rotation'] and ind['returns_5d'] > 0.02:
        return 1.0
    if sym in UNIVERSE['rotation'] and ind['returns_5d'] < -0.02:
        return -1.0
    return 0.0

def fox_signal(sym, ind):
    if ind['rsi'] and ind['rsi'] > 75 and ind['returns_5d'] > 0.08:
        return -1.0
    if ind['rsi'] and ind['rsi'] < 25 and ind['returns_5d'] < -0.08:
        return 1.0
    return 0.0

# --- Portfolio mechanics ---
def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        'capital': {a: START_CAPITAL for a in AGENTS},
        'positions': {a: {} for a in AGENTS},  # {sym: shares}
        'trades': {a: [] for a in AGENTS},
        'started': datetime.now(timezone.utc).isoformat(),
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def portfolio_value(positions, prices):
    val = 0.0
    for sym, shares in positions.items():
        if sym in prices and prices[sym]:
            val += shares * prices[sym][-1]['close']
    return val

def price_lookup(prices, sym):
    if sym in prices and prices[sym]:
        return prices[sym][-1]['close']
    return None

def run_simulation(prices, indicators):
    state = load_state()
    live_prices = {sym: bars[-1]['close'] for sym, bars in prices.items() if bars}
    today = _get_chicago_now().strftime('%Y-%m-%d %H:%M %Z')

    agent_signals = {
        'Turtle': {sym: turtle_signal(sym, ind) for sym, ind in indicators.items() if sym in UNIVERSE['trend']},
        'Shark': {sym: shark_signal(sym, ind) for sym, ind in indicators.items() if sym in UNIVERSE['momentum']},
        'Owl': {sym: owl_signal(sym, ind) for sym, ind in indicators.items() if sym in UNIVERSE['value']},
        'Wolf': {sym: wolf_signal(sym, ind) for sym, ind in indicators.items() if sym in UNIVERSE['rotation']},
        'Fox': {sym: fox_signal(sym, ind) for sym, ind in indicators.items() if sym in UNIVERSE['contrarian']},
    }

    # Rebalance each agent: hold top 2-3 positive signals, short top 1-2 negative, clear stale positions.
    for agent in AGENTS:
        signals = agent_signals[agent]
        pos = state['positions'][agent]
        cash = state['capital'][agent]
        current_val = cash + portfolio_value(pos, prices)

        # Score existing positions by unrealized return relative to entry? Use current signals.
        # Liquidate anything with opposite signal or not in watchlist anymore.
        to_close = []
        for sym, shares in list(pos.items()):
            sig = signals.get(sym, 0)
            if sig * shares < 0:  # opposite direction
                to_close.append(sym)
            elif sig == 0:
                to_close.append(sym)
        for sym in to_close:
            p = price_lookup(prices, sym)
            if p:
                cash += pos[sym] * p
                state['trades'][agent].append({
                    'date': today,
                    'sym': sym,
                    'action': 'SELL' if pos[sym] > 0 else 'COVER',
                    'shares': pos[sym],
                    'price': p,
                })
                del pos[sym]

        # Rank signals
        longs = sorted([(s, sym) for sym, s in signals.items() if s > 0], reverse=True)
        shorts = sorted([(s, sym) for sym, s in signals.items() if s < 0])

        target_longs = min(3, len(longs))
        target_shorts = min(1, len(shorts))
        n_positions = target_longs + target_shorts if (target_longs or target_shorts) else 0
        if n_positions == 0:
            state['capital'][agent] = cash
            continue
        budget_per = current_val * 0.95 / n_positions

        # Open/adjust positions
        for rank, (score, sym) in enumerate(longs[:target_longs]):
            p = price_lookup(prices, sym)
            if not p:
                continue
            desired = budget_per / p
            if sym in pos:
                # adjust size
                diff = desired - pos[sym]
                cash -= diff * p
                if abs(diff) >= 1:
                    state['trades'][agent].append({
                        'date': today,
                        'sym': sym,
                        'action': 'BUY' if diff > 0 else 'TRIM',
                        'shares': diff,
                        'price': p,
                    })
                pos[sym] = desired
            else:
                pos[sym] = desired
                cash -= desired * p
                state['trades'][agent].append({
                    'date': today,
                    'sym': sym,
                    'action': 'BUY',
                    'shares': desired,
                    'price': p,
                })

        for rank, (score, sym) in enumerate(shorts[:target_shorts]):
            p = price_lookup(prices, sym)
            if not p:
                continue
            desired = -budget_per / p  # short notional = budget
            if sym in pos:
                diff = desired - pos[sym]
                cash -= diff * p
                if abs(diff) >= 1:
                    state['trades'][agent].append({
                        'date': today,
                        'sym': sym,
                        'action': 'SHORT' if diff < 0 else 'COVER',
                        'shares': diff,
                        'price': p,
                    })
                pos[sym] = desired
            else:
                pos[sym] = desired
                cash -= desired * p
                state['trades'][agent].append({
                    'date': today,
                    'sym': sym,
                    'action': 'SHORT',
                    'shares': desired,
                    'price': p,
                })

        state['capital'][agent] = cash

    save_state(state)
    return state, agent_signals

# --- Equity curve ---
def build_equity_curve(prices, state):
    # Build historical portfolio value for each agent + SPY buy-and-hold
    benchmark_bars = prices[BENCHMARK]
    dates = [datetime.utcfromtimestamp(b['ts']).strftime('%Y-%m-%d') for b in benchmark_bars]
    spy_start = benchmark_bars[0]['close']
    series = {'SPY': [b['close'] / spy_start * START_CAPITAL for b in benchmark_bars]}
    # For agents we only have current state; estimate prior from current positions + price history (approx).
    # We'll compute backfilled portfolio value using current share holdings across historical closes.
    for agent in AGENTS:
        pos = state['positions'][agent]
        vals = []
        for i, bar in enumerate(benchmark_bars):
            val = state['capital'][agent]
            for sym, shares in pos.items():
                if sym in prices and len(prices[sym]) > i:
                    # align by date index
                    val += shares * prices[sym][i]['close']
            vals.append(val)
        series[agent] = vals
    return dates, series

# --- HTML dashboard ---
def build_dashboard(state, signals, prices, indicators, dates, series):
    today = _get_chicago_now()
    spy_last = prices[BENCHMARK][-1]['close']
    spy_prev = prices[BENCHMARK][-2]['close']
    spy_change = spy_last - spy_prev
    spy_pct = spy_change / spy_prev * 100
    spy_color = '#22c55e' if spy_pct >= 0 else '#ef4444'

    # Current values
    rows = []
    for agent in AGENTS:
        cash = state['capital'][agent]
        pos_val = portfolio_value(state['positions'][agent], prices)
        total = cash + pos_val
        pnl = total - START_CAPITAL
        pct = pnl / START_CAPITAL * 100
        rows.append((agent, total, pnl, pct, state['positions'][agent]))
    rows.sort(key=lambda x: x[1], reverse=True)

    # Colors per agent
    colors = {
        'Turtle': '#3b82f6', 'Shark': '#ef4444', 'Owl': '#a855f7',
        'Wolf': '#f97316', 'Fox': '#eab308', 'SPY': '#94a3b8'
    }

    # Trades table
    all_trades = []
    for agent in AGENTS:
        for t in state['trades'][agent][-10:]:
            all_trades.append({**t, 'agent': agent})
    all_trades.sort(key=lambda x: x['date'], reverse=True)
    trades_html = ''
    for t in all_trades[:20]:
        trades_html += f"""<tr><td>{t['date']}</td><td>{t['agent']}</td><td>{t['sym']}</td><td>{t['action']}</td><td>{t['shares']:.2f}</td><td>${t['price']:.2f}</td></tr>"""

    # Holdings table
    holdings_html = ''
    for agent, total, pnl, pct, pos in rows:
        for sym, shares in pos.items():
            p = price_lookup(prices, sym)
            val = shares * p if p else 0
            holdings_html += f"""<tr><td>{agent}</td><td>{sym}</td><td>{shares:.2f}</td><td>${p:.2f}</td><td>${val:,.2f}</td></tr>"""

    # Signals table
    signals_html = ''
    for agent in AGENTS:
        for sym, sig in sorted(signals[agent].items(), key=lambda x: -abs(x[1])):
            if sig != 0:
                signals_html += f"""<tr><td>{agent}</td><td>{sym}</td><td>{sig:+.1f}</td><td>{'LONG' if sig > 0 else 'SHORT'}</td></tr>"""

    # Chart data JSON
    chart_data = {
        'labels': dates,
        'datasets': [
            {'label': name, 'data': vals, 'borderColor': colors.get(name, '#999'), 'fill': False, 'tension': 0.2, 'pointRadius': 0}
            for name, vals in series.items()
        ]
    }

    cards = ''
    for rank, (agent, total, pnl, pct, pos) in enumerate(rows, 1):
        color = '#22c55e' if pnl >= 0 else '#ef4444'
        cards += f"""
        <div class="card">
          <div class="rank">#{rank}</div>
          <div class="agent-name">{agent}</div>
          <div class="strategy">{agent.lower()}</div>
          <div class="amount" style="color:{color}">${total:,.2f}</div>
          <div class="pnl" style="color:{color}">{pct:+.2f}% (${pnl:+,.2f})</div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trading Arena — Live Standings</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:20px; }}
header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }}
h1 {{ margin:0; font-size:1.8rem; color:#f8fafc; }}
.benchmark {{ font-size:1.2rem; color:{spy_color}; font-weight:600; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-bottom:24px; }}
.card {{ background:#1e293b; border-radius:12px; padding:18px; box-shadow:0 4px 12px rgba(0,0,0,.25); position:relative; }}
.rank {{ position:absolute; top:10px; right:14px; font-size:1.5rem; font-weight:800; color:#334155; }}
.agent-name {{ font-size:1.25rem; font-weight:700; margin-bottom:4px; }}
.strategy {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; color:#94a3b8; margin-bottom:12px; }}
.amount {{ font-size:1.6rem; font-weight:800; margin-bottom:4px; }}
.pnl {{ font-size:1rem; font-weight:600; }}
.panel {{ background:#1e293b; border-radius:12px; padding:16px; margin-bottom:20px; }}
.panel h2 {{ margin-top:0; font-size:1.1rem; color:#94a3b8; }}
table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
th, td {{ padding:8px 10px; text-align:left; border-bottom:1px solid #334155; }}
th {{ color:#94a3b8; font-weight:600; }}
tr:hover {{ background:#334155; }}
.footer {{ text-align:center; color:#64748b; font-size:.8rem; margin-top:30px; }}
.chart-wrap {{ height:360px; }}
</style>
</head>
<body>
<header>
  <div><h1>Trading Arena</h1><div style="color:#94a3b8;font-size:.9rem">AI trader competition • $10,000 each • vs SPY</div></div>
  <div class="benchmark">SPY ${spy_last:.2f} ({spy_pct:+.2f}%)</div>
</header>
<div class="grid">
{cards}
</div>
<div class="panel">
  <h2>Equity Curves</h2>
  <div class="chart-wrap"><canvas id="equityChart"></canvas></div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
  <div class="panel">
    <h2>Live Positions</h2>
    <table><thead><tr><th>Agent</th><th>Symbol</th><th>Shares</th><th>Price</th><th>Value</th></tr></thead><tbody>{holdings_html}</tbody></table>
  </div>
  <div class="panel">
    <h2>Recent Signals</h2>
    <table><thead><tr><th>Agent</th><th>Symbol</th><th>Score</th><th>Side</th></tr></thead><tbody>{signals_html}</tbody></table>
  </div>
</div>
<div class="panel">
  <h2>Recent Trades</h2>
  <table><thead><tr><th>Date</th><th>Agent</th><th>Symbol</th><th>Action</th><th>Shares</th><th>Price</th></tr></thead><tbody>{trades_html}</tbody></table>
</div>
<div class="footer">Generated {today.strftime('%Y-%m-%d %H:%M %Z')} • Trading Arena Agent</div>
<script>
const ctx = document.getElementById('equityChart').getContext('2d');
const data = {json.dumps(chart_data)};
new Chart(ctx, {{ type:'line', data:data, options: {{
  responsive:true, maintainAspectRatio:false,
  plugins: {{ legend: {{ labels: {{ color:'#e2e8f0' }} }}, tooltip: {{ mode:'index', intersect:false }} }},
  scales: {{
    x: {{ ticks: {{ color:'#94a3b8' }}, grid: {{ color:'#334155' }} }},
    y: {{ ticks: {{ color:'#94a3b8' }}, grid: {{ color:'#334155' }} }}
  }}
}} }});
</script>
</body>
</html>"""
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Dashboard written to {OUT_PATH}')

# --- Main ---
def main():
    if not market_open_now():
        print(f'Market closed ({_get_chicago_now().strftime("%Y-%m-%d %H:%M %Z")}). Skipping.')
        return
    print('Market open. Running Trading Arena...')
    prices = load_or_fetch_prices()
    indicators = analyze(prices)
    state, signals = run_simulation(prices, indicators)
    dates, series = build_equity_curve(prices, state)
    build_dashboard(state, signals, prices, indicators, dates, series)

if __name__ == '__main__':
    main()
