# kalshi_db.py - THE one prediction-model database. Every Kalshi job reads/writes here.
# SQLite WAL: safe for concurrent cron access. One file: data/kalshi_model.db (git-backed).
import sqlite3, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "kalshi_model.db"

def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=8000")
    conn.execute("PRAGMA synchronous=NORMAL")
    _ensure_schema(conn)
    return conn

def _ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS predictions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TEXT NOT NULL, source TEXT NOT NULL, kind TEXT NOT NULL,
      event TEXT NOT NULL, market TEXT, pick TEXT NOT NULL,
      side TEXT, shares REAL, entry_price REAL,
      model_prob REAL, market_prob REAL,
      status TEXT DEFAULT 'open', result TEXT, pnl REAL, settled_at TEXT,
      content_hash TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS learnings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TEXT NOT NULL, source TEXT, lesson TEXT NOT NULL,
      rule_change TEXT, status TEXT DEFAULT 'active',
      hits INTEGER DEFAULT 0, misses INTEGER DEFAULT 0, content_hash TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS model_state (
      key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT, updated_by TEXT
    );
    CREATE TABLE IF NOT EXISTS snapshots (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event TEXT NOT NULL, market TEXT NOT NULL, ts TEXT NOT NULL,
      yes_bid REAL, yes_ask REAL, no_bid REAL, no_ask REAL, volume REAL,
      content_hash TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS forecasts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TEXT NOT NULL, kind TEXT NOT NULL, target_date TEXT,
      blended REAL, market_center REAL, model_center REAL,
      ci_low REAL, ci_high REAL, note TEXT, content_hash TEXT UNIQUE
    );
    """)
    conn.commit()

def _hash(*vals):
    h = hashlib.md5("|".join("" if v is None else str(v) for v in vals).encode())
    return h.hexdigest()

# ---------- predictions ----------
def record_prediction(source, kind, event, pick, market=None, side=None,
                      shares=None, entry_price=None, model_prob=None,
                      market_prob=None, ts=None):
    conn = connect()
    t = ts or _now()
    ch = _hash(source, event, market, pick, t)
    conn.execute("INSERT OR IGNORE INTO predictions (ts,source,kind,event,market,pick,side,shares,entry_price,model_prob,market_prob,content_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                 (t, source, kind, event, market, pick, side, shares, entry_price, model_prob, market_prob, ch))
    conn.commit(); conn.close()

def settle_prediction(event, market, result, pnl, settled_at=None):
    conn = connect()
    conn.execute("UPDATE predictions SET status='settled', result=?, pnl=?, settled_at=? WHERE event=? AND (market=? OR ? IS NULL) AND status='open'",
                 (result, pnl, settled_at or _now(), event, market, market))
    conn.commit(); conn.close()

def open_predictions(source=None):
    conn = connect()
    q = "SELECT * FROM predictions WHERE status='open'" + (" AND source=?" if source else "")
    rows = conn.execute(q, (source,) if source else ()).fetchall()
    conn.close(); return [dict(r) for r in rows]

def accuracy(source=None, kind=None):
    conn = connect()
    q = "SELECT COUNT(*) n, SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) w FROM predictions WHERE status='settled'"
    args = []
    if source: q += " AND source=?"; args.append(source)
    if kind: q += " AND kind=?"; args.append(kind)
    r = conn.execute(q, args).fetchone()
    conn.close()
    n, w = r["n"] or 0, r["w"] or 0
    return {"total": n, "wins": w, "rate": (w / n) if n else 0.0}

# ---------- learnings ----------
def record_learning(lesson, source=None, rule_change=None):
    conn = connect()
    ch = _hash(lesson, rule_change or "")
    conn.execute("INSERT OR IGNORE INTO learnings (ts,source,lesson,rule_change,content_hash) VALUES (?,?,?,?,?)",
                 (_now(), source, lesson, rule_change, ch))
    conn.commit(); conn.close()

def bump_learning(lesson_like, hit=True):
    conn = connect()
    col = "hits" if hit else "misses"
    conn.execute(f"UPDATE learnings SET {col}={col}+1 WHERE lesson LIKE ? AND status='active'", (f"%{lesson_like}%",))
    conn.commit(); conn.close()

def active_learnings(limit=20):
    conn = connect()
    rows = conn.execute("SELECT lesson, rule_change, hits, misses FROM learnings WHERE status='active' ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

# ---------- model state (the LIVING parameters) ----------
def get_state(key, default=None):
    conn = connect()
    r = conn.execute("SELECT value FROM model_state WHERE key=?", (key,)).fetchone()
    conn.close()
    return r["value"] if r else default

def set_state(key, value, by="cron"):
    conn = connect()
    conn.execute("INSERT INTO model_state (key,value,updated_at,updated_by) VALUES (?,?,?,?) "
                 "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at, updated_by=excluded.updated_by",
                 (key, str(value), _now(), by))
    conn.commit(); conn.close()

def all_state():
    conn = connect()
    rows = conn.execute("SELECT key, value, updated_at, updated_by FROM model_state ORDER BY key").fetchall()
    conn.close(); return [dict(r) for r in rows]

# ---------- snapshots / forecasts ----------
def record_snapshot(event, market, yes_bid=None, yes_ask=None, no_bid=None, no_ask=None, volume=None, ts=None):
    conn = connect()
    t = ts or _now()
    ch = _hash(event, market, t)
    conn.execute("INSERT OR IGNORE INTO snapshots (event,market,ts,yes_bid,yes_ask,no_bid,no_ask,volume,content_hash) VALUES (?,?,?,?,?,?,?,?,?)",
                 (event, market, t, yes_bid, yes_ask, no_bid, no_ask, volume, ch))
    conn.commit(); conn.close()

def record_forecast(kind, target_date, blended=None, market_center=None, model_center=None, ci_low=None, ci_high=None, note=None):
    conn = connect()
    t = _now()
    ch = _hash(kind, target_date, t, blended)
    conn.execute("INSERT OR IGNORE INTO forecasts (ts,kind,target_date,blended,market_center,model_center,ci_low,ci_high,note,content_hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
                 (t, kind, target_date, blended, market_center, model_center, ci_low, ci_high, note, ch))
    conn.commit(); conn.close()

def latest_forecast(kind):
    conn = connect()
    r = conn.execute("SELECT * FROM forecasts WHERE kind=? ORDER BY ts DESC LIMIT 1", (kind,)).fetchone()
    conn.close(); return dict(r) if r else None

if __name__ == "__main__":
    c = connect()
    print(f"DB: {DB_PATH}")
    for t in ["predictions", "learnings", "model_state", "snapshots", "forecasts"]:
        n = c.execute(f"SELECT COUNT(*) n FROM {t}").fetchone()["n"]
        print(f"  {t}: {n} rows")
    a = accuracy()
    print(f"  accuracy: {a['wins']}/{a['total']} = {a['rate']:.0%}")
    c.close()