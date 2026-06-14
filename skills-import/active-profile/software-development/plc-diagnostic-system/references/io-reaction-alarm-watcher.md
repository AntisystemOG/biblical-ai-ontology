# I/O Reaction Alarm Watcher Pattern

Real-time validation engine that monitors PLC output states and verifies expected input sensors react correctly. It provides **two layers** of protection:

1. **Transition check** — when an output toggles, verify expected inputs respond within `timeout_sec`
2. **Continuous check** — while an output remains ON/OFF, verify expected inputs stay ON; catches sensor disconnects that happen *after* the transition

If validation fails, a deduplicated `AlarmEvent` is forwarded to the UI alarm log. Timeout is runtime-mutable from the Diagnostics tab.

## Use Cases

- Detect mechanical failures (solenoid fires but cylinder doesn't move)
- Detect wiring faults (output turns on but sensor never sees it)
- Detect **sensor drops after motion completes** (cable loosens mid-cycle)
- Provide immediate operator feedback when physical machine state diverges from commanded state

---

## Architecture

```
Poll cycle (every 1.0 sec)
    │
    ▼
┌──────────────────────────────────────────────────┐
│  _PollWorker reads all I/O tags via pycomm3      │
└────────────────┬─────────────────────────────────┘
                 │ io_values dict  {tag_name: bool}
                 ▼
┌──────────────────────────────────────────────────┐
│  MainWindow._on_poll_done(io_values)            │
│  ├─> IOAlarmWatcher.check(io_values)            │
│  │   returns list[AlarmEvent]                    │
│  ├─> for each alarm:                              │
│  │     _tab_alarms.log_event(...)               │
│  └─> Diagnostics tab optionally calls:            │
│        watcher.set_timeout_sec(new_value)         │
└──────────────────────────────────────────────────┘
```

**No extra threads.** The watcher runs synchronously inside the existing poll completion handler. This avoids race conditions and keeps the architecture simple.

---

## Alarm Pair JSON Format

```json
[
  {
    "output_physical": "_IO_X4_DO_07",
    "on_inputs_physical": ["_IO_X1_DI_01", "_IO_X1_DI_02"],
    "off_inputs_physical": ["_IO_X1_DI_03", "_IO_X1_DI_04"],
    "degater": "DEG1",
    "function": "Lower Extend",
    "note_on": "Lower justify assembly is commanded to extend. All extend sensors must switch ON.",
    "note_off": "Lower justify assembly is commanded to retract. All retract sensors must switch ON."
  }
]
```

| Field | Meaning |
|---|---|
| `output_physical` | PLC output tag to watch |
| `on_inputs_physical` | Tags expected to be **HIGH** when output is **ON** |
| `off_inputs_physical` | Tags expected to be **HIGH** when output is **OFF** |
| `degater` | Machine identifier for alarm grouping (e.g., `DEG1`, `DEG2`, `COMMON`) |
| `function` | Human-readable description used in alarm messages |
| `note_on` | Per-row diagnostic note appended to alarm when output is ON |
| `note_off` | Per-row diagnostic note appended to alarm when output is OFF |

> **Note:** `timeout_sec` is **not per-pair** in this design. It lives on the `IOAlarmWatcher` instance and is adjustable at runtime via `set_timeout_sec()`.

---

## Core Data Structures

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    FAULT = "fault"

@dataclass
class AlarmEvent:
    severity: Severity
    source: str
    message: str
    fault_key: str

@dataclass
class _PendingCheck:
    fired_at: datetime
    deadline: datetime
    expected_on: list[str]
    fault_key: str

@dataclass
class _AlarmPair:
    output_physical: str
    on_inputs_physical: list[str]
    off_inputs_physical: list[str]
    degater: str
    function: str
    note_on: str
    note_off: str
```

---

## Algorithm

### Phase 1: Transition Check

When an output changes state, create a `_PendingCheck` with a deadline `now + timeout_sec`.

```python
out_val = io_values.get(pair.output_physical, False)
prev = self._prev_outputs.get(pair.output_physical)

if prev is not None and out_val != prev:
    self._pending[pair.output_physical] = _PendingCheck(
        fired_at=now,
        deadline=now + timedelta(seconds=self._timeout_sec),
        expected_on=pair.on_inputs_physical if out_val else pair.off_inputs_physical,
        fault_key=f"{pair.output_physical}|{state_str}"
    )
self._prev_outputs[pair.output_physical] = out_val
```

### Phase 2: Pending Deadline Evaluation

For each pending check, if `now > deadline`, verify all expected inputs are HIGH. If not, construct an `AlarmEvent` and mark the `fault_key` as "already fired" to prevent duplicate alarms.

### Phase 3: Continuous Check (Post-Commit Addition)

For every output that is **currently ON**, regardless of when it turned on, verify that the `on_inputs_physical` are all HIGH. If any are missing, fire immediately.

```python
def _continuous_check(self, io_values: dict[str, Any], now: datetime) -> list[AlarmEvent]:
    alarms = []
    for pair in self._pairs:
        out_val = io_values.get(pair.output_physical, False)
        if not out_val:
            continue
        missing = [t for t in pair.on_inputs_physical if not io_values.get(t, False)]
        if missing:
            key = f"continuous|{pair.output_physical}|on"
            if key not in self._already_fired:
                alarms.append(self._build_alarm(pair, True, missing, continuous=True))
                self._already_fired[key] = True
    return alarms
```

**Why this matters:** Transition checks only fire on the *edge* when the output changes. If a sensor cable vibrates loose 3 seconds after the cylinder extended, transition checks are silent. Continuous checks catch this immediately.

### Deduplication Strategy — Two Domains

| Check Type | Dedup Key Format | Resets When |
|---|---|---|
| Transition | `output|on|timestamp` | Output toggles off |
| Continuous | `continuous|output|on` | Output goes off |

The composite key for **transition** checks includes the `fired_at` timestamp: e.g. `"_IO_X4_DO_07|on|20260531013045"`. This means each time the output turns on and times out, a **new** alarm fires. This is intentional — you want to know about every distinct transition failure.

The composite key for **continuous** checks is stable: `"continuous|_IO_X4_DO_07|on"`. While the output stays on and the sensor stays missing, this suppresses re-alarms. It will re-fire if the output toggles.

```python
# Transition key (changes every transition → re-alarms on each edge)
f"{pair.output_physical}|{state_str}|{check.fired_at.strftime('%Y%m%d%H%M%S')}"

# Continuous key (stable while output stays on)
f"continuous|{pair.output_physical}|{state_str}"
```

---

## Runtime Timeout Adjustment

Expose `set_timeout_sec()` and a `timeout_sec` property so the Diagnostics tab can change the grace period without restarting the program.

```python
class IOAlarmWatcher:
    def __init__(self, timeout_sec: float = 1.0):
        self._timeout_sec = timeout_sec
        # ...

    @property
    def timeout_sec(self) -> float:
        return self._timeout_sec

    def set_timeout_sec(self, value: float) -> None:
        self._timeout_sec = value
```

**Wiring from Diagnostics to Watcher:**

```python
# diagnostics.py
alarm_timeout_changed = Signal(float)

# main_window.py
self._tab_diag.alarm_timeout_changed.connect(self._on_alarm_timeout_changed)

def _on_alarm_timeout_changed(self, timeout_sec: float) -> None:
    self._io_alarm_watcher.set_timeout_sec(timeout_sec)
    self.statusBar().showMessage(f"Alarm timeout set to {timeout_sec}s", 3000)
```

---

## Building Alarm Messages

Every alarm message pulls the per-row diagnostic note from the JSON pair:

```python
def _build_alarm(self, pair: _AlarmPair, output_on: bool, missing: list[str],
                 continuous: bool = False) -> AlarmEvent:
    note = pair.note_on if output_on else pair.note_off
    state_str = "ON" if output_on else "OFF"
    missing_tags = ", ".join(missing)

    if continuous:
        msg = (
            f"[{pair.degater}] {pair.function}: output `{pair.output_physical}` "
            f"is {state_str} but expected input(s) are not "
            f"(continuous check): {missing_tags}. {note}"
        )
    else:
        msg = (
            f"[{pair.degater}] {pair.function}: output `{pair.output_physical}` "
            f"fired at {check.fired_at.strftime('%H:%M:%S')} but expected input(s) "
            f"are not ON (within {self._timeout_sec}s): {missing_tags}. {note}"
        )

    return AlarmEvent(
        severity=Severity.FAULT,
        source=pair.output_physical,
        message=msg,
        fault_key=fault_key
    )
```

---

## Critical: Zero-Padded Tag Format

Allen-Bradley Micro870 I/O tags use **zero-padded two-digit suffixes**:
- ✅ `_IO_X1_DI_01` through `_IO_X1_DI_19`
- ✅ `_IO_X3_DO_00` through `_IO_X3_DO_15`
- ❌ `_IO_X1_DI_1` — **silently fails to match** live tag values

**Always generate physical addresses with `f"_IO_X{n}_DI_{i:02d}"`.**

---

## Integration Points

### 1. Import and Instantiate

```python
from plc_tools.polling.io_alarm_watcher import IOAlarmWatcher

class MainWindow(QMainWindow):
    def __init__(self):
        ...
        self._io_alarm_watcher = IOAlarmWatcher()
```

### 2. Check in Poll Completion Handler

```python
def _on_poll_done(self, io_values: dict[str, Any]) -> None:
    ...
    for alarm in self._io_alarm_watcher.check(io_values):
        self._tab_alarms.log_event(
            alarm.severity, alarm.source, alarm.message, alarm.fault_key
        )
```

### 3. Clear on Disconnect

```python
def _disconnect(self) -> None:
    self._io_alarm_watcher.clear()
    self._update_ui_disconnected()
```

---

## Poll Error Throttling

Single-poll read spikes (e.g., switching to the Diagnostics tab or a momentary network glitch) can produce false "Read failure" alarms. In the MainWindow poll-completion handler, gate poll-error logging to **4 consecutive failures** before the alarm fires.

```python
if io_read_success:
    self._poll_alarm_ticks = 0
    if self._poll_alarm_was_on:
        self._poll_alarm_was_on = False
        ...
else:
    self._poll_alarm_ticks += 1
    if self._poll_alarm_ticks >= 4 and (
        self._poll_alarm_ticks == 4 or self._poll_alarm_ticks % 10 == 0
    ):
        self._tab_alarms.log_event(..., f"Read failure #{self._poll_alarm_ticks} ...")
        self._poll_alarm_was_on = True
```

| Threshold | Behavior |
|---|---|
| 1–3 failures | Silently accumulate; no alarm |
| ≥ 4 failures | Alarm fires once at 4, then every 10 cycles |
| Recovery | "cleared after N cycle(s)" only if alarm was previously fired |

---

## Deduplication Key Clearing on Reconnect

`_fault_keys` in `AlarmsLogTab` must be **cleared on every new PLC connect**, or deduplication will suppress all future alarms from the same output/input pair indefinitely.

```python
# In MainWindow._update_ui_connected()
self._tab_alarms.clear()   # resets _fault_keys set
```

Without this, if an alarm fires once and the operator disconnects/reconnects, the same fault can never alarm again until the program restarts.

---

## PyInstaller JSON Catalog Bundling

`io_alarm_pairs.json` must be explicitly included in PyInstaller `datas` or the EXE will load zero pairs and the watcher stays permanently silent.

```python
# PLCTools.spec  (or build_exe.py datas=)
datas = [
    ('src/plc_tools/catalog/io_alarm_pairs.json', 'plc_tools/catalog'),
    ...
]
```

Always verify at runtime that `len(watcher._pairs) > 0` after loading.

---

## Timeout UI Discoverability

The timeout control lives in the Diagnostics tab inside an **ALARM SETTINGS** group with a `QLineEdit("1.0")` and a `QPushButton("Apply")` (not "Accept"). Operators may miss it if:

- The group is collapsed inside a scroll area
- There is no status feedback after clicking Apply
- The button label doesn't match their mental model

**Fixes:**
1. Add a status label next to the button: `Timeout: 1.0 s`
2. Emit a status-bar message on apply: `Alarm timeout set to {x}s`
3. Consider moving the control to a dedicated Alarms tab if the Diagnostics tab is crowded

---

## Live Diagnostics Panel

When the user reports "partially working," add a **live diagnostics panel** (QTextEdit or QTableWidget) to the Diagnostics tab that refreshes every poll cycle and shows:

| Column | Content |
|---|---|
| Output | Physical tag name + current value (ON/OFF) |
| Expected Inputs | List of `on_inputs_physical` / `off_inputs_physical` |
| Resolved State | `TRUE` / `FALSE` / `None` (missing from poll) |
| Pending Checks | Count of active checks waiting for deadline |
| Acked Faults | Count of `_acked_faults` currently held |
| Timeout | Current `watcher.timeout_sec` value |

Expose a `watcher.diagnose_summary(io_values) -> dict` method so the UI can render without importing watcher internals.

---

## Catalog Mismatch Notes

If an alarm pair references an `output_physical` or `input_physical` tag not present in the PLC's live tag dict, it will silently produce no alarms. Cross-check pairs against `KNOWN_IO_TAGS` in the catalog after loading.

---

## Testing in WSL (No PLC)

Unit-test with synthetic `io_values` dicts:

```python
def test_watcher():
    watcher = IOAlarmWatcher()
    now = datetime.now()

    # Poll 1: output ON, all inputs respond → 0 alarms
    alarms = watcher.check({"_IO_X4_DO_07": True, "_IO_X1_DI_01": True, "_IO_X1_DI_02": True}, now)
    assert len(alarms) == 0

    # Poll 2: sensor drops while output stays ON → continuous check catches it
    alarms = watcher.check({"_IO_X4_DO_07": True, "_IO_X1_DI_01": True, "_IO_X1_DI_02": False},
                           now + timedelta(seconds=2.0))
    assert len(alarms) == 1
    assert "continuous check" in alarms[0].message

    # Poll 3: still missing → dedup kills it → 0 alarms
    alarms = watcher.check({"_IO_X4_DO_07": True, "_IO_X1_DI_01": True, "_IO_X1_DI_02": False},
                           now + timedelta(seconds=3.0))
    assert len(alarms) == 0

    # Poll 4: sensor restored → 0 alarms
    alarms = watcher.check({"_IO_X4_DO_07": True, "_IO_X1_DI_01": True, "_IO_X1_DI_02": True},
                           now + timedelta(seconds=4.0))
    assert len(alarms) == 0

    # Runtime timeout change
    watcher.set_timeout_sec(2.5)
    assert watcher.timeout_sec == 2.5
```

---

## Lifecycle & Restart Behavior

In-process, not a Windows service or background daemon.

| Event | Watcher Behavior |
|---|---|
| EXE launch | `IOAlarmWatcher()` instantiated in `MainWindow.__init__()` — auto-starts |
| Connected + polling | `check(io_values)` called synchronously inside `_on_poll_done()` every poll cycle |
| Disconnect | `watcher.clear()` resets all pending checks and dedup state |
| EXE close | Object destroyed with `MainWindow`. No persistent process, no registry entries |

---

## When NOT to Filter by Selected Degater (Global Ladder Dependencies)

A common pitfall: the alarm watcher auto-detects which degater is active via KM robot selection inputs (`KM_Selected_DEG1_Or_3`, `KM_Selected_DEG2_Or_3`) and skips monitoring outputs from unselected degaters.

**This is correct ONLY IF each degater operates independently.**

**This is WRONG if the ladder logic has a global dependency**, e.g.:
- The "Home" signal requires **ALL three degaters to be home**
- Safety interlocks check every degater's position before allowing cycle start
- A fault on DEG1 while DEG2 is selected should still alarm because DEG1 is part of the global home condition

### The Problem

| Scenario | With Filtering | Without Filtering |
|---|---|---|
| KM selects DEG2 | DEG1 and DEG3 outputs skipped silently | DEG1 and DEG3 still monitored |
| DEG1 sensor fails while DEG2 running | **No alarm** — DEG1 is filtered out | Alarm fires because DEG1 is part of global state |
| Home signal stalls | Ladder waits for DEG1, but PC is blind | PC sees DEG1 fault immediately |

### The Fix

Remove the per-pair degater filter from the `check()` loop:

```python
# REMOVED — do NOT skip pairs based on active degater
# if pair.get('degater') not in self._active_degaters:
#     continue

# Instead: process ALL pairs every poll cycle
for pair in self._pairs:
    phys_out = pair.get("output_physical", "")
    if not phys_out:
        continue
    # ... proceed with transition + continuous checks
```

Keep the `_active_degaters` field **for UI display only** (Diagnostics tab showing which degater KM selected), but never use it to skip alarm logic.

### When Filtering IS Appropriate

Filtering by active degater is correct when:
- Each degater has physically separate I/O wiring that is literally disconnected when unselected
- Unselected degater outputs are guaranteed OFF by hardware (not just ladder logic)
- There is no global state that depends on all degaters simultaneously

**When in doubt, default to monitoring ALL outputs.** A false positive on an unselected degater is better than a false negative on a sensor failure.

### Truth Table: KM Selection Inputs → Active Degater

The KM robot feeds two selection bits into the PLC. Decode them like this:

| `KM_Selected_DEG1_Or_3` (`_IO_EM_DI_00`) | `KM_Selected_DEG2_Or_3` (`_IO_EM_DI_01`) | Active degater |
|---|---|---|
| FALSE | FALSE | None (SYS only) |
| TRUE | FALSE | DEG1 |
| FALSE | TRUE | DEG2 |
| TRUE | TRUE | DEG3 |

> These inputs are **display-only indicators** of which station is selected. Do not use them to filter alarm logic unless you have verified the ladder has no global dependencies.

---

## Poll Rate Selection UI Pattern

When fast polling is needed to capture sensor transitions (e.g., cylinder motion completes in ~200–800 ms but default poll is 1000 ms), add a poll rate selector to the Diagnostics tab:

```python
# diagnostics.py — inside Alarm Settings group
self._poll_rate_combo = QComboBox()
for label, ms in [("1000 ms (1 Hz)", 1000), ("500 ms (2 Hz)", 500),
                  ("250 ms (4 Hz)", 250), ("100 ms (10 Hz)", 100)]:
    self._poll_rate_combo.addItem(label, ms)

self._poll_rate_apply = QPushButton("Accept")
self._poll_rate_apply.setStyleSheet("background-color: #22c55e; color: white;")

# Signal to MainWindow
poll_rate_changed = Signal(int)  # emits ms

self._poll_rate_apply.clicked.connect(
    lambda: self.poll_rate_changed.emit(self._poll_rate_combo.currentData())
)
```

```python
# main_window.py — slot wiring
self._tab_diag.poll_rate_changed.connect(self._on_poll_rate_changed)

def _on_poll_rate_changed(self, ms: int) -> None:
    self._poll_timer.setInterval(ms)
    self._status_bar.showMessage(f"Poll rate set to {ms} ms  ({1000/ms:.0f} Hz)", 3000)
```

**Recommended setting for cylinder motion monitoring:** 250 ms. Captures transitions that a 1-second poll window misses, eliminating false "sensor swap" perceptions.

---

## Grace Period: Suppressing Continuous Check Around State Changes

When an output changes state, sensors need time to respond physically. The transition check already provides a `timeout_sec` grace window. But without suppression, the **continuous check** fires immediately on the next poll — causing double alarms (one from transition timeout, one from continuous check) while the cylinder is still in motion.

### Solution

Suppress continuous check for `timeout_sec` after:
1. Any state change on this output (`state.changed_at`)
2. Any transition alarm that already fired for this output (`_transition_fired[output_tag]`)

```python
def _continuous_check(self, pair, out_val, io_values, now):
    # ... build expected inputs ...

    # Grace period 1: timeout_sec after state change
    state = self._output_states.get(phys_out)
    if state and state.changed_at:
        elapsed = (now - state.changed_at).total_seconds()
        if elapsed < self._timeout_sec:
            return []  # still settling

    # Grace period 2: timeout_sec after transition alarm fired
    tf = self._transition_fired.get(phys_out)
    if tf:
        elapsed_since_tf = (now - tf).total_seconds()
        if elapsed_since_tf < self._timeout_sec:
            return []  # already handled by transition check

    # ... proceed with continuous validation ...
```

Without these two suppressions, a typical cycle produces:
- 18 false continuous alarms in 10 minutes (at 1-second polling)
- All from continuous check firing during the transition grace window

With suppression: **zero false alarms** during normal cylinder motion.

