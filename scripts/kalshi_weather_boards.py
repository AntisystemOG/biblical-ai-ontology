# Kalshi weather boards: live prices for today + tomorrow vs NWS forecast (ASCII-safe for cron use).
import sys, datetime
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")
from kalshi_client import Kalshi
from weather_predictor import fetch_nws_forecast, CITIES

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

print(f"Kalshi weather boards {today} / {tomorrow} (live asks, NWS forecast)")
for (series, date) in sorted(events.keys()):
    st, nm = SERIES_TO_CITY.get(series, (None, series))
    ds = f"20{date[:2]}-{MON[date[2:5]]}-{date[5:]}"
    hi = nws_high_for(nm, ds) if nm in CITIES else None
    print(f"== {nm} ({series}) {ds} | NWS high: {hi}")
    for e in sorted(events[(series, date)], key=lambda x: x["ticker"]):
        tail = e["ticker"].rsplit("-", 1)[-1]
        print(f"  {tail:>10}  yes {fmt(e['yes_ask']):>5}  no {fmt(e['no_ask']):>5}  [bid {fmt(e['yes_bid']):>5} vol {e['vol']:.0f}]")