# NY Weather Band Watch - Aug 31, 2026 (KXHIGHNY-26AUG31)
# Read-only status + verdict. Order execution is done by the cron agent, not this script.
import sys, json, datetime
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
from kalshi_client import Kalshi
import urllib.request

TWC_ADJ_F = 1.5   # TWC reads ~1.5F hotter than NWS obs (our coded settlement adjustment)
STATION = "KNYC"  # CLINYC Central Park per rules_primary
BAND_LO, BAND_HI = 80, 81

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0 if c is not None else None

def obs():
    out = {"latest": None, "today_max": None}
    try:
        day = datetime.date.today().isoformat()
        u = f"https://api.weather.gov/stations/{STATION}/observations?start={day}T00:00:00-05:00"
        req = urllib.request.Request(u, headers={"User-Agent": "spock-ny-watch local"})
        d = json.load(urllib.request.urlopen(req, timeout=15))
        temps = []
        for f in d.get("features", []):
            p = f.get("properties", {})
            t = p.get("temperature", {}).get("value")
            if t is not None:
                temps.append(c_to_f(t))
        if temps:
            out["today_max"] = max(temps)
            out["latest"] = temps[-1]
    except Exception as e:
        out["error"] = f"{type(e).__name__}"
    return out

def fmt(x, pct=False):
    if x is None:
        return "--"
    return f"{float(x):.2f}" + ("c" if pct else "")

c = Kalshi()

# --- positions on today's NY weather event ---
pos = c.get_positions()
rows = []
for p in pos.get("market_positions", []) if isinstance(pos, dict) else pos:
    tk = p.get("ticker", "")
    if "KXHIGHNY" in tk and "26AUG31" in tk:
        sh = float(p.get("position_fp") or 0)
        traded = float(p.get("total_traded_dollars") or 0)
        rows.append({
            "ticker": tk, "shares": sh,
            "avg": (traded / sh) if sh else 0,
            "exposure": float(p.get("market_exposure_dollars") or 0),
        })

# --- live book for the 80-81 band ---
book = {}
mk = c.get_markets(series_ticker="KXHIGHNY", limit=30)
for m in mk:
    if m.get("ticker") == f"KXHIGHNY-26AUG31-B80.5":
        book = {"bid": m.get("yes_bid_dollars"), "ask": m.get("yes_ask_dollars")}

# --- rested order on the band ---
rest = []
o = c.get_orders(status="resting", ticker="KXHIGHNY-26AUG31-B80.5", limit=10)
for x in o.get("orders", []):
    rest.append(x.get("order_id", "")[:8])

oi = obs()
twc_max = None
if oi.get("today_max") is not None:
    twc_max = oi["today_max"] + TWC_ADJ_F

now = datetime.datetime.now()
late = now.hour >= 17  # after 5 PM CT

print(f"NY BAND WATCH {now:%H:%M} CT")
print(f"station {STATION} latest={fmt(oi.get('latest'))}F today_max_nws={fmt(oi.get('today_max'))}F twc_proxy_max={fmt(twc_max)}F")
print(f"band 80-81: bid={fmt(book.get('bid'), True)} ask={fmt(book.get('ask'), True)} resting_orders={rest}")
for r in rows:
    print(f"pos {r['ticker'].rsplit('-',1)[-1]} shares={r['shares']:.2f} avg={fmt(r['avg'])} exposure={fmt(r['exposure'])}")

# --- verdicts ---
if oi.get("error"):
    print("VERDICT: OBS-FAILED - retry reading, no action from bad data")
elif twc_max is None:
    print("VERDICT: WATCH - no station reading yet, ride resting order")
elif twc_max > 81.0:
    print("VERDICT: SELL-DEAD - TWC proxy above 81, band cannot win. Cancel resting order, sell shares at bid, then report.")
elif late and twc_max <= 79.0:
    print("VERDICT: SALVAGE-WINDOW - peaked at/below 79 after 5pm CT; sell if bid >= 25c else final hold call")
else:
    bid = book.get("bid")
    if twc_max is not None and twc_max >= BAND_LO:
        print("VERDICT: HOLD-SETTLE - reading inside/at the band, hold to settlement (no fee at 1.00)")
    elif bid is not None and float(bid) >= 0.40:
        print("VERDICT: HOLD-WATCH - big paper profit; watch giveback >30% from intraday high")
    else:
        print("VERDICT: HOLD-BACK - band still live pre-peak, let it play")