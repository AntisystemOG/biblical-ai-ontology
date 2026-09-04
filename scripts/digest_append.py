#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""digest_append.py - Append (or replace) a report section in today's Spock Daily Digest.

All non-Kalshi cron reports consolidate into ONE document per day:
    Spocks Reports/Spock_Daily_YYYY-MM-DD.md

Usage:
  python scripts/digest_append.py --report "Whale Watch" --file <md-file>
  python scripts/digest_append.py --report "Memory Dream" --file <md-file> --date 2026-09-04
  python scripts/digest_append.py --report "X" --file <md-file> --keep

Behavior:
  - Creates the digest file with a header + auto table of contents if missing.
  - Appends the report as a section:  <!-- section:Title --> ## Title (HH:MM CT)
  - IDEMPOTENT: if a section with the same title already exists, it is REPLACED
    (safe on cron reruns/retries).
  - Reads/writes UTF-8; console output is ASCII-only.
"""
import argparse
import datetime
import pathlib
import re
import sys

WORKSPACE = pathlib.Path(r"C:\Users\thadd\.openclaw\workspace")
REPORTS = WORKSPACE / "Spocks Reports"
TOC_OPEN = "<!-- TOC (auto-generated) -->"
TOC_CLOSE = "<!-- /TOC -->"


def build_toc(text: str) -> str:
    heads = []
    for line in text.splitlines():
        m = re.match(r"^## (.+?) \(\d{1,2}:\d{2} CT\)\s*$", line)
        if m:
            heads.append(m.group(1))
    toc = TOC_OPEN + "\n" + "\n".join("- " + h for h in heads) + "\n" + TOC_CLOSE
    if TOC_OPEN in text and TOC_CLOSE in text:
        pre, rest = text.split(TOC_OPEN, 1)
        _, post = rest.split(TOC_CLOSE, 1)
        return pre + toc + post
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, help="Section title, e.g. 'Whale Watch'")
    ap.add_argument("--file", required=True, help="Markdown source file with the report body")
    ap.add_argument("--date", help="Digest date YYYY-MM-DD (default: today, local time)")
    ap.add_argument("--keep", action="store_true", help="Do not delete the source file")
    args = ap.parse_args()

    src = pathlib.Path(args.file)
    if not src.is_absolute():
        src = WORKSPACE / src
    if not src.exists():
        print("ERROR: source file not found: %s" % src)
        return 2
    body = src.read_text(encoding="utf-8", errors="replace").strip()
    if not body:
        print("ERROR: source file is empty: %s" % src)
        return 2

    day = args.date or datetime.date.today().isoformat()
    target = REPORTS / ("Spock_Daily_%s.md" % day)

    if target.exists():
        text = target.read_text(encoding="utf-8", errors="replace")
    else:
        text = (
            "# Spock Daily Digest - %s\n\n"
            "_One consolidated document. Every non-Kalshi cron report appends a section "
            "here instead of creating its own file._\n\n%s\n%s\n" % (day, TOC_OPEN, TOC_CLOSE)
        )

    stamp = datetime.datetime.now().strftime("%H:%M")
    marker = "<!-- section:%s -->" % args.report
    section = "%s\n## %s (%s CT)\n\n%s\n" % (marker, args.report, stamp, body)

    replaced = False
    if marker in text:
        start = text.index(marker)
        nxt = text.find("\n<!-- section:", start + 1)
        end = len(text) if nxt == -1 else nxt
        text = text[:start] + section + text[end:]
        replaced = True
    else:
        text = text.rstrip("\n") + "\n\n---\n\n" + section

    text = build_toc(text)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")

    if not args.keep:
        try:
            src.unlink()
        except OSError:
            pass

    print("OK: %s '%s' -> %s" % ("replaced section" if replaced else "appended section",
                                 args.report, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())