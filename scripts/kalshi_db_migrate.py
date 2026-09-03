# kalshi_db_migrate.py - idempotent import of scattered JSON stores into kalshi_model.db.
# predictions.json -> forecasts table (model forecast history)
# learnings.json   -> forecasts table (graded outcomes, compact) + model_state
# accuracy.json    -> model_state (per-signal claims accuracy)
# price_snapshots.jsonl -> snapshots table
import sys, json
from pathlib import Path

sys.path.insert(0, r"C:\Users\thadd\.openclaw\workspace\scripts")
import kalshi_db as db

ES = Path(r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner\data")

def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return None

def forecast_exists(kind, target_date, note_prefix):
    conn = db.connect()
    r = conn.execute("SELECT COUNT(*) n FROM forecasts WHERE kind=? AND target_date=? AND note LIKE ?",
                     (kind, target_date, note_prefix + "%")).fetchone()["n"]
    conn.close()
    return r > 0

counts = {"forecasts": 0, "grades": 0, "bands": 0, "state": 0, "snapshots": 0, "skipped": 0}

# --- weather forecast history ---
p = load(ES / "weather" / "predictions.json")
if p:
    for x in p.get("predictions", []):
        try:
            date = str(x.get("date", "?"))
            city = str(x.get("city", "?"))
            if forecast_exists("weather", date, city):
                continue
            db.record_forecast(
                kind="weather", target_date=date,
                model_center=x.get("adjusted_forecast_high"),
                note=f"{city}|adj={x.get('adjusted_forecast_high')}|nws={x.get('nws_forecast_high')}|{';'.join(x.get('adjustments', []))[:180]}",
            )
            counts["forecasts"] += 1
            for band in x.get("predictions", []) or []:
                try:
                    db.record_prediction(
                        source="weather_daily", kind="weather",
                        event=f"{city}-{date}",
                        market=str(band.get("band") or band.get("ticker") or band.get("market", "?")),
                        pick=str(band.get("pick") or band.get("side") or "band"),
                        side=band.get("side"), model_prob=band.get("prob") or band.get("model_prob"),
                        market_prob=band.get("market_prob") or band.get("market_price"),
                        ts=date,
                    )
                    counts["bands"] += 1
                except Exception:
                    counts["skipped"] += 1
        except Exception:
            counts["skipped"] += 1

# --- graded outcomes (learnings.json) ---
l = load(ES / "weather" / "learnings.json")
if l:
    for x in l.get("learnings", []):
        try:
            date = str(x.get("predictions_made") or x.get("date") or "?")
            if forecast_exists("weather_grade", date, "GRADING"):
                continue
            db.record_forecast(
                kind="weather_grade", target_date=date,
                note="GRADING|" + json.dumps(x.get("actuals", {})) + "|" + json.dumps(x.get("results", []))[:400],
            )
            counts["grades"] += 1
        except Exception:
            counts["skipped"] += 1
    for ru in l.get("rule_updates", []):
        try:
            lesson = str(ru.get("rule") or ru.get("lesson") or ru) if isinstance(ru, dict) else str(ru)
            db.record_learning(lesson=lesson[:500], source="weather_rule_updates")
            counts["state"] += 1
        except Exception:
            counts["skipped"] += 1

# --- claims per-signal accuracy -> model_state ---
a = load(ES / "accuracy.json")
if isinstance(a, dict):
    for sig, v in a.items():
        if isinstance(v, dict) and "total" in v:
            db.set_state(f"claims_acc[{sig}]", f"{v.get('correct', 0)}/{v.get('total', 0)} err={round(v.get('avg_error', 0))}", by="migrate")
            counts["state"] += 1

# --- price snapshots jsonl ---
snap = Path(r"C:\AI Projects\Prediction Market\Kalshi\The Edge\data\price_snapshots.jsonl")
if snap.exists():
    for line in snap.read_text(encoding="utf-8").splitlines()[-500:]:
        try:
            s = json.loads(line)
            ev = s.get("event_ticker") or s.get("event") or "?"
            ts = s.get("ts") or s.get("timestamp")
            for m in s.get("markets", []):
                db.record_snapshot(
                    event=ev, market=m.get("ticker") or m.get("market") or "?",
                    yes_bid=m.get("yes_bid") or m.get("yes_bid_dollars"),
                    yes_ask=m.get("yes_ask") or m.get("yes_ask_dollars"),
                    no_bid=m.get("no_bid") or m.get("no_bid_dollars"),
                    no_ask=m.get("no_ask") or m.get("no_ask_dollars"),
                    volume=m.get("volume"), ts=ts,
                )
                counts["snapshots"] += 1
        except Exception:
            counts["skipped"] += 1

print(f"migrate done: {counts}")
conn = db.connect()
for t in ["predictions", "learnings", "model_state", "snapshots", "forecasts"]:
    n = conn.execute(f"SELECT COUNT(*) n FROM {t}").fetchone()["n"]
    print(f"  {t}: {n}")
acc = db.accuracy()
print(f"  settled predictions: {acc['wins']}/{acc['total']} = {acc['rate']:.0%}")
conn.close()