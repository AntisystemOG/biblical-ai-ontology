# Kalshi price snapshots - dynamic event discovery (replaces hardcoded stale tickers).
# Snapshot ALL currently-active events per claims/CPI/Fed series; skip resolved ones.
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\The Edge")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\The Edge\modules")
from kalshi_client import Kalshi
from timing_module import snapshot_market_prices, save_snapshot

SERIES = ["KXJOBLESSCLAIMS", "KXCPI", "KXCPICORE", "KXFEDDECISION"]
data_dir = r"C:\AI Projects\Prediction Market\Kalshi\The Edge\data"
k = Kalshi()
now = datetime.now(timezone.utc)

done = []
for series in SERIES:
    try:
        mkts = k.get_markets(series_ticker=series, limit=60)
    except Exception as e:
        print(f"ERR fetching {series}: {type(e).__name__}")
        continue
    events = {}
    for m in mkts:
        ev = m.get("event_ticker") or "-".join((m.get("ticker") or "").split("-")[:2])
        if not ev or ev == "-":
            continue
        if m.get("status") != "active":
            continue
        ct = m.get("close_time", "")
        events.setdefault(ev, ct)
    # keep active events; sort by close time; snapshot max 2 per series
    active = sorted(events.items(), key=lambda kv: kv[1] or "9999")[:2]
    for ev, ct in active:
        try:
            snap = snapshot_market_prices(ev)
            if snap:
                save_snapshot(snap, data_dir)
                done.append(f"{ev} (closes {ct or 'n/a'}, {len(snap.get('markets', []))} markets)")
            else:
                done.append(f"FAILED {ev}")
        except Exception as e:
            done.append(f"ERR {ev}: {type(e).__name__}")

print(f"Snapshots {now:%Y-%m-%d %H:%M}Z -> {len(done)}")
for d in done:
    print(" ", d)