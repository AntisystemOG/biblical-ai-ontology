"""Sell falsified NY weather positions - station math kills the win condition.
NWS forecast: 77°F high. B80.5 and B82.5 YES positions are dead.
Per Thad's Aug 31 trading authority: selling losing/falsified legs = no permission needed."""
import sys, json, requests, time, datetime
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")

from digest import get_auth_headers

BASE_URL = "https://external-api.kalshi.com/trade-api/v2"

# Place a sell order for YES shares at market or best available price
def place_sell_order(ticker, side, count, price=None):
    """Place a sell order. side='yes' or 'no'. For selling YES shares."""
    headers = get_auth_headers()
    
    # If no price specified, use a very low price to market sell
    if price is None:
        price = 0.01
    
    order = {
        "ticker": ticker,
        "side": side,  # 'yes' or 'no' - we're selling, so this is the side we hold
        "action": "sell",
        "type": "limit",
        "count": count,
        "price": price,
    }
    
    print(f"Placing SELL order: {json.dumps(order, indent=2)}")
    
    resp = requests.post(
        f"{BASE_URL}/portfolio/orders",
        headers=headers,
        json=order
    )
    
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    return resp

# Check current bid prices first
headers = get_auth_headers()

# Get market data for our positions
for ticker in ['KXHIGHNY-26AUG31-B80.5', 'KXHIGHNY-26AUG31-B82.5']:
    resp = requests.get(
        f"{BASE_URL}/markets/{ticker}",
        headers=headers
    )
    if resp.status_code == 200:
        data = resp.json()
        market = data.get('market', data)
        yes_bid = market.get('yes_bid_dollars', 'N/A')
        yes_ask = market.get('yes_ask_dollars', 'N/A')
        print(f"\n{ticker}:")
        print(f"  YES bid: {yes_bid} | YES ask: {yes_ask}")
        print(f"  Status: {market.get('status')}")
    else:
        print(f"\n{ticker}: Error {resp.status_code} - {resp.text[:200]}")

# Now sell at bid price (or slightly below to ensure fill)
print("\n=== SELLING FALSIFIED POSITIONS ===")

# B80.5 YES: 14 shares, bid likely ~0.08-0.09
print("\n--- Selling B80.5 YES (14 shares) ---")
place_sell_order('KXHIGHNY-26AUG31-B80.5', 'yes', 14, 0.07)

# B82.5 YES: 12 shares, bid likely ~0.02-0.03
print("\n--- Selling B82.5 YES (12 shares) ---")
place_sell_order('KXHIGHNY-26AUG31-B82.5', 'yes', 12, 0.02)