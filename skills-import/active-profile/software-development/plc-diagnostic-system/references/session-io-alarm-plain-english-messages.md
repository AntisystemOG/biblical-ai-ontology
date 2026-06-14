# Session Note: Plain-English I/O Alarm Messages

**Date:** 2026-06-01  
**Skill parent:** `plc-diagnostic-system` (Section 3 — I/O Reaction Validation)  
**File modified:** `src/plc_tools/polling/io_alarm_watcher.py`  

## Goal

Rewrite `_build_alarm()` so alarm messages read like plain English instead of raw tag dumps.

### Example transformation

**Before:**
```
[DEG2] Lower Extend: output DEG2_Lower_Ext_Sol active but expected input(s) are not ON (within 1.0s): _IO_X1_DI_21. Lower degating cylinder is commanded to extend...
```

**After:**
```
DEG2 Lower Extend turned ON, but the expected input 'D2_Low_Ext_Cyl_1_Ext' did not turn on.
  → Lower degating cylinder is commanded to extend...
```

## Changes Made

### 1. `_PendingCheck` dataclass — added `output_value: bool`

Both instantiation sites updated:
- `__process_transition_detection()` — passes `out_val`
- `_continuous_snapshot()` — passes `out_val`

### 2. `_build_alarm()` — new logic

```python
deg_str = "SYS" if check.degater == 0 else f"DEG{check.degater}"
action = "stayed ON" if continuous else ("turned ON" if check.output_value else "turned OFF")
msg = f"{deg_str} {check.function} {action}, but {missing_phrase}."
```

### 3. Filter blank / empty input tags from display list

```python
missing_display = [t.strip("_") for t in missing if t and t.strip()]
```

Prevents messages like:
```
...but the expected input '' did not turn on.
```

### 4. Handle single vs. multiple missing inputs

```python
if len(missing_display) == 1:
    missing_phrase = f"the expected input '{missing_display[0]}' did not turn on"
else:
    input_list = ", ".join("'" + t + "'" for t in missing_display)
    missing_phrase = f"the expected inputs {input_list} did not turn on"
```

### 5. Append `note_on` / `note_off` with leading arrow

```python
if note:
    msg += f"\n  → {note}"
```

## Pitfall: Backslashes in f-strings

This **does NOT work** under CPython f-string parsing rules:

```python
# SyntaxError: f-string expression part cannot include a backslash
input_list = ", ".join(f"'{t}'" for t in missing_display)
```

**Fix:** Build the string outside the f-string expression or use concatenation:

```python
input_list = ", ".join("'" + t + "'" for t in missing_display)
```

## Verification

```bash
python3 -m py_compile src/plc_tools/polling/io_alarm_watcher.py
```

Must report `Syntax OK`.

## Constraints Preserved

- `fault_key` logic unchanged (`_composite_key` for transition, `output_tag|CONTINUOUS` for continuous)
- Deduplication (`_active_faults`, `_acked_faults`) untouched
- Grace-period logic in `_continuous_check()` untouched
- Autonomous behavior — no new human steps required at runtime
