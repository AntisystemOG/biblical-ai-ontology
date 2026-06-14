# Dual-Solenoid Guard — Complete Fix Reference

## Session
- **Date:** 2026-06-01
- **Problem:** Sensor unplugged at rest produced NO alarm (false negative)
- **Root Cause:** Previous session removed `off_inputs` from JSON to fix false alarms. Removing `off_inputs` broke ALL off-side monitoring.
- **Correct Fix:** Restore `off_inputs` in JSON, add Python guards in `io_alarm_watcher.py` to prevent false alarms from timing issues.

## The Core Problem: False vs Real Alarms

### Why `off_inputs` Are Needed

When Extend solenoid turns OFF, if Retract solenoid is ON, the cylinder is actively commanded to retract. The system must verify the cylinder actually arrived by checking Retract sensors.

Without `off_inputs`, there is NO verification that the cylinder reached its destination.

### Why `off_inputs` Caused False Alarms

When Extend turns OFF, the PLC takes time to command Retract ON (~50-200ms). During that brief window, BOTH solenoids are OFF.

Naive check: Extend_OFF → immediately check Retract sensors → FALSE → ALARM.

The Retract sensors are FALSE because Retract hasn't been commanded yet, not because anything is broken.

## The Fix: Two Python Guards (NOT JSON removal)

### Guard 1: `_start_check()` — Transition Guard

When a solenoid turns OFF, only start an `off_inputs` check if the opposing solenoid is ON:

```python
if not out_val and io_values is not None:
    opp = self._opposing_solenoid(pair)
    if opp:
        opp_val = self._resolve(io_values, opp["output_physical"], ...)
        if opp_val is None or not opp_val:
            # Opposing solenoid is OFF — cylinder is at rest, not moving.
            # Do NOT start an off_inputs check → skip entirely
            return
```

**Effect:** When Extend turns OFF at the end of a cycle, Retract solenoid is also OFF (cylinder at rest). Guard 1 skips the off_inputs check. No false alarm.

**Effect:** When Extend turns OFF because Retract is being commanded (during motion), Retract solenoid is ON. Guard 1 allows the off_inputs check. Real faults are caught.

### Guard 2: `_continuous_check()` — Continuous Only on `on_inputs`

When a solenoid is OFF, continuous check only validates `on_inputs` (empty for OFF):

```python
if not out_val:
    # Continuous check only validates on_inputs (solenoid ON).
    # off_inputs describe the DESTINATION after a transition.
    # The transition check already verified arrival.
    expected_phys = []
    expected_log = []
```

**Effect:** While Extend solenoid is OFF (after a transition), continuous check does nothing. No false alarms.

**Effect:** When Retract solenoid is ON (cylinder should be retracting), continuous check monitors Retract sensors. If a sensor drops out mid-motion → alarm.

## State Machine Summary

| State | Ext Sol | Ret Sol | Transition Check | Continuous Check |
|---|---|---|---|---|---|
| **Transitioning Ext→Ret** | OFF | ON | off_inputs verify (Extend's off_inputs check Ret sensors) | Retract `on_inputs` monitored |
| **Transitioning Ret→Ext** | ON | OFF | off_inputs verify (Retract's off_inputs check Ext sensors) | Extend `on_inputs` monitored |
| **At rest** | OFF | OFF | SKIPPED by Guard 1 | SKIPPED (Guard 2: no `on_inputs`) |
| **Sensor failure during motion** | ON | OFF | `on_inputs` fire alarm within timeout | `on_inputs` fire immediately |
| **Sensor unplugged at rest** | OFF | OFF | SKIPPED — not commanded → not monitored | SKIPPED — not monitored |

## What the PDF Documented

The table in the PDF showed the "opposite" sensors as the `off_inputs` for each entry. This cross-reference is correct and was RESTORED via commit `6718077`.

Example for DEG2 Lower Extend:
- **on_inputs:** D2_Low_Ext_Cyl_1_Ext, D2_Low_Ext_Cyl_2_Ext
- **off_inputs:** D2_Low_Ext_Cyl_1_Ret, D2_Low_Ext_Cyl_2_Ret

## Plain-English Messages Added

`_build_alarm()` now says:
- "DEG2 Lower Extend **turned ON**, but the expected input 'D2_Low_Ext_Cyl_1_Ext' did not turn on."
- "DEG2 Lower Extend **stayed ON**, but the expected input 'D2_Low_Ext_Cyl_1_Ext' did not turn on."
- "DEG2 Lower Extend **turned OFF**, but the expected input 'D2_Low_Ext_Cyl_1_Ret' did not turn on."

Required `_PendingCheck` field: `output_value: bool`

## Testing Command (No PLC Required)

```python
from plc_tools.polling.io_alarm_watcher import IOAlarmWatcher
import datetime
json_path = "src/plc_tools/catalog/io_alarm_pairs.json"
w = IOAlarmWatcher(json_path=json_path, timeout_sec=1.0)

# Simulate: Extend turns ON, one sensor never responds
io = {
    "DEG2_Lower_Ext_Sol": True,
    "DEG2_Lower_Ret_Sol": False,
    "D2_Low_Ext_Cyl_1_Ext": False,  # stuck
    "D2_Low_Ext_Cyl_2_Ext": True,
    "D2_Low_Ext_Cyl_1_Ret": False,
    "D2_Low_Ext_Cyl_2_Ret": False,
}
alarms = w.check(io, datetime.datetime.now())
print(f"Alarms: {len(alarms)}")
for a in alarms:
    print(f"  {a.severity}: {a.message}")
```

## Files Modified

| File | Change |
|---|---|
| `src/plc_tools/polling/io_alarm_watcher.py` | Added `_opposing_solenoid()`, dual-solenoid guards in `_start_check()` and `_continuous_check()`, `output_value` field on `_PendingCheck`, plain-English `_build_alarm()` |
| `src/plc_tools/catalog/io_alarm_pairs.json` | Restored `off_inputs` + `off_inputs_physical` for all 12 dual-solenoid entries (DEG1/2/3 × Lower/Upper × Extend/Retract) |

## Commits
- `6718077` — fix: dual-solenoid I/O alarm false alarm suppression

## Limitations (Still True)

- **Sensor unplugged while cylinder is at rest → NOT detected.** Both solenoids are OFF, no `on_inputs` to check. Need a separate "Sensor Sanity" check (both Ext AND Ret FALSE simultaneously) regardless of solenoid state.
- **Rapid cycling faster than timeout → alarms suppressed.** If cycle completes before timeout expires, transition check sees the new state and cancels the pending check.
