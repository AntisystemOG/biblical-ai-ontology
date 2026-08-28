#!/usr/bin/env python3
"""
kalshi_longshot_tracker.py - Long-shot scanner + paper tracker for Kalshi weather bands.

Purpose (Thad, Aug 28 2026): track cheap long shots (priced <= $0.30) where OUR data
says the true probability is meaningfully higher than the market price, paper-stake
them at $1, grade at settlement, and build a stats base so we learn whether long
shots actually pay before risking real money.

HARD RULES (from live losses, do not remove):
  - YES SEMANTICS COME FROM rules_primary, NEVER FROM THE TICKER. T-tickers can be
    either side: KXHIGHCHI-26AUG28-T80 resolves YES on "high < 80" while
    KXHIGHDEN-26AUG28-T97 resolves YES on "high > 97". The Aug 26 Denver loss was a
    wrong-side read; this scanner parses the rules text or skips the market.
  - Real prices only (AGENTS.md universal rule). If the API fails: report and exit 1.

Model edges (coded rules):
  - Kalshi weather resolves on The Weather Company (TWC), which runs ~+1.5F hotter
    than NWS airport obs (Aug 26 rule). Long-shot center = adjusted NWS high + 1.5F.
  - sigma = 1.7F (empirical NWS-error sigma; MAE 1.62F over 8 samples).

Commands:
  python kalshi_longshot_tracker.py scan    # fetch markets, score, log, open paper bets
  python kalshi_longshot_tracker.py grade   # settle finished bets, update stats
  python kalshi_longshot_tracker.py report  # Thad-friendly summary of open bets + stats
  python kalshi_longshot_tracker.py run     # scan + grade + report (cron entrypoint)

Data: ~\\.openclaw\\workspace\\data\\longshots\\
  candidates.jsonl - every scored long-shot candidate (append-only)
  bets.json        - open paper bets awaiting settlement
  settled.jsonl    - graded bet results
  stats.json       - running hit rate / ROI by edge bucket
"""

import json
import math
import os
import re
import sys
from datetime import datetime, timedelta, timezone

KALSHI_DIR = r"C:\AI Projects\Prediction Market\Kalshi"
EDGE_DIR = os.path.join(KALSHI_DIR, "Kalshi Edge Scanner")
sys.path.insert(0, KALSHI_DIR)
sys.path.insert(0, EDGE_DIR)

DATA_DIR = os.path.expanduser(r"~\.openclaw\workspace\data\longshots")
os.makedirs(DATA_DIR, exist_ok=True)
CAND_FILE = os.path.join(DATA_DIR, "candidates.jsonl")
BETS_FILE = os.path.join(DATA_DIR, "bets.json")
SETTLED_FILE = os.path.join(DATA_DIR, "settled.jsonl")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")

# --- Model constants (from coded rules / empirical results) ---
TWC_BIAS_F = 1.5        # TWC prints ~1.5F hotter than NWS obs (Aug 26 rule)
SIGMA_F = 1.7           # empirical NWS-error sigma (MAE 1.62F over 8 samples)
MAX_PRICE = 0.30        # long shot = priced at or below 30c
MIN_EDGE = 0.08         # our prob must beat the ask by >= 8 pts
DAILY_BET_COUNT = 5     # max new paper bets per scan day
STAKE = 1.00            # per paper bet
MAX_PER_CITY = 1        # diversify across cities
MAX_OPEN_BETS = 40      # portfolio cap

MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
          "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def parse_ticker_date(ticker):
    """KXHIGHDEN-26AUG28-B90 -> '2026-08-28'.

    Kalshi weather tickers are {YY}{MMM}{DD}: 26AUG28 = Aug 28, 2026.
    (Verified against known events: kxhighden-26aug17 = Aug 17, 2026.)
    """
    try:
        parts = ticker.split("-")
        ds = parts[1]  # 26AUG28 -> yy=26, month=AUG, day=28
        year = 2000 + int(ds[:2])
        mon = MONTHS.get(ds[2:5], 0)
        day = int(ds[5:7])
        if not mon or not (1 <= day <= 31):
            return None
        return f"{year}-{mon:02d}-{day:02d}"
    except Exception:
        return None


def parse_rules(market):
    """Derive YES win condition from rules_primary (fallback: title).

    Returns (kind, a, b):
      ("below", T, None)  YES iff high <= T-1   e.g. "less than 80"  -> high < 80
      ("above", T, None)  YES iff high >= T+1   e.g. "greater than 97" -> high > 97
      ("band", lo, hi)    YES iff lo <= high <= hi  e.g. "between 88-89"
      (None, None, None)  unrecognized - SKIP the market (never guess a side).
    """
    text = (market.get("rules_primary") or market.get("title") or "")
    tl = text.lower()
    m = re.search(r"less than (\d+)", tl)
    if m:
        return "below", float(m.group(1)), None
    m = re.search(r"greater than (\d+)", tl)
    if m:
        return "above", float(m.group(1)), None
    m = re.search(r"between (\d+)-(\d+)", tl)
    if m:
        return "band", float(m.group(1)), float(m.group(2))
    return None, None, None


def win_prob(kind, a, b, center):
    """P(integer TWC high satisfies the YES condition), normal model around center."""
    if kind == "below":     # high < a  -> integers <= a-1
        return norm_cdf((a - 0.5 - center) / SIGMA_F)
    if kind == "above":     # high > a  -> integers >= a+1
        return 1.0 - norm_cdf((a + 0.5 - center) / SIGMA_F)
    if kind == "band":      # a <= high <= b
        return norm_cdf((b + 0.5 - center) / SIGMA_F) - norm_cdf((a - 0.5 - center) / SIGMA_F)
    return 0.0


def plain_english(kind, a, b, city):
    if kind == "below":
        return f"{city} high under {a:.0f}F"
    if kind == "above":
        return f"{city} high over {a:.0f}F"
    return f"{city} high {a:.0f}-{b:.0f}F"


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=True) + "\n")


def fetch_nws_map():
    """{date: {city_code: nws period}} for today + tomorrow."""
    from weather_predictor import CITIES, fetch_nws_forecast
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    out = {}
    for target in (today, tomorrow):
        out[target] = {}
        for city_name, (lat, lon, city_code) in CITIES.items():
            try:
                period = fetch_nws_forecast(lat, lon, target)
                if period:
                    out[target][city_code] = period
            except Exception as e:
                print(f"  NWS fetch failed {city_code} {target}: {e}")
    return out


def adjusted_centers(nws_map):
    """{date: {city_code: {nws_high, adjusted_high, longshot_center, ...}}}."""
    import weather_daily as wd
    centers = {}
    for date, cities in nws_map.items():
        centers[date] = {}
        for city_code, period in cities.items():
            try:
                base_high = period.get("temperature", 0) or 0
                if not base_high:
                    continue
                wind_dir = period.get("windDirection", "W")
                short = (period.get("shortForecast") or "").upper()
                precip = (period.get("probabilityOfPrecipitation") or {}).get("value") or 0
                has_tstm = "THUNDER" in short or "TSTRM" in short
                storm_prob = (precip / 100.0) if has_tstm else 0.0
                if "OVERCAST" in short:
                    cloud = 85
                elif "CLOUDY" in short:
                    cloud = 70
                elif "PARTLY" in short:
                    cloud = 50
                else:
                    cloud = 15
                condition = "STORM" if has_tstm else ("CLOUDY" if cloud >= 70 else ("PARTLY" if cloud >= 40 else "SUNNY"))
                adjusted, _details = wd.adjust_forecast(base_high, city_code, storm_prob, wind_dir, cloud, condition)
                # Cap downward adjustment at -2F (coded Aug 25 rule), then TWC bias.
                if adjusted < base_high - 2.0:
                    adjusted = base_high - 2.0
                centers[date][city_code] = {
                    "nws_high": base_high,
                    "adjusted_high": adjusted,
                    "longshot_center": adjusted + TWC_BIAS_F,  # TWC runs hot
                    "condition": condition,
                }
            except Exception as e:
                print(f"  adjust failed {city_code} {date}: {e}")
    return centers


def cmd_scan():
    from kalshi_client import Kalshi
    k = Kalshi()
    markets = k.get_weather_markets()
    if not markets:
        print("ERROR: no weather markets returned - holding cash.")
        return 1

    centers_by_date = adjusted_centers(fetch_nws_map())
    if not any(centers_by_date.values()):
        print("ERROR: no NWS data - cannot score. Holding cash.")
        return 1

    today = datetime.now().strftime("%Y-%m-%d")
    bets = load_json(BETS_FILE, {})

    # Dedup: tickers already logged today
    seen_today = set()
    if os.path.exists(CAND_FILE):
        with open(CAND_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("scan_date") == today:
                        seen_today.add(r.get("ticker"))
                except Exception:
                    continue

    candidates = []
    skipped_no_rules = 0
    for ticker, m in markets.items():
        try:
            yes_ask = float(m.get("yes_ask") or 0)
            no_ask = float(m.get("no_ask") or 0)
        except Exception:
            continue
        if not (0.01 < yes_ask <= MAX_PRICE) and not (0.01 < no_ask <= MAX_PRICE):
            continue
        settle_date = parse_ticker_date(ticker) or ""
        # Only score markets for dates we have NWS forecasts for (today/tomorrow).
        if settle_date not in centers_by_date:
            continue
        centers = centers_by_date[settle_date]
        city_code = next((cc for cc in centers if f"KXHIGH{cc}" in ticker), None)
        if not city_code or city_code not in centers:
            continue
        c = centers[city_code]
        kind, a, b = parse_rules(m)
        if not kind:
            skipped_no_rules += 1
            continue
        p_yes = win_prob(kind, a, b, c["longshot_center"])
        base = {
            "scan_date": today,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "ticker": ticker,
            "city": city_code,
            "kind": kind,
            "strike_low": a,
            "strike_high": b,
            "settle_date": settle_date,
            "title": m.get("title"),
            "rules": (m.get("rules_primary") or "")[:160],
            "close_time": m.get("close_time"),
            "volume": m.get("volume"),
            "nws_high": c["nws_high"],
            "adjusted_high": c["adjusted_high"],
            "longshot_center": round(c["longshot_center"], 1),
            "condition": c["condition"],
        }
        # YES-side long shot
        if 0.01 < yes_ask <= MAX_PRICE:
            edge = round(p_yes - yes_ask, 3)
            if edge >= MIN_EDGE:
                candidates.append({**base, "side": "YES", "yes_ask": yes_ask,
                                   "model_prob": round(p_yes, 3), "edge": edge, "paper_bet": False})
        # NO-side long shot (market overconfident in the YES outcome)
        p_no = 1.0 - p_yes
        if 0.01 < no_ask <= MAX_PRICE:
            edge = round(p_no - no_ask, 3)
            if edge >= MIN_EDGE:
                candidates.append({**base, "side": "NO", "yes_ask": no_ask,
                                   "model_prob": round(p_no, 3), "edge": edge, "paper_bet": False})

    # Rank by edge; open paper bets (max/day, max/city)
    ranked = sorted(candidates, key=lambda x: -x["edge"])
    per_city = {}
    open_count = sum(1 for x in bets.values() if x.get("status") == "open")
    opened = 0
    for cand in ranked:
        if cand["ticker"] in seen_today:
            continue
        if open_count >= MAX_OPEN_BETS:
            break
        if per_city.get(cand["city"], 0) >= MAX_PER_CITY:
            continue
        if opened >= DAILY_BET_COUNT:
            break
        cand["paper_bet"] = True
        bets[cand["ticker"] + ":" + cand["side"]] = {
            "key": cand["ticker"] + ":" + cand["side"],
            "ticker": cand["ticker"], "city": cand["city"], "side": cand["side"],
            "kind": cand["kind"], "strike_low": cand["strike_low"], "strike_high": cand["strike_high"],
            "settle_date": cand["settle_date"], "scan_date": today,
            "entry_ask": cand["yes_ask"], "model_prob": cand["model_prob"], "edge": cand["edge"],
            "stake": STAKE, "shares": round(STAKE / cand["yes_ask"], 2),
            "plain": plain_english(cand["kind"], cand["strike_low"], cand["strike_high"], cand["city"])
                     + (" (YES side)" if cand["side"] == "YES" else " (NO side)"),
            "title": cand.get("title"),
            "rules": cand.get("rules"),
            "status": "open",
        }
        per_city[cand["city"]] = per_city.get(cand["city"], 0) + 1
        open_count += 1
        opened += 1

    # Log all candidates (append-only, dedup by ticker+side within the day)
    new_rows = [c for c in candidates
                if (c["ticker"] + ":" + c["side"]) not in seen_today]
    with open(CAND_FILE, "a", encoding="utf-8") as f:
        for c in new_rows:
            f.write(json.dumps(c, ensure_ascii=True) + "\n")

    save_json(BETS_FILE, bets)

    print(f"SCAN {today}: {len(candidates)} candidates (edge >= {MIN_EDGE:.2f}), "
          f"{skipped_no_rules} skipped (unrecognized rules), {opened} new paper bets.")
    for c in ranked[:10]:
        tag = " [BET]" if c["paper_bet"] else ""
        print(f"  {plain_english(c['kind'], c['strike_low'], c['strike_high'], c['city'])} "
              f"({c['side']}){tag}: ask {c['yes_ask']:.2f}, model {c['model_prob']:.2f}, "
              f"edge {c['edge']:+.2f} (NWS {c['nws_high']:.0f}F -> center {c['longshot_center']:.1f}F)")
    return 0


def cmd_grade():
    from kalshi_client import Kalshi
    k = Kalshi()
    bets = load_json(BETS_FILE, {})
    stats = load_json(STATS_FILE, {"graded": 0, "wins": 0, "staked": 0.0, "returned": 0.0,
                                   "by_edge": {"0.08-0.15": [0, 0], "0.15-0.25": [0, 0], "0.25+": [0, 0]}})
    changed = False
    for key, b in list(bets.items()):
        if b.get("status") != "open":
            continue
        try:
            m = k.get_market(b["ticker"]).get("market", {})
        except Exception as e:
            print(f"  fetch failed {b['ticker']}: {e}")
            continue
        status = (m.get("status") or "").lower()
        result = (m.get("result") or "").lower()
        if status not in ("closed", "finalized") or not result:
            continue  # still live or awaiting settlement
        we_held_yes = (b["side"] == "YES")
        won = (result == "yes") == we_held_yes
        payout = b["shares"] * 1.0 if won else 0.0
        pnl = round(payout - b["stake"], 2)
        rec = dict(b)
        rec.update({"status": "settled", "won": won, "payout": round(payout, 2),
                    "pnl": pnl, "settled_at": datetime.now(timezone.utc).isoformat(),
                    "official_result": result})
        append_jsonl(SETTLED_FILE, rec)
        del bets[key]
        stats["graded"] += 1
        stats["wins"] += 1 if won else 0
        stats["staked"] += b["stake"]
        stats["returned"] += payout
        e = b["edge"]
        bucket = "0.08-0.15" if e < 0.15 else ("0.15-0.25" if e < 0.25 else "0.25+")
        bb = stats["by_edge"].setdefault(bucket, [0, 0])
        bb[0] += 1
        bb[1] += 1 if won else 0
        changed = True
        print(f"  SETTLED {'WIN ' if won else 'LOSS'} {b['plain']}: "
              f"{'+$' + format(pnl, '.2f') if pnl >= 0 else '-$' + format(-pnl, '.2f')} "
              f"(entry {b['entry_ask']:.2f}, edge {b['edge']:+.2f})")
    if changed:
        save_json(BETS_FILE, bets)
        save_json(STATS_FILE, stats)
    else:
        print("  No new settlements.")
    return 0


def cmd_report():
    bets = load_json(BETS_FILE, {})
    stats = load_json(STATS_FILE, {"graded": 0, "wins": 0, "staked": 0.0, "returned": 0.0})
    open_bets = [b for b in bets.values() if b.get("status") == "open"]
    print("=== LONG-SHOT TRACKER ===")
    print(f"Open paper bets: {len(open_bets)}")
    for b in open_bets:
        print(f"  {b['plain']} | ${b['stake']:.2f} @ {b['entry_ask']:.2f} "
              f"(model {b['model_prob']:.2f}, edge {b['edge']:+.2f})")
    g, w = stats.get("graded", 0), stats.get("wins", 0)
    st, ret = stats.get("staked", 0.0), stats.get("returned", 0.0)
    pnl = ret - st
    if g:
        print(f"Settled: {g} bets, {w} wins ({w / g:.0%}) | staked ${st:.2f}, "
              f"returned ${ret:.2f}, P&L {pnl:+.2f} ({pnl / st * 100 if st else 0:+.0f}%)")
        for bucket, (n, wins) in stats.get("by_edge", {}).items():
            if n:
                print(f"  edge {bucket}: {wins}/{n} wins")
    else:
        print("Settled: none yet - building the sample.")
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    rc = 0
    if cmd in ("scan", "run"):
        rc = cmd_scan()
    if cmd in ("grade", "run"):
        rc = cmd_grade() or rc
    if cmd in ("report", "run"):
        rc = cmd_report() or rc
    if cmd not in ("scan", "grade", "report", "run"):
        print("Usage: kalshi_longshot_tracker.py [scan|grade|report|run]")
        rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main())