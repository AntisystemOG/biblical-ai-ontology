#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
session_prompt.py - evolving session prompt for Spock main sessions.

Rebuilds SESSION_PROMPT.md (workspace root) from three live inputs:
  1. carry-in goal    (last --end call)
  2. open loops       (auto-scanned from recent memory/2026-*.md)
  3. active lessons   (learned from feedback; decay as they stick)

Events (each also rebuilds the prompt file):
  --learn "text"   record a miss: creates a lesson, or escalates an existing one
  --hit L2         record that a lesson was applied cleanly (streak++)
  --note "text"    neutral context note (logged, not shown in prompt)
  --end "wrap"     close session; optionally --end "wrap | next-session goal"
  --list           print active lesson table
  --drop L3        archive a lesson manually

Evolution rules:
  - A lesson that earns another miss escalates: watch -> critical (2 misses).
  - Clean applications build a streak: critical -> watch at 4, watch -> archived
    at 7. The prompt shrinks and sharpens as lessons are absorbed.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
STATE_PATH = WS / "session_evolution.json"
PROMPT_PATH = WS / "SESSION_PROMPT.md"
FEEDBACK_PATH = WS / "memory" / "session_feedback.jsonl"
MEMORY_DIR = WS / "memory"

STYLE = [
    "Lead with the answer. Short. Tables over prose.",
    "No unsolicited status updates - silence unless something material changed or Thad asks.",
    "If a needed fact is missing, name the gap out loud. Never guess.",
]

# Seeded from documented failure modes (Aug 26 wrong-side orders, Aug 27/28 exits).
SEED_LESSONS = [
    "Restate any Kalshi trade in plain English (side, band, dollars) and verify against rules_primary BEFORE executing.",
    "Odds movement alone is never an exit trigger. Station math or window math only.",
]


def norm(t):
    return re.sub(r"\s+", " ", t).strip().lower()


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def new_state():
    return {
        "version": 1,
        "next_id": 1,
        "lessons": [],
        "last_end": {"ts": None, "wrap": None, "goal": None},
        "stats": {"generates": 0, "learns": 0, "hits": 0, "notes": 0, "ends": 0},
        "history": [],
    }


def mk_lesson(st, text, tier="watch", misses=1, streak=0):
    lid = "L%d" % st["next_id"]
    st["next_id"] += 1
    return {
        "id": lid,
        "text": text.strip(),
        "tier": tier,
        "misses": misses,
        "streak": streak,
        "added": now_iso(),
        "last_hit": None,
    }


def save_state(st):
    STATE_PATH.write_text(
        json.dumps(st, indent=2, ensure_ascii=True), encoding="utf-8"
    )


def load_state():
    if STATE_PATH.exists():
        try:
            st = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            if isinstance(st, dict) and "lessons" in st:
                return st
        except Exception:
            pass
    st = new_state()
    for text in SEED_LESSONS:
        st["lessons"].append(mk_lesson(st, text, tier="critical"))
    save_state(st)
    return st


def log(kind, text, lid=None):
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": now_iso(), "kind": kind, "lesson": lid, "text": text}
    with FEEDBACK_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=True) + "\n")


def find_lesson(st, text):
    key = norm(text)[:48]
    for l in st["lessons"]:
        if norm(l["text"])[:48] == key:
            return l
    return None


def scan_open_loops():
    if not MEMORY_DIR.exists():
        return []
    files = sorted(MEMORY_DIR.glob("2026-*.md"), reverse=True)[:2]
    pat = re.compile(
        r"\b(OPEN|TODO|PENDING|follow-up|next step|awaiting|blocked on)\b", re.I
    )
    skip = re.compile(r"openclaw-memory-promotion|^<!--|^\|")
    out, seen = [], set()
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for raw in lines:
            line = raw.strip().lstrip("-*").strip()
            if not line or skip.search(raw):
                continue
            if pat.search(line):
                k = norm(line)[:60]
                if k in seen:
                    continue
                seen.add(k)
                if len(line) > 170:
                    line = line[:167] + "..."
                out.append(line)
            if len(out) >= 6:
                return out
    return out


def regenerate(st):
    loops = scan_open_loops()
    act = [l for l in st["lessons"] if l["tier"] in ("critical", "watch")]
    crit = [l for l in act if l["tier"] == "critical"]
    watch = [l for l in act if l["tier"] == "watch"]

    L = []
    L.append("# SESSION PROMPT v%d" % (st["stats"]["generates"] + 1))
    L.append(
        "_rebuilt %s | %d active lessons (%d critical, %d fading)_"
        % (now_iso(), len(act), len(crit), len(watch))
    )
    L.append("")
    L.append("## CARRY-IN GOAL")
    goal = st["last_end"].get("goal")
    L.append(goal if goal else "- (none set yet - set one with --end)")
    L.append("")
    L.append("## OPEN LOOPS (auto-scanned from recent daily memory)")
    if loops:
        for x in loops:
            L.append("- " + x)
    else:
        L.append("- none found in last two daily notes")
    L.append("")
    L.append("## ACTIVE LESSONS (earned from mistakes; clean streaks retire them)")
    if act:
        for l in crit:
            L.append("- [CRITICAL] " + l["text"])
        for l in watch:
            L.append("- [watch] %s (clean streak %d)" % (l["text"], l["streak"]))
    else:
        L.append("- none active")
    L.append("")
    L.append("## STYLE CONTRACT")
    for s in STYLE:
        L.append("- " + s)
    L.append("")
    L.append(
        "_Feedback verbs: 'lesson: X' -> --learn | --hit L# when applied cleanly "
        "| --end at session close._"
    )
    body = "\n".join(L) + "\n"
    PROMPT_PATH.write_text(body, encoding="utf-8")

    st["stats"]["generates"] += 1
    st["history"].append({"ts": now_iso(), "lines": len(L), "active": len(act)})
    st["history"] = st["history"][-20:]
    save_state(st)
    return body, len(act)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--learn")
    ap.add_argument("--hit")
    ap.add_argument("--note")
    ap.add_argument("--end")
    ap.add_argument("--drop")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    st = load_state()

    if args.list:
        for l in st["lessons"]:
            if l["tier"] == "archived":
                continue
            print(
                "%-4s %-8s misses=%d streak=%d | %s"
                % (l["id"], l["tier"], l["misses"], l["streak"], l["text"])
            )
        return 0

    did = False
    if args.drop:
        for l in st["lessons"]:
            if l["id"] == args.drop:
                l["tier"] = "archived"
                log("drop", "manual archive", l["id"])
                did = True
                print("archived %s" % l["id"])
                break

    if args.learn:
        ex = find_lesson(st, args.learn)
        if ex:
            ex["misses"] += 1
            ex["streak"] = 0
            if ex["tier"] == "watch" and ex["misses"] >= 2:
                ex["tier"] = "critical"
            log("learn", args.learn, ex["id"])
            print("escalated %s (misses=%d, tier=%s)" % (ex["id"], ex["misses"], ex["tier"]))
        else:
            nl = mk_lesson(st, args.learn)
            st["lessons"].append(nl)
            log("learn", args.learn, nl["id"])
            print("new lesson %s (watch)" % nl["id"])
        st["stats"]["learns"] += 1
        did = True

    if args.hit:
        for l in st["lessons"]:
            if l["id"] == args.hit:
                l["streak"] += 1
                l["last_hit"] = now_iso()
                if l["tier"] == "critical" and l["streak"] >= 4:
                    l["tier"] = "watch"
                    print("%s demoted critical->watch (clean streak %d)" % (l["id"], l["streak"]))
                if l["tier"] == "watch" and l["streak"] >= 7:
                    l["tier"] = "archived"
                    print("%s archived (absorbed after %d clean hits)" % (l["id"], l["streak"]))
                log("hit", "clean application", l["id"])
                st["stats"]["hits"] += 1
                did = True
                print("%s streak=%d tier=%s" % (l["id"], l["streak"], l["tier"]))
                break
        else:
            print("no such lesson: %s" % args.hit)
            return 1

    if args.note:
        log("note", args.note)
        st["stats"]["notes"] += 1
        did = True

    if args.end:
        parts = args.end.split("|", 1)
        st["last_end"] = {
            "ts": now_iso(),
            "wrap": parts[0].strip(),
            "goal": parts[1].strip() if len(parts) > 1 else None,
        }
        st["stats"]["ends"] += 1
        log("end", args.end)
        did = True

    body, n_act = regenerate(st)
    print(
        "SESSION_PROMPT.md rebuilt (v%d, %d lines, %d active lessons)"
        % (st["stats"]["generates"], body.count("\n"), n_act)
    )
    if not did:
        print("(no event flags given - plain regeneration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())