# Session — Standalone Simulated PLC Server (Timeline Replay + Fault Injection)

Date: June 4, 2026
Trigger: User requested a simulated PLC that replays recorded DEG3 timeline data and intermittently produces faults.

## Architecture

Two independent processes replace the older in-process `generate_sim_recordings.py` approach:

```
Standalone TCP Server (simulated_plc_server.py)
├── Loads real timeline JSON (608 snapshots, 127 tags)
├── Loops snapshots at configurable speed (1.0x → 20x)
├── Serves read_tag / read_tags / write_tag / info / mode / programs / faults / tag_list
├── Three-layer read precedence:
│   1. _write_overrides (manual GUI writes)
│   2. _compute_fault_overrides() (active fault overrides)
│   3. _timeline snapshot values
├── Fault injection via CLI or raw TCP JSON
│   └── 17 pre-defined faults (DEG1, DEG2, DEG3 variants)
├── Auto-fault mode: random injection every 15–60s, duration 3–12s
└── TCP JSON-line protocol on port 27007

GUI (unchanged)
├── SimulatorDriver (new driver, hooks into existing connection_manager.py)
│   ├── _PLCShim exposes .read(*tags) and .info
│   ├── Drives poll worker, diagnostics tab, I/O status without code changes
│   └── Pycomm3-compatible return shapes (bool/int/float, no pycomm3 dep)
└── Connect dialog has "Simulated DEG Server" option (PLCType.SIMULATED)
```

## Why a Standalone TCP Server Instead of In-Process

| Concern | In-Process (MockDriver) | Standalone TCP Server |
|---|---|---|
| Qt threading safety | Conflicts with QTimer + pycomm3 | Fully separate Python process |
| Replay real data | Requires timeline embed | Loads timeline JSON natively |
| Fault injection timing | Hard to control from GUI | Independent timer, inject via CLI |
| Manual write testing | Shared memory complexity | Network protocol keeps write overrides |
| pycomm3 state coupling | Leaks mock state into real paths | Zero mutation to Micro800Driver / LogixDriver / MockDriver |

## TCP Protocol (JSON Lines)

Every request/response is one JSON object terminated by newline on the same TCP connection.

### Commands

| Command | Args | Response |
|---|---|---|
| `read_tag` | `tag` | `{tag, value, error}` |
| `read_tags` | `tags: [str]` | `{values: {tag: val, ...}, errors: [str]}` |
| `write_tag` | `tag`, `value` | `{ok: true}` or `{ok: false, error}` |
| `info` | none | Controller info dict |
| `mode` | none | `{mode: "Run"}` |
| `programs` | none | `{programs: [...]}` |
| `faults` | none | `{faults: [...]}` |
| `tag_list` | none | `{tags: [str]}` |
| `inject_fault` | `name`, `duration` (sec) | `{ok: true/false}` |
| `clear_faults` | none | `{ok: true}` |

### Example Session over `nc 127.0.0.1 27007`

```
{"cmd": "read_tag", "tag": "DEG3_Lower_Ext_Sol"}
{"tag": "DEG3_Lower_Ext_Sol", "value": true}
{"cmd": "inject_fault", "name": "DEG3_stuck_lower_ext", "duration": 5.0}
{"ok": true}
{"cmd": "read_tag", "tag": "D3_Low_Ext_Cyl_1_Ext"}
{"tag": "D3_Low_Ext_Cyl_1_Ext", "value": false}   ← fault active, sensor overridden
{"cmd": "clear_faults"}
{"ok": true}
{"cmd": "read_tag", "tag": "D3_Low_Ext_Cyl_1_Ext"}
{"tag": "D3_Low_Ext_Cyl_1_Ext", "value": true}    ← back to timeline
```

## Write-Aware Fault Trigger Logic

When a fault spec has a `trigger_tag`, the server evaluates `trigger_tag`'s **effective value** (snapshot overridden by any manual writes) before activating the fault override.

Key snippet:
```python
# In _compute_fault_overrides()
effective = {**snapshot_values, **self._write_overrides}
if not effective.get(trigger_tag, False):
    continue  # trigger condition not met, skip this fault
```

**Why this matters:** If the user forces `DEG3_Lower_Ext_Sol = True` in the tool, the corresponding stuck-sensor fault correctly fires even though the timeline snapshot may have it as `False` at that moment.

## `_PLCShim` for Zero-GUI-Change Compatibility

The existing `_PollWorker` and diagnostics tab expect `drv._plc.read(*tags)` and `drv._plc.info` exactly as pycomm3's `LogixDriver` provides them. Rather than refactor the GUI, the `SimulatorDriver` wraps a `_PLCShim`:

```python
class _PLCShim:
    def __init__(self, driver):
        self._driver = driver

    def read(self, *tags):
        ret = []
        for t in tags:
            v = self._driver.read_tag(t)
            ret.append(_TagResponseShim(tag=t, value=v))
        return ret

    @property
    def info(self):
        return self._driver.get_controller_info()
```

This is returned as `drv._plc` so the GUI never knows it's talking to a simulator.

## Auto-Fault Mode

```
> fault auto on
```

- Random fault selected uniformly from `FAULT_SPECS`
- Random injection interval: 15–60 seconds
- Random duration: 3–12 seconds (or fault-default if no random)
- Can be combined with playback loop (no degradation)
- Enter command again to turn off

## How to Run

```bash
# In project directory (WSL)
python3 simulated_plc_server.py --timeline deg_timeline_20260525_224802.json --speed 5.0

# Or let it auto-discover timeline in project root
python3 simulated_plc_server.py

# On Windows
start_simulated_plc.bat 5.0
```

Then in the PLC Tool: **File → Connect → Simulated DEG Server → IP `127.0.0.1`**

## Fault Catalog (17 faults)

| Name | DEG | Affected Sensors | Trigger Tag |
|---|---|---|---|
| `DEG3_stuck_lower_ext` | 3 | D3_Low_Ext_Cyl_1/2_Ext | `DEG3_Lower_Ext_Sol` |
| `DEG3_stuck_lower_ext2` | 3 | D3_Low_Ext_Cyl_2_Ext | `DEG3_Lower_Ext_Sol` |
| `DEG3_stuck_upper_ext` | 3 | D3_Up_Ext_Cyl_1/2_Ext | `DEG3_Upper_Ext_Sol` |
| `DEG3_slow_grip` | 3 | D3_Low_Grip_Open_1/2 | `DEG3_Low_Grip_Close_Sol` |
| `DEG3_sensor_unplugged` | 3 | Ext + Ret sensors FALSE | `DEG3_Lower_Ext_Sol` |
| `DEG3_opposing_solenoids` | 3 | Dual solenoids both ON | `DEG3_Lower_Ext_Sol` |
| `DEG3_justify_stuck` | 3 | All justify cyls not showing | `DEG3_Up_Justify_Ext_Sol` |
| `DEG3_nip_close_fail` | 3 | Nip stays closed | `DEG3_Nip_Close_Sol` |
| `DEG1_stuck_lower_ext1` | 1 | D1_Low_Ext_Cyl_1/2_Ext | `DEG1_Lower_Ext_Sol` |
| `DEG2_stuck_lower_ext1` | 2 | D2_Low_Ext_Cyl_1/2_Ext | `DEG2_Lower_Ext_Sol` |

Additional DEG1/DEG2 variants for all fault types are defined for future timelines.

## Session Outcomes

- `simulated_plc_server.py` — 580 lines, standalone
- `src/plc_tools/communication/simulator_driver.py` — 270 lines, zero GUI changes
- `models.py` — added `PLCType.SIMULATED`
- `connection_manager.py` — added `SimulatorDriver` routing
- `connect_dialog.py` — added combo entry for Simulated DEG Server
- `deg_timeline_20260525_224802.json` — copied timeline (3.2 MB)
- `start_simulated_plc.bat` — Windows starter script
- All existing real-driver code paths unmodified (Micro800Driver, LogixDriver, MockDriver unchanged except routing)

## Pitfalls Discovered

1. **Evaluating fault triggers against unmerged state** — If `trigger_tag` is read from timeline snapshot without checking `_write_overrides`, manual GUI writes won't activate faults. Always merge `_write_overrides` before trigger evaluation.
2. **`_PLCShim` missing `.info` property** — The diagnostics tab accesses `drv._plc.info` directly; a method named `info()` instead of a property breaks it. Expose as `@property`.
3. **pycomm3 return shapes differ** — pycomm3 `read()` returns an object with `.tag` and `.value` attributes, not a raw dict. Match that shape in the shim.
4. **Timeline loop boundary** — After last snapshot, reset to index 0 and continue. Don't hang or stop the replay.
5. **Speed >10x may skip snapshots** — The server ticks every 100ms; at 20x a 1-second snapshot is consumed in 50ms. The server steps per tick, so some snapshots are indexed but may not have reads issued against them. This is acceptable for alarm testing but not for faithful playback timing.
