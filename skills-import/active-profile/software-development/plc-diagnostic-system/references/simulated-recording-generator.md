# Simulated Recording Generator for Offline Playback Testing

**Session:** 2026-06-02 | **Project:** Degater PLC Tool BST33/35

## Purpose

Generate deterministic `.json` timeline recordings that simulate realistic DEG1/2/3 degating cycles with configurable faults. No PLC or plant-floor access required. Load directly into the Playback Review window for UI/alarm testing, debugging, and operator training.

## Why This Pattern Exists

The user explicitly requested simulated recordings to validate playback behavior without leaving his desk. This pattern became a permanent part of the project after v2.23.13.

## Architecture

```
generate_sim_recordings.py          (standalone script, not shipped in .exe)
├── DegaterSimulator                (state machine per degater)
│   ├── step cycle: Home → Extend → Grip → Cut → Retract → … (10 Hz)
│   ├── _inject_fault()             (override sensor values mid-step)
│   └── make_alarm_events()         (generate AlarmEvent dicts per snapshot)
└── generate_recording()            (merge N degaters, produce JSON)
```

### Step Advancement Order (Critical)

**Step advancement MUST happen BEFORE make_alarm_events().** The alarm event builder checks the current step name from `self.steps[self.step]`. If the step advances inside `_snapshot_tag_values()`, the alarm builder sees the new step and skips the fault.

```python
for i in range(num_snaps):
    for deg, sim in simulators.items():
        # 1. Advance step BEFORE generating snapshot
        if sim.snaps_in_step >= sim.steps[sim.step][1]:
            sim.step = (sim.step + 1) % len(sim.steps)
            sim.snaps_in_step = 0
            sim.step_start_snap = i

        # 2. Generate snapshot at CURRENT step
        vals = sim._snapshot_tag_values(i)

        # 3. Generate alarms for CURRENT step
        events = sim.make_alarm_events(i, vals)
```

**Bug caused by wrong order:** If step advancement happens inside `_snapshot_tag_values()`, `make_alarm_events()` sees the next step and produces zero alarms.

### Fault Types Implemented

| Fault | Description | Alarm | Where to Look in Playback |
|---|---|---|---|
| `stuck_sensor_lower_ext` | Cylinder extends but sensor stays FALSE | FAULT — transition timeout | DEG1 tab → Lower section → sensor stays ⚪ |
| `slow_cylinder_ret` | Retract takes ~2.5s instead of 0.5s | FAULT — transition timeout | DEG1 tab → Lower section → delayed 🟢 |
| `grip_failed` | Grip solenoid ON but sensors stay FALSE | FAULT — transition timeout | DEG1 tab → Grip section |
| `sensor_unplugged` | Both Ext and Ret sensors FALSE simultaneously (impossible) | ERROR — sensor sanity | DEG1 tab → both sensors ⚪ at rest |
| `opposing_solenoid_both_on` | Both extend and retract solenoids ON | FAULT — bad wiring | DEG1 tab → both solenoids 🔴 |

### Scenario Definitions

```python
SCENARIOS = {
    "01_Normal_Cycle": {"fault": None, "duration_sec": 45, "seed": 42},
    "02_Stuck_Sensor_Lower_Ext": {"fault": "stuck_sensor_lower_ext", "duration_sec": 60, "seed": 10},
    "03_Slow_Cylinder_Retract": {"fault": "slow_cylinder_ret", "duration_sec": 60, "seed": 20},
    "04_Grip_Failure": {"fault": "grip_failed", "duration_sec": 60, "seed": 30},
    "05_Sensor_Unplugged": {"fault": "sensor_unplugged", "duration_sec": 50, "seed": 40},
    "06_Opposing_Solenoids_Both_On": {"fault": "opposing_solenoid_both_on", "duration_sec": 40, "seed": 50},
    "07_Mixed_Deg1_Faulty_Deg2_Normal": {"fault": "stuck_sensor_lower_ext", "duration_sec": 60, "seed": 60, "degaters": [1, 2]},
    "08_Multiple_Rapid_Alarms": {"fault": "slow_cylinder_ret", "duration_sec": 45, "seed": 70, "degaters": [1]},
}
```

### JSON Format Compatibility

Outputs exactly the `TimelineRecording` JSON format:
- `project_name`, `start_time`, `end_time`
- `snapshots[].timestamp` — ISO format
- `snapshots[].values` — all 206 boolean tags
- `snapshots[].fault_detected` — True if alarm_events present
- `snapshots[].alarm_events` — list of dicts with `severity`, `source`, `message`, `fault_key`
- `fault_snapshots` — indices of snapshots with alarms (for red markers on slider)

### Generator Script Location

`generate_sim_recordings.py` — lives in project root, NOT in `src/` (not shipped in .exe). Generates to `dist/sim_*.json`.

## Usage

```bash
# Generate all 8 scenarios
python3 generate_sim_recordings.py

# Load results in the app
# Playback & Record → 📂 Load Recording → select dist/sim_02_stuck_sensor_lower_ext.json
# Click ▶ Playback Recording → review window opens
```

## Adding New Scenarios

1. Add new fault type to `_inject_fault()` and `make_alarm_events()`
2. Add entry to `SCENARIOS` dict with unique seed
3. Run `python3 generate_sim_recordings.py`
4. Verify with `jq '.snapshots[] | select(.alarm_events | length > 0) | .alarm_events[0]' dist/sim_XX.json | head -5`

## Reproducibility

All random state is seeded. Same seed → identical recording. Use different seeds per scenario to get unique timing variations.
