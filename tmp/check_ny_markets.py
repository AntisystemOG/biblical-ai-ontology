"""Check NY weather markets - try different series tickers."""
import sys, json
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")

from digest import fetch_markets

# Try different series/event ticker formats
for ticker in ['KXHIGHNY', 'KXHIGHNY-26AUG31']:
    print(f"\n=== Trying series: {ticker} ===")
    markets = fetch_markets(ticker)
    print(f"Type: {type(markets)}, Count: {len(markets) if isinstance(markets, list) else 'N/A'}")
    if markets and isinstance(markets, list):
        for m in markets[:5]:
            print(f"  {m.get('ticker', '?')} | yes_ask: {m.get('yes_ask_dollars')} | no_ask: {m.get('no_ask_dollars')} | status: {m.get('status')}")
    elif markets and isinstance(markets, dict):
        print(f"  Keys: {list(markets.keys())[:10]}")
        print(f"  Raw (500): {str(markets)[:500]}")