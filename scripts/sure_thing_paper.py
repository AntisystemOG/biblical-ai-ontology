# sure_thing_paper.py - nightly paper-bets for the SURE-THING ladder (95%+ model odds, low yield).
# Feeds history.json in the paper trader's own format so the 8 PM run grades them automatically.
# Criteria (Thad standing orders Sep 3): model odds >=95pct, NO price <=96c, cushion >=5F,
#   not blacklisted-city-for-LIVE (paper ignores blacklist - that's the point of paper), gate = cushion math.
import sys, json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")
from kalshi_client import Kalshi
from weather_predictor import fetch_nws_forecast, CITIES
import kalshi_db as db

HIST = Path(r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner\data\weather\paper_trader\history.json")
SERIES_TO_CITY = {
    "KXHIGHDEN": ("Denver", "DEN", 2.0), "KXHIGHMIA": ("Miami", "MIA", 2.0),
    "KXHIGHCHI": ("Chicago", "CHI", 2.0), "KXHIGHNY": ("New York", "NY", 2.0),
    "KXHIGHLA": ("LA", "LA", 2.0), "KXHIGHHOU": ("Houston", "HOU", 2.0),
    "KXHIGHDAL": ("Dallas", "DAL", 2.0), "KXHIGHPHX": ("Phoenix", "PHX", 2.0),
}
MON = {"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06",
       "JUL":"07","AUG":"08","SEP":"09","OCT":"10","NOV":"11","DEC":"12"}
SIGMA_F = 2.0          # our weather sigma (documented)
MIN_ODDS = 0.95        # sure-thing: >=95 pct model odds
MAX_PRICE = 0.96       # never pay above 96c (spread/fee guard)
MIN_CUSHION = 5.0      # 5F+ from adjusted forecast to band edge
STAKE_PCT = 0.05       # 5 pct of paper bankroll per position
MAX_BETS = 5
DAILY_TARGET = 0.05    # SAME GOAL AS THE MAIN MODEL: 5 pct daily return (Thad Sep 3)
LOTTO_STAKE_PCT = 0.02 # lotto class 2 pct (mirrors live ladder)
LOTTO_MAX = 2          # max lotto paper bets/day
LOTTO_ODDS = (0.15, 0.45)  # model odds window for lotto class
LOTTO_MAX_PRICE = 0.25

def norm_cdf(z):
    return 0.5 * (1.0 + __import__("math").erf(z / __import__("math").sqrt(2.0)))

def main():
    c = Kalshi()
    hist = json.loads(HIST.read_text(encoding="utf-8"))
    ppath = HIST.parent / "portfolio.json"
    port = json.loads(ppath.read_text(encoding="utf-8"))
    open_tickers = ({h.get("ticker") for h in hist if h.get("status") == "open"}
                    | {p.get("ticker") for p in port.get("open_positions", []) if p.get("status") == "open"})
    cash = float(port.get("cash", 0.0))  # paper bankroll, live from portfolio.json
    budget = cash   # running spend guard so nightly stakes can't overcommit the bankroll
    pending = []    # entries to be written into portfolio.open_positions
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    want = (datetime.now() + timedelta(days=1)).strftime("%y%b%d").upper()  # 26SEP04

    mk = c.get_weather_markets()
    # group city-day books
    books = {}
    for ticker, m in mk.items():
        t = ticker.upper()
        if want in t:
            books.setdefault(t.split("-")[0], {})[ticker] = m

    bets = []
    dbg = []
    for series, book in sorted(books.items()):
        city, code, _ = SERIES_TO_CITY.get(series, (series, "?", 2.0))
        if city not in CITIES:
            continue
        lat, lon, _ = CITIES[city]
        # forecast for the SETTLE date (tomorrow)
        p = fetch_nws_forecast(lat, lon, tomorrow)
        if not p:
            import time as _t
            _t.sleep(3)
            p = fetch_nws_forecast(lat, lon, tomorrow)  # one retry (NWS rate-limits)
        if not p:
            print(f"  NWS-FETCH-FAILED {city} - no sure-thing eval possible tonight")
            continue
        nws_high = p.get("temperature")
        if nws_high is None:
            print(f"  NWS-FETCH-FAILED {city} - no temp in period")
            continue
        adjusted = nws_high + 1.5  # TWC premium
        # Improvements 1+2: apply learned city bias + per-city sigma
        bias = db.city_bias(code)
        sigma = db.city_sigma(code)
        adjusted = adjusted + bias
        SIGMA_F = sigma
        best = None
        seen = 0
        rej = {"no_ask": 0, "price": 0, "odds": 0, "cushion": 0}
        for ticker, m in book.items():
            if ticker in open_tickers or ticker.upper() in {t.upper() for t in open_tickers}:
                continue
            tail = ticker.rsplit("-", 1)[-1]
            yes_ask = float(m.get("yes_ask") or 0)
            no_ask = float(m.get("no_ask") or 0)
            if tail.startswith("B"):
                try:
                    mid = float(tail[1:])
                except Exception:
                    continue
                # B{X.5} = the X..X+1 band (Edge rule Sep 3: 'B92.5 = 92 or 93')
                lo, hi = mid - 0.5, mid + 0.5
                dist_below = lo - adjusted
                dist_above = adjusted - hi
                seen += 1
                if dist_below >= MIN_CUSHION:
                    direction, price = "NO", no_ask
                    cushion = dist_below
                elif dist_above >= MIN_CUSHION:
                    direction, price = "NO", no_ask
                    cushion = dist_above
                else:
                    rej["cushion"] += 1
                    continue
                z = cushion / SIGMA_F
                win_prob = norm_cdf(z)
            elif tail.startswith("T"):
                # Improvement 4: T-markets via semantics cache (rules_primary resolved once, stored in DB)
                sem = db.market_semantics(ticker)
                if sem is None:
                    try:
                        mm = c.get_market(ticker)
                        mm = mm.get("market", mm) if isinstance(mm, dict) else {}
                        stype = mm.get("strike_type")
                        thr = mm.get("floor_strike") or mm.get("cap_strike")
                        if stype == "greater" and thr is not None:
                            sem = ("greater", float(thr), None)
                            db.save_market_semantics(ticker, "greater", float(thr), None)
                        elif stype == "less" and thr is not None:
                            sem = ("less", None, float(thr))
                            db.save_market_semantics(ticker, "less", None, float(thr))
                    except Exception:
                        sem = None
                if sem is None:
                    rej["cushion"] += 1
                    continue
                stype, s_lo, s_hi = sem
                seen += 1
                if stype == "greater":
                    dist = adjusted - s_lo
                    if dist >= MIN_CUSHION:
                        direction, price, cushion = "YES", yes_ask, dist
                    elif -dist >= MIN_CUSHION:
                        direction, price, cushion = "NO", no_ask, -dist
                    else:
                        rej["cushion"] += 1
                        continue
                else:
                    dist = s_hi - adjusted
                    if dist >= MIN_CUSHION:
                        direction, price, cushion = "YES", yes_ask, dist
                    elif -dist >= MIN_CUSHION:
                        direction, price, cushion = "NO", no_ask, -dist
                    else:
                        rej["cushion"] += 1
                        continue
                z = cushion / SIGMA_F
                win_prob = norm_cdf(z)
            else:
                rej["cushion"] += 1
                continue
            if win_prob < MIN_ODDS:
                rej["odds"] += 1
                continue
            if price <= 0 or price > MAX_PRICE:
                rej["price"] += 1
                continue
            if direction == "NO" and price > MAX_PRICE:
                continue
            ev = win_prob / price if price else 0
            score = ev * win_prob
            if best is None or score > best["score"]:
                best = {"ticker": ticker, "tail": tail, "direction": direction, "price": price,
                        "win_prob": win_prob, "cushion": cushion, "score": score}
        dbg.append(f"{city}: bands_seen={seen} rejected={rej} best={'none' if best is None else best['tail']}")
        if best:
            bets.append((city, best))

    # stake 5 pct of paper bankroll per city (Thad Sep 3: ALL cities get paper picks
    # so we learn which cities are sure-things vs coin-flips - per-city track record)
    out = []
    for city, b in bets:
        stake = round(cash * STAKE_PCT, 2)
        if stake < 1.0 or budget - stake < 0:
            continue
        budget = round(budget - stake, 2)
        shares = round(stake / b["price"], 2) if b["price"] else 0
        entry = {
            "date": tomorrow, "prediction_date": datetime.now().strftime("%Y-%m-%d"),
            "city": city, "bet_type": "band",
            "direction": b["direction"], "ticker": b["ticker"],
            "band_low": float(b["tail"][1:]) - 0.5 if b["tail"].startswith("B") else None,
            "band_high": float(b["tail"][1:]) + 0.5 if b["tail"].startswith("B") else None,
            "threshold": None,
            "purchase_price": b["price"], "bet_amount": stake, "shares": shares,
            "status": "open", "placed_at": datetime.now().isoformat(),
            "rationale": f"sure-thing ladder: {b['cushion']:.1f}F cushion, model odds {b['win_prob']:.0%}, paper test of 95pct class",
            "exit_plan": "peak-window watcher: dead after peak outside range = salvage; winning >=90c = hold; 30 pct giveback = lock",
        }
        pending.append(entry)
        out.append(f"{city} {b['tail']} {b['direction']} {shares:.0f}sh @ {b['price']:.2f} (model {b['win_prob']:.0%}, cushion {b['cushion']:.1f}F)")

    # LOTTO section: mirror the live strategy mix so the paper book can reach the 5 pct/day goal.
    # In paper, lotto risk is FREE - testing the long-shot class is how we learn its true hit rate.
    lottos = []
    for series, book in sorted(books.items()):
        city, code, _ = SERIES_TO_CITY.get(series, (series, "?", 2.0))
        if city not in CITIES:
            continue
        lat, lon, _ = CITIES[city]
        p = fetch_nws_forecast(lat, lon, tomorrow)
        if not p:
            continue
        nws_high = p.get("temperature")
        if nws_high is None:
            continue
        adjusted = nws_high + 1.5
        for ticker, m in book.items():
            if ticker in open_tickers or ticker.upper() in {t.upper() for t in open_tickers}:
                continue
            tail = ticker.rsplit("-", 1)[-1]
            if not tail.startswith("B"):
                continue
            try:
                mid = float(tail[1:])
            except Exception:
                continue
            lo, hi = mid - 0.5, mid + 0.5
            yes_ask = float(m.get("yes_ask") or 0)
            if not (LOTTO_MAX_PRICE >= yes_ask > 0):
                continue
            z_lo = (lo - adjusted) / SIGMA_F
            z_hi = (hi - adjusted) / SIGMA_F
            prob = norm_cdf(z_hi) - norm_cdf(z_lo)
            if not (LOTTO_ODDS[0] <= prob <= LOTTO_ODDS[1]):
                continue
            ev = prob / yes_ask
            if ev < 1.3:
                continue
            lottos.append((city, ticker, tail, yes_ask, prob, ev))
    lottos.sort(key=lambda x: -x[5])
    seen_cities = set()
    for city, ticker, tail, price, prob, ev in lottos:
        if city in seen_cities:
            continue  # one lotto per city for coverage
        seen_cities.add(city)
        stake = round(cash * LOTTO_STAKE_PCT, 2)
        if stake < 1.0 or budget - stake < 0:
            continue
        budget = round(budget - stake, 2)
        shares = round(stake / price, 2) if price else 0
        entry = {
            "date": tomorrow, "prediction_date": datetime.now().strftime("%Y-%m-%d"),
            "city": city, "bet_type": "band",
            "direction": "YES", "ticker": ticker,
            "band_low": float(tail[1:]) - 0.5, "band_high": float(tail[1:]) + 0.5,
            "threshold": None,
            "purchase_price": price, "bet_amount": stake, "shares": shares,
            "status": "open", "placed_at": datetime.now().isoformat(),
            "rationale": f"paper lotto (mirrors live 2 pct class): model {prob:.0%} vs market {price:.0%}, EV {ev:.2f}x",
            "exit_plan": "peak-window watcher: dead after peak outside range = salvage; winning >=90c = hold; 30 pct giveback = lock",
        }
        pending.append(entry)
        out.append(f"LOTTO {city} {tail} YES {shares:.0f}sh @ {price:.2f} (model {prob:.0%}, EV {ev:.2f}x)")

    # daily target bookkeeping + portfolio integration: open bets live in
    # portfolio.open_positions (cash debited) so the 8 PM run's grade_settled
    # grades them automatically. history.json keeps graded entries only.
    port["daily_target_pct"] = DAILY_TARGET
    port["goal_note"] = "same goal as main model: 5 pct daily return (Thad Sep 3)"
    for entry in pending:
        port.setdefault("open_positions", []).append(entry)
        port["cash"] = round(float(port.get("cash", 0)) - entry["bet_amount"], 2)
        port["total_wagered"] = round(float(port.get("total_wagered", 0)) + entry["bet_amount"], 2)
    ppath.write_text(json.dumps(port, indent=1), encoding="utf-8")

    print(f"sure-thing paper bets placed: {len(pending)} | paper daily target: {DAILY_TARGET:.0%} (goal = main model)")
    for d in dbg:
        print("  diag:", d)
    for o in out:
        print(" ", o)

if __name__ == "__main__":
    main()