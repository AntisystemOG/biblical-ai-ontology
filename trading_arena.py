#!/usr/bin/env python3
"""
Trading Arena - 5 AI trading agents compete live vs S&P 500 benchmark.
Outputs an HTML dashboard with embedded snapshot data.
"""
import json
import os
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pytz
import yfinance as yf

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
WORKSPACE = Path(r"C:\Users\thadd\.openclaw\workspace")
STATE_DIR = WORKSPACE / ".openclaw" / "tmp"
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_PATH = STATE_DIR / "trading_arena_state.json"

OUTPUT_PATH = Path(r"C:\Users\thadd\OneDrive\Desktop\Spocks Reports\market\trading_arena.html")
TZ = pytz.timezone("America/Chicago")

STARTING_CAPITAL = 10_000.00
MAX_POSITIONS = 5
AGENTS = ["Turtle", "Shark", "Owl", "Wolf", "Fox"]

UNIVERSE = [
    "SPY", "QQQ", "IWM", "XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLU",
    "SMH", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "AMD",
    "JPM", "UNH", "V", "MA", "PG", "HD", "XOM", "CVX", "WMT", "KO", "PEP",
    "MCD", "DIS", "NFLX", "CRM", "BABA", "TSM", "JNJ", "VZ", "T", "IBM",
]

SECTOR_ETFS = {
    "XLK": "Tech", "XLF": "Financials", "XLE": "Energy", "XLV": "Health Care",
    "XLI": "Industrials", "XLP": "Consumer Staples", "XLU": "Utilities", "SMH": "Semiconductors",
}

VALUE_TICKERS = ["JNJ", "PG", "KO", "WMT", "XOM", "CVX", "VZ", "T", "IBM", "PEP", "MCD"]

# -----------------------------------------------------------------------------
# Market-hours check
# -----------------------------------------------------------------------------
def is_market_open(now: datetime) -> bool:
    # Monday=0 .. Friday=4
    if now.weekday() >= 5:
        return False
    # Agent schedule: 8:30 AM - 3:00 PM CDT. The 3:00 PM slot gets a small
    # closing grace (until 3:05 PM) so scheduler/startup jitter doesn't skip
    # it; the run still fills at the day's closing prices.
    t = now.time()
    return time(8, 30) <= t <= time(15, 5)

# -----------------------------------------------------------------------------
# Data fetching
# -----------------------------------------------------------------------------
def fetch_daily_history(tickers: List[str]) -> pd.DataFrame:
    """Download ~3 months of daily adjusted close data."""
    df = yf.download(
        tickers=tickers,
        period="3mo",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    return df

def get_last_close(prices: pd.DataFrame, ticker: str) -> float:
    """Return the most recent adjusted close price for a ticker."""
    if len(prices.columns.levels) if isinstance(prices.columns, pd.MultiIndex) else 0:
        series = prices[ticker]["Close"].dropna()
    else:
        series = prices["Close"].dropna()
    if series.empty:
        raise ValueError(f"No price data for {ticker}")
    return float(series.iloc[-1])

def compute_returns(prices: pd.DataFrame, ticker: str) -> Dict[str, float]:
    series = prices[ticker]["Close"].dropna()
    last = float(series.iloc[-1])
    r5 = (last / float(series.iloc[-6]) - 1) if len(series) >= 6 else 0.0
    r10 = (last / float(series.iloc[-11]) - 1) if len(series) >= 11 else 0.0
    r20 = (last / float(series.iloc[-21]) - 1) if len(series) >= 21 else 0.0
    r60 = (last / float(series.iloc[-61]) - 1) if len(series) >= 61 else 0.0
    return {"last": last, "r5": r5, "r10": r10, "r20": r20, "r60": r60}

# -----------------------------------------------------------------------------
# Portfolio helpers
# -----------------------------------------------------------------------------
def portfolio_value(cash: float, positions: Dict[str, float], prices: pd.DataFrame) -> float:
    total = cash
    for ticker, shares in positions.items():
        if shares == 0:
            continue
        try:
            price = get_last_close(prices, ticker)
        except Exception:
            continue
        total += shares * price
    return round(total, 2)

def execute_targets(
    cash: float,
    positions: Dict[str, float],
    targets: List[str],
    prices: pd.DataFrame,
    max_positions: int = MAX_POSITIONS,
) -> Dict[str, float]:
    """Rebalance to hold an equal-weight basket of target tickers."""
    # Close positions not in target list
    new_positions: Dict[str, float] = {}
    proceeds = cash
    for ticker, shares in positions.items():
        try:
            price = get_last_close(prices, ticker)
        except Exception:
            new_positions[ticker] = shares
            continue
        if ticker in targets:
            new_positions[ticker] = shares
        else:
            proceeds += shares * price

    # Allocate equally among targets (cap at max_positions)
    chosen = [t for t in targets if t in prices.columns.get_level_values(0).unique()] if isinstance(prices.columns, pd.MultiIndex) else targets
    chosen = chosen[:max_positions]
    if not chosen:
        return new_positions

    available_prices = {t: get_last_close(prices, t) for t in chosen}
    # Sell existing positions that are in targets so we can rebalance to equal weight
    for ticker in list(new_positions.keys()):
        if ticker in chosen:
            proceeds += new_positions.pop(ticker) * available_prices[ticker]

    allocation = proceeds / len(chosen)
    for ticker in chosen:
        price = available_prices[ticker]
        if price > 0:
            new_positions[ticker] = allocation / price
        else:
            new_positions[ticker] = 0

    cash_left = proceeds - sum(new_positions[t] * available_prices[t] for t in chosen)
    # caller only gets positions; cash returned separately
    return new_positions, round(cash_left, 2)

# -----------------------------------------------------------------------------
# Agent strategies
# -----------------------------------------------------------------------------
def turtle_signals(prices: pd.DataFrame) -> List[str]:
    """20-day breakout for entry; exit on 10-day low. Long-only."""
    universe = [t for t in UNIVERSE if t not in ("SPY",)]
    scores = {}
    for t in universe:
        try:
            series = prices[t]["Close"].dropna()
            high20 = series.iloc[-21:-1].max()
            low10 = series.iloc[-11:-1].min()
            last = series.iloc[-1]
            if last > high20:
                scores[t] = last / high20 - 1  # strength above breakout
            elif last < low10 and False:  # no short in this arena
                pass
        except Exception:
            continue
    # Pick top MAX_POSITIONS breakouts
    return sorted(scores, key=scores.get, reverse=True)[:MAX_POSITIONS]

def shark_signals(prices: pd.DataFrame) -> List[str]:
    """Momentum: top 5-day performers."""
    universe = [t for t in UNIVERSE if t not in ("SPY",)]
    scores = {}
    for t in universe:
        try:
            r = compute_returns(prices, t)
            scores[t] = r["r5"]
        except Exception:
            continue
    return sorted(scores, key=scores.get, reverse=True)[:MAX_POSITIONS]

def owl_signals(prices: pd.DataFrame) -> List[str]:
    """Value/mean-reversion oversold quality: lowest 20-day return in value basket."""
    scores = {}
    for t in VALUE_TICKERS:
        try:
            r = compute_returns(prices, t)
            scores[t] = r["r20"]
        except Exception:
            continue
    return sorted(scores, key=scores.get)[:MAX_POSITIONS]

def wolf_signals(prices: pd.DataFrame) -> List[str]:
    """Sector rotation: top 10-day return sector ETFs."""
    scores = {}
    for t, _ in SECTOR_ETFS.items():
        try:
            r = compute_returns(prices, t)
            scores[t] = r["r10"]
        except Exception:
            continue
    return sorted(scores, key=scores.get, reverse=True)[:2]

def fox_signals(prices: pd.DataFrame) -> List[str]:
    """Contrarian: worst 5-day performers, expecting snap-back."""
    universe = [t for t in UNIVERSE if t not in ("SPY",)]
    scores = {}
    for t in universe:
        try:
            r = compute_returns(prices, t)
            scores[t] = r["r5"]
        except Exception:
            continue
    return sorted(scores, key=scores.get)[:MAX_POSITIONS]

# -----------------------------------------------------------------------------
# State management
# -----------------------------------------------------------------------------
def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return new_state()

def new_state() -> dict:
    return {
        "created_at": datetime.now(TZ).isoformat(),
        "last_run": None,
        "run_count": 0,
        "agents": {
            name: {"cash": STARTING_CAPITAL, "positions": {}, "history": []}
            for name in AGENTS
        },
        "benchmark": {"cash": 0.0, "shares": 0.0, "history": []},
        "market_snapshot": {},
    }

def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, default=str))

# -----------------------------------------------------------------------------
# HTML dashboard generation
# -----------------------------------------------------------------------------
def make_sparkline(values: List[float], width: int = 180, height: int = 50) -> str:
    if len(values) < 2:
        return '<svg width="{}" height="{}"><text x="5" y="25" font-size="10">insufficient data</text></svg>'.format(width, height)
    mn = min(values)
    mx = max(values)
    rng = mx - mn if mx != mn else 1
    n = len(values)
    points = []
    for i, v in enumerate(values):
        x = i / (n - 1) * width
        y = height - ((v - mn) / rng) * height
        points.append(f"{x:.1f},{y:.1f}")
    poly = " ".join(points)
    color = "#22c55e" if values[-1] >= values[0] else "#ef4444"
    return (
        f'<svg width="{width}" height="{height}" style="overflow:visible">'
        f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2"/>'
        f'</svg>'
    )

def generate_html(state: dict, prices: pd.DataFrame) -> str:
    snapshot = json.dumps(state, indent=2, default=str)
    benchmark = state["benchmark"]
    agents_state = state["agents"]
    market = state.get("market_snapshot", {})

    # Determine current prices for holdings table
    holdings_rows = []
    for name in AGENTS:
        pos = agents_state[name]["positions"]
        for ticker, shares in pos.items():
            try:
                price = get_last_close(prices, ticker)
            except Exception:
                price = 0.0
            value = round(shares * price, 2)
            holdings_rows.append((name, ticker, round(shares, 4), price, value))

    agent_rows = []
    for name in AGENTS:
        equity = agents_state[name]["history"][-1]["equity"] if agents_state[name]["history"] else STARTING_CAPITAL
        start = agents_state[name]["history"][0]["equity"] if agents_state[name]["history"] else STARTING_CAPITAL
        pnl_pct = (equity / STARTING_CAPITAL - 1) * 100
        vs_bench = equity - (benchmark["history"][-1]["equity"] if benchmark["history"] else STARTING_CAPITAL)
        hist = [h["equity"] for h in agents_state[name]["history"]]
        spark = make_sparkline(hist)
        agent_rows.append((name, equity, pnl_pct, vs_bench, spark))

    bench_equity = benchmark["history"][-1]["equity"] if benchmark["history"] else STARTING_CAPITAL
    bench_pnl = (bench_equity / STARTING_CAPITAL - 1) * 100
    bench_hist = [h["equity"] for h in benchmark["history"]]
    bench_spark = make_sparkline(bench_hist)

    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M %Z")

    # Color styles
    style = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 2rem; }
    h1 { color: #f8fafc; margin-bottom: 0.2rem; }
    .subtitle { color: #94a3b8; margin-bottom: 1.5rem; }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; background: #1e293b; border-radius: 8px; overflow: hidden; }
    th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
    th { background: #334155; color: #f8fafc; }
    tr:last-child td { border-bottom: none; }
    .right { text-align: right; }
    .green { color: #22c55e; }
    .red { color: #ef4444; }
    .card { background: #1e293b; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
    .snapshot { display: none; }
    """

    rows_html = ""
    for name, equity, pnl_pct, vs_bench, spark in agent_rows:
        pnl_class = "green" if pnl_pct >= 0 else "red"
        vs_class = "green" if vs_bench >= 0 else "red"
        rows_html += (
            f"<tr><td><strong>{name}</strong></td>"
            f'<td class="right">${equity:,.2f}</td>'
            f'<td class="right {pnl_class}">{pnl_pct:+.2f}%</td>'
            f'<td class="right {vs_class}">${vs_bench:+,.2f}</td>'
            f'<td class="right">{spark}</td></tr>'
        )

    rows_html += (
        f'<tr style="background:#334155;font-weight:bold"><td>S&P 500 Benchmark (SPY)</td>'
        f'<td class="right">${bench_equity:,.2f}</td>'
        f'<td class="right {"green" if bench_pnl >= 0 else "red"}">{bench_pnl:+.2f}%</td>'
        f'<td class="right">—</td>'
        f'<td class="right">{bench_spark}</td></tr>'
    )

    holdings_html = ""
    for name, ticker, shares, price, value in holdings_rows:
        holdings_html += (
            f"<tr><td>{name}</td><td>{ticker}</td><td class='right'>{shares}</td>"
            f"<td class='right'>${price:,.2f}</td><td class='right'>${value:,.2f}</td></tr>"
        )

    market_html = ""
    signals = market.get("signals", {})
    for name, tickers in signals.items():
        market_html += f'<div class="card"><strong>{name} target basket:</strong> {", ".join(tickers)}</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trading Arena Dashboard</title>
<style>{style}</style>
</head>
<body>
<h1>🏟️ Trading Arena</h1>
<p class="subtitle">Live AI trader simulation vs S&P 500 benchmark &mdash; updated {now}</p>

<h2>Standings</h2>
<table>
<thead>
<tr><th>Agent</th><th class="right">Equity</th><th class="right">Total Return</th><th class="right">vs Benchmark</th><th class="right">Equity Curve</th></tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>

<h2>Signals & Baskets</h2>
{market_html}

<h2>Current Holdings</h2>
<table>
<thead>
<tr><th>Agent</th><th>Ticker</th><th class="right">Shares</th><th class="right">Price</th><th class="right">Value</th></tr>
</thead>
<tbody>
{holdings_html}
</tbody>
</table>

<p style="color:#64748b;font-size:0.85rem;margin-top:2rem;">
Each agent starts with ${STARTING_CAPITAL:,.0f}. Benchmark is SPY buy-and-hold. Data via Yahoo Finance. Past performance is simulated, not investment advice.
</p>

<script id="arena-snapshot" type="application/json" class="snapshot">
{snapshot}
</script>
</body>
</html>
"""
    return html

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> int:
    now = datetime.now(TZ)
    print(f"Trading Arena run at {now.isoformat()}")

    if not is_market_open(now):
        print("Market closed. Skipping.")
        return 0

    print("Fetching market data...")
    try:
        prices = fetch_daily_history(UNIVERSE)
        # Flatten single-ticker case
        if not isinstance(prices.columns, pd.MultiIndex):
            prices.columns = pd.MultiIndex.from_product([UNIVERSE[:1], prices.columns])
    except Exception as e:
        print(f"Failed to fetch market data: {e}")
        return 1

    state = load_state()
    state["run_count"] += 1
    state["last_run"] = now.isoformat()

    # Benchmark: buy SPY on first run and hold
    spy_price = get_last_close(prices, "SPY")
    if state["benchmark"]["shares"] == 0:
        state["benchmark"]["shares"] = STARTING_CAPITAL / spy_price
    bench_equity = state["benchmark"]["shares"] * spy_price
    state["benchmark"]["history"].append({"date": now.isoformat(), "equity": round(bench_equity, 2)})

    # Strategy signals
    signals = {
        "Turtle (trend breakout)": turtle_signals(prices),
        "Shark (momentum)": shark_signals(prices),
        "Owl (value / oversold quality)": owl_signals(prices),
        "Wolf (sector rotation)": wolf_signals(prices),
        "Fox (contrarian)": fox_signals(prices),
    }

    strategy_map = {
        "Turtle": turtle_signals(prices),
        "Shark": shark_signals(prices),
        "Owl": owl_signals(prices),
        "Wolf": wolf_signals(prices),
        "Fox": fox_signals(prices),
    }

    for name in AGENTS:
        targets = strategy_map[name]
        agent = state["agents"][name]
        new_positions, cash_left = execute_targets(
            agent["cash"], agent["positions"], targets, prices
        )
        agent["positions"] = new_positions
        agent["cash"] = cash_left
        equity = portfolio_value(agent["cash"], agent["positions"], prices)
        agent["history"].append({"date": now.isoformat(), "equity": equity})
        print(f"{name}: ${equity:,.2f} | cash ${cash_left:,.2f} | positions {list(new_positions.keys())}")

    # Market snapshot
    snapshot_prices = {}
    for t in UNIVERSE[:30]:
        try:
            snapshot_prices[t] = get_last_close(prices, t)
        except Exception:
            pass
    state["market_snapshot"] = {
        "date": now.isoformat(),
        "spy_price": spy_price,
        "prices": snapshot_prices,
        "signals": {k.split()[0]: v for k, v in signals.items()},
    }

    save_state(state)

    # Generate HTML
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    html = generate_html(state, prices)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_PATH}")

    print("Done")
    return 0

if __name__ == "__main__":
    sys.exit(main())
