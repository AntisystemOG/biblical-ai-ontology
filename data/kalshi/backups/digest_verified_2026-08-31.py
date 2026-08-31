"""
Kalshi Digest — Context Compressor
===================================
Runs scanner + web research, outputs a tight 10-15 line briefing
designed for AI context efficiency. Instead of feeding raw API output
to the agent, this pre-digests everything into decision-ready text.

Usage: python digest.py [--claims | --cpi | --fed | --all]
Output: Prints compressed briefing to stdout (10-15 lines max)
       Also saves full data to data/digest_YYYY-MM-DD.json
"""

import sys
import json
import os
import math
import requests
import re
from datetime import datetime, timedelta
from pathlib import Path

# ── Setup ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Kalshi Client (uses shared kalshi_client.py)
sys.path.insert(0, r"C:\\AI Projects\\Prediction Market\\Kalshi")
try:
    from kalshi_client import Kalshi
    _kalshi = Kalshi()
except Exception:
    _kalshi = None

KALSHI_API = "https://external-api.kalshi.com/trade-api/v2"
KALSHI_KEY_ID = "8eb3c7cd-e77c-4f40-9519-3d9f6c3fbd60"
KALSHI_KEY_FILE = r"C:\AI Projects\Prediction Market\Kalshi\For Spock\For Spock 0813.txt"

# ── Kalshi API Client (lightweight) ───────────────────────────────────

def get_auth_headers(method="GET", path="/portfolio/balance"):
    """Get authenticated headers for Kalshi API — direct signed requests.
    NOTE: path must be the FULL path from root (/trade-api/v2/portfolio/balance),
    not just the endpoint path (/portfolio/balance).
    """
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.backends import default_backend
        import base64, datetime

        with open(KALSHI_KEY_FILE, "rb") as f:
            key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        path_without_query = path.split('?')[0]
        message = f"{timestamp}{method}{path_without_query}".encode('utf-8')
        sig = key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256(),
        )
        sig_b64 = base64.b64encode(sig).decode("utf-8")

        return {
            "KALSHI-ACCESS-KEY": KALSHI_KEY_ID,
            "KALSHI-ACCESS-SIGNATURE": sig_b64,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
        }
    except Exception as e:
        pass
    return {}


def fetch_markets(series_ticker, limit=50):
    """Fetch open markets from Kalshi (public, no auth needed)."""
    if _kalshi:
        return _kalshi.get_markets(series_ticker=series_ticker, limit=limit)
    try:
        r = requests.get(f"{KALSHI_API}/markets",
                         params={"series_ticker": series_ticker, "status": "open", "limit": limit},
                         headers={"Accept": "application/json"}, timeout=15)
        if r.ok:
            return r.json().get("markets", [])
    except:
        pass
    return []


def fetch_balance():
    """Get portfolio balance."""
    if _kalshi:
        return _kalshi.get_balance() or {}
    full_path = "/trade-api/v2/portfolio/balance"
    headers = get_auth_headers("GET", full_path)
    try:
        r = requests.get(f"{KALSHI_API}/portfolio/balance", headers=headers, timeout=15)
        if r.ok:
            return r.json()
    except:
        pass
    return {}


def fetch_positions():
    """Get open positions."""
    if _kalshi:
        return _kalshi.get_positions() or {}
    full_path = "/trade-api/v2/portfolio/positions"
    headers = get_auth_headers("GET", full_path)
    try:
        r = requests.get(f"{KALSHI_API}/portfolio/positions", headers=headers, timeout=15)
        if r.ok:
            return r.json()
    except:
        pass
    return {}

# ── Data Processing ───────────────────────────────────────────────────



def validate_positions(positions, our_forecast, consensus):
    """Check if existing positions are on the RIGHT side of the forecast.
    Returns list of warnings for positions that bet against the forecast.
    YES = betting claims >= threshold
    NO  = betting claims < threshold
    """
    warnings = []
    open_pos = positions.get("market_positions", [])
    for p in open_pos:
        ticker = p.get("ticker", "")
        shares = float(p.get("position_fp", 0) or 0)
        # Positive shares = YES, negative shares = NO
        is_yes = shares > 0
        threshold = extract_threshold(ticker)
        if threshold is None:
            continue

        threshold_k = threshold / 1000
        forecast_k = our_forecast / 1000
        consensus_k = (consensus or our_forecast) / 1000

        if is_yes:
            # YES = betting claims >= threshold
            if our_forecast < threshold:
                # Forecast says claims BELOW threshold, but we're betting above
                warnings.append(
                    f"  ⚠️ WRONG SIDE: {ticker} YES (betting >={threshold_k:.0f}K) "
                    f"but forecast is {forecast_k:.1f}K — consider selling"
                )
        else:
            # NO = betting claims < threshold
            if our_forecast >= threshold:
                # Forecast says claims ABOVE threshold, but we're betting below
                warnings.append(
                    f"  ⚠️ WRONG SIDE: {ticker} NO (betting <{threshold_k:.0f}K) "
                    f"but forecast is {forecast_k:.1f}K — consider selling"
                )
    return warnings


def extract_threshold(ticker):
    """Extract numeric threshold from ticker like KXJOBLESSCLAIMS-26AUG20-210000."""
    match = re.search(r"-(\d{6})$", ticker)
    return int(match.group(1)) if match else None


def get_claims_consensus(markets, target_date="26AUG20"):
    """Extract Kalshi market consensus from threshold markets."""
    target_markets = [m for m in markets if target_date in m.get("ticker", "")]
    thresholds = []
    for m in target_markets:
        t = extract_threshold(m.get("ticker", ""))
        if t is None:
            continue
        yes_bid = float(m.get("yes_bid_dollars") or 0)
        yes_ask = float(m.get("yes_ask_dollars") or 0)
        no_bid = float(m.get("no_bid_dollars") or 0)
        no_ask = float(m.get("no_ask_dollars") or 0)
        vol = float(m.get("volume_fp", 0) or 0)

        if yes_bid and yes_ask:
            yes_mid = (yes_bid + yes_ask) / 2
        elif yes_ask:
            yes_mid = yes_ask
        elif no_ask:
            yes_mid = 1.0 - no_ask
        else:
            yes_mid = 0.5

        thresholds.append({
            "ticker": m.get("ticker", ""),
            "threshold": t,
            "yes_mid": yes_mid,
            "no_mid": 1.0 - yes_mid,
            "yes_ask": yes_ask,
            "no_ask": no_ask,
            "volume": vol,
        })

    thresholds.sort(key=lambda x: x["threshold"])

    # Find 50% crossing
    consensus = None
    for i, t in enumerate(thresholds):
        if t["yes_mid"] <= 0.50:
            if i > 0:
                prev = thresholds[i - 1]
                if prev["yes_mid"] > 0.50:
                    frac = (prev["yes_mid"] - 0.50) / (prev["yes_mid"] - t["yes_mid"])
                    consensus = prev["threshold"] + frac * (t["threshold"] - prev["threshold"])
                else:
                    consensus = t["threshold"]
            else:
                consensus = t["threshold"]
            break

    return consensus, thresholds


def find_best_edges(thresholds, our_forecast, spread=10000):
    """Find the markets with the best edge."""
    picks = []
    for t in thresholds:
        threshold = t["threshold"]
        yes_price = t["yes_ask"] if t["yes_ask"] > 0 else (1 - t["no_ask"] if t["no_ask"] > 0 else 0.5)
        no_price = t["no_ask"] if t["no_ask"] > 0 else (1 - t["yes_ask"] if t["yes_ask"] > 0 else 0.5)

        z = (threshold - our_forecast) / spread
        our_prob_above = 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
        our_prob_below = 1 - our_prob_above

        if our_prob_above > 0.60 and yes_price < our_prob_above:
            edge = our_prob_above - yes_price
            if edge > 0.03:
                picks.append({
                    "ticker": t["ticker"], "side": "YES", "price": yes_price,
                    "prob": our_prob_above, "edge": edge, "vol": t["volume"],
                })
        elif our_prob_below > 0.60 and no_price < our_prob_below:
            edge = our_prob_below - no_price
            if edge > 0.03:
                picks.append({
                    "ticker": t["ticker"], "side": "NO", "price": no_price,
                    "prob": our_prob_below, "edge": edge, "vol": t["volume"],
                })

    picks.sort(key=lambda x: x["edge"], reverse=True)
    return picks[:5]


def get_timing_info():
    """Determine where we are in the weekly claims cycle."""
    today = datetime.now()
    weekday = today.weekday()  # 0=Mon, 6=Sun

    # Claims release: Thursday 8:30 AM ET
    thursday = 3
    days_to_thursday = (thursday - weekday) % 7

    if days_to_thursday == 0:
        hour = today.hour
        if hour < 7:
            timing = "T-0 (release day, pre-close)"
        elif hour < 8:
            timing = "T-0 (release day, closing soon)"
        else:
            timing = "T-0+ (post-release, grade now)"
    elif days_to_thursday == 1:
        timing = "T-1 (last chance to pre-position)"
    elif days_to_thursday == 2:
        timing = "T-2 (sweet spot entry window)"
    elif days_to_thursday == 3:
        timing = "T-3 (buy window opening)"
    elif days_to_thursday == 4:
        timing = "T-4 (early watch)"
    elif days_to_thursday == 5:
        timing = "T-5 (post-release grading)"
    else:
        timing = "T-6 (weekend, no action)"

    return timing, days_to_thursday


# ── Recent claims data (hardcoded from known data, would be fetched) ──

MAX_CLAIMS_SIGMA = 3500  # empirical claims sigma (8-sample record)

RECENT_CLAIMS = [
    {"date": "2026-08-15", "actual": 206000, "consensus": 209900},
    {"date": "2026-08-08", "actual": 209000, "consensus": 202000},
    {"date": "2026-08-01", "actual": 200000, "consensus": 205000},
    {"date": "2026-07-25", "actual": 198000, "consensus": 201000},
    {"date": "2026-07-18", "actual": 189000, "consensus": 195000},
]


# ── Main Digest Function ───────────────────────────────────────────────

def digest_claims():
    """Generate compressed claims market briefing."""
    timing, days_to = get_timing_info()

    # Fetch data
    markets = fetch_markets("KXJOBLESSCLAIMS")

    # Find next Thursday target date
    today = datetime.now()
    next_thursday = today + timedelta(days=days_to)
    target_str = next_thursday.strftime("%y%b%d").upper()
    # Kalshi format: 26AUG20
    target_str = f"{next_thursday.year % 100:02d}{next_thursday.strftime('%b').upper()}{next_thursday.day:02d}"

    consensus, thresholds = get_claims_consensus(markets, target_str)

    # Our forecast: blend Kalshi consensus + recent average
    recent_actuals = [r["actual"] for r in RECENT_CLAIMS]
    recent_avg = sum(recent_actuals) / len(recent_actuals)

    if consensus:
        # Claims model v2.3 (coded Aug 26): Kalshi 0.70 / analyst 0.10 / recent 0.20
        # digest has no analyst feed; redistribute analyst weight to recent
        our_forecast = consensus * 0.70 + recent_avg * 0.30
    else:
        our_forecast = recent_avg

    # sigma = 3500 claims (empirical, coded Aug 26; 1.28*sigma = 4.5K 80% CI)
    spread = MAX_CLAIMS_SIGMA

    # Find best edges
    top_picks = find_best_edges(thresholds, our_forecast, spread)

    # Get portfolio
    balance = fetch_balance()
    positions = fetch_positions()

    cash = balance.get("balance_dollars", "?")
    # Portfolio value = cash + marked positions. The balance endpoint does NOT
    # carry a portfolio_value field (old code printed garbage like 1704).
    pos_value_total = 0.0
    pv = None
    pv_str = "?"  # computed after position marks below

    open_pos = positions.get("market_positions", [])
    pos_lines = []
    
    # Fetch live market prices for positions.
    # BUG FIXED Aug 30: get_market() returns null *_dollars for non-weather series
    # (documented Aug 26) - which zeroed every Fed position mark. Use series-level
    # get_markets() instead, which always carries *_dollars.
    series_seen = []
    for p_ in open_pos:
        t_ = p_.get("ticker", "")
        s = t_.split("-")[0]  # first segment IS the series (KXHIGHDEN, KXFEDDECISION, ...)
        if s and s not in series_seen:
            series_seen.append(s)
    live_prices = {}
    if series_seen and _kalshi:
        try:
            for s in series_seen:
                for market in _kalshi.get_markets(series_ticker=s, limit=100):
                    tk = market.get("ticker")
                    if tk:
                        live_prices[tk] = {
                            "yes_bid": float(market.get("yes_bid_dollars", 0) or 0),
                            "yes_ask": float(market.get("yes_ask_dollars", 0) or 0),
                            "no_bid": float(market.get("no_bid_dollars", 0) or 0),
                            "no_ask": float(market.get("no_ask_dollars", 0) or 0),
                        }
        except Exception:
            pass
    
    for p in open_pos:
        ticker = p.get("ticker", "?")
        shares = float(p.get("position_fp", 0) or 0)
        # market_exposure_dollars = basis of the CURRENT position (correct after trims);
        # total_traded_dollars includes trimmed legs and overstates cost.
        cost = float(p.get("market_exposure_dollars", 0) or 0) or float(p.get("total_traded_dollars", 0) or 0)
        direction = "YES" if shares > 0 else "NO"
        threshold = extract_threshold(ticker)
        thresh_str = f" (>={threshold/1000:.0f}K)" if threshold else ""
        
        # Calculate current value and P&L
        current_value = 0
        pnl_str = ""
        action_str = ""
        
        if ticker in live_prices:
            lp = live_prices[ticker]
            if direction == "YES":
                current_price = lp["yes_bid"]  # Sell at bid
                current_value = abs(shares) * current_price
            else:
                current_price = lp["no_bid"]  # Sell at bid
                current_value = abs(shares) * current_price
            if current_price <= 0:
                # zero bid from a dead/illiquid series: mark unknown, use cost (no fake -100%)
                current_value = cost
            
            if cost > 0:
                pnl = current_value - cost
                pnl_pct = (pnl / cost) * 100
                pnl_str = f" | P&L: ${pnl:+.2f} ({pnl_pct:+.0f}%)"
                
                # Exit discipline (Thad, Aug 28): consensus can be wrong-but-close.
                # Aug 27: overnight market flipped to 205K YES 0.80 (our NO at ~0.20),
                # actual printed 203K - held through the panic and WON. Market moves
                # are never an exit signal; hold to settlement unless settlement-grade
                # data falsifies the win condition (Thad's judgment, never automatic).
                if pnl > 0.05:
                    action_str = " | HOLD to settlement (profitable)"
                elif pnl < -0.05:
                    action_str = " | HOLD (underwater - consensus can be wrong)"
                else:
                    action_str = " | HOLD"
        
        if current_value:
            pos_value_total += current_value

        pos_lines.append(f"  {ticker}: {direction}{thresh_str} | {abs(shares):.2f} sh @ ${cost}{pnl_str}{action_str}")

    # Compute portfolio value: cash + live marks
    try:
        cash_num = float(cash)
    except Exception:
        cash_num = 0.0
    pv_value = cash_num + pos_value_total

    # Build compressed output (10-15 lines max)
    lines = []
    lines.append(f"KALSHI CLAIMS DIGEST | {datetime.now().strftime('%b %d %H:%M CDT')} | Timing: {timing}")
    lines.append(f"Portfolio: ${cash} cash | ${pos_value_total:.2f} in live positions | book ${cash_num + pos_value_total:.2f} | {len(open_pos)} open")

    if pos_lines:
        for p in pos_lines[:5]:
            lines.append(p)

    # Validate positions against forecast
    pos_warnings = validate_positions(positions, our_forecast, consensus)
    if pos_warnings:
        lines.append("⚠️ POSITION VALIDATION:")
        for w in pos_warnings:
            lines.append(w)

    lines.append(f"Recent claims: {' -> '.join(str(r['actual']//1000)+'K' for r in RECENT_CLAIMS[:4])} | 4wk avg: {recent_avg/1000:.0f}K")

    if consensus:
        lines.append(f"Kalshi consensus: {consensus/1000:.1f}K | Our forecast: {our_forecast/1000:.1f}K (+/-{spread/1000:.0f}K)")
    else:
        lines.append(f"No Kalshi consensus for {target_str} | Our forecast: {our_forecast/1000:.1f}K (±{spread/1000:.0f}K)")

    if top_picks:
        lines.append("TOP EDGES:")
        for p in top_picks[:3]:
            ret = (1.0 / p["price"] - 1) * 100
            lines.append(f"  {p['ticker']}: {p['side']} @ {p['price']:.2f} | edge +{p['edge']:.0%} | return {ret:.0f}% | vol {p['vol']:,.0f}")
    else:
        lines.append("No edges >3% found. Market is efficient.")

    # Try to load lessons from prompt_evolution
    try:
        sys.path.insert(0, str(BASE_DIR))
        from prompt_evolution import get_current_lessons
        lessons = get_current_lessons()
        lines.append(lessons)
    except:
        pass
    
    # Timing-specific action
    if "T-3" in timing:
        action = "ACTION: Buy window open. Log prices. Don't rush — only if edge >10%."
    elif "T-2" in timing:
        action = "ACTION: Sweet spot entry. Buy if edge >5% and prices favorable."
    elif "T-1" in timing:
        action = "ACTION: Last chance. Execute if edge >5% and confidence >80%."
    elif "T-0 (release day, pre-close" in timing or "T-0 (release day, closing" in timing:
        action = "ACTION: Final call. Markets close soon. Buy or pass. Don't force."
    elif "post-release" in timing:
        action = "ACTION: Grade results. Run grade_predictions.py."
    else:
        action = "ACTION: Monitor. No rush."

    lines.append(action)
    
    # Long shots section
    long_shots = [p for p in top_picks if p["price"] < 0.15 or p["edge"] > 0.30]
    if long_shots:
        lines.append("")
        lines.append("LONG SHOTS (high risk / high reward — small bets only):")
        for p in long_shots[:3]:
            ret = (1.0 / p["price"] - 1) * 100
            lines.append(f"  {p['ticker']}: {p['side']} @ {p['price']:.2f} | edge +{p['edge']:.0%} | return {ret:.0f}% | vol {p['vol']:,.0f}")
    
    # Weather market section (uses weather_model.py rules)
    try:
        sys.path.insert(0, str(BASE_DIR))
        from weather_model import weather_digest
        weather = weather_digest()
        lines.append("")
        lines.append(weather)
    except:
        pass
    else:
        # Scan for cheap markets across all series
        cheap_markets = []
        for series in ["KXJOBLESSCLAIMS", "KXFEDDECISION", "KXHIGHNY", "KXHIGHMIA", "KXHIGHCHI", "KXHIGHDEN"]:
            try:
                mks = fetch_markets(series, limit=50)
                for m in mks:
                    yes_ask = float(m.get("yes_ask_dollars") or 0)
                    no_ask = float(m.get("no_ask_dollars") or 0)
                    vol = float(m.get("volume_fp", 0) or 0)
                    ticker = m.get("ticker", "")
                    title = m.get("title", "")[:60]
                    if vol < 10:
                        continue
                    # Cheap YES tickets with high return potential
                    if 0.02 <= yes_ask <= 0.10 and vol > 50:
                        ret = (1.0 / yes_ask - 1) * 100
                        cheap_markets.append((ticker, "YES", yes_ask, ret, vol, title))
                    # Cheap NO tickets with high return potential
                    if 0.02 <= no_ask <= 0.10 and vol > 50:
                        ret = (1.0 / no_ask - 1) * 100
                        cheap_markets.append((ticker, "NO", no_ask, ret, vol, title))
            except:
                pass
        cheap_markets.sort(key=lambda x: x[3], reverse=True)
        if cheap_markets:
            lines.append("")
            lines.append("LONG SHOTS (high risk / high reward — small bets only):")
            for t, s, price, ret, vol, title in cheap_markets[:3]:
                lines.append(f"  {t}: {s} @ {price:.2f} | return {ret:.0f}% | vol {vol:,.0f} | {title[:40]}")

    # Save full data
    full_data = {
        "timestamp": datetime.now().isoformat(),
        "timing": timing,
        "portfolio": {"cash": cash, "positions_marked": round(pos_value_total, 2),
                      "book_value": round(cash_num + pos_value_total, 2), "positions": open_pos},
        "recent_claims": RECENT_CLAIMS,
        "kalshi_consensus": consensus,
        "our_forecast": our_forecast,
        "spread": spread,
        "top_picks": top_picks,
        "all_thresholds": thresholds,
    }
    digest_path = DATA_DIR / f"digest_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(digest_path, "w") as f:
        json.dump(full_data, f, indent=2, default=str)

    return "\n".join(lines)


def digest_all():
    """Run all digests."""
    return digest_claims()


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "claims"

    if target == "claims":
        print(digest_claims())
    elif target == "all":
        print(digest_all())
    else:
        print(f"Usage: python digest.py [claims|all]")
        print(digest_claims())  # default to claims


if __name__ == "__main__":
    main()
