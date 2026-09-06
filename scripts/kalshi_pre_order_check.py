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
from pathlib import Path
import time
import os
import json
import math
import sys

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
from kalshi_client import Kalshi

from datetime import datetime
from kalshi_client import Kalshi

# Fresh forecasts (Aug 31 audit fix): the old hardcoded anchors (DEN 91 / claims 205303)
# were 4-6 days stale and made the printed odds wrong. Live NWS fetch per ticker date +
# newest-digest claims read; the constants below are ONLY offline fallbacks.
FALLBACK_NWS = {"KXHIGHDEN": 88, "KXHIGHMIA": 89, "KXHIGHCHI": 88, "KXHIGHNY": 81}
SIGMA_WEATHER = 2.0
FALLBACK_CLAIMS = 205303
SIGMA_CLAIMS = 3500

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")
try:
    from weather_predictor import CITIES, fetch_nws_forecast, adjust_forecast
    _HAVE_WX = True
except Exception:
    _HAVE_WX = False


def _live_nws(series, ticker):
    """Fresh NWS forecast for the ticker's own date, city rules + TWC(+1.5, capped).
    Returns the fallback constant only when the live fetch fails."""
    if not _HAVE_WX or not series.startswith("KXHIGH"):
        return FALLBACK_NWS.get(series)
    try:
        code = series.replace("KXHIGH", "")
        latlon = next((v[:2] for v in CITIES.values() if v[2] == code), None)
        if not latlon:
            return FALLBACK_NWS.get(series)
        tok = ticker.split("-")[1]
        dt = datetime.strptime(f"20{tok[0:2]}-{tok[2:5]}-{tok[5:7]}", "%Y-%b-%d").date().isoformat()
        period = fetch_nws_forecast(latlon[0], latlon[1], dt)
        if not period:
            return FALLBACK_NWS.get(series)
        base = float(period.get("temperature") or 0)
        if not base:
            return FALLBACK_NWS.get(series)
        short_fc = (period.get("shortForecast") or "").lower()
        wind = (period.get("windDirection") or "").upper()
        pprob = (period.get("probabilityOfPrecipitation") or {}).get("value") or 0
        adj, _n = adjust_forecast(base, code, wind, 0, pprob,
                                  "thunder" in short_fc or "storm" in short_fc)
        return round(min(adj + 1.5, base + 2.0), 1)  # TWC settlement bias, capped vs raw NWS
    except Exception:
        return FALLBACK_NWS.get(series)


def _live_claims_forecast():
    """Newest digest's blended forecast (fallback if absent)."""
    try:
        import glob
        files = sorted(glob.glob(r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner\data\digest_*.json"))
        if files:
            with open(files[-1]) as fh:
                of = json.load(fh).get("our_forecast")
            if of:
                return float(of)
    except Exception:
        pass
    return FALLBACK_CLAIMS


def p_below(f, thr, sigma):
    z = (thr - f) / sigma
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))




def city_realized_pnl(k):
    """Net lifetime P&L per city/series: settlement revenue + sell proceeds - fill costs.
    Fill conventions VERIFIED from live records (Aug 30 forensics):
      YES buy:  action=buy,  side=yes, book_side=bid -> cash OUT at yes_price
      NO buy:   action=sell, side=no,  book_side=ask -> cash OUT at no_price
      NO trim:  action=sell, side=yes, book_side=bid -> cash IN  at no_price
    Cached for 6h in workspace data dir."""
    from collections import defaultdict
    cache_path = Path(os.path.expanduser(r"~\.openclaw\workspace\data\kalshi\city_pnl.json"))
    try:
        if cache_path.exists():
            age_h = (time.time() - cache_path.stat().st_mtime) / 3600
            if age_h < 6:
                return {c: v for c, v in json.loads(cache_path.read_text()).items()}
    except Exception:
        pass
    fills = k.get("/portfolio/fills", params={"limit": 200}, auth=True)
    frows = (fills.get("fills") if isinstance(fills, dict) else None) or []
    cash_out = defaultdict(float)
    cash_in = defaultdict(float)
    for f in frows:
        t = f.get("ticker")
        if not t:
            continue
        sh = float(f.get("count_fp") or 0)
        fee = float(f.get("fee_cost") or 0)
        act, side = f.get("action"), f.get("side")
        book = f.get("book_side")
        yp = float(f.get("yes_price_dollars") or 0)
        np_ = float(f.get("no_price_dollars") or 0)
        # Verified across both API eras (Aug 17 old-API vs Aug 27+ V2):
        #   old NO buys:  act=buy,  side=no,  book=ask  -> OUT at no_price (MIA Aug25)
        #   V2  NO buys:  act=sell, side=no,  book=ask  -> OUT at no_price (DEN Aug30)
        #   YES buys:     act=buy,  side=yes, book=bid  -> OUT at yes_price
        #   NO trims:     act=sell, side=yes, book=bid  -> IN  at no_price (cash in 2.04 = 2.11 x 0.97)
        #   plain YES sells: act=sell, side=yes, book=ask -> IN at yes_price
        if act == "buy" and side == "yes":
            cash_out[t] += sh * yp + fee          # YES buy
        elif act == "buy" and side == "no":
            cash_out[t] += sh * np_ + fee         # old-era NO buy
        elif act == "sell" and side == "no":
            cash_out[t] += sh * np_ + fee         # V2-era NO buy (sell/no + ask book)
        elif act == "sell" and side == "yes":
            if book == "bid":
                cash_in[t] += sh * np_ - fee      # V2 NO trim (sold into no side at 0.97)
            else:
                cash_in[t] += sh * yp - fee       # plain YES sale
    st = k.get("/portfolio/settlements", params={"limit": 100}, auth=True)
    srows = (st.get("settlements") if isinstance(st, dict) else None) or []
    gpnl = defaultdict(float)
    for r in srows:
        t = r.get("ticker", "")
        rev = float(r.get("revenue") or 0) / 100.0
        key = t.split("-")[0].replace("KXHIGH", "") if t.startswith("KXHIGH") else t.split("-")[0].replace("KX", "")
        gpnl[key] += rev - cash_out.get(t, 0.0) + cash_in.get(t, 0.0)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(gpnl))
    except Exception:
        pass
    return dict(gpnl)


def _market_center(k, ticker, series):
    """Market-implied modal center for the same city-day band ladder (YES-mid weighted).
    The market settles on TWC, so its center ALREADY embeds the TWC premium -
    never pay the premium twice (NY Aug 31 lesson)."""
    try:
        date_part = ticker.split("-")[1]
        mkts = k.get_markets(series_ticker=series, limit=100)
        rows = []
        for x in mkts:
            t = x.get("ticker", "")
            if "-" not in t or t.split("-")[1] != date_part:
                continue
            lo, hi = x.get("floor_strike"), x.get("cap_strike")
            if lo is None or hi is None:
                continue  # bands only
            ya = float(x.get("yes_ask_dollars") or 0)
            yb = float(x.get("yes_bid_dollars") or 0)
            mid = (ya + yb) / 2.0
            mid = (ya + yb) / 2.0
            if 0 < mid <= 1:
                rows.append((mid, (float(lo) + float(hi)) / 2.0))
        if not rows:
            return None
        tw = sum(r[0] for r in rows)
        if tw <= 0:
            return None
        return sum(r[0] * r[1] for r in rows) / tw
    except Exception:
        return None


def _same_day_lottery_exposure(k, ticker, new_cost, new_price):
    """Aggregate same-day YES-lottery exposure across all cities.

    Sums total cost of ALL open positions with entry avg <= 30c that resolve
    on the SAME date as `ticker`, plus the proposed new order cost.
    Returns (total_exposure, settled_bankroll, pct, breach: bool).
    Settled bankroll = current cash balance (post-settlement, pre-order)."""
    try:
        date_part = ticker.split("-")[1]  # e.g. "26SEP04"
    except (IndexError, ValueError):
        date_part = ""
    if not date_part:
        return 0.0, 0.0, 0.0, False

    total_exposure = 0.0
    try:
        positions = k.get_positions().get("market_positions", [])
        for p in positions:
            t = p.get("ticker", "")
            if date_part not in t:
                continue
            fp = float(p.get("position_fp") or 0)
            if fp <= 0:
                continue  # only YES positions (positive fp)
            sh = abs(fp)
            cost = float(p.get("total_traded_dollars") or 0) + float(p.get("fees_paid_dollars") or 0)
            avg_entry = cost / sh if sh else 0
            if avg_entry <= 0.30:
                total_exposure += cost
    except Exception:
        pass

    total_exposure += new_cost  # include the proposed order

    bal = int(k.get_balance().get("balance", 0)) / 100.0
    pct = (total_exposure / bal) if bal else 1.0
    LOTTERY_DAY_CAP_PCT = 0.03  # 3% of settled bankroll, all cities combined
    breach = pct > LOTTERY_DAY_CAP_PCT
    return total_exposure, bal, pct, breach



def main():

    if len(sys.argv) not in (5, 6):
        print("Usage: kalshi_pre_order_check.py TICKER SIDE PRICE SIZE [OVERRIDE]")
        sys.exit(2)
    ticker, side, price, size = sys.argv[1], sys.argv[2].upper(), float(sys.argv[3]), int(sys.argv[4])
    override = sys.argv[5].upper() if len(sys.argv) == 6 else ""

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
        f = _live_nws(series, ticker)
        # Model upgrade Sep 4: apply learned city bias + per-city sigma
        try:
            import kalshi_db as _kdb
            _code = series.replace("KXHIGH", "")
            if f is not None:
                f = f + _kdb.city_bias(_code)
            _sig = _kdb.city_sigma(_code)
        except Exception:
            _sig = SIGMA_WEATHER
        if f is not None:
            p_in_nws = p_below(f, hi, _sig) - p_below(f, lo - 1, _sig)
            odds = (1 - p_in_nws) if side == "NO" else p_in_nws
        # MARKET-CENTER SANITY (NY Aug 31 lesson: TWC premium is already inside
        # market prices - buying bands above market center on NWS+TWC double-counts)
        mc = _market_center(k, ticker, series)
        if f is not None and mc is not None:
            gap = f - mc
            print(f"Model center {f:.1f}F vs market-implied center {mc:.1f}F (gap {gap:+.1f}F)")
            if gap >= 2.0:
                print("!! RED FLAG: model sits 2F+ ABOVE market center - market already prices TWC; buying the premium double-counts. Need Thad override.")
    elif st in ("less", "greater"):
        thr = m.get("cap_strike") or m.get("floor_strike")
        if st == "less":
            win = f"max < {thr}" if side == "YES" else f"max >= {thr}"
        else:
            win = f"max > {thr}" if side == "YES" else f"max <= {thr}"
        series = ticker.split("-")[0]
        f = _live_nws(series, ticker)
        try:
            import kalshi_db as _kdb
            _code = series.replace("KXHIGH", "")
            if f is not None:
                f = f + _kdb.city_bias(_code)
            _sig = _kdb.city_sigma(_code)
        except Exception:
            _sig = SIGMA_WEATHER
        if f is not None and thr:
            p_yes_nws = p_below(f, thr, _sig) if st == "less" else 1 - p_below(f, thr, _sig)
            odds = p_yes_nws if side == "YES" else 1 - p_yes_nws
    elif st == "greater_or_equal":
        thr = m.get("floor_strike") or m.get("cap_strike")
        win = f"claims >= {thr:,}" if side == "YES" else f"claims < {thr:,}"
        if thr:
            p_yes = 1 - p_below(_live_claims_forecast(), thr - 1, SIGMA_CLAIMS)
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

    # Regime-shift blackout (improvement 2, Sep 5): no new entries during forecast instability
    try:
        import kalshi_db as _kdb2
        _today = datetime.now().strftime("%Y-%m-%d")
        for _s in _kdb2.all_state():
            if _s["key"].startswith("regime_shift_") and _today in str(_s["value"]):
                print(f"!! REGIME BLACKOUT: {_s['key']} active today - {_s['value']}")
                print("   New entries during a revision window need Thad override.")
                break
    except Exception:
        pass

    # SIZING GATE (added Aug 30 after Aug 29 MIA oversize: 43sh @ $0.06 = $2.70 ~5% of cash,
    # plus a second same-city leg = ~8% total. Lottery cap is 2%.)
    LOTTERY_CAP_PCT = 0.02   # cheap-band YES lotteries: 2% of cash max
    LOTTERY_DAY_CAP_PCT = 0.03  # aggregate same-day YES-lottery cap: 3% of settled bankroll (all cities combined)
    GENERAL_CAP_PCT = 0.08   # sure-thing/edge ladder top
    EVENT_CAP = 20.00        # per city-day event cap
    pct = (cost / bal) if bal else 1.0
    flags = []
    if price <= 0.30 and pct > LOTTERY_CAP_PCT * 1.10:  # 10% tolerance for fee/float noise
        flags.append(f"LOTTERY OVERSIZE: ${cost:.2f} = {pct:.0%} of cash (cap 2%)")
    # AGGREGATE SAME-DAY YES-LOTTERY CAP (Sep 4 lesson: $7.22 on three YES lotteries all lost)
    # Total exposure on positions with entry <= 30c, same date, all cities combined, must stay <= 3% of settled bankroll.
    if price <= 0.30:
        try:
            agg_expo, agg_bankroll, agg_pct, agg_breach = _same_day_lottery_exposure(k, ticker, cost, price)
            print(f"Same-day YES-lottery exposure (all cities, entry<=30c): ${agg_expo:.2f} / ${agg_bankroll:.2f} bankroll = {agg_pct:.1%} (cap {LOTTERY_DAY_CAP_PCT:.0%})")
            if agg_breach:
                flags.append(f"AGGREGATE LOTTERY CAP BREACH: same-day YES-lottery exposure ${agg_expo:.2f} = {agg_pct:.1%} of bankroll (cap {LOTTERY_DAY_CAP_PCT:.0%})")
        except Exception as _e:
            print(f"(aggregate lottery cap check skipped: {_e})")
    if pct > GENERAL_CAP_PCT * 1.05:
        flags.append(f"GENERAL OVERSIZE: {pct:.0%} of cash (cap 8%)")
    try:
        ev = ticker.rsplit("-", 1)[0]
        pos = k.get_positions(event_ticker=ev) or []
        rows = pos.get("market_positions", pos) if isinstance(pos, dict) else pos
        expo, n_open = 0.0, 0
        for rp in rows:
            if abs(float(rp.get("position_fp") or 0)) == 0:
                continue
            mp = rp.get("market_exposure_dollars")
            if mp is not None:
                expo += abs(float(mp))
                n_open += 1
        if expo > 0:
            print(f"Open exposure in {ev}: ${expo:.2f} across {n_open} position(s); with this order: ${expo + cost:.2f}")
            if expo + cost > EVENT_CAP:
                flags.append(f"EVENT CAP BREACH: ${expo + cost:.2f} > ${EVENT_CAP:.0f}/city-day")
    except Exception as _e:
        print(f"(event exposure check skipped: {_e})")
    # CITY REALITY CHECK (Aug 30 night): lifetime realized P&L printed every gate run.
    # Miami alone bled -$60.95 on these exact shapes; enforce a hard blacklist.
    CITY_LOSS_CAP = -20.00
    city = ticker.split("-")[0].replace("KXHIGH", "") if ticker.startswith("KXHIGH") else None
    if city:
        try:
            gpnl = city_realized_pnl(k)
            if gpnl:
                srt = sorted(gpnl.items(), key=lambda kv: kv[1])
                print("City net P&L (realized + open cost, lifetime): " + ", ".join(f"{c} {v:+.2f}" for c, v in srt))
                c_pnl = gpnl.get(city)
                if c_pnl is not None and c_pnl < CITY_LOSS_CAP:
                    if override == f"OK-{city}":
                        print(f"!! OVERRIDE ACCEPTED: proceeding on {city} ({c_pnl:+.2f} lifetime) per explicit token")
                    else:
                        flags.append(
                            f"CITY BLACKLIST: {city} realized {c_pnl:+.2f} lifetime (cap {CITY_LOSS_CAP:+.2f})"
                            f" - requires explicit Thad override: run again with 5th arg OK-{city}"
                        )
        except Exception as _e:
            print(f"(city P&L check skipped: {_e})")

    for fl in flags:
        print(f"!! RED FLAG: {fl}")
    print()
    # STANDING RULE Sep 3 (Thad): no exit plan, no order
    print("EXIT-PLAN RULE: every pick MUST have a recorded exit strategy (dead condition, salvage trigger, decision windows, profit-lock) - record it in the DB with the fill (predictions.exit_plan). No plan = no order.")
    print()
    # Reminder of the V2 order semantics bug this tool guards against
    if side == "NO":
        print(f"V2 NOTE: this NO buy will be sent as sell-YES @ {(1-price):.2f} - the client handles conversion.")
    print("=" * 78)
    print("If any line above looks wrong, STOP. Re-read rules_primary before ordering.")


if __name__ == "__main__":
    main()