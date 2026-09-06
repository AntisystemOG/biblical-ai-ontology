# kalshi_peak_exit.py - v2 peak-window exit watcher (improvements 3+4, Sep 5).
# Trajectory-based salvage: acts on physics (obs_max + remaining_possible_climb), not the clock.
# Confidence-priced exits: TWC rounding risk near band edges -> sell when confidence low + bid >= 65c.
# Handles YES and NO positions on TODAY's KXHIGH markets. Read-only; cron agent executes.
import sys, json, urllib.request
from datetime import datetime

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")
sys.path.insert(0, r"C:\Users\thadd\.openclaw\workspace\scripts")
from kalshi_client import Kalshi
import kalshi_db as db

CITY = {
    "KXHIGHDEN": {"name": "Denver", "station": "KDEN", "peak_end": 15},
    "KXHIGHCHI": {"name": "Chicago", "station": "KMDW", "peak_end": 16},
    "KXHIGHMIA": {"name": "Miami", "station": "KMIA", "peak_end": 15},
    "KXHIGHNY":  {"name": "NYC", "station": "KNYC", "peak_end": 16},
}

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0 if c is not None else None

def obs_max(station):
    try:
        d0 = datetime.now().strftime("%Y-%m-%dT05:00:00-05:00")
        u = f"https://api.weather.gov/stations/{station}/observations?start={d0}"
        req = urllib.request.Request(u, headers={"User-Agent": "spock-peak-exit local"})
        d = json.load(urllib.request.urlopen(req, timeout=15))
        temps = [f["properties"]["temperature"]["value"] for f in d.get("features", [])
                 if f.get("properties", {}).get("temperature", {}).get("value") is not None]
        temps = [t * 9 / 5 + 32 for t in temps]
        if temps:
            return round(temps[-1], 1), round(max(temps), 1)
    except Exception:
        pass
    return None, None

def remaining_climb(now_hour):
    """Physics cap on additional heating after this hour (F). Conservative."""
    table = {13: 4.0, 14: 2.5, 15: 1.5, 16: 0.5}
    return table.get(now_hour, 0.5 if now_hour < 17 else 0.0)

def band_range(tail):
    """B{X.5} = band X..X+1. Returns (lo, hi) or None."""
    if not tail.startswith("B"):
        return None
    try:
        mid = float(tail[1:])
    except Exception:
        return None
    return mid - 0.5, mid + 0.5

def thr_range(tail):
    """T{X}: resolve via semantics cache. Returns ('greater'|'less', thr) or None."""
    if not tail.startswith("T"):
        return None
    try:
        thr = float(tail[1:])
    except Exception:
        return None
    sem = db.market_semantics(ticker_key(tail))
    return (sem[0], thr) if sem else None

def ticker_key(tail):
    return f"KXHIGH-{tail}"  # semantics cache is per-ticker; series-specific cache preferred

c = Kalshi()
now = datetime.now()
datecode = now.strftime("%y%b%d").upper()
print(f"PEAK-EXIT V2 {now:%H:%M} CT | watching {datecode} positions")

pos = c.get_positions()
have = {}
for p in pos.get("market_positions", []):
    t = p.get("ticker", "")
    if datecode in t and "KXHIGH" in t:
        fp = float(p.get("position_fp") or 0)
        if abs(fp) > 0:
            have[t] = {"side": "YES" if fp > 0 else "NO", "shares": abs(fp)}

mk = c.get_weather_markets()
for t, m in mk.items():
    if datecode in t and "KXHIGH" in t and t not in have:
        # resting/other exposure check not needed here - positions only
        pass

if not have:
    print("No open positions on today's markets - nothing to watch.")
    sys.exit(0)

series_of = {}
for t in have:
    series_of[t] = t.split("-")[0]

for t, info in sorted(have.items()):
    series = t.split("-")[0]
    city_cfg = CITY.get(series)
    tail = t.rsplit("-", 1)[-1]
    bid, ask = float(m.get(t, {}).get("yes_bid") or 0), 0.0
    # live book for this market
    book = mk.get(t, {})
    bid = float(book.get("yes_bid") or 0)
    ask = float(book.get("yes_ask") or 0)
    city_cfg = CITY.get(series, {"name": series, "station": None, "peak_end": 16})
    latest, tmax = (None, None)
    if city_cfg.get("station"):
        latest, tmax = obs_max(city_cfg["station"])
    proxy = round(tmax + 1.5, 1) if tmax is not None else None
    peak_passed = now.hour >= city_cfg["peak_end"]
    rem = remaining_climb(now.hour)

    line = f"{city_cfg['name']} {tail} {info['side']} {info['shares']:.1f}sh bid={bid:.2f} ask={ask:.2f} obs_max={tmax}F proxy={proxy}F peak={'PASSED' if peak_passed else 'OPEN(+%sF max)' % rem}"

    # win range in proxy terms (TWC integer T -> proxy [T+1.0, T+1.9]; bands 1F wide)
    brange = band_range(tail)
    if brange:
        lo, hi = brange
        yes_win = (lo + 1.0, hi + 1.9)   # TWC 87-88 -> proxy 88.0-89.9
        if proxy is None:
            print(line + " | WATCH (no obs)")
            continue
        in_win = yes_win[0] <= proxy <= yes_win[1]
        if info["side"] == "YES":
            won = in_win
            dead = proxy > yes_win[1] + 0.0 or (proxy + rem < yes_win[0] - 0.5)
            near_edge = min(abs(proxy - yes_win[0]), abs(proxy - yes_win[1])) <= 0.4
        else:  # NO
            won = not in_win
            dead = in_win and (peak_passed or proxy >= yes_win[0] + 0.5)
            near_edge = min(abs(proxy - yes_win[0]), abs(proxy - yes_win[1])) <= 0.4
    else:
        sem = db.market_semantics(t)
        if sem is None:
            print(line + " | WATCH (no semantics - verify rules manually)")
            continue
        stype, s_lo, s_hi = sem
        if proxy is None:
            print(line + " | WATCH (no obs)")
            continue
        if stype == "greater":
            yes_win = (s_lo + 2.0, None)  # TWC > thr (thr+1) -> proxy >= thr+2.0
            won = proxy >= s_lo + 2.0
            dead = proxy + rem < s_lo + 2.0 - 0.5
        else:
            yes_win = (None, s_hi + 0.9)  # TWC < thr (thr-1) -> proxy <= thr+0.9
            won = proxy <= s_hi + 0.9
            dead = proxy - rem > s_hi + 0.9 + 0.5
        near_edge = False

    if won and bid >= 0.90:
        v = "WINNING - hold to settlement (no fee at 1.00)"
    elif won and near_edge and bid >= 0.65:
        v = "WINNING but rounding coin-flip (proxy near edge) - SELL at bid (improvement 4)"
    elif won:
        v = "WINNING - hold (peak math locked)"
    elif dead:
        v = "DEAD - trajectory math confirms: salvage sell at bid NOW"
    else:
        v = "WATCH - trajectory still can reach win range"
    print(line + " | " + v)