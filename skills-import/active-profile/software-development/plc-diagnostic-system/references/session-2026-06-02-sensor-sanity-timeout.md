# Session Notes: Sensor Sanity Independent Timeout (June 2, 2026)

## Problem

The original Sensor Sanity check shared the same `timeout_sec` (default 1.0 second) with I/O Reaction. This was problematic because:

1. **I/O Reaction** needs fast detection (1 sec) — commanded motion should produce sensor response quickly.
2. **Sensor Sanity** validates persistent faults at rest — but during a real cylinder transition, the magnet passes between reed switches and both sensors briefly read FALSE for ~2-3 seconds.

With the shared timeout, Sensor Sanity would false-alarm during every normal cylinder transition: the solenoid commands motion, sensors briefly go through a dead zone, Sensor Sanity sees both FALSE for 1 second, and fires an alarm even though the cylinder is moving normally.

## Solution: Independent Timeouts

Sensor Sanity now has its own timeout parameter, distinct from I/O Reaction:

| Parameter | Default | Rationale |
|---|---|---|
| `timeout_sec` | 1.0 | I/O Reaction: fast detection of commanded-motion failures |
| `sensor_sanity_timeout_sec` | 4.0 | Sensor Sanity: longer than a normal mechanical transition, short enough to catch unplugged sensors within a few seconds |

A typical mechanical transition takes ~2 seconds (air pressure + piston travel + magnet passing reed switches). The 4-second window is:
- **Longer** than any normal transition → no false alarms
- **Short enough** to catch an unplugged sensor within a few seconds of failure

## Code Change

```python
class IOAlarmWatcher:
    def __init__(self, json_path=None, timeout_sec=1.0,
                 sensor_sanity_timeout_sec=4.0):
        self._timeout_sec = timeout_sec
        self._sensor_sanity_timeout_sec = sensor_sanity_timeout_sec
```

In `_sensor_sanity_check()`:
```python
if elapsed >= self._sensor_sanity_timeout_sec:  # was self._timeout_sec
    # fire alarm
```

## Verification

With 4-second timeout:
- Normal cylinder transition (both sensors briefly FALSE for ~2-3 seconds): ❌ **No false alarm**
- Unplugged sensor at rest (both sensors FALSE for 60+ seconds): ✅ **Alarm fires after 4 seconds**

## When to Adjust

| Scenario | Adjust To | Why |
|---|---|---|
| Very slow cylinders (low air pressure) | 5-6 seconds | More margin for transition |
| Fast pneumatics, quick-reacting sensors | 3 seconds | Faster unplug detection |
| Unusually long reed-switch dead zones | 5+ seconds | Physical characteristic of sensor arrangement |
