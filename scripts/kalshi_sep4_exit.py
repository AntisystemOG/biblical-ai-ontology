# kalshi_sep4_exit.py - Sep 4 ridge-bet exit watcher (read-only; cron agent executes).
# Cities: DEN (peak 13-15 CT), CHI (peak 14-16 CT), MIA (peak 13-15 CT), NY (peak 14-16 CT).
# Positions: DEN >95 YES 75sh (7.53 filled), DEN 94-95 YES 15sh, NY 86-87 YES 11sh, MIA 93-94 YES 22sh.
import sys, json, urllib.request
from datetime import datetime

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")
from kalshi_client import Kalshi

CITY = {
    "KXHIGHDEN": {"name": "Denver", "station": "KDEN", "peak_end": 15},
    "KXHIGHCHI": {"name": "Chicago", "station": "KMDW", "peak_end": 16},
    "KXHIGHMIA": {"name": "Miami", "station": "KMIA", "peak_end": 15},
    "KXHIGHNY":  {"name": "NYC", "station": "KNYC", "peak_end": 16},
}
POS = {  # ticker tail -> (shares target, buy price)
    "T95": 75, "B94.5": 15, "B86.5": 11, "B93.5": 22,
}

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0 if c is not None else None

def obs_max(station):
    """Latest obs + today's observed max so far (NWS station obs, since 5 AM CT today)."""
    try:
        d0 = datetime.now().strftime("%Y-%m-%dT05:00:00-05:00")
        u = f"https://api.weather.gov/stations/{station}/observations?start={d0}"
        req = urllib.request.Request(u, headers={"User-Agent": "spock-exit-watch local"})
        d = json.load(urllib.request.urlopen(req, timeout=15))
        temps = [f["properties"]["temperature"]["value"] for f in d.get("features", [])
                 if f.get("properties", {}).get("temperature", {}).get("value") is not None]
        temps = [t * 9 / 5 + 32 for t in temps]
        if temps:
            return round(temps[-1], 1), round(max(temps), 1)
    except Exception as e:
        pass
    return None, None

c = Kalshi()
now = datetime.now()
print(f"SEP4 EXIT WATCH {now:%H:%M} CT")

# live positions (filled shares) - keyed by FULL ticker (tails collide across cities)
pos = c.get_positions()
have = {}
for p in pos.get("market_positions", []):
    t = p.get("ticker", "")
    if "26SEP04" in t:
        sh = float(p.get("position_fp") or 0)
        if sh > 0:
            have[t] = sh

mk = c.get_weather_markets()
for series, info in CITY.items():
    latest, today_max = obs_max(info["station"])
    twc_proxy = round(today_max + 1.5, 1) if today_max is not None else None
    peak_passed = now.hour >= info["peak_end"]
    print(f"\n== {info['name']} ({series}) obs_latest={latest}F obs_max={today_max}F twc_proxy={twc_proxy}F peak_window={'PASSED' if peak_passed else 'OPEN'}")
    for ticker, m in mk.items():
        if series in ticker and "26SEP04" in ticker:
            tail = ticker.rsplit("-", 1)[-1]
            sh = have.get(ticker, 0)
            if sh <= 0 and tail not in POS:
                continue
            bid, ask = m.get("yes_bid"), m.get("yes_ask")
            line = f"  {tail:>6} bid={bid} ask={ask}"
            if sh > 0:
                line += f" HOLD {sh:.2f}sh"
            # win conditions in PROXY terms (proxy = obs_max + 1.5; TWC integer T => proxy [T+1.0, T+1.9])
            #   T95 (>95, i.e. 96+) => proxy >= 97.0 | B94.5 => 95.0-96.9 | B86.5 => 87.0-88.9 | B93.5 => 94.0-95.9
            LO, HI = {"T95": (97.0, None), "B94.5": (95.0, 96.9), "B86.5": (87.0, 88.9), "B93.5": (94.0, 95.9)}[tail]
            if twc_proxy is None:
                v = "WATCH (no obs data)"
            elif twc_proxy >= LO and (HI is None or twc_proxy <= HI):
                v = "WINNING - hold to settlement (no fee at 1.00)"
            elif HI is not None and twc_proxy > HI + 0.9:
                v = "DEAD-EARLY - max only rises: cancel resting order + salvage sell at bid"
            elif peak_passed:
                v = "DEAD - peak passed outside win range: salvage sell at bid (borderline = judge on TWC page)"
            elif twc_proxy >= LO - 1.0:
                v = "CLOSE - within 1F of win range, watch each hour"
            else:
                v = "WATCH - below range, window open"
            print(line, "|", v)