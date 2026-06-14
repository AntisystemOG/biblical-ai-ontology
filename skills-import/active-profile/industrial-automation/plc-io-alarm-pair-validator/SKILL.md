---
name: plc-io-alarm-pair-validator
description: |
  Prevent copy-paste diagnostic text errors in the Degater PLC Tool
  io_alarm_pairs.json catalog. Provides an automated validator that catches
  the specific mistake pattern that produced 31 text-direction bugs.
triggers:
  - editing io_alarm_pairs.json
  - adding new alarm pair entries
  - copy-pasting entries in the catalog
  - before committing catalog changes
---

# PLC I/O Alarm Pair Validator

## The Bug Pattern

`io_alarm_pairs.json` pairs every PLC output with:
- `note_on`  → text shown when the output **energizes** (fires)
- `note_off` → text shown when the output **de-energizes** (drops)

Because many entries are structurally similar, they are often created by
**copy-pasting an existing entry and editing only the tag names**.
This leads to two classic errors:

1. **Direction text not updated** — a "Retract" entry still says "extend
   command issued" because it was copied from the "Extend" entry.
2. **note_on == note_off** — the off-state text was never rewritten, so the
   tool shows the identical message whether the solenoid fires or drops.

These bugs **do not affect tag reading or alarm logic** — they only mislead
maintenance staff reading the diagnostic note.

## Automated Validator

File: `src/plc_tools/catalog/test_io_alarm_pairs.py`

### Run it

```bash
cd /mnt/c/Users/thadd/.claude/projects/Degater\ PLC\ Tool\ BST33\ and\ 35
python3 src/plc_tools/catalog/test_io_alarm_pairs.py
```

Or via pytest:

```bash
pytest src/plc_tools/catalog/test_io_alarm_pairs.py -v
```

### What it checks

| Rule | Catches |
|------|---------|
| Justify Retract `note_on` | Must **not** say "extend command issued" or "extend sensors should switch ON" |
| Grip Close `note_on` | Must **not** say "open command issued" or "grip-open sensors should switch ON" |
| Nip entries | `note_on` must **!=** `note_off` |
| KM handshake (`degater=0`) | `note_on` must **!=** `note_off` |

### Exit codes

- `0` — PASS, 0 errors
- `1` — FAIL, error list printed

## Workflow Rule

**Always run the validator before committing changes to `io_alarm_pairs.json`.**

```
Edit JSON  →  Run validator  →  Fix any FAIL  →  Commit
```

## Adding New Rules

If a new mechanical direction pair is added (e.g. "Clamp / Release"),
add a matching `check_*` function to `test_io_alarm_pairs.py` and call it
from both `main()` and `test_io_alarm_pairs()`.

## Historical Context

- **Date:** 2026-06-05
- **Bugs found:** 31 total (6 Justify Retract, 6 Grip Close, 12 Nip, 7 KM)
- **Root cause:** Copy-paste entry creation without updating human-readable text
- **Fix method:** Corrected all 31 `note_on` / `note_off` strings; no tag names,
  addresses, or timeout values were changed.
