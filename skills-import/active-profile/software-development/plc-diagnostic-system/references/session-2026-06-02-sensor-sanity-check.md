# Session Notes: Sensor Sanity Check (June 2, 2026)

## Problem

The I/O Reaction watcher has a **blind spot at rest**: when both solenoids are OFF, the cylinder is "at rest" and no transition or continuous check runs. This means a **broken or unplugged sensor goes completely undetected** — neither the Extend nor Retract side is commanded, so nothing evaluates the sensors.

Real example from production timeline:
- Snapshots 10-23: D2_Low_Ext_Cyl_1_Ext = False, D2_Low_Ext_Cyl_1_Ret = False
- **Both solenoids OFF** → no I/O Reaction check runs
- Zero alarms fired. Sensor was physically unplugged.

## Solution: Sensor Sanity (Separate from I/O Reaction)

A new check phase runs after all pair-level checks. It validates a physical invariant that should always hold, regardless of commanded state:

> **For a single cylinder in a dual-solenoid assembly, both position sensors (Ext and Ret) should NEVER be FALSE simultaneously.**

A healthy sensor is always ON at one position or the other. If both are OFF for more than the timeout (default 1 sec), at least one sensor is unplugged or broken.

## What Sensor Sanity Checks

| Condition | Sensor Sanity Alarm? |
|---|---|
| One sensor TRUE, cylinder at rest | ❌ OK — known position |
| Both sensors FALSE for > timeout, at rest | ✅ **ALARM** — unplugged/broken |
| Any solenoid ON | ❌ **Skipped** — I/O Reaction handles this |
| Sensors recover (one goes TRUE) | ✅ Auto-clears, can re-fire |

## Why Separate from I/O Reaction

Keep the two systems orthogonal so they don't fight:

| System | Validates | When |
|---|---|---|
| **I/O Reaction** | Commanded motion → sensor response | During commanded motion (solenoid ON) |
| **Sensor Sanity** | Physical sensor integrity (both never FALSE) | When assembly is at rest (both solenoids OFF) |

## Per-Cylinder Granularity (Critical)

Degater Lower and Upper assemblies each contain **2 cylinders** (Cyl_1 and Cyl_2). Sensor Sanity must check each independently:

```
DEG2 Lower has:
  Extend pair: on_inputs = [D2_Low_Ext_Cyl_1_Ext, D2_Low_Ext_Cyl_2_Ext]
  Retract pair: on_inputs = [D2_Low_Ext_Cyl_1_Ret, D2_Low_Ext_Cyl_2_Ret]
```

Matching is done by extracting the cylinder number from the tag name:
- `D2_Low_Ext_Cyl_1_Ext` — cylinder number = `1` (comes after literal "Cyl")
- `D2_Low_Ext_Cyl_1_Ret` — cylinder number = `1`

If Cyl_1 Ext AND Ret are both FALSE → alarm for Cyl_1. Cyl_2 being OK doesn't mask it.

**Extraction code (tag naming convention dependent):**
```python
parts = tag.split("_")
for i, p in enumerate(parts):
    if p == "Cyl" and i + 1 < len(parts) and parts[i + 1].isdigit():
        cyl_num = parts[i + 1]  # "1" for "D2_Low_Ext_Cyl_1_Ext"
```

## State Machine

```
Per cylinder: (key = "DEG{deg}_{cyl}_Cyl{num}")

  Assembly moving?
    (Ext_SOL=True OR Ret_SOL=True)
       |    → Clear timer, SKIP check
       |
       |    Assembly at rest
       v    (both solenoids OFF)
    ┌──────────────────────────┐
    | Read Ext sensor → ext_val|
    | Read Ret sensor → ret_val|
    |                          |
    | ext_val=True OR ret_val=True?
    |    |    → Clear timer, OK
    |    |
    |    |    Both FALSE
    └──> |    (potential fault)
         |    Start / continue timer
         |
         |    Elapsed >= timeout_sec?
         |        │    → Fire alarm ONCE (dedup)
         |        │    → Add to _sensor_sanity_fired
         |        │    → Keep timer running (for elapsed display)
         |
         Sensors recover?
              → Pop timer, DISCARD fired key
              → Can re-fire if failure happens again
```

## Deduplication Strategy (Different from I/O Reaction)

I/O Reaction uses a composite key with `fired_at` timestamp to allow re-arming:
```python
f"{check.output_tag}|{check.expected_state}|{inputs_hash}|{ts}"
```

Sensor Sanity uses a **stable key without timestamp** to fire **once per fault**:
```python
fired_key = f"SANITY|{cyl_key}"  # e.g. "SANITY|DEG2_Lower_Cyl1"
```

This key is kept in `_sensor_sanity_fired` until the sensors recover, at which point it is DISCARDED via `discard()`. This allows re-firing a new alarm if the same sensor breaks again later.

## Clear on Disconnect

Both `_sensor_sanity_timers` and `_sensor_sanity_fired` must be cleared in the `clear()` method:
```python
def clear(self):
    self._output_states.clear()
    self._pending.clear()
    self._acked_faults.clear()
    self._sensor_sanity_timers.clear()
    self._sensor_sanity_fired.clear()
```

## User Request: Every-Poll Recording

The user explicitly rejected subsampled recording (which saved 1 snapshot per second). They want **every poll saved** in timeline JSON. In the poll handler:

```python
if self._timeline_recorder and self._timeline_recorder.is_recording:
    self._timeline_recorder.add_snapshot(io_values)
```

Disk usage at 100ms polling, 12 hours: ~6 GB worst case. The user accepts this tradeoff for forensic visibility.
