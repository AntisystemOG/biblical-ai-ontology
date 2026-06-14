# Session 2026-06-01: Sensor Unplug Test — No Alarm with Both Solenoids OFF

## Scenario

Production test: a sensor was physically disconnected from the degater. Both the Extend and Retract solenoids were OFF (cylinder at rest). The user observed the I/O Reaction watcher for over a minute and **no alarm fired**.

## Expected? Yes — After the Dual-Solenoid Fix

Tonight's fix removed `off_inputs` from all dual-solenoid entries (Lower/Upper Extend + Retract) to stop false alarms:

```
Extend solenoid turns OFF → immediately checks Retract sensors → FALSE ALARM
(because Retract solenoid hasn't turned ON yet)
```

With `off_inputs` removed, the watcher only checks sensors **when the solenoid is ON**. When the cylinder is at rest (both solenoids OFF), nothing is being monitored.

## The Fundamental Limitation

A disconnected Extend sensor while the cylinder is **retracted** is **indistinguishable** from a properly working sensor:

| Condition | Extend Sensor | Retract Sensor | Watcher sees... |
|---|---|---|---|
| Working sensor (retracted) | FALSE | TRUE | Cylinder home — normal |
| Disconnected sensor | FALSE | TRUE | Cylinder home — **same** |
| Both false (impossible) | FALSE | FALSE | **Wiring fault** |

With no output command and no `off_inputs` to check, the watcher sees "retracted, normal" and moves on.

## What the Alarm Watchers CAN and CANNOT Catch

| Fault | Can Catch? | Mechanism |
|---|---|---|
| Sensor stuck mid-motion | ✅ | Transition check ON → sensors don't move within timeout |
| Sensor unplugged during motion | ✅ | Transition check sees FALSE where TRUE expected |
| Sensor unplugged at rest | ❌ | Both solenoids OFF, no transition check running |
| Both sensors false simultaneously | ✅ | Impossible state — needs separate "sensor sanity" check |
| Sensor stuck opposite position | ✅ | Transition fails on next commanded move |

## Lesson: Sensor-at-Rest Monitoring Needs a Different Architecture

If the user wants to catch sensors that are **permanently dead even when not moving**, that's a **separate feature** — not an I/O Reaction alarm.

### "Sensor Sanity" Check (Not Implemented)

```python
# Runs every poll regardless of solenoid state
for each dual-sensor cylinder:
    if Extend_Sensor == FALSE and Retract_Sensor == FALSE:
        alarm: (
            "BOTH sensors false for {function} — this is an impossible state.\n"
            "Indicates disconnected wiring, failed 24V supply, or both sensors dead."
        )
```

This catches:
- Sensor disconnected at rest (both FALSE)
- Both sensors failed simultaneously
- 24V supply lost to sensor bank

## User Workflow Note

The user runs **production validation tests by physically unplugging sensors** on the actual machine. This is the most reliable test method. Software-side simulation cannot replicate real-world noise, bounce, and mechanical timing.

When testing, **clear `_acked_faults`** (disconnect/reconnect) to reset the deduplication state, otherwise alarms won't refire after being acknowledged.

## Code State at This Session

- `io_alarm_pairs.json`: 12 dual-solenoid entries with empty `off_inputs`
- `io_alarm_watcher.py`: no degater filtering, transition/continuous dedup
- TimelineRecorder: subsampled 10:1 (100ms poll → 1-second saves)
- Poll rate: 100 ms default
- Timeout: 4.0 seconds
- 2 uncommitted files in working tree: `io_status.py`, `io_alarm_watcher.py`
