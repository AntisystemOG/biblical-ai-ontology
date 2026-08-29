# -*- coding: utf-8 -*-
"""Sample https://weather.com/kalshi and append a cadence row to CSV.
Temporary probe (Thad directive 2026-08-29 07:23): measure update cadence of the
official TWC/Kalshi settlement page + capture intraday data for pattern work.

Each run appends one row: timestamp, byte size, content hash, cache headers,
degree readings found in the shell, station codes, ISO timestamps.
Cadence = compare hashes across rows (silent logging; no alerts on success)."""
import urllib.request, hashlib, json, re, datetime, os, csv, sys

URL = "https://weather.com/kalshi"
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "twc_probe_log.csv")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    req = urllib.request.Request(URL, headers={
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read()
        hdrs = {k.lower(): v for k, v in r.headers.items()}
    body = raw.decode("utf-8", "replace")
    row = {
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "bytes": len(body),
        "hash": hashlib.sha1(body.encode("utf-8", "replace")).hexdigest()[:12],
        "cache_control": hdrs.get("cache-control", ""),
        "age": hdrs.get("age", ""),
        "last_modified": hdrs.get("last-modified", ""),
        "x_vercel_cache": hdrs.get("x-vercel-cache", ""),
        "deg_nums": " ".join(re.findall(r"-?\d{1,3}\s*(?:\u00b0|&deg;)", body)[:40]),
        "stations": " ".join(sorted(set(re.findall(
            r"CLIDEN|KMDW|KMIA|KLGA|KPHX|KDAL|KHOU|KLAX|KLAS", body)))[:12]),
        "iso_stamps": " | ".join(sorted(set(re.findall(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?", body)))[:10]),
        "chunk_hits": len(re.findall(r"static/chunks/", body)),
    }
    exists = os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            w.writeheader()
        w.writerow(row)
    print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"error": repr(e)}))