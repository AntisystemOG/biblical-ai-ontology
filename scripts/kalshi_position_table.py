#!/usr/bin/env python3
"""
kalshi_position_table.py - Live Kalshi position board for Spock.

Pulls real positions + real market prices from the Kalshi API (via kalshi_client.py),
computes cost/value/P&L/win-odds, assigns actions, and prints a table Thad can read
at a glance.

Usage:
  python kalshi_position_table.py [--paper] [--json] [--save]

Flags:
  --paper  Include paper-trader open positions with market-implied outcomes
  --json   Output machine-readable JSON instead of the text table
  --save   Save a timestamped JSON snapshot to Spocks Reports/kalshi/

Universal rule (AGENTS.md): REAL API PRICES ONLY. If the API fails, report it and exit 1.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

KALSHI_DIR = r"C:\AI Projects\Prediction Market\Kalshi"
sys.path.insert(0, KALSHI_DIR)

PAPER_PORTFOLIO = os.path.join(
    KALSHI_DIR, "Kalshi Edge Scanner", "data", "weather", "paper_trader", "portfolio.json"
)
SAVE_DIR = os.path.expanduser(r"~\.openclaw\workspace\Spocks Reports\kalshi")

# Kalshi weather markets resolve on The Weather Company (TWC), not NWS stations.
# We never guess TWC values - grading uses our own market's official result once
# finalized, otherwise its live YES/NO pricing (which embeds the TWC expectation).


def mkt_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def side_of(position_fp):
    """Positive fp = YES shares, negative fp = NO shares."""
    return "YES" if position_fp > 0 else "NO"


def shares_of(position_fp):
    return abs(position_fp)


def our_side_bid(market, side):
    key = "yes_bid_dollars" if side == "YES" else "no_bid_dollars"
    return mkt_float(market.get(key))


def our_side_ask(market, side):
    key = "yes_ask_dollars" if side == "YES" else "no_ask_dollars"
    return mkt_float(market.get(key))


def win_probability(market, side):
    """Market-implied probability that OUR side wins (mid of our-side bid/ask)."""
    bid = our_side_bid(market, side)
    ask = our_side_ask(market, side)
    if ask <= 0.0 or (bid == 0.0 and ask >= 1.0):
        # Degenerate book: use last trade on our side
        return mkt_float(market.get("last_price_dollars"))
    if ask - bid <= 0:
        return bid
    return bid + (ask - bid) / 2.0


def classify_action(row):
    """Thad's rules (rev Aug 28): HOLD is the default. Kalshi consensus is fallible
    (8/9 record - wrong-but-close); being underwater is NOT an exit signal. Write off
    dead positions; real exits need settlement-grade falsification + Thad's call."""
    bid = row["bid"]
    pnl = row["pnl"]
    prob = row["win_odds"]
    close = row.get("close_time", "")
    try:
        ct = close.replace("Z", "+00:00")
        hrs = (datetime.fromisoformat(ct) - datetime.now(timezone.utc)).total_seconds() / 3600
    except Exception:
        hrs = 999
    # Closed book with EMPTY official result = awaiting settlement, NOT decided.
    # Kalshi zeroes the order book at expiry before assigning the TWC result;
    # treating zeroed bids as "decided against us" produced false WRITE-OFFs.
    m_status = (row.get("status") or "").lower()
    m_result = (row.get("result") or "").lower()
    if m_status in ("closed", "finalized") and not m_result:
        return "PENDING SETTLEMENT", "book closed at expiry, bids zeroed - awaiting official TWC settlement"
    # Dead book with a nearly-settled market (close within 24h) = decided. Write off.
    # Dead book with lots of time left (e.g. Sep Fed) = no exit liquidity, just hold.
    if bid <= 0.011 and prob <= 0.05:
        if hrs < 36:
            return "WRITE-OFF", "market decided against us - resolves soon, hold for $0"
        return "HOLD (dead)", "no bid; far from close - nothing to sell into"
    # EXIT DISCIPLINE (Thad, Aug 28): Kalshi consensus can be wrong-but-close.
    # Aug 27: our 205K NO traded to ~0.20 overnight (consensus flipped to 205K YES
    # 0.80), the actual printed 203K, and BOTH positions WON. Market-price
    # deterioration alone is NEVER an exit signal. Underwater + low odds = HOLD;
    # the settlement source (TWC/BLS actual) decides, not the interim book.
    # Exits require settlement-grade falsification of the win condition AND
    # Thad's explicit judgment - never fire automatically.
    if pnl <= -0.05 and hrs <= 24:
        return "HOLD (underwater)", (
            f"down ${-pnl:.2f} at {prob:.0%} market odds, settles in {hrs:.0f}h - "
            "consensus is 8/9 (wrong-but-close): Aug 27 205K NO held through a 20% "
            "overnight panic and WON. Exit only on settlement-grade falsification."
        )
    # Winners ride to settlement too: the old "SELL NOW on profit with < 70% odds"
    # rule would have sold 210K NO @91% pre-release on Aug 27. Holding is free via
    # maker orders; exits pay the spread and cap the payout. Manual profit-taking
    # stays available to Thad but is never auto-recommended.
    if prob >= 0.80:
        return "HOLD", "high confidence"
    if prob >= 0.60:
        return "HOLD", "favored"
    if prob >= 0.45:
        return "HOLD", "coin flip - let it ride"
    return "HOLD", "underdog - small size, ride it"


def fetch_live_rows(k):
    bal = k.get_balance()
    cash = mkt_float(bal.get("balance")) / 100.0

    positions = k.get_positions().get("market_positions", [])
    rows = []
    for p in positions:
        ticker = p.get("ticker", "")
        fp = mkt_float(p.get("position_fp"))
        if fp == 0:
            continue  # fully closed
        side = side_of(fp)
        shares = shares_of(fp)
        try:
            market = k.get_market(ticker) or {}
            if isinstance(market, dict) and isinstance(market.get("market"), dict):
                market = market["market"]  # legacy wrapped shape
        except Exception as e:
            market = {"ticker": ticker, "title": f"FETCH ERROR: {e}"}

        bid = our_side_bid(market, side)
        ask = our_side_ask(market, side)
        last = mkt_float(market.get("last_price_dollars"))
        # The `last` trade price is side-agnostic (it's the last traded price of the market,
        # usually on the winning side). Using it to value OUR side is wrong when our side's
        # book is dead. Only value from our-side bid; if bid is 0 our position is worth $0
        # minus whatever the exit ask would cost. Value = bid (conservative, mark-to-market).
        price_used = bid
        cost = mkt_float(p.get("total_traded_dollars")) + mkt_float(p.get("fees_paid_dollars"))
        value = shares * price_used
        rows.append(
            {
                "ticker": ticker,
                "title": market.get("title", ticker),
                "side": side,
                "shares": shares,
                "avg_entry": round(cost / shares, 3) if shares else 0,
                "cost": round(cost, 2),
                "bid": round(bid, 2),
                "ask": round(ask, 2),
                "last": round(last, 2),
                "value": round(value, 2),
                "pnl": round(value - cost, 2),
                "win_odds": round(win_probability(market, side), 2),
                "close_time": market.get("close_time", ""),
                "status": market.get("status", ""),
                "result": (market.get("result") or ""),
                "event": market.get("event_ticker", ""),
            }
        )
    for r in rows:
        r["action"], r["reason"] = classify_action(r)
    return cash, rows


def paper_rows(k):
    """Paper trader open positions + market-implied outcome for each.

    Grading logic (fixed Aug 27): check OUR OWN market's final result first (settled
    markets), then our own band's YES pricing (which includes our position - that is
    exactly what determines whether our NO loses). Do NOT exclude our own ticker -
    that bug made a 0.99-YES hit band look like a WIN for the NO side.
    """
    try:
        pf = json.load(open(PAPER_PORTFOLIO, encoding="utf-8"))
    except Exception as e:
        return None, [{"error": f"portfolio.json unreadable: {e}"}]
    cash = mkt_float(pf.get("cash"))
    rows = []
    for x in pf.get("open_positions", []):
        ticker = x.get("ticker", "")
        try:
            market = k.get_market(ticker) or {}
            if isinstance(market, dict) and isinstance(market.get("market"), dict):
                market = market["market"]  # legacy wrapped shape
        except Exception as e:
            rows.append({"bet": f"{x.get('city')} {ticker}", "error": str(e)})
            continue
        # Paper bets are always NO on band markets
        no_bid = mkt_float(market.get("no_bid_dollars"))
        status = market.get("status", "")
        result = (market.get("result") or "").lower()
        yes_bid = mkt_float(market.get("yes_bid_dollars"))
        # 1) Finalized markets: use the official result. result=yes => band hit => NO loses.
        if status == "finalized" and result in ("yes", "no"):
            outcome = "WIN" if result == "no" else "LOSS"
        # 2) Active markets: our own band's YES bid IS the market's verdict on our band.
        elif yes_bid >= 0.50:
            outcome = "LOSS"
        elif no_bid >= 0.50:
            outcome = "WIN"
        else:
            outcome = "PENDING"
        payout = mkt_float(x.get("shares")) * 1.0 if outcome == "WIN" else 0.0
        rows.append(
            {
                "bet": f"{x.get('city')} {x.get('band_low')}-{x.get('band_high')}F NO",
                "ticker": ticker,
                "shares": mkt_float(x.get("shares")),
                "entry": mkt_float(x.get("purchase_price")),
                "cost": mkt_float(x.get("bet_amount")),
                "no_bid": round(no_bid, 2),
                "projected": outcome,
                "payout": round(payout, 2),
                "pnl": round(payout - mkt_float(x.get("bet_amount")), 2) if outcome != "PENDING" else None,
                "market_status": status,
                "result": result or None,
            }
        )
    return cash, rows


def fmt_table(live_cash, live_rows, paper_cash, paper_rows_):
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M %Z").strip()
    lines.append(f"KALSHI POSITION BOARD - {now} (live API prices)")
    lines.append("=" * 118)
    lines.append(f"LIVE ACCOUNT  |  Cash: ${live_cash:.2f}  |  {len(live_rows)} open positions")
    lines.append("-" * 118)
    hdr = (
        f"{'#':<2} {'Position':<44} {'Side':<4} {'Shares':>6} {'Entry':>6} "
        f"{'Bid':>5} {'Value':>7} {'Cost':>7} {'P&L':>8} {'Odds':>5}  {'Action':<16} {'Note'}"
    )
    lines.append(hdr)
    lines.append("-" * 118)
    tot_val = tot_cost = tot_pnl = 0.0
    for i, r in enumerate(live_rows, 1):
        tot_val += r["value"]
        tot_cost += r["cost"]
        tot_pnl += r["pnl"]
        name = r["title"][:44]
        lines.append(
            f"{i:<2} {name:<44} {r['side']:<4} {r['shares']:>6.1f} ${r['avg_entry']:>5.2f} "
            f"${r['bid']:>4.2f} ${r['value']:>6.2f} ${r['cost']:>6.2f} ${r['pnl']:>+7.2f} {r['win_odds']*100:>4.0f}%  {r['action']:<16} {r['reason']}"
        )
    lines.append("-" * 118)
    lines.append(
        f"   TOTALS: cost ${tot_cost:.2f} -> value ${tot_val:.2f}  |  unrealized P&L ${tot_pnl:+.2f}  "
        f"|  account ${live_cash + tot_val:.2f}"
    )
    if paper_rows_ is not None:
        lines.append("")
        lines.append("=" * 118)
        lines.append(f"PAPER WEATHER TRADER  |  Cash: ${paper_cash:.2f} (from $100)")
        lines.append("-" * 118)
        lines.append(
            f"{'#':<2} {'Bet':<28} {'Shares':>6} {'Entry':>6} {'NO Bid':>7} {'Cost':>7} {'Projected':>10} {'Payout':>8} {'P&L':>8}"
        )
        for i, r in enumerate(paper_rows_, 1):
            if "error" in r:
                lines.append(f"{i:<2} {str(r.get('bet')):<28} ERROR: {r['error'][:70]}")
                continue
            if r.get("pnl") is None:
                # PENDING: book undecided, no reliable mark yet - don't print fake numbers
                lines.append(
                    f"{i:<2} {r['bet']:<28} {r['shares']:>6.1f} ${r['entry']:>5.2f} "
                    f"${r['no_bid']:>6.2f} ${r['cost']:>6.2f} {r['projected']:>9} {'--':>8} {'--':>8}"
                )
                continue
            lines.append(
                f"{i:<2} {r['bet']:<28} {r['shares']:>6.1f} ${r['entry']:>5.2f} "
                f"${r['no_bid']:>6.2f} ${r['cost']:>6.2f} {r['projected']:>9} ${r['payout']:>7.2f} ${r['pnl']:>+7.2f}"
            )
        net = sum(r["pnl"] for r in paper_rows_ if r.get("pnl") is not None)
        lines.append(f"   Projected net tonight: ${net:+.2f} -> cash ~${paper_cash + max(net,0) + min(net,0):.2f}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    from kalshi_client import Kalshi

    try:
        k = Kalshi()
        live_cash, live_rows = fetch_live_rows(k)
        paper_cash, paper_rows_ = (None, None)
        if args.paper:
            paper_cash, paper_rows_ = paper_rows(k)
    except Exception as e:
        print(f"KALSHI API UNAVAILABLE: {e}")
        sys.exit(1)

    if args.save:
        os.makedirs(SAVE_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        snap = {
            "timestamp": datetime.now().isoformat(),
            "live_cash": live_cash,
            "positions": live_rows,
        }
        if paper_rows_ is not None:
            snap["paper_cash"] = paper_cash
            snap["paper_positions"] = paper_rows_
        path = os.path.join(SAVE_DIR, f"positions_{stamp}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
        print(f"[saved: {path}]", file=sys.stderr)

    if args.json:
        out = {"timestamp": datetime.now().isoformat(), "live_cash": live_cash, "positions": live_rows}
        if paper_rows_ is not None:
            out["paper_cash"] = paper_cash
            out["paper_positions"] = paper_rows_
        print(json.dumps(out, indent=2))
    else:
        print(fmt_table(live_cash, live_rows, paper_cash, paper_rows_))


if __name__ == "__main__":
    main()