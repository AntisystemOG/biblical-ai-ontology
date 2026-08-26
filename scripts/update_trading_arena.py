import json
import os
import datetime
import random
from decimal import Decimal, ROUND_HALF_UP

# Use yfinance for real market data
try:
    import yfinance as yf
except ImportError:
    raise ImportError("yfinance not installed")

# Paths
PREV_JSON = os.path.join(os.path.dirname(__file__), "trading_arena_prev.json")
OUT_JSON = r"C:\Users\thadd\OneDrive\Desktop\Spocks Reports\market\trading_arena.json"
OUT_HTML = r"C:\Users\thadd\OneDrive\Desktop\Spocks Reports\market\trading_arena.html"
# Save a copy of the generated script under workspace for version control
SCRIPT_COPY = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "update_trading_arena.py")

START_CAPITAL = 10000.0
SESSION_START = "2026-08-14"

# Universe of stocks/ETFs per strategy
UNIVERSE = {
    "turtle": ["AAPL", "MSFT", "AVGO", "AMZN", "GOOGL", "CRM"],  # Mega-cap trend
    "shark": ["NVDA", "AMD", "TSLA", "PLTR", "COIN", "MSTR"],    # Momentum/high beta
    "owl": ["JPM", "BRK-B", "UNH", "JNJ", "PG", "V", "MA"],     # Value/quality
    "wolf": ["XLK", "XLF", "XLE", "XLV", "XLI", "XLU", "XLRE"], # Sector ETFs
    "fox": ["QQQ", "TLT", "GLD", "XLU", "VZ", "MO", "KO"],      # Contrarian/rotation
}

# Strategy descriptions
STRATEGIES = {
    "turtle": "Trend Following",
    "shark": "Momentum",
    "owl": "Value",
    "wolf": "Sector Rotation",
    "fox": "Contrarian",
}

EMOJIS = {
    "turtle": "🐢",
    "shark": "🦈",
    "owl": "🦉",
    "wolf": "🐺",
    "fox": "🦊",
}

SYMBOL_MAP = {
    "BRK-B": "BRK.B",
}


def yf_price(symbol):
    """Fetch latest price via yfinance."""
    yf_sym = SYMBOL_MAP.get(symbol, symbol)
    try:
        t = yf.Ticker(symbol)
        # Prefer fast_info, fallback to history
        # Use history so we have both current and prior close consistently
        hist = t.history(period="5d", interval="1d")
        if hist is not None and not hist.empty:
            price = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
        else:
            price = None
            prev = None
        return float(price) if price else None, float(prev) if prev else None
    except Exception as e:
        print(f"yfinance failed for {symbol}: {e}")
        return None, None


def get_prices(symbols):
    prices = {}
    previous = {}
    for sym in symbols:
        p, prev = yf_price(sym)
        prices[sym] = p
        previous[sym] = prev
        print(f"  {sym}: {p} (prev {prev})")
    return prices, previous


def round2(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def total_value(cash, holdings, prices):
    val = cash
    for sym, qty in holdings.items():
        val += qty * (prices.get(sym) or 0)
    return val


def random_action(trader, prices, prev_prices, market_theme):
    """Generate a plausible action for a trader based on strategy and price moves."""
    holdings = trader["holdings"]
    cash = trader["cash"]
    strat = trader["id"]
    actions = []

    # Determine biggest winner/loser among holdings
    held = list(holdings.keys())
    moves = {}
    for sym in held:
        if prev_prices.get(sym) and prices.get(sym):
            moves[sym] = (prices[sym] - prev_prices[sym]) / prev_prices[sym]
    if not moves:
        return "HOLD — monitoring market"

    winner = max(moves, key=moves.get)
    loser = min(moves, key=moves.get)
    win_pct = moves[winner] * 100
    lose_pct = moves[loser] * 100

    # Strategy-specific action tendencies
    if strat == "shark":
        if cash > 500 and win_pct > 1.5:
            qty = max(1, int(min(cash * 0.15, 3000) / prices[winner]))
            actions.append(f"ADD {winner} +{qty} @ ${prices[winner]:.2f} — chasing momentum")
        elif lose_pct < -2.0 and holdings.get(loser, 0) > 0:
            qty = max(1, holdings[loser] // 3)
            actions.append(f"CUT {loser} -{qty} @ ${prices[loser]:.2f} — stop loss hit")
        else:
            actions.append(f"HOLD — riding momentum leaders")
    elif strat == "turtle":
        if win_pct > 2.0 and holdings.get(winner, 0) > 0:
            qty = max(1, holdings[winner] // 4)
            actions.append(f"TRIM {winner} -{qty} @ ${prices[winner]:.2f} — take trend profits")
        elif lose_pct < -1.5 and cash > 1000:
            qty = max(1, int(min(cash * 0.10, 2000) / prices[loser]))
            actions.append(f"ADD {loser} +{qty} @ ${prices[loser]:.2f} — buy the dip in trend")
        else:
            actions.append(f"HOLD — trend intact")
    elif strat == "owl":
        if lose_pct < -1.0 and cash > 1000:
            qty = max(1, int(min(cash * 0.20, 3000) / prices[loser]))
            actions.append(f"ADD {loser} +{qty} @ ${prices[loser]:.2f} — value opportunity")
        elif win_pct > 2.5 and holdings.get(winner, 0) > 0:
            qty = max(1, holdings[winner] // 5)
            actions.append(f"TRIM {winner} -{qty} @ ${prices[winner]:.2f} — rebalance to fair value")
        else:
            actions.append(f"HOLD — waiting for better entry")
    elif strat == "wolf":
        # Sector rotation
        sectors = list(holdings.keys())
        if cash > 800 and random.random() < 0.6:
            target = random.choice(sectors)
            qty = max(1, int(min(cash * 0.15, 2500) / prices[target]))
            actions.append(f"ROTATE INTO {target} +{qty} @ ${prices[target]:.2f} — sector exposure")
        else:
            actions.append(f"HOLD — sector positioning steady")
    elif strat == "fox":
        if win_pct > 2.0 and holdings.get(winner, 0) > 0:
            qty = max(1, holdings[winner] // 3)
            actions.append(f"TAKE PROFIT {winner} -{qty} @ ${prices[winner]:.2f} — contrary signal")
        elif lose_pct < -1.5 and cash > 500:
            qty = max(1, int(min(cash * 0.12, 2000) / prices[loser]))
            actions.append(f"CONTRARIAN BUY {loser} +{qty} @ ${prices[loser]:.2f} — oversold bounce")
        else:
            actions.append(f"HOLD — patience for reversal")

    return actions[0] if actions else "HOLD — monitoring market"


def rebalance_portfolio(trader, prices):
    """Simulate holdings drift with daily market prices."""
    holdings = dict(trader.get("holdings", {}))
    cash = float(trader.get("cash", START_CAPITAL))
    strat = trader["id"]

    # Every now and then, make a small allocation shift
    if random.random() < 0.15:
        universe = UNIVERSE.get(strat, [])
        # Sell a small piece of a current holding to free cash or buy a new name
        if holdings and random.random() < 0.5:
            sell_sym = random.choice(list(holdings.keys()))
            qty = max(1, holdings[sell_sym] // 5)
            proceeds = qty * prices.get(sell_sym, 0)
            if proceeds > 0:
                holdings[sell_sym] -= qty
                if holdings[sell_sym] <= 0:
                    del holdings[sell_sym]
                cash += proceeds
        # Buy something from universe if cash available
        available = [s for s in universe if prices.get(s, 0) > 0 and cash > prices[s] * 1.05]
        if available:
            buy_sym = random.choice(available)
            max_qty = int(cash * 0.15 / prices[buy_sym])
            qty = max(1, min(max_qty, 5))
            cost = qty * prices[buy_sym]
            if cost <= cash:
                holdings[buy_sym] = holdings.get(buy_sym, 0) + qty
                cash -= cost
    return holdings, cash


def load_previous():
    if not os.path.exists(PREV_JSON):
        return None
    with open(PREV_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_html(data):
    now_str = data["lastUpdate"]
    benchmark = data["benchmark"]
    traders = sorted(data["traders"], key=lambda x: x["rank"])
    rows = []
    for t in traders:
        rows.append(f"""
        <tr class="{'leader' if t['rank'] == 1 else ''}">
            <td class="rank">#{t['rank']}</td>
            <td><span class="emoji">{t['emoji']}</span> {t['name']} <span class="strategy">{t['strategy']}</span></td>
            <td class="value">${t['portfolioValue']:,.2f}</td>
            <td class="return {'pos' if t['totalReturn'] >= 0 else 'neg'}">{t['totalReturn']:+.2f}%</td>
            <td class="vs {'pos' if t['vsSP500'] >= 0 else 'neg'}">{t['vsSP500']:+.2f}%</td>
            <td class="action">{t['lastAction']}</td>
        </tr>
        """)
    holdings_rows = []
    for t in traders:
        for sym, qty in t["holdings"].items():
            price = data.get("_prices", {}).get(sym, 0)
            holdings_rows.append(f"""
        <tr><td>{t['emoji']} {t['name']}</td><td>{sym}</td><td>{qty}</td><td>${price:,.2f}</td><td>${qty*price:,.2f}</td></tr>
        """)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="60">
<title>Trading Arena | Live Standings</title>
<style>
  :root {{--bg:#0b0f19;--card:#111827;--text:#e5e7eb;--muted:#9ca3af;--accent:#22d3ee;--pos:#34d399;--neg:#f87171;--leader:#fbbf24;}}
  body{{font-family:Inter,Segoe UI,system-ui,sans-serif;background:var(--bg);color:var(--text);margin:0;padding:24px;}}
  .container{{max-width:1100px;margin:0 auto;}}
  h1{{margin:0 0 4px 0;font-size:2rem;}}
  .subtitle{{color:var(--muted);margin-bottom:24px;}}
  .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:24px;}}
  .card{{background:var(--card);border-radius:12px;padding:16px;}}
  .card .label{{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;}}
  .card .value2{{font-size:1.6rem;font-weight:700;margin-top:6px;}}
  .card .delta{{font-size:.85rem;margin-top:4px;}}
  table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;overflow:hidden;margin-bottom:24px;}}
  th,td{{padding:12px 14px;text-align:left;}}
  th{{background:#1f2937;color:var(--muted);font-size:.75rem;text-transform:uppercase;}}
  tr{{border-bottom:1px solid #1f2937;}}
  tr.leader{{background:rgba(251,191,36,.08);}}
  .rank{{font-weight:800;color:var(--accent);}}
  .emoji{{font-size:1.2rem;}}
  .strategy{{color:var(--muted);font-size:.75rem;}}
  .pos{{color:var(--pos);}}
  .neg{{color:var(--neg);}}
  .action{{font-size:.8rem;color:var(--muted);}}
  .footer{{color:var(--muted);font-size:.8rem;margin-top:20px;}}
</style>
</head>
<body>
<div class="container">
  <h1>🥊 Trading Arena</h1>
  <p class="subtitle">5 AI traders • $10K each • Session started {SESSION_START} • Updated {now_str}</p>
  <div class="cards">
    <div class="card"><div class="label">Benchmark (SPY)</div><div class="value2">${benchmark['price']:,.2f}</div><div class="delta {'pos' if benchmark['returnPercent'] >= 0 else 'neg'}">{benchmark['returnPercent']:+.2f}% since start</div></div>
    <div class="card"><div class="label">Trading Days Elapsed</div><div class="value2">{data['tradingDaysElapsed']}</div><div class="delta">Session active</div></div>
    <div class="card"><div class="label">Market Theme</div><div class="value2" style="font-size:1rem;">{data.get('marketTheme','')}</div><div class="delta">{data.get('marketConditions','')}</div></div>
    <div class="card"><div class="label">Current Leader</div><div class="value2">{traders[0]['emoji']} {traders[0]['name']}</div><div class="delta pos">{traders[0]['totalReturn']:+.2f}% return</div></div>
  </div>
  <table>
    <thead><tr><th>Rank</th><th>Trader</th><th>Portfolio</th><th>Total Return</th><th>vs S&P 500</th><th>Latest Action</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <h2>Current Holdings</h2>
  <table>
    <thead><tr><th>Trader</th><th>Symbol</th><th>Qty</th><th>Price</th><th>Value</th></tr></thead>
    <tbody>{''.join(holdings_rows)}</tbody>
  </table>
  <p class="footer">Runs every 30 min during market hours (8:30 AM – 3:00 PM CDT). Data embedded; works offline via file:// protocol.</p>
</div>
</body>
</html>"""
    return html


def main():
    now = datetime.datetime.now()
    print(f"Trading Arena update at {now.isoformat()}")

    # Market hours check (CDT)
    market_open = now.weekday() < 5 and now.replace(hour=8, minute=30, second=0) <= now <= now.replace(hour=15, minute=0, second=0)
    print(f"Market open: {market_open}")

    # Load previous state
    prev = load_previous()
    if prev is None:
        # First run: initialize
        traders_init = []
        for tid in ["turtle", "shark", "owl", "wolf", "fox"]:
            traders_init.append({
                "id": tid,
                "name": tid.capitalize(),
                "emoji": EMOJIS[tid],
                "strategy": STRATEGIES[tid],
                "cash": START_CAPITAL,
                "holdings": {},
                "portfolioValue": START_CAPITAL,
                "totalReturn": 0.0,
                "vsSP500": 0.0,
                "rank": 0,
                "lastAction": "INIT — $10,000 cash",
                "intradayMove": 0.0,
            })
        prev = {
            "sessionStart": SESSION_START,
            "lastUpdate": now.isoformat(),
            "tradingDaysElapsed": 0.0,
            "marketOpen": market_open,
            "marketTheme": "initializing",
            "benchmark": {"symbol": "SPY", "price": 0.0, "priceAtStart": 0.0, "change": 0.0, "changePercent": 0.0, "returnPercent": 0.0},
            "traders": traders_init,
            "recentActivity": [],
            "marketConditions": "",
            "marketNote": "",
            "_prices": {},
        }

    # Collect all symbols
    all_symbols = set()
    for lst in UNIVERSE.values():
        all_symbols.update(lst)
    all_symbols.add("SPY")
    all_symbols = sorted(all_symbols)

    # Fetch prices
    print("Fetching prices via yfinance...")
    prices, prev_prices = get_prices(all_symbols)

    # Seed missing prices if needed (fallback to prev state)
    for sym in all_symbols:
        if prices.get(sym) is None:
            prices[sym] = prev.get("_prices", {}).get(sym, 0.0)
            prev_prices[sym] = prices[sym]

    # yfinance returns BRK-B as BRK-B; our holdings key is BRK.B, ensure price alias
    if "BRK-B" in prices and "BRK.B" not in prices:
        prices["BRK.B"] = prices["BRK-B"]
        prev_prices["BRK.B"] = prev_prices.get("BRK-B", prices["BRK-B"])

    # Fallback for BRK.B from previous state if still missing
    if "BRK.B" not in prices:
        prices["BRK.B"] = prev.get("_prices", {}).get("BRK.B", 0.0)
        prev_prices["BRK.B"] = prices["BRK.B"]

    spy_price = prices.get("SPY", prev["benchmark"].get("price", 0.0))
    spy_start = prev["benchmark"].get("priceAtStart") or spy_price
    spy_return = (spy_price - spy_start) / spy_start * 100 if spy_start else 0.0
    spy_change = spy_price - (prev_prices.get("SPY") or spy_price)
    spy_change_pct = spy_change / (prev_prices.get("SPY") or spy_price) * 100 if prev_prices.get("SPY") else 0.0

    # Update each trader
    updated_traders = []
    for t in prev["traders"]:
        # Apply occasional portfolio drift/rebalance
        new_holdings, new_cash = rebalance_portfolio(t, prices)
        port_val = total_value(new_cash, new_holdings, prices)
        total_ret = (port_val - START_CAPITAL) / START_CAPITAL * 100
        vs_sp = total_ret - spy_return

        # Intraday move (vs previous close or previous state)
        prev_val = float(t.get("portfolioValue", port_val))
        intraday_move = (port_val - prev_val) / prev_val if prev_val else 0.0

        # Generate action based on current holdings moves
        action = random_action(t, prices, prev_prices, prev.get("marketTheme", ""))

        updated_traders.append({
            "id": t["id"],
            "name": t["name"],
            "emoji": t["emoji"],
            "strategy": t["strategy"],
            "cash": round2(new_cash),
            "holdings": {k: int(v) for k, v in new_holdings.items() if v > 0},
            "portfolioValue": round2(port_val),
            "totalReturn": round2(total_ret),
            "vsSP500": round2(vs_sp),
            "rank": 0,
            "lastAction": action,
            "intradayMove": round2(intraday_move),
        })

    # Rank traders by portfolio value
    ranked = sorted(updated_traders, key=lambda x: x["portfolioValue"], reverse=True)
    for i, t in enumerate(ranked, 1):
        t["rank"] = i

    # Recent activity log
    activity = []
    for t in ranked:
        if not t["lastAction"].startswith("HOLD") and not t["lastAction"].startswith("INIT"):
            activity.append(f"{t['emoji']} {t['name']}: {t['lastAction']}")
    if not activity:
        activity.append("No major trades this interval.")

    # Determine market theme from price moves
    sector_moves = {}
    for sym in ["XLK", "XLF", "XLE", "XLV", "XLU", "XLRE", "XLI", "SPY", "QQQ"]:
        if prev_prices.get(sym) and prices.get(sym):
            sector_moves[sym] = (prices[sym] - prev_prices[sym]) / prev_prices[sym] * 100
    theme_parts = []
    if sector_moves:
        strongest = max(sector_moves, key=sector_moves.get)
        weakest = min(sector_moves, key=sector_moves.get)
        theme_parts.append(f"{strongest} strongest ({sector_moves[strongest]:+.2f}%), {weakest} weakest ({sector_moves[weakest]:+.2f}%)")
    else:
        theme_parts.append("mixed")
    market_theme = ", ".join(theme_parts)

    # Trading days elapsed: increment by ~1 if this is first run of a new trading day
    last_update = datetime.datetime.fromisoformat(prev.get("lastUpdate", now.isoformat()))
    trading_days = float(prev.get("tradingDaysElapsed", 0.0))
    if now.date() != last_update.date() and now.weekday() < 5:
        trading_days += 1.0

    # Update benchmark previous close based on last SPY close
    if prev_prices.get("SPY"):
        prev_spy_close = prev_prices["SPY"]
    else:
        prev_spy_close = spy_price - spy_change

    data = {
        "sessionStart": prev.get("sessionStart", SESSION_START),
        "lastUpdate": now.isoformat(),
        "tradingDaysElapsed": round2(trading_days),
        "marketOpen": market_open,
        "marketTheme": market_theme,
        "benchmark": {
            "symbol": "SPY",
            "price": round2(spy_price),
            "priceAtStart": round2(spy_start),
            "previousClose": round2(prev_spy_close),
            "change": round2(spy_change),
            "changePercent": round2(spy_change_pct),
            "returnPercent": round2(spy_return),
        },
        "traders": ranked,
        "recentActivity": activity[:10],
        "marketConditions": f"S&P 500 (SPY) is at ${spy_price:,.2f}, {spy_change_pct:+.2f}%",
        "marketNote": "Market Open" if market_open else "Market Closed",
        "_prices": {k: round2(v) for k, v in prices.items()},
    }

    # Save JSON
    save_json(data, OUT_JSON)
    print(f"Saved JSON: {OUT_JSON}")

    # Save HTML
    html = build_html(data)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML: {OUT_HTML}")

    # Keep workspace copy of script up to date
    import shutil
    shutil.copyfile(__file__, SCRIPT_COPY)
    print(f"Copied script to: {SCRIPT_COPY}")


if __name__ == "__main__":
    main()
