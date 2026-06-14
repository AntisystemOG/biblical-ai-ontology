# Session: Tag Case-Consistency Errors & Hardcoded Version (June 2, 2026)

## Problem
Two distinct bugs appeared after a build that included catalog typo fixes:

1. **Polling error flood:** `D3_Low_Justify_Ret_Sol: no response` — repeated every ~6 seconds, up to #920 in alarm log.
2. **About dialog showed stale version:** `Version 1.05` from May 2026, while window title showed `2.23.2`.

## Root Cause #1: Physical Mapping Not Synced with Catalog

When `io_catalog.py` was fixed (`D3_Low_justify_Ret_Sol` → `D3_Low_Justify_Ret_Sol`), `physical_mapping.py` was NOT updated. Same for `D3_low_Nip_Open_Sol` → `D3_Low_Nip_Open_Sol`.

The driver builds its tag list from `io_catalog.py`, then looks up physical addresses in `physical_mapping.py`. When the mapping key doesn't exist (old case typo), pycomm3 falls back to the logical tag name, gets "no response" for every poll, and floods the alarm log.

**Fix pattern:** Any tag rename must touch **all three** files atomically in a single commit:
- `io_catalog.py` — canonical list (`KNOWN_IO_TAGS`)
- `physical_mapping.py` — `PHYSICAL_ADDRESS_MAP`
- `io_alarm_pairs.json` — pair definitions (if tag appears there)

## Root Cause #2: OUTPUT Read Errors Logged as Alarms

Micro870 DO_ (digital output) addresses are write-only. Reading them always returns "no response." The `_PollWorker` was logging these as `first_error` for every output on every cycle.

**Fix:** In `main_window.py`, skip error-logging for OUTPUT tags:

```python
if direction == "OUTPUT":
    io_values[logical_name] = self._last_known_values.get(...)
    # Do NOT log as first_error — DO_ read failure is normal plumbing
else:
    io_values[logical_name] = False
    if not first_error:
        first_error = f"{logical_name}: {err}"
```

## Root Cause #3: Hardcoded Version in About Dialog

`main_window.py` line 1481 contained:
```python
"<p><b>Version 1.05</b></p>"
```

This was the original string from May 2026. It never used `__version__` from `plc_tools.version`. The window title (`v2.23.2`) was dynamic; the About dialog was not.

**Fix:** Import `__version__` at call site and use f-string:
```python
from plc_tools.version import __version__
QMessageBox.about(self, "About...", f"<p><b>Version {__version__}</b></p>...")
```

## Additional Typo Found During Fix

While running the new consistency script, a second hardcoded typo was caught:
- `D1__Low_Grip_Close_Sol` (double underscore) in catalog, physical mapping, AND alarm pairs.

This existed before the session and would have caused similar issues had it been referenced by newer code.

## Pre-Build Validation Script

Created `scripts/verify_tag_consistency.py` (also saved as skill `plc-tag-case-consistency-guard`):

Checks:
1. Catalog ↔ Physical mapping bidirectional match
2. Catalog ↔ Alarm pairs JSON bidirectional match  
3. Extra underscore typos (`__` in tag names)

Exits 1 on mismatch → blocks build. Exits 0 on clean → safe to build.

Run before every PyInstaller build:
```bash
python scripts/verify_tag_consistency.py
```

## Key Takeaway

Tag names are case-sensitive dict keys. A single character case difference between catalog and mapping creates a silent read failure that spams the alarm log. Always run the consistency script before building.

Version strings in UI must always use the dynamic `__version__`. Any hardcoded version in dialogs, splash screens, or window titles will drift and confuse users.
