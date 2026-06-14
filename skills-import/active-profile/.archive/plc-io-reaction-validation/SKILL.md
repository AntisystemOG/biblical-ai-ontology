---
name: plc-io-reaction-validation
description: "Industrial PLC output→input reaction validation: two-phase checker with grace periods, per-zone filtering, direction-aware fail-safe reads, and runtime timeout tuning."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [plc, micro800, pycomm3, pyside6, io-validation, alarm-watcher, industrial, fail-safe]
    related_skills: [micro800-mode-operation, plc-output-force-safety, pyinstaller-desktop-app]
---

# PLC I/O Reaction Validation

Real-time validation that verifies **PLC outputs produce expected input sensor reactions** within a timeout window. Covers the full v3 architecture including unified grace periods, per-zone (degater) filtering, direction-aware fail-safe reads, and runtime timeout adjustment.

> **Relationship to `micro800-mode-operation`:** That skill contains a v1 alarm-watcher reference (`io-reaction-alarm-watcher.md`) covering transition + continuous checks without grace periods. This skill is the authoritative v3 umbrella with grace suppression, zone filtering, and the lessons learned from eliminating false alarms in production.

---

## When to Use This Skill

- Your PLC app needs to detect **mechanical failures** (solenoid fires but cylinder doesn't move)
- You need **sensor disconnect detection** after motion completes
- You see **false alarms during normal operation** because continuous checks fire instantly while transition checks wait for a timeout
- You have **multiple machine zones** (e.g., DEG1, DEG2, DEG3, SYS) and need to disable unwired zones
- Your timeout must be **adjustable at runtime** from a diagnostics UI
- You need **fail-safe direction-aware reads** that treat INPUT failures differently from OUTPUT failures

> **User Constraint:** This user prefers **software-side fixes only** — no PLC ladder logic edits. All solutions (polling rates, filtering, timeouts, UI tuning) are implemented within the PC application. Never propose ladder logic changes.

---

## Architecture Overview

```
Poll cycle (every N sec via QTimer)
    │
    ▼
┌──────────────────────────────────────────────────┐
│  _PollWorker reads all I/O tags via pycomm3       │
└────────────────┬─────────────────────────────────┘
                 │ io_values dict {tag_name: bool}
                 ▼
┌──────────────────────────────────────────────────┐
│  MainWindow._on_poll_complete(io_values)        │
│  ├─> UI Panels update (every poll)             │
│  ├─> IOAlarmWatcher.check(io_values)           │
│  │   ├─ Phase 1: detect_output_transition()   │
│  │   ├─ Phase 2: evaluate_pending_deadlines() │
│  │   └─ Phase 3: continuous_validate() + grace  │
│  │       returns list[AlarmEvent]              │
│  ├─> TimelineRecorder.record_snapshot()       │
│  │   └─ saves every Nth snapshot (subsampled) │
│  └─> (optional) Diagnostics tab → live panel   │
└──────────────────────────────────────────────────┘
```

No extra threads. The watcher runs synchronously inside the existing poll handler.

> **Poll fast, record slow:** The poll loop serves two independent consumers — the alarm watcher (needs every poll) and the timeline recorder (only needs every Nth). Decoupling them is critical for long recordings. See `references/timeline-subsampling-for-recording.md`.

---

### The Double-Alarm Problem (Root Cause of False Alarms)

### v1 Behavior (Broken)

One cylinder motion produces **two alarms**:

| Time | Event | Check Type | Result |
|---|---|---|---|
| `T+0.000s` | Output turns ON | Transition check created | pending, deadline = `T+1.0s` |
| `T+0.200s` | Sensors haven't moved yet | **Continuous check** fires | **FALSE ALARM #1** |
| `T+1.000s` | Deadline expires | Transition check evaluates | **FALSE ALARM #2** |

The user sets timeout to 4.0 seconds in the UI. Transition check deadline becomes `T+4.0s`. But continuous check still fires at `T+0.2s` with **zero grace period**.

**PLC scan cycle insight:** The Micro870 commits I/O state changes at the **end of each scan cycle**. By the time pycomm3 reads values, the PLC has already allowed one full scan for internal settling. Grace periods **do not** need to account for scan-cycle jitter — they account for **mechanical settling time** (cylinders move 200-800ms *after* the solenoid bit turns on in the PLC scan).

**Consequence:** 18 of 38 alarms in a 10-minute log were `[Continuous]` — all false positives during normal cylinder motion.

### v3 Fix: Unified Grace Period

Three suppression rules applied in `_continuous_check()`:

1. **Output-recently-changed grace:** If `(now - state.changed_at) < timeout_sec`, suppress continuous check. The cylinders need the same grace period as transition checks.

2. **Transition-alarm-fires grace:** If a transition alarm fired for this output within `timeout_sec`, suppress continuous check. Transition owns the grace window.

3. **Per-zone enable/disable:** Skip pairs from disabled zones entirely. If DEG1 is unwired, no DEG1 alarms fire regardless of output state.

```python
# _continuous_check() — v3
now = datetime.now()
for pair in self._pairs:
    # Skip disabled zones
    if pair.degater not in self._active_degaters:
        continue

    out_val = io_values.get(pair.output_physical, False)
    if not out_val:
        continue

    # Grace rule 1: output changed recently
    changed_at = self._output_state[pair.output_physical].changed_at
    if (now - changed_at) < timedelta(seconds=self._timeout_sec):
        continue

    # Grace rule 2: transition alarm already fired recently
    transition_time = self._transition_fired.get(pair.output_physical)
    if transition_time and (now - transition_time) < timedelta(seconds=self._timeout_sec):
        continue

    # Now run continuous validation
    missing = [t for t in pair.on_inputs_physical if not io_values.get(t, False)]
    if missing:
        ...  # fire continuous alarm
```

| Time | Event | Check Type | v1 Result | v3 Result |
|---|---|---|---|---|
| `T+0.000s` | Output turns ON | Transition pending | pending | pending |
| `T+0.200s` | Sensors haven't moved | Continuous | **FALSE ALARM** | **suppressed** |
| `T+1.000s` | Timeout, sensors OK | Transition evaluates | — | no alarm |
| `T+3.5s` | Sensor cable vibrates loose | Continuous | — | **REAL ALARM** (valid continuous) |

---

## Core Implementation (`IOAlarmWatcher` v3)

### Data Structures

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    FAULT = "FAULT"

@dataclass
class AlarmEvent:
    severity: Severity
    source: str
    message: str
    fault_key: str

@dataclass
class _OutputState:
    is_on: bool
    changed_at: datetime = field(default_factory=datetime.now)

class IOAlarmWatcher:
    def __init__(self, timeout_sec: float = 1.0, pairs: list[dict] | None = None):
        self._timeout_sec: float = timeout_sec
        self._pairs: list[_AlarmPair] = self._load_pairs(pairs or [])
        self._output_states: dict[str, _OutputState] = {}   # current + changed_at
        self._pending: dict[str, _PendingCheck] = {}       # transition checks waiting
        self._acked_faults: dict[str, datetime] = {}        # fault_key → ack time
        self._transition_fired: dict[str, datetime] = {}      # output → last alarm time
        self._active_degaters: set[str] = {"DEG1", "DEG2", "DEG3", "SYS"}
```

### Three-Phase `check()`

```python
def check(self, io_values: dict[str, Any]) -> list[AlarmEvent]:
    now = datetime.now()
    alarms: list[AlarmEvent] = []

    # Phase 1: detect transitions, create pending checks
    for pair in self._pairs:
        if pair.degater not in self._active_degaters:
            continue
        alarms += self._detect_transition(pair, io_values, now)

    # Phase 2: evaluate pending deadlines
    for phys_out, check in list(self._pending.items()):
        if now > check.deadline:
            alarms += self._evaluate_pending_check(phys_out, check, io_values, now)

    # Phase 3: continuous validation with grace
    for pair in self._pairs:
        if pair.degater not in self._active_degaters:
            continue
        alarms += self._continuous_check(pair, io_values, now)

    return alarms
```

### Grace Logic in `_continuous_check()`

```python
def _continuous_check(self, pair, io_values, now):
    out_val = io_values.get(pair.output_physical, False)
    if not out_val:
        return []

    state = self._output_states.get(pair.output_physical)
    if state and (now - state.changed_at) < timedelta(seconds=self._timeout_sec):
        return []   # Grace Rule 1

    last_alarm = self._transition_fired.get(pair.output_physical)
    if last_alarm and (now - last_alarm) < timedelta(seconds=self._timeout_sec):
        return []   # Grace Rule 2

    missing = [t for t in pair.on_inputs_physical if not io_values.get(t, False)]
    if not missing:
        return []

    key = f"continuous|{pair.output_physical}|on"
    if key in self._acked_faults:
        return []

    return [self._build_alarm(pair, True, missing, continuous=True)]
```

#### Grace Rule 2b: Transition alarm suppresses continuous for the same fault

When the transition check deadline expires and fires an alarm, **also add the continuous composite key to `_acked_faults`**. Otherwise, the continuous check fires its own duplicate alarm `timeout_sec` later for the same persistent sensor fault.

```python
# In _evaluate_pending, when deadline has passed:
if composite not in self._acked_faults:
    self._acked_faults.add(composite)
    alarms.append(self._build_alarm(check, missing))
    # Record that transition handled this output
    self._transition_fired[check.output_tag] = now
    # ALSO suppress the continuous check for the same inputs+state
    inputs_hash = ",".join(check.expected_inputs)
    continuous_key = f"{check.output_tag}|{check.expected_state}|{inputs_hash}|CONTINUOUS"
    self._acked_faults.add(continuous_key)
```

Without this, a sensor unplugged for 10 seconds produces:
- `T+4s`: Transition alarm "did not respond within 4s" 
- `T+8s`: Continuous alarm "not ON (continuous check)" — **duplicate for the same root cause**

With the fix: only the transition alarm fires. Continuous stays silent until the sensor recovers, clearing `_acked_faults`, at which point a new fault can trigger again.

### Runtime Timeout Adjustment with In-Flight Updates

When the user changes timeout from `1.0s` to `4.0s`, existing pending checks must have their deadlines extended proportionally:

```python
def set_timeout_sec(self, value: float) -> None:
    """Change timeout and extend in-flight pending deadlines."""
    old = self._timeout_sec
    delta = value - old
    if abs(delta) < 0.05:
        return
    self._timeout_sec = value

    for check in self._pending.values():
        check.deadline += timedelta(seconds=delta)

    # Propagate to UI via signal (see Wiring section)
```

### Per-Zone (Degater) Filtering — DEPRECATED / REMOVED v2026-06-01

> **Session context:** A previously-applied filter skipped outputs from degaters not "selected" by KM robot inputs. This was removed because the user's ladder logic checks **all three degaters** for the home signal — a sensor failure on an unselected degater is still a real fault.

**Current policy:** All pairs in `io_alarm_pairs.json` are monitored unconditionally. `_active_degaters` and `_auto_detect_degaters` remain in the class (exposed to the Diagnostics UI for display/status purposes), but they no longer gate the alarm check.

### Historical API (Kept for UI display, not filtering)

```python
def set_active_degaters(self, degaters: list[str]) -> None:
    """Update the set but no longer gates alarm checks."""
    self._active_degaters = set(degaters)

def set_auto_detect_degaters(self, enabled: bool = True) -> None:
    self._auto_detect_degaters = enabled
```

### Why Filtering Was Removed

| Requirement | Filtered Behavior | Correct Behavior (Current) |
|---|---|---|
| Home signal requires ALL degaters home | DEG1 sensor failure hidden when DEG2 selected | DEG1 failure alarms regardless |
| Ladder logic commands all degaters | Unselected degaters' outputs fire → false alarms | All outputs monitored, all sensors validated |
| KM selects active degater | Only active station monitored | Selection used for UI display only |

**Rule:** If the PLC ladder commands outputs from all stations (e.g., homing sequence checking all limit switches), do NOT filter alarm pairs by KM selection. Filter only if unselected stations are physically absent AND their outputs are electrically isolated.

---

## Direction-Aware Fail-Safe Read Policy

A critical safety decision: **how to handle pycomm3 read failures** in the poll worker.

| Direction | Read Failure Behavior | Rationale |
|---|---|---|
| **INPUT** | Return `False` (fail-safe) | Sensor unplugged → should trigger alarm via continuous check |
| **OUTPUT** | Preserve last-known value | Prevents solenoid display from flickering during transient comm spikes |
| **STATUS** | Return `False` (fail-safe) | Status bits should always be readable; failure means fault |

Implementation in `_PollWorker`:

```python
for logical_name, res in zip(catalog_tags, raw):
    if res and not res.error:
        io_values[logical_name] = res.value
        self._last_known_values[logical_name] = res.value
    else:
        direction = self._tag_directions.get(logical_name, "STATUS")
        if direction == "OUTPUT":
            io_values[logical_name] = self._last_known_values.get(logical_name, False)
        else:
            io_values[logical_name] = False   # fail-safe for INPUT/STATUS
```

**Danger without this:** If a read error caches `True` for an unplugged sensor, the alarm watcher sees the sensor as still ON and never fires an alarm. Hides real failures.

---

## Poll Error Throttling

Single-poll glitches (e.g., switching to the Diagnostics tab) produce transient read failures. Don't alarm immediately.

```python
if io_read_success:
    self._poll_alarm_ticks = 0
    if self._poll_alarm_was_on:
        self._tab_alarms.log_event(..., "Read failure cleared")
        self._poll_alarm_was_on = False
else:
    self._poll_alarm_ticks += 1
    if self._poll_alarm_ticks >= 4 and self._poll_alarm_ticks == 4:
        self._tab_alarms.log_event(..., f"Read failure #{self._poll_alarm_ticks}...")
        self._poll_alarm_was_on = True
```

---

## Pre-Implementation Verification: Show the Mapping Table

Before implementing the background watcher, **display a visual table of all loaded output→input pairs** so the user can confirm correctness.

```python
class IOAssociationDialog(QDialog):
    def __init__(self, pairs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("I/O Alarm Association Table")
        self.resize(900, 500)

        self._table = QTableWidget(len(pairs), 5)
        self._table.setHorizontalHeaderLabels(
            ["Output", "Degater", "Action", "Expected ON Inputs", "Expected OFF Inputs"]
        )
        for i, pair in enumerate(pairs):
            self._table.setItem(i, 0, QTableWidgetItem(pair.output_physical))
            self._table.setItem(i, 1, QTableWidgetItem(pair.degater))
            self._table.setItem(i, 2, QTableWidgetItem(pair.function))
            self._table.setItem(i, 3, QTableWidgetItem(", ".join(pair.on_inputs_physical)))
            self._table.setItem(i, 4, QTableWidgetItem(", ".join(pair.off_inputs_physical)))

        layout = QVBoxLayout(self)
        layout.addWidget(self._table)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
```

**Workflow:**
1. Load `io_alarm_pairs.json` during startup
2. If `len(pairs) > 0`, show `IOAssociationDialog` with **OK / Cancel**
3. If user clicks **Cancel**, halt background implementation until they fix the catalog
4. Only proceed to watcher instantiation after user confirms

This catches:
- Missing/zero-padded tag mismatches (`_DI_1` vs `_DI_01`)
- Wrong degater associations (e.g., DEG2 pair pointing to DEG1 inputs)
- Outputs with empty `on_inputs_physical` (indicates incomplete catalog)
- Disconnected pairs that should be wired

---

## Wiring: Diagnostics Tab → Watcher

### 1. Timeout Signal

```python
# diagnostics.py
class DiagnosticsTab(QWidget):
    alarm_timeout_changed = Signal(float)
    degaters_changed = Signal(list)   # list of active degater names
```

### 2. Connect in MainWindow

```python
# main_window.py
self._tab_diag.alarm_timeout_changed.connect(self._on_alarm_timeout_changed)
self._tab_diag.degaters_changed.connect(self._on_degaters_changed)

def _on_alarm_timeout_changed(self, timeout_sec: float) -> None:
    self._io_alarm_watcher.set_timeout_sec(timeout_sec)
    self.statusBar().showMessage(f"Alarm timeout set to {timeout_sec}s", 3000)

def _on_degaters_changed(self, active_degaters: list[str]) -> None:
    self._io_alarm_watcher.set_active_degaters(active_degaters)
```

### 3. UI Elements on Diagnostics Tab

- **I/O Timeout** row: `QLineEdit("1.0")` + `QPushButton("Accept")`
- **Active Degaters** row: `QCheckBox` for each degater (`DEG1`, `DEG2`, `DEG3`, `SYS`)
- Use inline stylesheets (not theme classes) for the Accept button: `#22c55e` green background + white bold text

---

## Deduplication & Lifecycle

| State | When Set | When Cleared |
|---|---|---|
| `_pending` check | Output transitions | Deadline expires (fires alarm) or output toggles back |
| `_acked_faults` key | Alarm fires OR zone disabled | Output toggles (next edge clears previous edge's key) |
| `_transition_fired` time | Transition alarm fires | Output goes OFF, or zone disabled |
| `_output_states.changed_at` | Output changes | Never; updated in-place |

### Clear on Disconnect

```python
def clear(self) -> None:
    self._pending.clear()
    self._acked_faults.clear()
    self._transition_fired.clear()
    self._output_states.clear()
```

**Call from MainWindow's `_disconnect()`** to prevent stale state from surviving across reconnects.

---

## 8. Automatic Degater Detection from KM Robot Inputs

Instead of manual checkboxes, the watcher can **read KM robot selection inputs** directly from the PLC and determine which degater is active automatically. This eliminates false alarms from unwired stations whose outputs are commanded ON by PLC ladder logic but are not physically in use.

### KM Selection Input Convention (Degater Project)

| PLC Input | Typical Tag | Meaning when TRUE |
|---|---|---|
| `EM_DI_00` | `KM_Selected_DEG1_Or_3` | DEG1 **or** DEG3 is active (odd) |
| `EM_DI_01` | `KM_Selected_DEG2_Or_3` | DEG2 **or** DEG3 is active |

### Decoding Logic

```python
def _detect_active_degaters(self, io_values: dict[str, Any]) -> list[str]:
    """Read KM selection inputs and return list of active degater names."""
    sel_1_or_3 = io_values.get("_IO_EM_DI_00", False)  # KM_Selected_DEG1_Or_3
    sel_2_or_3 = io_values.get("_IO_EM_DI_01", False)  # KM_Selected_DEG2_Or_3

    if sel_1_or_3 and not sel_2_or_3:
        return ["DEG1", "SYS"]
    elif not sel_1_or_3 and sel_2_or_3:
        return ["DEG2", "SYS"]
    elif sel_1_or_3 and sel_2_or_3:
        return ["DEG3", "SYS"]
    else:
        return ["SYS"]  # 00 = none selected
```

### Wiring in `check()`

```python
def check(self, io_values: dict[str, Any], now: datetime | None = None) -> list[AlarmEvent]:
    # Auto-detect active degaters every poll
    if self._auto_detect_degaters:
        active = self._detect_active_degaters(io_values)
        self.set_active_degaters(active)  # flushes stale pending/acked for disabled zones

    # Continue normal three-phase check...
```

### Why This Pattern Is Better Than Manual Checkboxes

| Problem | Manual Checkboxes | Auto Detection |
|---|---|---|
| User forgets to disable DEG1 | False alarms | Never happens |
| KM switches stations mid-shift | User must manually re-check | Automatic per poll cycle |
| DEG1 outputs fire from ladder logic | Still alarms if not unchecked | Correctly ignored |
| Operator absent at startup | Could miss UI setting | Reads PLC directly, no setup |
| Maintenance disconnects a station | Requires manual intervention | KM already tells the PLC |

### Diagnostics Tab Display

Replace the 4 checkboxes with a **status label** that shows the currently detected degater in real time:

```python
# diagnostics.py
self._deg_status_lbl = QLabel("KM-detected degater: — (waiting for PLC poll)")
self._deg_status_lbl.setStyleSheet(
    "QLabel { font-size: 12px; color: #6b7280; padding: 4px 0; }"
)

# Called from main_window.py after every poll cycle
self._tab_diag.update_degater_status(active_degaters)
```

```python
def update_degater_status(self, active_degaters: list[str]) -> None:
    if not active_degaters:
        self._deg_status_lbl.setText("KM-detected degater: None")
        self._deg_status_lbl.setStyleSheet(
            "QLabel { font-size: 12px; color: #9ca3af; padding: 4px 0; }"
        )
    else:
        self._deg_status_lbl.setText(
            f"KM-detected degater: {', '.join(sorted(active_degaters))}"
        )
        self._deg_status_lbl.setStyleSheet(
            "QLabel { font-size: 12px; color: #22c55e; font-weight: 600; padding: 4px 0; }"
        )
```

### Manual Override API

Preserve `set_active_degaters()` for manual override (e.g., forcing DEG1 to be monitored during bench testing):

```python
def set_active_degaters(self, degaters: list[str]) -> None:
    self._auto_detect_degaters = False  # Disables auto mode
    self._active_degaters = set(degaters)  # Manual active set

def set_auto_detect_degaters(self, enabled: bool = True) -> None:
    self._auto_detect_degaters = enabled
```

**When to allow manual override:**
- Field debugging a specific unwired station
- Bench testing a single degater without the KM robot connected
- Factory commissioning where KM selection inputs are not yet wired

---

## Alarm Detail Dialog (UX Pattern)

`QTableWidget` truncates long alarm messages. Add a double-click detail dialog with `QPlainTextEdit`:

```python
def _on_cell_double_clicked(self, row, col, table):
    entry_id = table.item(row, 0).data(Qt.UserRole)
    entry = self._find_entry_by_id(entry_id)
    if not entry:
        return

    dlg = QDialog(self)
    dlg.setWindowTitle(f"Alarm Detail — {entry.severity}")
    dlg.setStyleSheet(
        "QDialog { background-color: #1a1a2e; color: #e0e0e0; }"
        "QPlainTextEdit { background-color: #16213e; color: #e0e0e0; border: 1px solid #0f3460; }"
    )
    layout = QVBoxLayout(dlg)

    meta = QPlainTextEdit(
        f"Timestamp: {entry.timestamp:%Y-%m-%d %H:%M:%S}\n"
        f"Severity:  {entry.severity}\n"
        f"Source:    {entry.source}\n"
        f"Acked:     {entry.acknowledged}"
    )
    meta.setReadOnly(True)
    layout.addWidget(meta)

    msg = QPlainTextEdit(entry.message)
    msg.setReadOnly(True)
    msg.setLineWrapMode(QPlainTextEdit.WidgetWidth)
    layout.addWidget(msg)

    btns = QDialogButtonBox(QDialogButtonBox.Close)
    btns.rejected.connect(dlg.reject)
    layout.addWidget(btns)
    dlg.exec()
```

---

## PyInstaller Bundling Requirements

`io_alarm_pairs.json` must be in `datas`:

```python
# PLCTools.spec or build_exe.py
datas = [
    ('src/plc_tools/catalog/io_alarm_pairs.json', 'plc_tools/catalog'),
    ...
]
```

Verify at runtime:

```python
if len(watcher._pairs) == 0:
    logging.error("No alarm pairs loaded — io_alarm_pairs.json missing from bundle")
```

---

## Testing Without PLC (WSL)

See `references/io-reaction-v3-test-recipes.md` for full unit tests covering:
- Grace period suppression (continuous doesn't fire until timeout after transition)
- Transition alarm fires after grace, continuous suppressed for same window
- Per-degater filtering with zone enable/disable
- Runtime timeout change affecting in-flight pending checks
- Sensor unplug detection: fail-safe INPUT reads → `False` → continuous alarm fires after grace

### Quick Example

```python
def test_grace_period():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)

    # Poll 1: output ON + sensors not yet moved
    values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": False, "_IO_X1_DI_02": False}
    alarms = watcher.check(values, now)
    assert len(alarms) == 0   # suppressed by grace

    # Poll 2: 1.5s later, sensors still missing → continuous check fires
    alarms = watcher.check(values, now + timedelta(seconds=1.5))
    assert len(alarms) == 1
    assert "continuous" in alarms[0].message.lower()
```

---

## Polling Rate: Critical for Pneumatic Cylinder Validation

### The Sampling Problem

Pneumatic cylinder sensor transitions (reed/magnetic) take **100-500ms** to settle. If your poll interval is **1 second**, the sample will often capture the sensor **in its old state** right after the solenoid energizes:

```
T+0.00s  DEG2_Upper_Ret turns ON          ← solenoid energized
T+0.10s  Cylinder starts retracting
T+0.30s  Sensor reed switch starts opening
T+0.50s  Sensor settles to FALSE (old: Extended)
T+0.60s  Sensor settles to TRUE  (new: Retracted)
T+1.00s  POLL HAPPENS                     ← catches mid-transition or old state
```

With `timeout_sec=1.0`, the continuous check fires because the sensor still reads Extended when the poll occurs at `T+1.00s`. This is a **false positive** caused by sampling rate, not a real failure.

**The "swap" misperception:** What looks like "extend and retract swapped" in a timeline is actually the **old sensor state** persisting for 1-2 seconds after the solenoid changes. At 1-second sampling, you don't see the transition — you see Extend ON with Extended sensors still TRUE (from the previous cycle).

### Recommended Rates

| Application | Poll Rate | Rationale |
|---|---|---|
| **Hydraulic cylinders** (slow) | 500-1000ms | Slow motion, sensors settle in 200-400ms |
| **Pneumatic cylinders** (fast) | **100-250ms** | Reed switches settle in 100-500ms; need 2-3 samples per transition |
| **High-speed automation** | 50-100ms | Festo / SMC sensors with response times <10ms |
| **Micro870 over Ethernet/IP** | **Minimum 50ms** | pycomm3 batch read of 127 tags; round-trip ~15-30ms |

### Implementation

```python
# diagnostics.py — Alarm Settings panel
self._poll_rate_combo = QComboBox()
self._poll_rate_combo.addItem("100 ms", 100)
self._poll_rate_combo.addItem("250 ms", 250)
self._poll_rate_combo.addItem("500 ms", 500)
self._poll_rate_combo.addItem("1000 ms", 1000)
self._poll_rate_combo.setCurrentIndex(3)  # default 1000 ms (safe)

# ... on Accept click ...
ms = self._poll_rate_combo.currentData()
self.poll_rate_changed.emit(ms)

# main_window.py
self._poll_timer.setInterval(ms)
```

**Important:** The `timeout_sec` (alarm grace period) and `poll_interval` are **independent**. Set `timeout_sec` to your machine's worst-case sensor settle time (2-5s), and set `poll_interval` to capture the transition. Don't conflate them.

---

## Pitfalls & Anti-Patterns

| Pitfall | Why It Happens | Fix |
|---|---|---|
| **Continuous check has zero grace** | Added continuous check after transition check, forgot to link grace periods | Apply Grace Rules 1 + 2 (see unified grace section) |
| **Double alarm on every motion** | Transition fires alarm at timeout, continuous fires same cycle | Grace Rule 2: transition owns the window |
| **Disabling DEG1 doesn't stop alarms** | Watcher stores output-specific state, doesn't know degater filter exists in `check()` only | Purge `_pending`, `_acked_faults`, `_transition_fired` when zone disabled |
| **Timeout change doesn't affect pending checks** | `set_timeout_sec()` only updates property | Recalculate or extend existing `_pending` deadlines by `(new - old)` |
| **Sensor unplug never alarms** | Read failure caches `True` via last-known fallback | Direction-aware reads: INPUT → `False`, OUTPUT → last-known |
| **Tab-switch glitch alarms** | Single poll failure triggers alarm | Require 4+ consecutive failures |
| **Alarm pairs silently absent** | JSON not in PyInstaller `datas` | Verify `len(watcher._pairs) > 0` at startup |
| **Slow polling creates false "swaps"** | 1-second sampling catches sensors in old state | Increase to 250ms; sensors need 2-3 samples during transition |
| **Proposing ladder logic fixes** | User explicitly doesn't want to edit PLC ladder | **All fixes must be software-side** — polling, filtering, UI timeout tuning. See `references/io-reaction-polling-rate.md` |
| **Theme class names on dynamic buttons** | `#uiverse_green` or `#uiverse_btn` class doesn't resolve on runtime-created `QPushButton` | Always use `setStyleSheet()` with hard-coded hex values (e.g., `#22c55e`) for Accept buttons in dynamically created widgets |
| **Filtering outputs by active degater** | Auto-detect only shows which degater the KM selected, but ladder logic may still check ALL degaters for home signal | **Remove filter** — monitor ALL pairs unconditionally. Use degater status for UI display only, not alarm gating |
| **Transition and continuous both alarm for same stuck sensor** | Transition alarms at T+timeout, then continuous fires T+timeout later because `_acked_faults` doesn't block the continuous composite key | After firing transition alarm, add `continuous_key` to `_acked_faults` (see Grace Rule 2b) |
| **Dual-solenoid cylinders produce false alarms on every cycle** | Extend solenoid turns OFF → watchdog checks Ret sensors (should wait for Retract solenoid ON). 2 false alarms per complete cycle. | Remove `off_inputs` from Extend/Retract entries. Only validate one solenoid's ON state. See `references/session-2026-06-01-dual-solenoid-off-inputs-fix.md` |
| **Alarm notes flip between "Expected Ext" and "Expected Ret"** | Both solenoids have `off_inputs` set, so OFF-state checks for the counterpart's sensors fire immediately. The alarm text depends on which check's note gets used. | Remove `off_inputs` from dual-solenoid pairs. Only check `on_inputs` when the solenoid is actually ON. |

---

## References

- `references/io-reaction-v3-implementation.md` — Full v3 implementation with `_transition_fired`, `_active_degaters`, grace logic, auto-detection wiring, and Diagnostics tab integration
- `references/io-reaction-v3-test-recipes.md` — WSL unit tests (no PLC required)
- `references/io-reaction-polling-rate.md` — Adjustable polling rate, sampling considerations, and Micro870 throughput limits
- `micro800-mode-operation` skill (and its `references/io-reaction-alarm-watcher.md`) — v1 reference for historical context

---

## References

- `references/io-reaction-v3-implementation.md` — Full v3 implementation with grace, auto-detection, and Diagnostics tab integration
- `references/io-reaction-v3-test-recipes.md` — WSL unit tests (no PLC required)
- `references/io-reaction-polling-rate.md` — Adjustable polling rate, Micro870 throughput, end-of-scan insight, inline stylesheet pattern
- `references/session-2026-06-01-double-alarm-fix.md` — Transition/continuous dedup fix and degater filtering removal notes
- `references/timeline-subsampling-for-recording.md` — Decouple poll rate from record rate to bound 12-hour recording size from 1.5 GB → ~150 MB

## Related Skills

- `micro800-mode-operation` — PLC mode detection, OTE vs OTL coils, ladder logic analysis
- `plc-output-force-safety` — Manual/auto interlocks, dimmed button pattern, force/release workflows
- `pyinstaller-desktop-app` — Single-file EXE builds, asset bundling
