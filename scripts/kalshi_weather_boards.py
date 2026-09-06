# Kalshi weather boards: live prices for today + tomorrow vs NWS forecast (ASCII-safe for cron use).
# v2 (Sep 4 model upgrade): prints bias, sigma, market center, and the BLENDED center per city.
import sys, datetime, urllib.request, json
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")
sys.path.insert(0, r"C:\Users\thadd\.openclaw\workspace\scripts")
from kalshi_client import Kalshi
from weather_predictor import fetch_nws_forecast, CITIES
import kalshi_db as db

SERIES_TO_CITY = {
    "KXHIGHDEN": ("Denver", "DEN"), "KXHIGHMIA": ("Miami", "MIA"),
    "KXHIGHCHI": ("Chicago", "CHI"), "KXHIGHNY": ("New York", "NY"),
    "KXHIGHLA": ("LA", "LA"), "KXHIGHHOU": ("Houston", "HOU"),
    "KXHIGHDAL": ("Dallas", "DAL"), "KXHIGHPHX": ("Phoenix", "PHX"),
}
MON = {"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06",
       "JUL":"07","AUG":"08","SEP":"09","OCT":"10","NOV":"11","DEC":"12"}

def nws_high_for(city_name, date_str):
    """Points-flow NWS fetch (the endpoint that actually works)."""
    if city_name not in CITIES:
        return None
    lat, lon, _ = CITIES[city_name]
    p = fetch_nws_forecast(lat, lon, date_str)
    return p.get("temperature") if p else None

def market_center(bands):
    """YES-mid-weighted center from the band ladder (Improvement 3)."""
    rows = []
    for tail, b in bands.items():
        if not tail.startswith("B"):
            continue
        try:
            mid = float(tail[1:])
        except Exception:
            continue
        ya, yb = float(b.get("yes_ask") or 0), float(b.get("yes_bid") or 0)
        w = (ya + yb) / 2.0
        if 0 < w <= 1:
            rows.append((w, mid))
    if not rows:
        return None
    tw = sum(r[0] for r in rows)
    return round(sum(r[0] * r[1] for r in rows) / tw, 1) if tw else None

def fmt(x):
    if x is None: return "--"
    return f"{float(x):.2f}"

c = Kalshi()
mk = c.get_weather_markets()
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
want = {(f"{today:%y}{today:%b}{today:%d}").upper(), (f"{tomorrow:%y}{tomorrow:%b}{tomorrow:%d}").upper()}

events = {}
for ticker, m in mk.items():
    t = ticker.upper()
    for w in want:
        if w in t:
            events.setdefault((t.split("-")[0], w), []).append({
                "ticker": ticker, "yes_ask": m.get("yes_ask"), "no_ask": m.get("no_ask"),
                "yes_bid": m.get("yes_bid"), "vol": m.get("volume"),
            })

print(f"Kalshi weather boards {today} / {tomorrow} (live asks, bias-corrected)")
for (series, date) in sorted(events.keys()):
    st, nm = SERIES_TO_CITY.get(series, (None, series))
    code = SERIES_TO_CITY.get(series, (None, series))[1]
    ds = f"20{date[:2]}-{MON[date[2:5]]}-{date[5:]}"
    hi = nws_high_for(nm, ds) if nm in CITIES else None
    bands = {e["ticker"].rsplit("-", 1)[-1]: e for e in events[(series, date)]}
    mc = market_center(bands)
    bias = db.city_bias(code)
    sigma = db.city_sigma(code)
    if hi is not None:
        blended, model_c, _ = db.blended_center(code, hi, mc)
        print(f"== {nm} ({series}) {ds} | NWS {hi} | bias {bias:+.1f} | sigma {sigma:.1f} | market {mc} | model {model_c} | BLENDED {blended}")
    else:
        print(f"== {nm} ({series}) {ds} | NWS: None | market {mc} | sigma {sigma:.1f}")
    for e in sorted(events[(series, date)], key=lambda x: x["ticker"]):
        tail = e["ticker"].rsplit("-", 1)[-1]
        print(f"  {tail:>10}  yes {fmt(e['yes_ask']):>5}  no {fmt(e['no_ask']):>5}  [bid {fmt(e['yes_bid']):>5} vol {e['vol']:.0f}]")