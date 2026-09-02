"""Check NY weather positions and sell falsified ones."""
import sys, json
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")

from digest import fetch_markets, fetch_positions

# Check positions first
print("=== CURRENT POSITIONS ===")
positions = fetch_positions()
print(f"Positions type: {type(positions)}")
print(f"Positions raw (first 1000 chars): {str(positions)[:1000]}")

# Check NY Aug 31 market prices for our positions
print("\n=== NY AUG 31 MARKET PRICES ===")
markets = fetch_markets('KXHIGHNY-26AUG31')
print(f"Markets type: {type(markets)}")
print(f"Markets raw (first 1000 chars): {str(markets)[:1000]}")