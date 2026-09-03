#!/usr/bin/env python3
"""History Rhymes data fetcher for September 3, 2026 (pre-market).
Fetches Yahoo Finance chart API market data + Google News RSS headlines.
Saves JSON to Spocks Reports history_rhymes dir.
NOTE (Aug 27 yfinance gotcha): ^TNX/^FVX/^IRX return RAW percent yields (4.80 = 4.80%). Never divide by 10.
"""
import json, os, sys, time, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Windows console (cp1252) chokes on unicode headlines; make stdout lossless-replace
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

OUTPUT = r'C:\Users\thadd\OneDrive\Desktop\Spocks Reports\history_rhymes\2026-09-03_history_rhymes_data.json'
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

SYMBOLS = {
    "^GSPC": "S&P 500", "^IXIC": "Nasdaq Composite", "^DJI": "Dow Jones", "^RUT": "Russell 2000",
    "^TNX": "10Y Treasury Yield", "^FVX": "5Y Treasury Yield", "^IRX": "13W T-Bill Yield",
    "^VIX": "VIX", "DX-Y.NYB": "USD Index", "CL=F": "WTI Crude", "GC=F": "Gold",
    "BTC-USD": "Bitcoin",
    "NVDA": "NVDA", "AAPL": "AAPL", "MSFT": "MSFT", "GOOGL": "GOOGL", "AMZN": "AMZN",
    "META": "META", "TSLA": "TSLA",
    "TLT": "TLT (20Y+ Bonds)", "HYG": "HY Credit (HYG)", "KRE": "KRE (Regionals)", "RSP": "RSP (Equal-Wt S&P)",
    "XLK": "XLK (Tech)", "XLE": "XLE (Energy)", "XLF": "XLF (Financials)", "XLV": "XLV (Health)",
    "XLY": "XLY (Discretionary)", "XLP": "XLP (Staples)", "XLU": "XLU (Utilities)",
    "XLI": "XLI (Industrials)", "XLB": "XLB (Materials)",
}

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
DAY = 86400

def fetch_chart(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym)}?range=2y&interval=1d"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def summarize(sym, name):
    try:
        j = fetch_chart(sym)
        res = j["chart"]["result"][0]
        ts = res.get("timestamp") or []
        closes = res["indicators"]["quote"][0].get("close") or []
        pairs = [(t, c) for t, c in zip(ts, closes) if c is not None]
        if len(pairs) < 60:
            return {"error": "insufficient data"}
        price = pairs[-1][1]
        last_dt = datetime.fromtimestamp(pairs[-1][0], tz=timezone.utc)
        out = {"price": round(price, 2), "last_date": last_dt.strftime("%Y-%m-%d")}
        # find index of close nearest to N days back (calendar), using last close as anchor
        def close_n_calendar_days_ago(days):
            target = pairs[-1][0] - days * DAY
            best = None
            for t, c in pairs:
                if t <= target:
                    best = (t, c)
                else:
                    break
            return best[1] if best else None
        for label, days in (("chg_1d_pct", 1), ("chg_5d_pct", 5), ("chg_1m_pct", 30),
                            ("chg_3m_pct", 91), ("chg_6m_pct", 182), ("chg_1y_pct", 365)):
            base = close_n_calendar_days_ago(days)
            out[label] = round((price / base - 1) * 100, 2) if base else None
        window = [c for _, c in pairs[-200:]]
        ma200 = sum(window) / len(window)
        out["above_200dma"] = round((price / ma200 - 1) * 100, 2)
        return out
    except Exception as e:
        return {"error": str(e)[:120]}

def fetch_news(query, limit=8):
    url = f"https://news.google.com/rss/search?q={urllib.request.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            root = ET.fromstring(r.read())
        items = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            if title:
                items.append({"title": title, "pub": pub})
            if len(items) >= limit:
                break
        return items
    except Exception as e:
        return [{"error": str(e)[:120]}]

market_data = {}
for sym, name in SYMBOLS.items():
    market_data[name] = summarize(sym, name)
    time.sleep(0.4)

news = {}
for cat, q in [
    ("stock_market", "stock market selloff bonds oil"),
    ("fed_rates", "Federal Reserve Warsh rate hike September"),
    ("oil_iran", "oil prices Iran Hormuz"),
    ("ai_valuation", "AI bubble stocks valuation Dalio"),
    ("inflation", "inflation CPI report oil"),
    ("jobs", "jobs report payrolls August jobless claims"),
]:
    news[cat] = fetch_news(q)

payload = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "market_data": market_data,
    "news": news,
}
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=1)

# Compact console summary for the agent
print("=== MARKET (last close) ===")
for name, d in market_data.items():
    if "error" in d:
        print(f"{name}: ERROR {d['error']}")
    else:
        print(f"{name}: {d['price']} ({d['last_date']}) 1d={d['chg_1d_pct']}% 1m={d['chg_1m_pct']}% 3m={d['chg_3m_pct']}% 1y={d['chg_1y_pct']}% vs200dma={d['above_200dma']}%")
print("=== NEWS ===")
for cat, items in news.items():
    print(f"--- {cat} ---")
    for it in items[:6]:
        if "error" in it:
            print(f"  ERROR {it['error']}")
        else:
            print(f"  [{it['pub'][:16]}] {it['title'][:150]}")