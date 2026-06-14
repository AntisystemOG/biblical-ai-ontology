# Session Note: Double-Alarm Fix + Degater Filtering Removal
_Session: 2026-06-01 | Degater PLC Tool BST33 and 35_

## Problem 1: Duplicate Alarms for Stuck Sensors

**Observation:** A sensor that stays OFF indefinitely produced two alarms:
- `T+4.0s`: `[DEG2] Upper Retract: ... within 4.0s` (transition check)
- `T+8.0s`: `[DEG2] Upper Retract: ... continuous check` (continuous check)

**Root cause:** `_evaluate_pending()` fired the transition alarm but only added the transition composite key to `_acked_faults`. The continuous check's separate composite key (ending in `|CONTINUOUS`) was never blocked, so it fired `timeout_sec` later.

**Fix in `io_alarm_watcher.py`:** After transition alarm fires, compute the continuous composite key and add it to `_acked_faults`:
```python
inputs_hash = ",".join(check.expected_inputs)
continuous_key = f"{check.output_tag}|{check.expected_state}|{inputs_hash}|CONTINUOUS"
self._acked_faults.add(continuous_key)
```

**Verification test:**
```python
# Run watcher with timeout_sec=4.0 for 15 simulated seconds
# Stuck sensor state (output ON, both sensors OFF)
# Expected: exactly 1 alarm at T+4.0s, 0 continuous alarms
# Result: PASS (transition_count=1, continuous_count=0)
```

---

## Problem 2: Degater Filtering Hid Real Failures

**Observation:** `_active_degaters` filtering in `check()` skipped outputs from "unselected" degaters. When KM selected DEG2, DEG1/DEG3 sensors could fail silently.

**User requirement:** Ladder logic checks ALL three degaters for the home signal. A failure on any degater is a real fault regardless of which one the robot is currently using.

**Fix:** Removed the 6-line filter block from `check()`:
```python
# REMOVED:
deg = pair.get('degater', 0)
deg_str = 'SYS' if deg == 0 else f'DEG{deg}'
if deg_str not in self._active_degaters:
    continue
```

**Verification test:**
```python
# Force _active_degaters = {"SYS"}
# Provide DEG1 output ON with missing sensors
# Expected: DEG1 alarm fires despite not being "selected"
# Result: PASS
```

**Policy change:** `_active_degaters` and `_auto_detect_degaters` remain in the class (Diagnostics UI shows detected degater for operator awareness), but they no longer gate alarm checks.

---

## Configuration at End of Session

| Parameter | Value | Rationale |
|---|---|---|
| Poll rate | **100 ms** | Two devices on Ethernet-IP network; captures pneumatic sensor transitions |
| Default poll rate UI | **100 ms** (top of combo) | User explicitly wants fastest possible |
| Timeout | **4.0 sec** (user-adjustable) | Cylinder settle time for user's machine |
| Grace periods | `timeout_sec` after state change AND after transition alarm | Prevents continuous from firing during normal motion |
| Degater monitoring | **ALL** (DEG1, DEG2, DEG3, SYS) | Ladder logic checks all three for home signal |

---

## EXE Build Status

`dist/Degater PLCTool BST33 and 35.exe` rebuilt ~03:00 CDT June 1, 2026 (~46 MB).
