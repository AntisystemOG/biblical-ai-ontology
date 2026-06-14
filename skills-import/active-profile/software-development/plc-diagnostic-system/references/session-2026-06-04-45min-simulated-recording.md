# 45-Minute Simulated Recording Generator — Session 2026-06-04

## Purpose

Generate deterministic `.json` timeline recordings for testing playback features (skip buttons, alarm markers, speed control) without requiring a physical PLC. The recording is 45 minutes of wall-clock time with 3 fault windows.

## Polling rate trade-off

| Polling | Snapshots | JSON Size | Notes |
|---|---|---|---|
| 100 ms | 27,000 | ~38 MB | Heavy, unmanageable file |
| **500 ms** (chosen) | **5,400** | **~38 MB** | Matches live PLC granularity; step timing scaled accordingly |

During testing, 500ms polling at 45 min produced **0 fault snapshots** with the original short window (24 snaps = 12s). Root cause: 500ms step durations (7 snaps each) meant an 80-snap fault window (40s) was needed to overlap a single relevant step.

| Fault window | Wall-clock duration | Shots |
|---|---|---|
| stuck_sensor_lower_ext | 80 snaps | 40 sec |
| slow_cylinder_ret | 80 snaps | 40 sec |
| grip_failed | 80 snaps | 40 sec |

After widening, **10 fault snapshots** were produced across 5,400 total — enough to verify alarm arrows on the timeline.

## Key implementation details

### DegaterCycle class

- 10 steps with 500ms snap durations: Home/Idle (7), Extend Lower (7), Grip Lower (7), Cut/Hold (8), Retract Lower (7), Extend Upper (7), Grip Upper (7), Cut Upper/Hold (8), Retract Upper (7), Home Complete (7)
- Total cycle: 72 snaps = 36 seconds

### Fault injection timing

- Faults scheduled by absolute snapshot index (wall-clock mapped)
- `inject_fault()` sets a flag + `fault_active_until_snap`
- `is_faulted()` checks flag + duration
- `generate_values()` reads current fault state and applies sensor falsification
- `make_alarm_events()` reads current fault state and emits `alarm_events` entries

### Step advancement order (critical)

Advance **before** generating the snapshot. If alarm generation runs after step advance but before snapshot, alarms are for the PREVIOUS step. The correct order is:

```python
for i in range(num_snaps):
    for deg, sim in simulators.items():
        if sim.snaps_in_step >= sim.STEP_DURATIONS[sim.step]:
            sim.advance(i)   # advance first
        vals = sim.generate_values()
        events = sim.make_alarm_events(i, vals)   # eval against CURRENT step
```

### Alarm message format

Matches `IOAlarmWatcher._build_alarm()` pattern for seamless playback compatibility:

```json
{
  "severity": "FAULT",
  "source": "DEG1_Lower_Extend",
  "message": "D1_Lower_Ext_Sol=ON but sensor D1_Low_Ext_Cyl_1_Ext stuck FALSE",
  "fault_key": "DEG1_stuck_1234"
}
```

## Script

`generate_45min_test.py` — standalone, not shipped in `.exe`
- Generates `dist/sim_45min_test.json`
- Also writes `.json.gz` for compression testing

## Usage

```bash
python generate_45min_test.py
# Or on Windows:
C:/path/to/python.exe generate_45min_test.py
```

Output file can be loaded via **Playback & Record → Load Recording** in the app.

## Anti-patterns

| Anti-Pattern | Why Wrong | Fix |
|---|---|---|
| 100ms polling for 45 min | 27K snapshots, ~38 MB JSON, slow to load | 500ms polling, 5.4K snapshots, same info |
| Short fault windows (24 snaps) | Step duration changed but window didn't scale | Scale proportionally: 80 snaps for 500ms steps |
| Step advance inside value generation | Alarms evaluate against wrong step | Advance before `generate_values()`, events after |

## File

`generate_45min_test.py` (project root, not in `src/`)

## Build

Not included in `.exe` — a development/testing tool only.
