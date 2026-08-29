"""Watch the Miami 88-89 long shot + NY 81-82 tail + snapshot full ladder to ledger.
Every run appends a market snapshot row set to data/ledger/snapshots_YYYY-MM-DD.csv
(ticker, prices, volume, obs temps) — builds the intraday path dataset for bias recalibration.
"""
import sys, json, urllib.request, os
from datetime import datetime, timezone

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
from kalshi_client import Kalshi

UA = {"User-Agent": "SpockWeather/1.0"}
LEDGER_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ledger")

def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)

def get_obs(station):
    d = fetch_json(f"https://api.weather.gov/stations/{station}/observations/latest")
    p = d["properties"]
    t = p.get("temperature", {}) or {}
    temp = t.get("value")
    return {
        "time": (p.get("timestamp") or "")[:16],
        "temp_f": round(temp * 9 / 5 + 32) if temp is not None else None,
        "wx": p.get("textDescription", ""),
    }

def get_hourly(lat, lon):
    pts = fetch_json(f"https://api.weather.gov/points/{lat},{lon}")
    fdata = fetch_json(pts["properties"]["forecastHourly"])
    out = []
    for p in fdata["properties"]["periods"]:
        st = p.get("startTime", "")
        if not st.startswith("2026-08-29"):
            continue
        pp = p.get("probabilityOfPrecipitation", {}).get("value", 0) or 0
        out.append(f"{int(st[11:13]):02d}h:{p.get('temperature')}F/p{pp}%")
    return " ".join(out)

def log_snapshot(all_markets, mia_temp, nyc_temp):
    os.makedirs(LEDGER_DIR, exist_ok=True)
    day = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(LEDGER_DIR, f"snapshots_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.csv")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("ts_utc,ticker,city,band,yes_bid,yes_ask,no_bid,no_ask,volume,kmia_obs,nyc_obs\n")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    with open(path, "a", encoding="utf-8") as f:
        for t, m in sorted(all_markets.items()):
            f.write(f"{ts},{t},{m.get('city')},{t.split('-')[-1]},{m['yes_bid']:.2f},{m['yes_ask']:.2f},{m['no_bid']:.2f},{m['no_ask']:.2f},{m['volume']:.0f},{mia_temp or ''},{nyc_temp or ''}\n")
    return path

def main():
    print("=== LIVE OBS ===")
    mia_temp = nyc_temp = None
    for st, label in [("KMIA", "MIA-KMIA"), ("KNYC", "NYC-CP")]:
        try:
            o = get_obs(st)
            if label == "MIA-KMIA":
                mia_temp = o["temp_f"]
            else:
                nyc_temp = o["temp_f"]
            print(f"{label}: {o['temp_f']}F | {o['wx']} | as of {o['time']}")
        except Exception as e:
            print(f"{label}: obs error {e}")
    print("=== MIA HOURLY (today) ===")
    try:
        print(get_hourly(25.7729, -80.1983))
    except Exception as e:
        print(f"hourly error {e}")
    print("=== KALSHI LIVE ===")
    try:
        k = Kalshi()
        m = k.get_weather_markets()
        for t in ["KXHIGHMIA-26AUG29-B88.5", "KXHIGHMIA-26AUG29-B90.5",
                  "KXHIGHMIA-26AUG29-T88", "KXHIGHNY-26AUG29-B81.5"]:
            row = m.get(t)
            if row:
                tag = t.replace("KXHIGH", "")
                print(f"{tag}: yes {row['yes_bid']:.2f}/{row['yes_ask']:.2f} | vol {row['volume']:.0f}")
        # full-ladder snapshot to ledger (path dataset for per-city TWC bias calibration)
        try:
            p = log_snapshot(m, mia_temp, nyc_temp)
            print(f"ledger+ {os.path.basename(p)}")
        except Exception as e:
            print(f"ledger append failed: {e}")
    except Exception as e:
        print(f"kalshi error {e}")

if __name__ == "__main__":
    main()