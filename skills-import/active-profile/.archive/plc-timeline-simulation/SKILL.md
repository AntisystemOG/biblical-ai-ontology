---
name: plc-timeline-simulation
description: >-
  Generate deterministic simulated PLC timeline recordings for playback review
  testing without hardware. Includes state-machine I/O cycle simulation and
  configurable fault injection that produces alarm events in the exact format the
  IOAlarmWatcher emits.
triggers:
  - simulate PLC recording
  - generate test fixture
  - playback review testing
  - deterministic I/O simulation
  - simulate alarm event
keywords:
  - timeline recording
  - simulated recording
  - test fixture
  - playback test
  - alarm simulation
  - state machine
  - fault injection
---

# PLC Timeline Recording Simulation

Produce deterministic `.json` timeline recordings that the Degater PLC Tool's
Playback Review window can load directly. Useful for testing playback features,
alarm visualizations, and UI layouts without a live PLC or trip to the plant.

## Table of Contents

1. [When to Use](#when-to-use)
2. [Architecture](#architecture)
3. [Usage](#usage)
4. [Scenario Catalog](#scenario-catalog)
5. [Extending the Simulator](#extending-the-simulator)
6. [Pitfalls](#pitfalls)
7. [References](#references)

## When to Use

| Situation | Use simulator? |
|---|---|
| Testing playback review layout / new columns | ✅ Yes |
| Verifying alarm marker visualization | ✅ Yes |
| Reproducing a customer-reported bug | ✅ Yes — reproduce exact sequence |
| Regression testing UI after code changes | ✅ Yes |
| Validating real-time alarm logic | ❌ No — use hardware + `io_alarm_watcher.py` |

## Architecture

```
DegaterSimulator
├── _define_steps()          # Cycle: Home → Extend Lower → Grip → Cut →
│                             #      Retract → Extend Upper → Grip → Cut →
│                             #      Retract → Home
├── _snapshot_tag_values()  # Execute current step, write TRUE tags
├── _inject_fault()         # Override normal I/O per fault type
└── make_alarm_events()     # Emit alarm_events list with FAULT/ERROR severity
                    ^
                    |
TimelineRecording (snapshots per 100 ms)
```

**Key design:** step advancement happens **outside** `_snapshot_tag_values()` so
`make_alarm_events()` sees the correct step context.

**Fault types supported:**
- `stuck_sensor_lower_ext` — sensor never goes ON after solenoid command
- `slow_cylinder_ret` — cylinder takes >2 s instead of ~0.5 s
- `sensor_unplugged` — both Ext and Ret sensors FALSE simultaneously
- `grip_failed` — grip OPEN sensors stay FALSE after solenoid command
- `opposing_solenoid_both_on` — both extend and retract solenoids TRUE

## Usage

Copy `scripts/generate_sim_recordings.py` into the project root (or run directly
from skill). Edit `SCENARIOS` dict, then:

```bash
python generate_sim_recordings.py
```

Outputs `dist/sim_*.json` files. Load them in the PLC Tool via:
1. **Playback & Record** tab → **📂 Load Recording**
2. Select a `sim_*.json`
3. Click **▶ Playback Recording**

## Scenario Catalog

| ID | File | Fault | Alarm Snapshots | Visual Target |
|---|---|---|---|---|
| 01 | `sim_01_normal_cycle.json` | None | 0 | Baseline clean cycle |
| 02 | `sim_02_stuck_sensor_lower_ext.json` | Stuck sensor | 36 | DEG1 Lower Extend |
| 03 | `sim_03_slow_cylinder_retract.json` | Slow retract | 32 | DEG1 Lower Retract |
| 04 | `sim_04_grip_failure.json` | Grip failure | 26 | DEG1 Lower Grip |
| 05 | `sim_05_sensor_unplugged.json` | Unplugged | 40 | Sensor Sanity (ERROR) |
| 06 | `sim_06_opposing_solenoids_both_on.json` | Bad wiring | 12 | Both solenoids |
| 07 | `sim_07_mixed_deg1_faulty_deg2_normal.json` | Stuck sensor (DEG1 only) | 36 | DEG1 fault, DEG2 clean |
| 08 | `sim_08_multiple_rapid_alarms.json` | Slow retract | 16 | Quick succession |

## Extending the Simulator

1. Add new `fault` entry in `_inject_fault()`
2. Add matching `make_alarm_events()` block with correct `step_name` and relative-snap window
3. Add scenario to `SCENARIOS` dict
4. Ensure step durations in `_define_steps()` are long enough for alarm windows to fit

## Pitfalls

| Pitfall | Why | Fix |
|---|---|---|
| Zero alarm snapshots generated | Step advance happens AFTER `make_alarm_events()` checks `self.step` | Move step advance before `_snapshot_tag_values()` call, update `step_start_snap` |
| Alarm window out of bounds | Step duration shorter than alarm-relative window | Increase step duration to ≥ 35 snapshots for 1.0 s timeout windows |
## Related Skills

- [`plc-io-reaction-monitoring`](skill:plc-io-reaction-monitoring) — I/O alarm watcher implementation patterns, including dual-solenoid guard and transition/continuous check design. Use that skill when *implementing* alarm logic; use this skill when *testing* it with simulated data.

## References

- `scripts/generate_sim_recordings.py` — Standalone script to regenerate all eight scenarios
- `references/fault_scenarios.md` — Detailed per-scenario explanation and expected visual output
- `references/recording_format.md` — TimelineRecording JSON schema and Snapshot field mapping
- `references/arrow_marker_painting.md` — PySide6 code for drawing downward-pointing alarm arrows on a QSlider groove
