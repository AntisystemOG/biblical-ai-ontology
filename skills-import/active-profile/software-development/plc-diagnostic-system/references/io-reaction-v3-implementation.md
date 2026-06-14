# I/O Reaction Alarm Watcher v3 — Implementation Notes

Full annotated implementation of `IOAlarmWatcher` v3 with unified grace periods, per-degater filtering, direction-aware fail-safe reads, and runtime timeout adjustment.

> **Session context:** June 2026, Degater PLC Tool BST33 and 35. False alarms during normal cylinder motion (18 `[Continuous]` + 20 `[Transition]` in 10 min). User increased timeout to 4.0s but continuous checks fired instantly with zero grace.

---

## Problem Statement

The Degater PLC Tool monitors solenoid outputs (extend, retract, open, close) and expects input sensors to react within a configurable timeout. The v1 watcher had:

- **Transition check:** fire alarm if expected inputs aren't ON within `timeout_sec` after output changes
- **Continuous check:** fire alarm immediately if expected inputs aren't ON while output remains ON

**The bug:** One cylinder motion produced two alarms. Transition checks respected the timeout (4.0s), but continuous checks fired at the next poll cycle (200ms later) because sensors hadn't moved yet.

---

## Root Causes

| # | Cause | Evidence from alarm_log CSV |
|---|---|---|
| 1 | Continuous check had **zero grace period** | `10:05:25.434 [Continuous]` fires 200ms after output ON |
| 2 | Transition & continuous checks **didn't coordinate** | Same output, same cycle, two distinct alarms |
| 3 | DEG1 alarms fired even though DEG1 not wired | DEG1 outputs controlled by ladder, sensors absent |
| 4 | Disabling DEG1 in UI didn't purge watcher state | `_pending` and `_acked_faults` retained DEG1 entries |

---

## v3 Solution Design

### Grace Rules

1. **Output-changed grace:** `_continuous_check()` returns empty `alarms` if `(now - state.changed_at) < timeout_sec`
2. **Transition-alarm-fires grace:** Also returns empty if `(now - _transition_fired[phys_out]) < timeout_sec`
3. **Degater skip:** `check()` skips pairs whose degater is not in `_active_degaters`

### State Machine Changes

Added fields to `IOAlarmWatcher`:

- `_transition_fired: dict[str, datetime]` — when a transition alarm (Phase 2) last fired per output
- `_active_degaters: set[str]` — enabled zones; default all four
- `_output_states: dict[str, _OutputState]` — replaces raw bool, adds `changed_at` timestamp

### When Transition Alarm Fires (Phase 2)

```python
def _evaluate_pending_check(self, phys_out, check, io_values, now):
    missing = [t for t in check.expected_on if not io_values.get(t, False)]
    if missing:
        alarm = self._build_alarm(..., continuous=False)
        self._transition_fired[phys_out] = now   # ← NEW: record transition alarm time
        return [alarm]
    # else: all sensors OK before deadline, no alarm
    return []
```

### When Continuous Check Runs (Phase 3)

```python
def _continuous_check(self, pair, io_values, now):
    out_val = io_values.get(pair.output_physical, False)
    if not out_val:
        return []

    state = self._output_states.get(pair.output_physical)
    if state and (now - state.changed_at) < timedelta(seconds=self._timeout_sec):
        return []

    last_alarm = self._transition_fired.get(pair.output_physical)
    if last_alarm and (now - last_alarm) < timedelta(seconds=self._timeout_sec):
        return []

    # ... run actual continuous validation
```

### Runtime Timeout Adjustment

```python
def set_timeout_sec(self, value: float) -> None:
    old = self._timeout_sec
    self._timeout_sec = value
    delta = value - old
    for check in self._pending.values():
        check.deadline += timedelta(seconds=delta)
    # Also update transition_fired timestamps? No — they represent "when alarm fired",
    # not "when to expire." Grace uses (now - fired_at) < timeout, so changing
    # timeout naturally extends the suppression window next cycle.
```

### Per-Degater Filtering

```python
def set_active_degaters(self, active: list[str]) -> None:
    new_set = set(active)
    disabled = self._active_degaters - new_set
    self._active_degaters = new_set

    for phys_out, check in list(self._pending.items()):
        pair = self._find_pair_by_output(phys_out)
        if pair and pair.degater in disabled:
            del self._pending[phys_out]
            key = f"{phys_out}|{self._state_str(check)}"
            self._acked_faults[key] = datetime.now()

    for phys_out in list(self._transition_fired.keys()):
        pair = self._find_pair_by_output(phys_out)
        if pair and pair.degater in disabled:
            del self._transition_fired[phys_out]
```

**Why ack the fault?** So if the user re-enables DEG1 later, the output that was transitioning when disabled won't alarm spuriously on the first polling cycle after re-enable.

---

## Auto-Degater Detection from KM Robot Inputs (v3.1)

Instead of manual checkboxes, the watcher reads **KM robot selection inputs** from the PLC to determine which degater is active.

### KM Selection Input Convention

| PLC Input | Tag | Meaning |
|---|---|---|
| `_IO_EM_DI_00` | `KM_Selected_DEG1_Or_3` | TRUE = odd degater (DEG1 or DEG3) active |
| `_IO_EM_DI_01` | `KM_Selected_DEG2_Or_3` | TRUE = even-or-DEG3 (DEG2 or DEG3) active |

### Decoding Logic

| DI_00 | DI_01 | Active Degater |
|---|---|---|
| TRUE | FALSE | **DEG1** (odd only) |
| FALSE | TRUE | **DEG2** (even only) |
| TRUE | TRUE | **DEG3** (both) |
| FALSE | FALSE | **None** (only SYS monitored) |

```python
def _detect_active_degaters(self, io_values: dict[str, Any]) -> list[str]:
    sel_1_or_3 = io_values.get("_IO_EM_DI_00", False)
    sel_2_or_3 = io_values.get("_IO_EM_DI_01", False)

    if sel_1_or_3 and not sel_2_or_3:
        return ["DEG1", "SYS"]
    elif not sel_1_or_3 and sel_2_or_3:
        return ["DEG2", "SYS"]
    elif sel_1_or_3 and sel_2_or_3:
        return ["DEG3", "SYS"]
    else:
        return ["SYS"]
```

### Automatic Detection in `check()`

```python
def check(self, io_values: dict[str, Any], now: datetime | None = None) -> list[AlarmEvent]:
    # Auto-detect every poll cycle
    if self._auto_detect_degaters:
        active = self._detect_active_degaters(io_values)
        self.set_active_degaters(active)

    # Normal three-phase check continues...
```

### Why This Is Better Than Manual Checkboxes

The PLC ladder may command outputs for **all** degaters simultaneously (pre-staging, or a ladder bug), but only the KM-selected degater is physically wired and intended to operate. Auto-detection ensures the watcher:
- Ignores DEG1 outputs when the KM selects DEG2
- Never requires manual UI intervention
- Updates automatically every poll cycle as the KM robot changes stations
- Still allows manual override via `set_active_degaters()` for bench testing

### UI: Replace Checkboxes with Status Label

```python
# diagnostics.py
self._deg_status_lbl = QLabel("KM-detected degater: — (waiting for PLC poll)")
```

Shows the currently active degater(s) in real time. Green text when active, gray when none selected.

### Integration in MainWindow

```python
# After every alarm check:
self._tab_diag.update_degater_status(
    sorted(self._io_alarm_watcher._active_degaters)
)
```

---

## Diagnostics Tab Wiring

### Timeout Control

```python
# diagnostics.py, inside DiagnosticsTab._build_ui()
to_layout = QHBoxLayout()
to_layout.addWidget(QLabel("I/O Timeout:"))
self._alarm_timeout_input = QLineEdit("1.0")
self._alarm_timeout_input.setFixedWidth(60)
to_layout.addWidget(self._alarm_timeout_input)

self._alarm_timeout_btn = QPushButton("Accept")
self._alarm_timeout_btn.setFixedSize(80, 28)
# Force inline stylesheet — theme classes invisible in QFormLayout
self._alarm_timeout_btn.setStyleSheet(
    "QPushButton { background-color: #22c55e; color: #ffffff; font-weight: 700; "
    "font-size: 13px; border: 2px solid #16a34a; border-radius: 6px; padding: 2px 10px; }"
    "QPushButton:hover { background-color: #16a34a; }"
    "QPushButton:pressed { background-color: #15803d; }"
")
self._alarm_timeout_btn.clicked.connect(self._on_accept_timeout)
to_layout.addWidget(self._alarm_timeout_btn)
to_layout.addStretch()

settings_layout.addRow(to_layout)
```

```python
def _on_accept_timeout(self):
    try:
        timeout = float(self._alarm_timeout_input.text().strip() or "1.0")
    except ValueError:
        timeout = 1.0
    self.alarm_timeout_changed.emit(max(timeout, 0.1))
```

### Degater Checkboxes (Deprecated — Replaced by Auto Detection in v3.1)

```python
# DEPRECATED: Manual checkboxes replaced by KM auto-detection status label
# Kept for reference only — do not use in new projects
self._degater_checks = {}
for name in ["DEG1", "DEG2", "DEG3", "SYS"]:
    cb = QCheckBox(name)
    cb.setChecked(True)
    cb.stateChanged.connect(self._on_degaters_changed)
    deg_layout.addWidget(cb)
    self._degater_checks[name] = cb
```

### MainWindow connections

```python
def _on_alarm_timeout_changed(self, timeout_sec: float) -> None:
    self._io_alarm_watcher.set_timeout_sec(timeout_sec)
    self.statusBar().showMessage(f"Alarm timeout set to {timeout_sec}s", 3000)

def _on_degaters_changed(self, active_degaters: list[str]) -> None:
    self._io_alarm_watcher.set_active_degaters(active_degaters)
```

---

## Direction-Aware Fail-Safe Reads (Poll Worker)

The `_PollWorker.poll()` method was previously caching last-known values for **all** tags on read failure. For sensors, this hid unplug failures.

### Fixed Logic

```python
# Build direction map once from catalog
tag_dir = {
    t: (drv._io_tags.get(t, {}).get("direction", "STATUS")
        if hasattr(drv, "_io_tags") and drv._io_tags else "STATUS")
    for t in catalog_tags
}

for logical_name, res in zip(catalog_tags, raw):
    if res and not res.error:
        io_values[logical_name] = res.value
        self._last_known_values[logical_name] = res.value
    else:
        direction = tag_dir.get(logical_name, "STATUS")
        if direction == "OUTPUT":
            io_values[logical_name] = self._last_known_values.get(logical_name, False)
        else:
            io_values[logical_name] = False   # INPUT or STATUS: fail-safe

# Total failure path
except Exception:
    for t in catalog_tags:
        direction = tag_dir.get(t, "STATUS")
        if direction == "OUTPUT":
            io_values[t] = self._last_known_values.get(t, False)
        else:
            io_values[t] = False
```

**Catalog entry example:**

```python
KNOWN_IO_TAGS = {
    "DEG1_Feed_Ret_Sol": {
        "physical": "_IO_X3_DO_00",
        "comment": "DEG1 Lower Retract Solenoid",
        "direction": "OUTPUT",
    },
    "DEG1_Low_Extend_Sensor1": {
        "physical": "_IO_X1_DI_01",
        "comment": "Lower Extend Sensor 1",
        "direction": "INPUT",
    },
}```

---

## File Locations (Degater Project)

| File | Role |
|---|---|
| `src/plc_tools/polling/io_alarm_watcher.py` | Core `IOAlarmWatcher` class |
| `src/plc_tools/gui/tabs/diagnostics.py` | Timeout UI + KM status label |
| `src/plc_tools/gui/main_window.py` | Signal wiring, poll error throttling, status update |
| `src/plc_tools/gui/alarms_log.py` | Double-click detail dialog, dedup reset |
| `src/plc_tools/catalog/io_alarm_pairs.json` | 55 alarm pairs (output→input mapping) |
| `src/plc_tools/polling/poller.py` | `_PollWorker` with direction-aware reads |

---

## Commit History (v3 Changes)

| Commit | Description |
|---|---|
| `e19316e` | Continuous I/O alarm validation + configurable timeout on Diagnostics tab |
| `4c34aee` | Bundled `io_alarm_pairs.json` in EXE + reset dedup on reconnect |
| `2c90754` | Suppressed poll alarm until 4 consecutive failures |
| `7eb9f7a` | Suppressed false alarms + added degater filtering |
| `f459210` | Automatic degater detection from KM robot selection inputs |

---

## Test Script (WSL, No PLC)

```python
import json
from datetime import datetime, timedelta
from plc_tools.polling.io_alarm_watcher import IOAlarmWatcher

watcher = IOAlarmWatcher(timeout_sec=1.0)
now = datetime.now()

# Test 1: Grace period suppresses continuous
values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": False, "_IO_X1_DI_02": False}
alarms = watcher.check(values, now)
assert len(alarms) == 0, f"Expected 0, got {len(alarms)}"

# Test 2: After grace expires, continuous fires
alarms = watcher.check(values, now + timedelta(seconds=1.5))
assert len(alarms) == 1, f"Expected 1, got {len(alarms)}"
assert "continuous" in alarms[0].message.lower()

# Test 3: Degater filter
watcher.set_active_degaters(["DEG2", "DEG3", "SYS"])
# Re-create a DEG1 transition + pending check, then verify skipped

# Test 4: Auto-detection
values = {"_IO_EM_DI_00": True, "_IO_EM_DI_01": False}
assert watcher._detect_active_degaters(values) == ["DEG1", "SYS"]

values = {"_IO_EM_DI_00": False, "_IO_EM_DI_01": True}
assert watcher._detect_active_degaters(values) == ["DEG2", "SYS"]

values = {"_IO_EM_DI_00": True, "_IO_EM_DI_01": True}
assert watcher._detect_active_degaters(values) == ["DEG3", "SYS"]

values = {"_IO_EM_DI_00": False, "_IO_EM_DI_01": False}
assert watcher._detect_active_degaters(values) == ["SYS"]

print("All tests pass")
```
