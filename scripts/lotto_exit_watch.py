"""lotto_exit_watch.py - intraday falsification watch for open lottery legs.
Pulls LIVE station observations (api.weather.gov) + live Kalshi bids, applies the
falsification matrix, SELLS falsified legs immediately (losing-position exit is
pre-authorized by Thad), alerts on big profitable bids. Silent otherwise.

Trigger rules (set Aug 31 for tomorrow's lotteries, station = TWC settlement source):
  CHI <89 (4sh):  DEAD if KMDW obs max >= 89 (1hr margin: >=90 earlier)
  NY 80-81 (14sh): DEAD if KNYC obs max >= 82; window-closed if <=78 at 3:30 PM CDT
  NY 82-83 (12sh): DEAD if KNYC obs max >= 84; or <=80 at 3:30 PM CDT
Stations: KMDW (Chicago CLIMDW), KNYC (Central Park CLINYC)."""
import sys, json, os, urllib.request
from datetime import datetime, timezone, timedelta

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
from kalshi_client import Kalshi

MIA = False  # Miami legs none open (banned)

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0 if c is not None else None

def today_max_obs(station):
    """Max observed temp (F) for today at station, from api.weather.gov."""
    try:
        midnight = datetime.now(timezone(timedelta(hours=-5))).replace(hour=0, minute=0, second=0, microsecond=0)
        start = midnight.strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.weather.gov/stations/{station}/observations?start={start}&limit=50"
        req = urllib.request.Request(url, headers={"User-Agent": "SpockLottoWatch/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        mx = None
        for ob in data.get("features", []):
            t = (ob.get("properties") or {}).get("temperature")
            if t and t.get("value") is not None:
                f = c_to_f(t["value"])
                if mx is None or f > mx:
                    mx = f
        return mx
    except Exception as e:
        print(f"WARN obs {station}: {e}")
        return None

def main():
    sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")
    from kalshi_client import Kalshi
    k = Kalshi()
    pos = k.get_positions()
    rows = pos.get("market_positions", pos) if isinstance(pos, dict) else pos
    book = {}
    for r in rows:
        t = r.get("ticker", "")
        if "26AUG31" in t and t.startswith("KXHIGH") and abs(float(r.get("position_fp") or 0)) > 0:
            side = "Y" if float(r["position_fp"]) > 0 else "N"
            book[t] = (side, abs(float(r["position_fp"])))
    if not book:
        print("NO_REPLY")  # nothing to watch
        return

    obs_max = {"CHI": today_max_obs("KMDW"), "NY": today_max_obs("KNYC")}
    quotes = k.get_weather_markets()
    actions = []

    for t, (side, sh) in sorted(book.items()):
        series = t.split("-")[0].replace("KXHIGH", "")
        omax = obs_max.get(series if series in obs_max else t[:14], None)
        city = series if series in ("CHI", "NY", "DEN", "MIA") else None
        om = obs_max.get(series, None)
        q = quotes.get(t, {})
        bid = q.get("yes_bid", 0) if side == "Y" else q.get("no_bid", 0)
        dead = False
        reason = ""
        if om is not None:
            if t.startswith("KXHIGHCHI") and om >= 89:
                dead, reason = True, f"CHI obs max {om} >= 89 -> 'under 89' dead"
            if t.startswith("KXHIGHNY") and "B80.5" in t and om >= 82:
                dead, reason = True, f"NY obs max {om} >= 82 -> 80-81 dead"
            if t.startswith("KXHIGHNY") and "B82.5" in t and om >= 84:
                dead, reason = True, f"NY obs max {om} >= 84 -> 82-83 dead"
        now_cdt = datetime.utcnow() - timedelta(hours=5)
        pm_window = now_cdt.hour >= 15
        if not dead and pm_window and om is not None:
            if "B80.5" in t and om <= 78:
                dead, reason = True, f"NY 3:30 PM obs {om} <= 78 -> 80-81 window closed"
            if "B82.5" in t and om <= 80:
                dead, reason = True, f"NY 3:30 PM obs {om} <= 80 -> 82-83 window closed"
        px = (q.get("yes_bid") if side == "Y" else q.get("no_bid")) or 0
        if dead and px >= 0.01:
            try:
                res = k.sell_position(t, side.lower(), px, sh, order_type="market")
                actions.append("SOLD %s %d sh @ %.2f (%s) -> fill %s" % (t, sh, px, reason, res.get("fill_count")))
            except Exception as e:
                actions.append("SELL FAILED %s: %s" % (t, str(e)[:120]))
        elif dead:
            actions.append("DEAD (bid %0.2f - no salvage) %s: %s" % (px, t, reason))
        elif om is not None and (sh >= 10):
            # alive; report only if big bid (profit protection) — Thad's standing rule
            if (side == "Y" and px >= 0.60) or (side == "N" and px >= 0.70):
                actions.append("ALERT big bid %s: %s-side bid %.2f sh %.0f — recommend hold (toward par)" % (t, side, px, sh))
    if actions:
        print("\n".join(actions))
    else:
        print("NO_REPLY")  # silent while alive

if __name__ == "__main__":
    main()