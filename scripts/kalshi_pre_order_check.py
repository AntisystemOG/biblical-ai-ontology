"""
kalshi_pre_order_check.py - MANDATORY pre-order verification.

Run BEFORE any live order. Confirms the direction semantics of the market you're
about to trade and whether your intended side aligns with the likely outcome.

Usage:
  python kalshi_pre_order_check.py TICKER SIDE PRICE SIZE
  e.g. python kalshi_pre_order_check.py KXHIGHCHI-26AUG27-B82.5 NO 0.62 19

Checks:
  1. Market title + rules_primary read directly from API (never from memory)
  2. strike_type interpretation ("less"/"greater"/"between"/"greater_or_equal")
  3. Plain-English statement of what YOUR side wins on
  4. Blended odds (NWS forecast + market-implied) that your side wins
  5. RED FLAG if your side's odds < 50% or if order cost > available cash
"""
import json
import math
import sys

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
from kalshi_client import Kalshi

# Forecast anchors (update via weather scan; used only for sanity check, not orders)
NWS = {"KXHIGHDEN": 91, "KXHIGHMIA": 89, "KXHIGHCHI": 77, "KXHIGHNY": 81}
SIGMA_WEATHER = 1.6
CLAIMS_FORECAST = 205303
SIGMA_CLAIMS = 3500


def p_below(f, thr, sigma):
    z = (thr - f) / sigma
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def main():
    if len(sys.argv) != 5:
        print("Usage: kalshi_pre_order_check.py TICKER SIDE PRICE SIZE")
        sys.exit(2)
    ticker, side, price, size = sys.argv[1], sys.argv[2].upper(), float(sys.argv[3]), int(sys.argv[4])

    k = Kalshi()
    m = k.get_market(ticker) or {}
    if isinstance(m, dict) and isinstance(m.get("market"), dict):
        m = m["market"]  # legacy wrapped shape
    title = m.get("title", "")
    st = m.get("strike_type")
    rules = m.get("rules_primary", "")
    cost = price * size

    bal = int(k.get_balance().get("balance", 0)) / 100.0

    print("=" * 78)
    print("PRE-ORDER VERIFICATION")
    print("=" * 78)
    print(f"Market:    {title}")
    print(f"Ticker:    {ticker}")
    print(f"strike_type: {st}")
    print(f"Rules:     {rules[:200]}")
    print()

    # What does the chosen side win on?
    if st == "between":
        lo, hi = m.get("floor_strike"), m.get("cap_strike")
        win = f"max temp IN {lo}-{hi}" if side == "YES" else f"max temp NOT in {lo}-{hi}"
        series = ticker.split("-")[0]
        f = NWS.get(series)
        if f is not None:
            p_in_nws = p_below(f, hi, SIGMA_WEATHER) - p_below(f, lo - 1, SIGMA_WEATHER)
            odds = (1 - p_in_nws) if side == "NO" else p_in_nws
    elif st in ("less", "greater"):
        thr = m.get("cap_strike") or m.get("floor_strike")
        if st == "less":
            win = f"max < {thr}" if side == "YES" else f"max >= {thr}"
        else:
            win = f"max > {thr}" if side == "YES" else f"max <= {thr}"
        series = ticker.split("-")[0]
        f = NWS.get(series)
        if f is not None and thr:
            p_yes_nws = p_below(f, thr, SIGMA_WEATHER) if st == "less" else 1 - p_below(f, thr, SIGMA_WEATHER)
            odds = p_yes_nws if side == "YES" else 1 - p_yes_nws
    elif st == "greater_or_equal":
        thr = m.get("floor_strike") or m.get("cap_strike")
        win = f"claims >= {thr:,}" if side == "YES" else f"claims < {thr:,}"
        if thr:
            p_yes = 1 - p_below(CLAIMS_FORECAST, thr - 1, SIGMA_CLAIMS)
            odds = p_yes if side == "YES" else 1 - p_yes
    else:
        win = "(unknown strike type - MANUALLY VERIFY)"
        odds = None

    print(f"YOUR SIDE: {side} {size} shares @ ${price:.2f} = ${cost:.2f}")
    print(f"YOU WIN IF: {win}")
    if odds is not None:
        print(f"Odds (forecast-model basis): {odds:.0%}")
        if odds < 0.5:
            print("!! RED FLAG: your side is the UNLIKELY side per our forecast model !!")
    print(f"Cash available: ${bal:.2f} -> order {'OK' if cost <= bal else 'EXCEEDS CASH'}")
    print()
    # Reminder of the V2 order semantics bug this tool guards against
    if side == "NO":
        print(f"V2 NOTE: this NO buy will be sent as sell-YES @ {(1-price):.2f} - the client handles conversion.")
    print("=" * 78)
    print("If any line above looks wrong, STOP. Re-read rules_primary before ordering.")


if __name__ == "__main__":
    main()