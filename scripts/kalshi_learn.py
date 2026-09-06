# kalshi_learn.py - nightly settlement + learning pipeline (Thad Sep 3: all wins/losses + WHY -> one DB).
# 1. Paper bets: settle open history.json entries whose date has a graded actual -> DB predictions + WHY.
# 2. Live positions: finalized Kalshi markets -> settle DB rows + WHY.
# 3. Model learning: per-city NWS-vs-actual rolling bias -> model_state (feeds better forecasts).
import sys, json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, r"C:\Users\thadd\.openclaw\workspace\scripts")
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi")
from kalshi_client import Kalshi
import kalshi_db as db

ES = Path(r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner\data")
PT = ES / "weather" / "paper_trader"
CITY_CODE = {"Denver": "DEN", "Miami": "MIA", "Chicago": "CHI", "New York": "NY",
             "LA": "LA", "Houston": "HOU", "Dallas": "DAL", "Phoenix": "PHX"}
now = datetime.now().astimezone()

def jload(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return None

def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

stats = {"paper_settled": 0, "live_settled": 0, "learnings": 0, "bias": 0, "skipped": 0}

# ---------- 1. PAPER settlement ----------
graded = []
g = jload(PT / "results.json")
if g and isinstance(g.get("graded"), list):
    for x in g["graded"]:
        d, c = x.get("date"), x.get("city")
        a = f(x.get("actual_high"))
        if d and c and a is not None:
            graded.append((d, c, a))
actual_by = {(d, c): a for d, c, a in graded}

hist_path = PT / "history.json"
hist = jload(hist_path) or []
changed = False
for h in hist:
    if h.get("status") != "open":
        continue
    d, c = h.get("date"), h.get("city")
    actual = actual_by.get((d, c))
    if actual is None:
        stats["skipped"] += 1
        continue
    lo, hi = f(h.get("band_low")), f(h.get("band_high"))
    price = f(h.get("purchase_price")) or 0
    shares = f(h.get("shares")) or 0
    direction = (h.get("direction") or "").upper()
    if lo is None or hi is None:
        thr = f(h.get("threshold"))
        if thr is None:
            stats["skipped"] += 1
            continue
        in_band = (actual >= thr) if direction == "YES" else (actual < thr)
    else:
        in_band = lo <= actual <= hi
    win = in_band if direction == "YES" else (not in_band)
    bet_amount = f(h.get("bet_amount")) or round((shares or 0) * (price or 0), 2)
    profit = round((shares or 0) - bet_amount, 2) if win else round(-bet_amount, 2)
    h["status"] = "settled"
    h["actual_high"] = actual
    h["result"] = "WIN" if win else "LOSS"
    h["profit"] = profit
    changed = True
    stats["paper_settled"] += 1
    # DB row (create + settle in one flow)
    code = CITY_CODE.get(c, c)
    ticker = h.get("ticker") or f"{code}-{d}"
    db.record_prediction(source="paper_trader", kind="weather", event=f"KXHIGH{code}-{d}",
                         market=ticker, pick=f"{c} {direction} {h.get('band_low')}-{h.get('band_high')}",
                         side=direction, shares=shares, entry_price=price,
                         model_prob=None, market_prob=None, ts=h.get("placed_at"),
                         exit_plan="paper ladder (sure-thing/lotto test)")
    db.settle_prediction(f"KXHIGH{code}-{d}", ticker, "WIN" if win else "LOSS", profit,
                         settled_at=h.get("placed_at"))
    # WHY learning on losses
    if not win:
        why = f"WHY LOST {c} {d}: band {lo}-{hi} missed, actual {actual}F. "
        conn = db.connect()
        r = conn.execute("SELECT nws_forecast_high, adjusted_forecast_high FROM forecasts WHERE target_date=? AND note LIKE ? ORDER BY ts DESC LIMIT 1",
                         (d, f"{c}|")).fetchone()
        conn.close()
        if r:
            nws_f, adj_f = f(r["nws_forecast_high"]), f(r["adjusted_forecast_high"])
            if nws_f is not None:
                why += f"NWS said {nws_f:.0f} (err {actual - nws_f:+.1f}), adjusted {adj_f}. "
        why += "Band too close to forecast distribution."
        db.record_learning(lesson=why[:480], source="paper_trader_loss")
        stats["learnings"] += 1

if changed:
    HIST_PATH = hist_path
    HIST_PATH.write_text(json.dumps(hist, indent=1), encoding="utf-8")

# ---------- 2. LIVE settlement ----------
live = Kalshi()
pos = live.get_positions()
open_db = {r["market"]: r["id"] for r in [dict(x) for x in (db.connect().execute("SELECT id, market FROM predictions WHERE status='open'").fetchall())]}
for p in pos.get("market_positions", []):
    tk = p.get("ticker", "")
    if "26SEP" not in tk and "KXHIGH" not in tk and "KXJOBLESS" not in tk and "KXFED" not in tk:
        continue
    m = live.get_market(tk) or {}
    m = m.get("market", m) if isinstance(m, dict) else {}
    if m.get("status") == "finalized":
        result = m.get("result")
        fp = float(p.get("position_fp") or 0)
        traded = float(p.get("total_traded_dollars") or 0)
        side = "YES" if fp > 0 else "NO"
        won = (result == "yes" and side == "YES") or (result == "no" and side == "NO")
        pnl = round(abs(fp) - traded, 2) if won else round(-traded, 2)
        if tk in open_db:
            db.settle_prediction(tk.replace("-" + tk.rsplit("-", 1)[-1], ""), tk, "WIN" if won else "LOSS", pnl)
        else:
            db.record_prediction(source="live", kind="weather" if "KXHIGH" in tk else "other",
                                 event="-".join(tk.split("-")[:2]), market=tk,
                                 pick=f"{side} {tk.rsplit('-',1)[-1]}", side=side,
                                 shares=abs(fp), entry_price=(traded / abs(fp)) if fp else 0)
            db.settle_prediction("-".join(tk.split("-")[:2]), tk, "WIN" if won else "LOSS", pnl)
        stats["live_settled"] += 1

# ---------- 3. Per-city bias learning (NWS vs actual, rolling) ----------
conn = db.connect()
per_city = {}
for (d, c, a) in graded:
    code = CITY_CODE.get(c)
    if not code:
        continue
    per_city.setdefault(code, []).append((d, a))
NAME_BY_CODE = {v: k for k, v in CITY_CODE.items()}
for code, pairs in per_city.items():
    pairs.sort()
    cname = NAME_BY_CODE.get(code, code)
    errs = []
    for (d, a) in pairs[-5:]:
        conn_r = conn.execute("SELECT note FROM forecasts WHERE target_date=? AND note LIKE ? ORDER BY ts DESC LIMIT 1",
                              (d, f"{cname}|%")).fetchone()
        if conn_r:
            try:
                note = conn_r["note"]
                n = f(note.split("nws=")[1].split("|")[0])
            except Exception:
                n = None
            if n is not None:
                errs.append(n - a)
                # Improvement 5: forecast-revision tracking (regime-shift detector)
                try:
                    shifted = db.record_revision(cname, d, n)
                    if shifted:
                        stats["learnings"] += 1
                except Exception:
                    pass
    if errs:
        bias = round(sum(errs) / len(errs), 2)
        db.set_state(f"city_bias_{code}", f"{bias:+.2f}F over last {len(errs)} graded days (positive = NWS runs hot)", by="kalshi_learn")
        stats["bias"] += 1
        # Improvement 2: per-city sigma (std of errors) once we have 3+ graded days
        if len(errs) >= 3:
            mean = sum(errs) / len(errs)
            var = sum((e - mean) ** 2 for e in errs) / len(errs)
            sigma = round(var ** 0.5, 2)
            db.set_state(f"city_sigma_{code}", f"{sigma:.2f}F over last {len(errs)} graded days", by="kalshi_learn")
            stats["bias"] += 1
conn.close()

print(f"kalshi_learn {now:%Y-%m-%d %H:%M}: {stats}")
acc = db.accuracy()
print(f"DB settled accuracy: {acc['wins']}/{acc['total']} = {acc['rate']:.0%} (target 80%)")
for s in db.all_state():
    if s["key"].startswith("city_bias_"):
        print(f"  {s['key']}: {s['value']}")