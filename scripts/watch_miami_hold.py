"""Watch the Miami 88-89 long shot + NY 81-82 tail. Live obs + hourly + market prices."""
import sys, json, urllib.request

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
from kalshi_client import Kalshi

UA = {"User-Agent": "SpockWeather/1.0"}

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

def main():
    print("=== LIVE OBS ===")
    for st, label in [("KMIA", "MIA-KMIA"), ("KNYC", "NYC-CP")]:
        try:
            o = get_obs(st)
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
    except Exception as e:
        print(f"kalshi error {e}")

if __name__ == "__main__":
    main()