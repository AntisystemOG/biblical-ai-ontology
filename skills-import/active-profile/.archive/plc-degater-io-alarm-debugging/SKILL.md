---
name: plc-degater-io-alarm-debugging
description: |
  Critical debugging and false-alarm suppression patterns for the Degater PLC Tool's I/O alarm watcher.
  Covers dual-solenoid logic pitfalls, alarm deduplication, polling rate vs recording rate, and the complete workflow for diagnosing I/O Reaction alarms on the Allen-Bradley Micro870 system.

triggers:
  - When I/O Reaction alarms fire unexpectedly or alternate text between Ext/Ret sensors
  - When alarm log shows both "within Xs" and "continuous check" for the same fault
  - When degater monitoring needs to be verified for all three stations
  - When timeline file sizes need to be managed during long recordings
  - When false alarms happen at solenoid turn-off moments
---

# PLC Degater I/O Alarm Debugging — Critical Patterns

## 1. Dual-Solenoid Cylinder Pitfall (MOST COMMON FALSE ALARM)

**Problem**: The degater uses separate Extend and Retract solenoids. The alarm table had `off_inputs` defined for every solenoid. When a solenoid turns OFF, the watcher immediately checks for the opposite-position sensors — but the opposing solenoid hasn't turned ON yet, so those sensors are FALSE.

**False alarm cycle** (every degating cycle produces 2 false alarms):
```
T+0.0s  Ext_Sol=ON   → check Ext sensors → passes
T+0.5s  Ext_Sol=OFF  → check Ret sensors → FAILS (Ret solenoid not ON yet) ← FALSE ALARM
T+1.0s  Ret_Sol=ON   → check Ret sensors → passes
T+1.5s  Ret_Sol=OFF  → check Ext sensors → FAILS (cylinder still retracting) ← FALSE ALARM
```

**Fix**: Remove `off_inputs` from ALL dual-solenoid entries. Only monitor sensors when the solenoid is ON.

Affected entries in `io_alarm_pairs.json` (12 total):
- DEG1/DEG2/DEG3: Lower Extend, Lower Retract, Upper Extend, Upper Retract

```json
// BEFORE (wrong)
"off_inputs": ["D2_Low_Ext_Cyl_1_Ret", "D2_Low_Ext_Cyl_2_Ret"]

// AFTER (correct)
"off_inputs": [],
"off_inputs_physical": [],
"note_off": "Lower Extend solenoid OFF. Cylinder position not monitored in this state."
```

> **Rule**: Single-solenoid cylinders (justify, grip) keep their off_inputs. Dual-solenoid cylinders remove off_inputs entirely.

---

## 2. Transition vs Continuous Alarm Deduplication

**Problem**: A sensor is permanently stuck. The transition check fires an alarm after timeout. Then 4 seconds later, the continuous check fires AGAIN for the same fault.

**Fix**: When a transition alarm fires, ALSO add the continuous composite key to `_acked_faults`:

```python
# In _evaluate_pending(), when timeout is reached:
if composite not in self._acked_faults:
    self._acked_faults.add(composite)
    alarms.append(self._build_alarm(check, missing))
    self._transition_fired[check.output_tag] = now
    # NEW: prevent continuous from double-firing
    inputs_hash = ",".join(check.expected_inputs)
    continuous_key = f"{check.output_tag}|{check.expected_state}|{inputs_hash}|CONTINUOUS"
    self._acked_faults.add(continuous_key)
```

---

## 3. Grace Period Suppression (After State Change AND After Transition Alarm)

**Problem**: Continuous check fires while the cylinder is still in motion.

**Two suppression layers**:
1. `timeout_sec` after output state change (gives cylinder time to move)
2. `timeout_sec` after transition alarm fires (prevents immediate re-check)

```python
tf = self._transition_fired.get(phys_out)
if tf:
    elapsed = (now - tf).total_seconds()
    if elapsed < self._timeout_sec:
        return alarms  # suppressed
```

---

## 4. No Degater Filtering — Monitor ALL Outputs

**Problem**: Auto-detecting the active degater from KM inputs and only monitoring that one. But the ladder logic looks at ALL three degaters for the home signal.

**Fix**: Remove the degater filter from the `check()` loop:

```python
# REMOVED:
# if deg_str not in self._active_degaters:
#     continue
```

The `_active_degaters` field is now display-only (shown in Diagnostics). All 48 pairs run every poll.

---

## 5. Polling Rate vs Recording Rate (Option A: Decouple)

**Problem**: 100 ms polling × 127 tags × 12 hours = ~1.5 GB JSON file.

**Fix**: Poll at 100 ms for real-time UI + alarm watcher, but record only every Nth snapshot.

| Poll Rate | Record Interval | File Size (12 hr) |
|---|---|---|
| 100 ms | 1 (every poll) | ~1.5 GB |
| 100 ms | 10 (every 1 sec) | ~150 MB ← recommended |
| 250 ms | 4 (every 1 sec) | ~150 MB |

Implementation:
```python
# In TimelineRecorder.__init__:
self._record_interval: int = 1
self._record_tick: int = 0

def set_record_interval(self, interval: int) -> None:
    self._record_interval = max(1, int(interval))
    self._record_tick = 0

# In record_snapshot():
self._record_tick += 1
if self._record_tick < self._record_interval:
    return None  # skip this snapshot
self._record_tick = 0
```

**Auto-compute from poll rate**:
```python
poll_ms = self._poll_timer.interval()
interval = max(1, int(1000 / poll_ms))  # always target ~1 second wall time
self._timeline_recorder.set_record_interval(interval)
```

---

## 6. Complete Diagnostic Workflow

When user reports "alarms keep firing" or "text keeps changing":

1. **Get the alarm CSV** → read messages, severity, timestamps
2. **Get the timeline JSON** → extract snapshots around alarm time
3. **Trace the output + sensor values** during the alarm window
4. **Check for these patterns**:
   - Does alarm text alternate between Ext and Ret sensors? → dual-solenoid off_inputs
   - Does alarm fire immediately when output turns OFF? → dual-solenoid off_inputs
   - Are there duplicate transition + continuous alarms? → missing dedup key
   - Does alarm fire during sensor transition? → increase timeout or polling rate
   - Are false alarms from unselected degaters? → check degater filtering

5. **Look at the JSON** in `io_alarm_pairs.json` specifically for:
   - `off_inputs` arrays on dual-solenoid entries → should be empty
   - `on_inputs` vs what the alarm message says → must match
   - Physical tag addresses vs logical tag names → must both resolve

6. **Verify with script** — simulate the exact timeline transitions using Python to confirm the fix before rebuilding EXE.

---

## Key Files

| File | Role |
|---|---|
| `src/plc_tools/polling/io_alarm_watcher.py` | Alarm engine: transition + continuous checks |
| `src/plc_tools/catalog/io_alarm_pairs.json` | 48 I/O pairs: output → expected inputs per degater |
| `src/plc_tools/gui/main_window.py` | Poll timer, record trigger, alarm wiring |
| `src/plc_tools/recording/timeline_recorder.py` | Snapshot save with subsampling |
| `src/plc_tools/catalog/io_catalog.py` | 127 known I/O tags with direction metadata |

---

## Testing Command (Python simulation)

Always simulate before rebuilding:

```python
from plc_tools.polling.io_alarm_watcher import IOAlarmWatcher
w = IOAlarmWatcher(json_path="src/plc_tools/catalog/io_alarm_pairs.json", timeout_sec=4.0)

# Simulate exact cycle from timeline
io_vals = {
    "DEG2_Lower_Ext_Sol": True,
    "D2_Low_Ext_Cyl_1_Ext": False,  # transitioning
    "D2_Low_Ext_Cyl_2_Ext": False,
}
alarms = w.check(io_vals)
print(alarms)
```
