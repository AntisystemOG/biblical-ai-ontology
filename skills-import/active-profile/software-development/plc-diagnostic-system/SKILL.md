---
name: plc-diagnostic-system
description: "Build, deploy, and operate industrial PLC diagnostic desktop apps — Allen-Bradley Micro800/Micro870 with PySide6, pycomm3, real-time I/O monitoring, output force safety, reaction validation, and PyInstaller bundling."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
---

# PLC Diagnostic System

## Purpose

This skill covers the complete lifecycle of a desktop diagnostic application for Allen-Bradley Micro800 / Micro870 PLCs:

- **Safety-first output forcing** — only write outputs when the PLC is in manual mode, with visual interlocks
- **PLC mode detection** — read status word via CIP, understand why remote mode switching is impossible
- **Ladder logic analysis** — decode rungs from .docx EMF exports, determine if app writes will win
- **Real-time I/O reaction validation** — detect stuck cylinders, unplugged sensors, and mechanical faults
- **Direction-aware fail-safe reads** — treat INPUT read errors differently from OUTPUT read errors
- **PyInstaller bundling** — single-file Windows .exe with assets, JSON catalogs, and icons

> **Project origin:** Degater diagnostics (KM robot fixture management). All examples use Micro870 / pycomm3 / PySide6.
> **User constraint:** Keep all fixes software-side — no PLC ladder logic edits.

---

## Triggers

- Building or modifying a PySide6 + pycomm3 desktop app that monitors or controls a Micro800 / Micro870
- Need to force PLC outputs safely from a GUI
- Need to validate that outputs cause expected input reactions (cylinder motion detection)
- Need to analyze ladder logic from CCW .docx exports when the source .l5x is unavailable
- Building a single-file Windows .exe from a PySide6 + pycomm3 project

---

## Table of Contents

1. **Output Force Safety** — manual mode interlocks, visual feedback, force/release workflows
2. **PLC Mode & Ladder Logic** — status word decoding, OTE vs OTL coils, CCW .docx EMF analysis
3. **I/O Reaction Validation** — three-phase alarm watcher with unified grace periods
4. **Fail-Safe Read Policy** — direction-aware fallbacks on pycomm3 errors
5. **PyInstaller Bundling** — asset paths, _MEIPASS, dead-code auditing, data-file inclusion
8. **Diagnostics Tab Safety & Reconnect Reliability** — avoiding GUI freeze on tab switch, safe disconnect/reconnect, UI generation tag consistency
9. **Verification** — ladder logic compatibility table for manual writes
10. **Simulated Recordings for Offline Testing** — deterministic test data generation without PLC access

---

## Table of Contents

1. **Output Force Safety**
2. **PLC Mode & Ladder Logic**
3. **I/O Reaction Validation**
4. **Fail-Safe Read Policy**
5. **PyInstaller Bundling**
6. **Diagnostics Tab Safety & Reconnect Reliability**
7. **Playback & Recording**
8. **Verification**
9. **Simulated Recordings for Offline Testing**

---

## Section 1: Output Force Safety

> **Related references:** `references/manual-mode-popup-final.md`, `references/manual-button-photo-popup.md`, `references/top-row-manual-status-button.md`

### Core Principle

**Output forcing is only permitted when the PLC program is in manual mode.** The GUI must detect the mode from the PLC in real time, lock controls in auto mode, and provide unambiguous visual feedback.

### User Preference (Degater Project)

Keep the original ON / OFF / Release buttons always visible. In auto mode, **dim them** (gray text, muted borders) so they look inactive. Any click on ON, OFF, or Release opens the Manual Mode dialog with a photo of the physical MAN-AUTO switch. Only in manual mode do the buttons brighten to full color and become functional.

### Detecting Manual Mode

| Tag (project-specific) | Value | Meaning |
|---|---|---|
| `DEG_MAN_AUTO` (X2 DI 30) | `FALSE` | Manual mode → controls ACTIVE |
| `DEG_MAN_AUTO` | `TRUE`  | Auto mode  → controls LOCKED |

**Critical:** Polarity is project-specific. Verify with the PLC programmer.

### Dimmed Button Pattern (Pattern A — Preferred)

Each `ManualControlWidget` receives live mode state from the poll handler. Cache the last mode to prevent flicker during timeline playback:

```python
def _set_manual_mode_banner(self, manual_enabled: bool) -> None:
    """Show mode banner: green = Manual active, amber = Auto locked."""
    if manual_enabled:
        self._mode_banner.setText("🟢 MANUAL MODE — Output controls are ACTIVE")
        self._mode_banner.setStyleSheet(
            "QLabel { background-color: #d1fae5; color: #065f46; "
            "border-radius: 6px; padding: 4px 12px; "
            "font-size: 11px; font-weight: bold; }"
        )
    else:
        self._mode_banner.setText(
            "🟡 AUTO MODE — Hover over buttons to see details"
        )
        self._mode_banner.setStyleSheet(
            "QLabel { background-color: #fef3c7; color: #92400e; "
            "border-radius: 6px; padding: 4px 12px; "
            "font-size: 11px; font-weight: bold; }"
        )
```

**Details learned in production:**
- Button width 112px, font-size 10px, padding 2px 4px — prevents clipping
- Cache `_cached_man_auto` and only update on change — prevents banner flicker during playback
- `StatusIndicator.set_on()` must `return` early if `on == self._is_on` — avoids repaint spam

### Side Buttons in Auto Mode — Final Pattern (Updated 2026-06-01)

When the machine is **not** in Manual mode:
- **Disable the side ON / OFF / Release buttons** (`setEnabled(False)`)
- Buttons are **grayed out and unclickable** — no state flip, no popup, no dialog
- The **only** button that opens the `ManualModeDialog` is the top-row **Manual: ON/OFF** status button
- All side buttons show the same tooltip: `"These buttons will not work unless manual switch is on."`
- The Release button is disabled only when `not self._forced`; otherwise it stays clickable even in Auto so the user can clear a lingering force without switching modes
- **`update_from_plc()` must NOT return early** when `not self._manual_enabled` — buttons must follow the real PLC state regardless of mode so operators can see what's happening

**Required: `:checked:disabled` stylesheet rules**

Disabled buttons that are checked must still show their ON/OFF color so the operator can see the PLC state at a glance. Add these alongside the normal enabled styles:

```css
ManualControlButton:checked:disabled#ON  {
    background-color: #10b981;  /* green */
    color: white;
    border-color: #059669;
}
ManualControlButton:checked:disabled#OFF {
    background-color: #ef4444;  /* red */
    color: white;
    border-color: #dc2626;
}
```

Without these rules, a disabled checked button falls back to the base disabled gray, hiding the real PLC state.

```python
def _update_button_states(self, enabled: bool):
    self._on_btn.setEnabled(enabled)
    self._off_btn.setEnabled(enabled)
    self._release_btn.setEnabled(enabled and self._forced)
    for btn in (self._on_btn, self._off_btn, self._release_btn):
        if not btn.isEnabled():
            btn.setToolTip("These buttons will not work unless manual switch is on.")

def update_from_plc(self, output_on: bool):
    # NEVER return early here — sync state regardless of Auto/Manual
    if not self._forced:
        self._on_btn.setChecked(output_on)
        self._off_btn.setChecked(not output_on)
```

**Why disable instead of intercept?**
- Using `setEnabled(False)` is cleaner than allowing a click and then reverting state
- It naturally prevents any popup or signal emission without extra guards
- It gives the user immediate visual feedback (dimmed/grayed out)

### Top-Row Manual Status Button

The **Manual: ON / OFF** indicator at the top of the I/O Status tab remains clickable at all times. Clicking it opens the `ManualModeDialog` with a photo of the physical MAN-AUTO switch:

```python
class ManualModeDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Switch to Manual Mode")
        self.setFixedSize(640, 540)
        # ... load image from sys._MEIPASS / plc_tools/gui/assets / Manual.jpg
```

**Bundling the photo:** Add to `.spec` `datas`:
```python
datas=[
    ('src/plc_tools/gui/assets', 'plc_tools/gui/assets'),
]
```

### Release in Auto Mode

A forced output remains active if the PLC switches to auto while the force is held. **Do NOT disable the Release button in auto mode.** The user must be able to clear the force without switching back to manual.

### Anti-Patterns

| Anti-Pattern | Why Dangerous | What To Do |
|---|---|---|
| Let the GUI decide the mode | GUI state can drift from PLC reality | Always read mode from PLC every poll |
| One-time warning | User may miss it, mode changes later | Persistent banner + live control state |
| Disable the entire tab | User still needs to monitor I/O in auto | Only disable the force controls |
| Force without any interlock | Direct tag writes in any mode | Always check mode first |
| Rely on PLC-side interlock only | GUI gives false confidence | Defense in depth: GUI + PLC |

---

## Section 2: PLC Mode & Ladder Logic Analysis

> **Related references:** `references/micro800-mode-status-decoder.md`, `references/degater-project-notes.md`, `references/ladder-logic-analysis-from-python.md`, `references/ladder-emf-conversion.md`

### 2.1 Status Word Decoding (Read-Only)

The Micro870 exposes a status word via the Identity Object. Decode it to determine Run / Program / Faulted mode.

```python
from pycomm3 import Services, ClassCode

def get_controller_mode(self) -> dict:
    result = self._plc.generic_message(
        service=Services.get_attribute_single,
        class_code=ClassCode.identity_object,
        instance=1, attribute=5,  # Status word
        connected=False, unconnected_send=True, route_path=True,
    )
    if result and not result.error and result.value:
        status_word = int.from_bytes(result.value[:2], 'little')
        return self._decode_status_word(status_word)

def _decode_status_word(self, word: int) -> dict:
    modes = {
        0x00: "Program", 0x01: "Run", 0x02: "Run",
        0x03: "Faulted", 0x04: "Booting",
    }
    mode = modes.get(word & 0x0F, f"Unknown({word & 0x0F})")
    flags = []
    if word & 0x10:   flags.append("Minor Fault Non-Recoverable")
    if word & 0x40:   flags.append("Major Recoverable Fault")
    if word & 0x80:   flags.append("Major Non-Recoverable Fault")
    if word & 0x100:  flags.append("Minor Recoverable Fault")
    return {"mode": mode, "flags": flags or ["None"], "raw": word}
```

**Key point:** The status word is read-only. There is no CIP service to switch Micro800 modes remotely. pycomm3's `Services.start` and `Services.reset` are ControlLogix-specific. Switch modes via:
- Physical front panel **Run/Stop button**, or
- **Connected Components Workbench (CCW)** → right-click PLC → Mode

### 2.2 Program Mode for Troubleshooting

| | Run Mode | Program Mode |
|---|---|---|
| Ladder logic scan | Evaluates AND drives physical outputs | Evaluates internally, does **not** drive physical outputs |
| App tag writes | PLC overwrites on next scan (OTE coils) | **Value sticks** — no physical output driving |

**OTE coils are rewritten every scan.** In Run mode, an app write is overwritten on the next PLC scan. In Program mode, the app write "sticks" in the tag value and you can read it back to verify.

### 2.3 Will Manual Writes Win?

| Pattern | Result |
|---|---|
| `XIO DEG_MAN_AUTO` breaks auto rung | App writes win cleanly |
| Manual override rung with `XIC DEG_MAN_AUTO` | App writes feed manual rung. Verify latching holds |
| No bypass — auto always active | App writes fight ladder every scan (fight/flicker) |
| OTL/OTU (latch/unlatch) coils | Manual set/reset holds state across scans |
| OTE only, no manual break | State rewritten every scan. Unsafe. |

### 2.4 Analyzing Ladder Logic Without CCW

When the PLC programmer provides a `.docx` ladder export (from CCW print):

```bash
# Step 1: Extract
python3 -m zipfile -e ladder.docx extracted/
# Images at: extracted/word/media/*.emf

# Step 2: Convert EMF to PNG (requires Windows)
# Use PowerShell from WSL; see scripts/convert_ladder_emf_to_png.py

# Step 3: Visual analysis with vision_analyze
# Ask: tag names, parallel branches, NO vs NC contacts, coil type
```

### 2.5 Robot Controller I/O vs PLC Physical I/O

**Critical boundary:** Robot controllers (e.g., Kawasaki KM) maintain their own internal DI/DO numbering that does NOT map 1:1 to PLC physical tags.

- **PLC physical tags** are module-based: `_IO_X1_DI_00` through `_IO_X5_DI_31`, `_IO_EM_DI_00` through `_IO_EM_DI_31`, etc. These appear in `io_catalog.py` and `physical_mapping.py`.
- **Robot internal DIs** (e.g., DI-186) are mapped to PLC outputs via the robot's I/O assignment table in the robot controller itself — NOT in the PLC ladder.

**When you see an alarm like "wait DI-186 Time out":**
1. It is a **robot program alarm**, not a PLC ladder timer
2. DI-186 maps to a PLC output through the robot's I/O configuration (not the PLC's physical mapping)
3. The fix requires the **robot I/O assignment table** or robot pendant inspection — the PLC ladder alone cannot explain it

**PLC outputs that feed the robot** (known from `physical_mapping.py`):

| PLC Output | Robot sees as | Meaning |
|---|---|---|
| `_IO_EM_DO_00` | Configured robot DI | Upper_Ready_For_Parts |
| `_IO_EM_DO_01` | Configured robot DI | Lower_Ready_For_Parts |
| `_IO_EM_DO_02` | Configured robot DI | Upper_Completed_Cuts |
| `_IO_EM_DO_03` | Configured robot DI | Lower_Completed_Cuts |
| `_IO_EM_DO_04` | Configured robot DI | Tilt_DEG_Pos_Deflector |
| `_IO_EM_DO_05` | Configured robot DI | Complete_Runner_Drop |
| `_IO_EM_DO_06` | Configured robot DI | DEG_Home_And_Ready |

**Robot inputs the PLC receives** (known from physical mapping):
| PLC Input | Meaning |
|---|---|
| `_IO_EM_DI_00` | KM_Selected_DEG1_Or_3 |
| `_IO_EM_DI_01` | KM_Selected_DEG2_Or_3 |
| `_IO_EM_DI_02` | KM_Command_To_Home |
| `_IO_EM_DI_03` | KM_Infront_Upper_Deg |
| `_IO_EM_DI_04` | KM_Infront_Lower_Deg |
| `_IO_EM_DI_05` | KM_Command_to_Cut |
| `_IO_EM_DI_06` | KM_Away_From_Deg |
| `_IO_EM_DI_07` | KM_Command_To_Drop |
| `_IO_EM_DI_08` | KM_Door_Is_Close |
| `_IO_EM_DI_10` | KM_Emergency_Stop |

### 2.6 Searching Ladder Logic in `.docx` Exports

The Degater project's `D14/` directory contains CCW ladder logic exports as `.docx` files. These are not images — they are text paragraphs with PLC instructions. Use `python-docx` to search them programmatically:

```python
from docx import Document

doc = Document("D14/d14variables/Degaters_Operation.docx")
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    if "TON" in text or "XIC" in text or "OTE" in text:
        print(f"Para {i}: {text[:200]}")
```

**Instructions found in these exports:**
- `XIC` — Normally Open contact
- `XIO` — Normally Closed contact
- `TON` — On-delay timer (e.g., `TON TON_1 T#500ms`)
- `OTE` — Output Energize coil
- `OTS` — Output Set (latch)
- `OTR` — Output Reset (unlatch)
- `BST` / `NXB` / `BND` — Branch start / next branch / branch end

**The `.docx` exports do NOT contain robot controller logic.** Robot wait/timeout alarms ("wait DI-186 Time out") originate in the robot's AS-language program, not the PLC ladder.

---

## Section 3: I/O Reaction Validation

> **Related references:** `references/io-reaction-v3-implementation.md`, `references/io-reaction-v3-test-recipes.md`, `references/io-reaction-polling-rate.md`, `references/session-2026-06-01-double-alarm-fix.md`

Real-time validation that verifies PLC outputs produce expected input sensor reactions within a timeout window. The authoritative umbrella for the v3 architecture (v1 reference in `references/io-reaction-alarm-watcher.md` for historical context).

### Architecture

```
Poll cycle (every N ms via QTimer)
    │
    ▼
PollWorker reads all I/O tags via pycomm3
    │ io_values dict
    ▼
MainWindow._on_poll_complete(io_values)
    ├─ UI Panels update
    ├─ IOAlarmWatcher.check(io_values)
    │   ├─ Phase 1: detect_output_transition()
    │   ├─ Phase 2: evaluate_pending_deadlines()
    │   └─ Phase 3: continuous_validate() with grace suppression
    ├─ TimelineRecorder.record_snapshot() (every Nth poll)
    └─ Diagnostics tab live panel
```

No extra threads. The watcher runs synchronously inside the poll handler.

### The Double-Alarm Problem

One cylinder motion produces two alarms in naive (v1) implementations:

| Time | Event | v1 Result | v3 Result |
|---|---|---|---|
| T+0.0s | Output turns ON | Transition check pending | Transition pending |
| T+0.2s | Sensors haven't moved | **Continuous alarm fires** | **Suppressed by grace** |
| T+1.0s | Deadline expires | **Transition alarm fires** | No alarm (OK) |

**Grace rules in `_continuous_check()`:**
1. **Output-recently-changed grace:** If `(now - changed_at) < timeout_sec`, suppress continuous check
2. **Transition-alarm-fires grace:** If transition alarm fired within `timeout_sec`, suppress continuous check
3. **Transition-dedup fix:** After firing a transition alarm, also add the continuous composite key to `_acked_faults` to prevent a second alarm for the same stuck sensor

### Dual-Solenoid Cylinder: False-Alarm Prevention

For a comprehensive deep-dive, see `references/dual-solenoid-guard-design.md` (initial analysis) and `references/session-2026-06-02-sensor-sanity-check.md` (Sensor Sanity design at rest).

The session reference covers the entire Sensor Sanity check lifecycle, including false-alarm prevention logic for dual-solenoid assemblies. Review it for guard strategies.

### What Falsely Alarms

When Extend_Sol turns OFF → watcher immediately checks Retract sensors (off_inputs) → FALSE → ALARM. But Retract_Sol hasn't been commanded yet. The cylinder is still physically extended.

### Sensor Sanity: Detecting Dead Sensors While at Rest

The Dual-Solenoid guard in Section 3 prevents false alarms, but creates a **blind spot at rest**: when both solenoids are OFF, the cylinder is at rest and no transition or continuous check runs. A **broken or unplugged sensor goes completely undetected**.

**Solution: Sensor Sanity Check** (added June 2, 2026)

A separate check phase running after all pair-level checks validates a physical invariant:

> For a single cylinder in a dual-solenoid assembly, both position sensors (Ext and Ret) should NEVER be FALSE simultaneously.

| Condition | Sensor Sanity Alarm? |
|---|---|
| One sensor TRUE, cylinder at rest | ❌ No alarm — known position |
| Both sensors FALSE for > timeout (at rest) | ✅ **ALARM** — unplugged/broken |
| Any solenoid ON | ❌ Skipped — I/O Reaction handles this |
| Sensors recover (one goes TRUE) | ✅ Auto-clears, can re-fire |

**Key implementation details:**
- Runs per-cylinder independently (Cyl_1 and Cyl_2 in Degater assemblies)
- Extracts cylinder number from tag names using literal `"Cyl"` token extraction (e.g., `D2_Low_Ext_Cyl_1_Ext` → cylinder `1`)
- Uses a **stable dedup key** (no timestamp) to fire once per fault: `f"SANITY|DEG{deg}_{cyl}_Cyl{num}"`
- Discards fired key when sensors recover so new failures can re-alarm
- Must clear `_sensor_sanity_timers` and `_sensor_sanity_fired` in `clear()`

**Full design:** `references/session-2026-06-02-sensor-sanity-check.md`

**Independent timeout rationale:** `references/session-2026-06-02-sensor-sanity-timeout.md`

#### The Fix: Two Guards in Python (NOT JSON Changes)

**Guard 1 — `_start_check()` transition guard:**
When a solenoid turns OFF, only start an off_inputs check if the opposing solenoid is already ON:

```python
if not out_val and io_values is not None:
    opp = self._opposing_solenoid(pair)
    if opp:
        opp_val = self._resolve(io_values, opp["output_physical"], opp.get("output_tag", ""))
        if opp_val is None or not opp_val:
            # Opposing solenoid is OFF — cylinder is at rest, not moving.
            # Do NOT start an off_inputs check or we'll false-alarm.
            return
```

**Guard 2 — `_continuous_check()` continuous guard:**
When a solenoid is OFF, only validate `on_inputs` (solenoid ON). The `off_inputs` describe the DESTINATION after a transition — the transition check already verified arrival. Removing off_inputs entirely broke sensor-at-rest monitoring forever.

```python
# In _continuous_check(), solenoid OFF branch:
expected_phys = []
expected_log = []
note = ""
# Continuous only validates on_inputs. off_inputs are transition-only.
```

#### Why NOT Remove off_inputs from JSON

Removing off_inputs from the JSON eliminated ALL off-side monitoring. Transition checks couldn't verify the cylinder actually arrived at the retracted position. The fix is guards in Python, not removing data from JSON.

#### _opposing_solenoid() Helper

```python
def _opposing_solenoid(self, pair: dict) -> dict | None:
    """For dual-solenoid cylinders, return the opposite pair entry."""
    deg = pair.get("degater", 0)
    func = pair.get("function", "")
    if "Extend" not in func and "Retract" not in func:
        return None
    opp_func = func.replace("Extend", "Retract") if "Extend" in func else func.replace("Retract", "Extend")
    for p in self._pairs:
        if p.get("degater") == deg and p.get("function") == opp_func:
            return p
    return None
```

#### Plain-English Alarm Messages

The `_build_alarm()` method uses the `output_value` field (added to `_PendingCheck`) to say "turned ON", "turned OFF", or "stayed ON" in plain English:

```python
deg_str = "SYS" if check.degater == 0 else f"DEG{check.degater}"
action = "stayed ON" if continuous else ("turned ON" if check.output_value else "turned OFF")
msg = f"{deg_str} {check.function} {action}, but {missing_phrase}."
```

Missing inputs are filtered to remove blanks:

```python
missing_display = [t.strip("_") for t in missing if t and t.strip()]
```

### Runtime Timeout Adjustment

When the user changes timeout in the Diagnostics tab, extend existing pending check deadlines:

```python
def set_timeout_sec(self, value: float) -> None:
    old = self._timeout_sec
    delta = value - old
    if abs(delta) < 0.05:
        return
    self._timeout_sec = value
    for check in self._pending.values():
        check.deadline += timedelta(seconds=delta)
```

### Auto-Degater Detection from KM Robot Inputs

Read KM robot selection inputs directly from the PLC and determine which degater is active:

```python
def _detect_active_degaters(self, io_values):
    sel_1_or_3 = io_values.get("_IO_EM_DI_00", False)  # DEG1 or DEG3
    sel_2_or_3 = io_values.get("_IO_EM_DI_01", False)  # DEG2 or DEG3
    if sel_1_or_3 and not sel_2_or_3: return ["DEG1", "SYS"]
    elif not sel_1_or_3 and sel_2_or_3: return ["DEG2", "SYS"]
    elif sel_1_or_3 and sel_2_or_3: return ["DEG3", "SYS"]
    else: return ["SYS"]
```

**Important:** Do NOT filter alarm pairs by active degater if the ladder logic checks ALL degaters for home/safety signals. Use auto-detection for UI display only; monitor all pairs unconditionally.

### Poll Rate Selection

Pneumatic cylinder sensors settle in 100–500 ms. At 1-second polling, the sample may capture sensors in their old state.

```python
self._poll_rate_combo = QComboBox()
for label, ms in [("100 ms", 100), ("250 ms", 250), ("500 ms", 500), ("1000 ms", 1000)]:
    self._poll_rate_combo.addItem(label, ms)
# Wire to QTimer.setInterval()
### Testing Without PLC (WSL)

See `references/io-reaction-v3-test-recipes.md` and the test command at the end of this section for full unit tests. A quick example:

```python
def test_grace_period():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)
    values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": False, "_IO_X1_DI_02": False}
    alarms = watcher.check(values, now)
    assert len(alarms) == 0   # suppressed by grace
    alarms = watcher.check(values, now + timedelta(seconds=1.5))
    assert len(alarms) == 1
    assert "continuous" in alarms[0].message.lower()
```

---

## Section 3.5: Degater-Specific Alarm Debugging

> **Former standalone skill:** `plc-degater-io-alarm-debugging`

Session-specific debugging patterns for the Degater PLC Tool's I/O alarm watcher. Consolidated here for operational reference.

### Complete Diagnostic Workflow

When the user reports "alarms keep firing" or "text keeps changing":

1. **Get the alarm CSV** — read messages, severity, timestamps
2. **Get the timeline JSON** — extract snapshots around alarm time
3. **Trace the output + sensor values** during the alarm window
4. **Check for these patterns**:
   - Alarm text alternates between Ext and Ret sensors? → dual-solenoid off_inputs
   - Alarm fires immediately when output turns OFF? → dual-solenoid off_inputs
   - Duplicate transition + continuous alarms? → missing dedup key
   - Alarm fires during sensor transition? → increase timeout or polling rate
   - False alarms from unselected degaters? → check degater filtering (removed)
5. **Simulate with a Python script** before rebuilding the EXE (see test command below)
6. **Check key files**:
   - `src/plc_tools/polling/io_alarm_watcher.py` — alarm engine
   - `src/plc_tools/catalog/io_alarm_pairs.json` — 48 I/O pairs
   - `src/plc_tools/gui/main_window.py` — poll timer, record trigger
   - `src/plc_tools/recording/timeline_recorder.py` — snapshot save with subsampling
   - `src/plc_tools/catalog/io_catalog.py` — 127 known I/O tags with direction metadata

### Plain-English Alarm Messages

The `_build_alarm()` method should produce operator-readable sentences, not raw tag dumps.

#### Message Template

```python
deg_str = "SYS" if check.degater == 0 else f"DEG{check.degater}"
action = "stayed ON" if continuous else ("turned ON" if check.output_value else "turned OFF")
msg = f"{deg_str} {check.function} {action}, but {missing_phrase}."
```

#### Building the Missing-Inputs Phrase

```python
missing_display = [t.strip("_") for t in missing if t and t.strip()]
# Filter blanks — prevents broken phrases like "the expected input '' did not turn on"

if len(missing_display) == 1:
    missing_phrase = f"the expected input '{missing_display[0]}' did not turn on"
else:
    input_list = ", ".join("'" + t + "'" for t in missing_display)
    missing_phrase = f"the expected inputs {input_list} did not turn on"
```

#### Appending the Context Note

```python
if note:
    msg += f"\n  → {note}"
```

#### Example Outputs

| Scenario | Output |
|---|---|
| Single missing sensor | `DEG2 Lower Extend turned ON, but the expected input 'D2_Low_Ext_Cyl_1_Ext' did not turn on.` |
| Multiple missing sensors | `DEG2 Lower Extend turned ON, but the expected inputs 'D1_Ret_1', 'D1_Ret_2' did not turn on.` |
| Continuous alarm (output stayed ON) | `DEG2 Lower Extend stayed ON, but the expected input 'D2_Low_Ext_Cyl_1_Ext' did not turn on.` |
| Output turned OFF | `DEG2 Lower Extend turned OFF, but the expected input 'D2_Low_Ext_Cyl_1_Ext' did not turn on.` |
| With `note_on`/`note_off` | `...did not turn on.\n  → Lower degating cylinder is commanded to extend...` |

#### Required: `output_value` on `_PendingCheck`

Add `output_value: bool` to the `_PendingCheck` dataclass so `_build_alarm()` knows whether the output turned ON or OFF. Both instantiation sites (transition and continuous) must pass `out_val`.
---

### Testing Command (Python Simulation, No PLC Required)

```python
from plc_tools.polling.io_alarm_watcher import IOAlarmWatcher
w = IOAlarmWatcher(json_path="src/plc_tools/catalog/io_alarm_pairs.json", timeout_sec=4.0)

# Simulate exact cycle from timeline
io_vals = {
    "DEG2_Lower_Ext_Sol": True,
    "D2_Low_Ext_Cyl_1_Ext": False,
    "D2_Low_Ext_Cyl_2_Ext": False,
}
alarms = w.check(io_vals)
print(alarms)
```

---

## Section 3.5: Degater-Specific Alarm Debugging

> **Related reference:** `references/io-reaction-alarm-watcher.md#direction-aware-fail-safe-read-policy`

How to handle pycomm3 read failures in the poll worker:

| Direction | Read Failure Behavior | Rationale |
|---|---|---|
| **INPUT** | Return `False` (fail-safe) | Sensor unplugged → should trigger alarm |
| **OUTPUT** | Preserve last-known value | Prevents solenoid display flicker during transient comm spikes |
| **STATUS** | Return `False` (fail-safe) | Status bits should always be readable; failure means fault |

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

**Danger without this:** If read error caches `True` for an unplugged sensor, the watcher sees it as still ON and never fires an alarm.

### The Hidden Cost: Output Read Failures Blind the Alarm Watcher

The direction-aware policy above prevents **display flicker**, but it creates a far worse problem on Micro870 PLCs: **outputs that fail to read are invisible to the transition alarm system.**

The `IOAlarmWatcher` relies on `_start_check()` seeing an output transition (OFF → ON) to begin a pending deadline. If the physical address (e.g. `_IO_X3_DO_05`) reads unreliably, the poller falls back to `last_known_values` — which is `False` from the last successful read. The watcher therefore:

1. **Never sees the OFF→ON transition** on the first successful read after multiple failures
2. **Starts the timer late** — by the time the output is visible, sensors have already timed out
3. **Never fires a transition alarm** if the read failure rate is high enough to always hide the transition

**Why Micro870 DO_ addresses fail:** The Compact I/O and Embedded Module digital outputs are write-only in many firmware versions. pycomm3 returns `"no response"` or `"Tag doesn't exist"` for physical DO_ reads. Symbolic tag names (program-level tags like `D1_Low_Justify_Ext_Sol`) may succeed where physical addresses fail — test with the actual PLC before assuming.

**Symptom:** A robot alarm like "wait DI-186 Time out" fires, but the PLC Tool shows **zero alarms** because the watcher never started its timer. The ladder is working correctly; a sensor is physically failed. The tool simply couldn't see the output turn on.

**Detection:** Watch for outputs whose `io_values` in the CSV/timeline show `True` only ~30-50% of the time with `None`/error in between. High failure rate on DO_ tags is the smoking gun.

**Fix options (software-side only):**
- **Option A — Try symbolic names:** Read `D1_Low_Justify_Ext_Sol` instead of `_IO_X3_DO_05`. Symbolic program tags often read reliably even when physical addresses don't.
- **Option B — Monitor PLC state bits:** Track internal ladder variables (`USER_BIT_16`, `USER_BIT_22`, etc.) instead of physical outputs. State bits are regular program tags and read reliably.
- **Option C — Pattern-based stuck-sensor detection:** Alert if a sensor stays OFF for longer than its normal cycle time, regardless of whether the output was visible. No dependency on output reads.

> **Session reference:** `references/session-km-robot-di186-wait-timeout-investigation.md` — Full ladder trace for DI-186 robot timeout: root cause (Cyl3_Ext sensor failed), why the watcher missed it, and all three fix options with pros/cons.

---

## Section 5: PyInstaller Bundling

> **Related references:** `references/pyinstaller-datas-mapping.md`, `references/pyinstaller-bloat-cleanup.md`

### Asset Path Resolution

```python
from pathlib import Path
import sys

def _asset_path(filename: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "plc_tools" / "assets" / filename
    return Path(__file__).parent.parent.parent / "assets" / filename
```

| `datas` entry | Correct `_MEIPASS` path |
|---|---|
| `('src/plc_tools/assets', 'plc_tools/assets')` | `sys._MEIPASS / "plc_tools" / "assets"` |
| `('src/plc_tools/gui/assets', 'plc_tools/gui/assets')` | `sys._MEIPASS / "plc_tools" / "gui" / "assets"` |

### Silent Data-File Failure

Data files (JSON, CSV) fail **silently** when missing from `datas`:

```python
if len(watcher._pairs) == 0:
    logging.error("No alarm pairs loaded — io_alarm_pairs.json missing from bundle")
```

**Never** `try/except FileNotFoundError: pass` on data loads. Always warn on 0 records.

### Dead-Code Audit Before Build

```bash
# 1. Find all Python source files
find src/ -name "*.py"

# 2. For each module, grep the entire tree for its class name
# If ZERO non-class-definition hits, the module is dead
grep -r "FaultLogTab\|fault_log\.py" src/ --include="*.py" | grep -v "class FaultLogTab"

# 3. Check main entry point for instantiation
grep -r "FaultLogTab(" src/plc_tools/gui/main_window.py
```

### Pruning Checklist

- [ ] Remove dead `hiddenimports`
- [ ] Replace directory `datas` with individual files if directory has dead weight
- [ ] Add `excludes` for wrongly-included stdlib modules: `tkinter`, `matplotlib`, `scipy`, `pandas`, etc.
- [ ] Purge `__pycache__` and `.egg-info`
- [ ] Previous `.exe` is not running (or renamed) before rebuild

---

## Section 6: Diagnostics Tab Safety & Reconnect Reliability

> **Related reference:** `references/session-2026-06-02-diagnostics-freeze-reconnect.md`

### 6.1 Never Auto-Load Data-Heavy Tabs on Tab Switch

If a tab requires synchronous CIP reads, **do not auto-load it when the user switches to it.** The synchronous pycomm3 calls block the GUI thread, which has cascading effects:

1. **GUI freeze** — The main thread is blocked for seconds while CIP objects are read
2. **Poll worker errors** — The background `_PollWorker` continues on its QThread but shares the pycomm3 instance; its reads now error because the synchronous calls are hogging the CIP session
3. **False alarms** — Read errors force outputs to `False` in cached `io_values`, which trips the `IOAlarmWatcher`

**Fix pattern:** Make the tab load **manual** (Refresh button) or run it in a dedicated background thread with result delivery via Qt signal.

```python
# BAD — in _on_nav_changed():
elif index == 5:
    self._load_diagnostics()   # Synchronous CIP blocking!

# GOOD — only load on initial connect + Refresh button click
def _on_nav_changed(self, index):
    self._stack.setCurrentIndex(index)
    # NO auto-load here

def _on_connect(self, ...):
    ...
    self._load_diagnostics()   # Once on connect

def _on_refresh_clicked(self):
    self._load_diagnostics()   # Only when user asks
```

### 6.2 Disconnect Must Wait for In-Flight CIP Reads

pycomm3 is **not thread-safe** for concurrent operations on the same connection. Tearing down the TCP socket while an in-flight CIP read is active leaves it in a **half-closed state** on the Micro870. The PLC still thinks the old CIP/TCP session is alive and rejects the new `open()` attempt.

**Two-layer fix:**

**Layer 1 — Client-side idle wait (in `_do_disconnect()`):**
```python
def _do_disconnect(self):
    if self._poll_timer and self._poll_timer.isActive():
        self._poll_timer.stop()
    # Wait for in-flight poll to finish before tearing down socket
    waited = 0.0
    while self._poll_worker and getattr(self._poll_worker, "_busy", False) and waited < 0.3:
        time.sleep(0.05)
        waited += 0.05
    self._driver = None
    self._connection_manager.disconnect()
```

**Layer 2 — Server-side cooldown (in `ConnectionManager.connect()`):**
```python
def connect(self, ip, slot=0, plc_type="micro800"):
    if self.is_connected():
        self.disconnect()
        time.sleep(0.8)  # Let Micro870 GC old TCP/CIP session
    self._driver = self._create_driver(ip, slot, plc_type)
    return self._driver.open()
```

**Why both?** Either alone is insufficient. The idle wait prevents mid-read teardown; the cooldown gives the PLC time to garbage-collect the old session. Together they make reconnect reliable under live PLC load.

**Micro870-specific note:** Unlike ControlLogix, the Micro870 does not aggressively garbage-collect half-closed sessions. A sub-second sleep after disconnect is required for reliable reconnect.

### 6.3 Tag Naming Consistency Across UI Generation

A double underscore in the UI (`D1__Low_Grip_Close_Sol`) that is NOT present in the catalog means the bug is in **UI generation code** (string formatting), not the catalog.

**Search pattern:** Look for ternaries or f-strings with `__` in tab generation code:
```python
# BAD — special case in UI generation
output_name = f"D{degater_num}__Low_Grip_Close_Sol" if degater_num == 1 else f"D{degater_num}_Low_Grip_Close_Sol"

# GOOD — uniform naming
output_name = f"D{degater_num}_Low_Grip_Close_Sol"
```

**Verification:** `grep -n '__' src/plc_tools/gui/tabs/io_status.py` should return no hits in tag generation strings.

---

## Section 7: Playback & Recording — Standalone Review Window

> **Related references:** `references/playback-review-window.md`, `references/alarm-marker-slider.md`, `references/playback-live-mode-toggle.md` (deprecated), `references/playback-info-window.md` (deprecated)

### Problem

When the user loads a recording for review, three bad things happen simultaneously:

1. **Live polls continue** — the background `QTimer` keeps firing, and `_on_poll_done()` overwrites the playback display with fresh live PLC data
2. **Outputs don't stay on** — an aggressive stability filter in `_on_playback_update()` suppresses boolean values that haven't been stable for 2 snapshots, making solenoids appear to flicker off
3. **No visual indication of mode** — the user can't tell whether they're looking at live data or a recording

### What Failed: Mode-Toggle Architecture (deprecated)

Earlier attempts used a `MainWindow._data_mode` flag ("live" ↔ "playback") that stopped the poll timer in playback mode and showed a "▶ PLAYBACK" badge in the ConnectionBar. This was **completely removed** in v2.23.10 because:

- **Live data leaked** — queued poll events still fired after `QTimer.stop()`, overwriting playback
- **Outputs flickered** — the stability filter hid real ON values
- **User confusion** — toggling back and forth between modes was unintuitive
- **Connection bar clutter** — the PLAYBACK badge added visual noise
- **Button redundancy** — `_mode_btn` in the tab + `_playback_badge` in the bar = two sources of truth

**All mode-toggle code removed:**
- `_set_data_mode()` from `MainWindow` — replaced by standalone review window
- `_data_mode` attr from `MainWindow` — no longer needed
- `mode_changed` Signal from `PlaybackRecordTab` — disconnected
- `_playback_badge`/`set_playback_mode()` from `ConnectionBar` — removed
- `_mode_btn`/`_toggle_mode()` from `PlaybackRecordTab` — removed; no buttons at all

The correct pattern: **never switch the main app's mode**. The main app is always live. Review happens in a separate `QMainWindow`.

### What Works: Standalone Playback Review Window (v2.23.17 — Final Architecture)

When the user wants to review a recording **without disrupting live PLC monitoring**, open a separate `QMainWindow` instead of switching the main app's mode.

**Architecture (v2.23.17 — final, no in-app playback):**
```
MainWindow (live PLC, always running — never stops polling)
    └── PlaybackRecordTab (index 4)
            ├── ▶ Start Recording
            ├── ■ Stop Recording
            ├── 📂 Load Recording
            └── ▶ Playback Recording → opens PlaybackReviewWindow
                    └── PlaybackReviewWindow (separate QMainWindow)
                            ├── DEG 1 / DEG 2 / DEG 3 / System Controls / Robot Interface tabs
                            ├── Inputs (green) / Outputs (red) with Physical Address column
                            ├── Timeline slider with red alarm arrows + TimelineRuler (30-min labels)
                            ├── Double-click arrow → jumps ~10 sec before alarm
                            └── Transport controls (play/pause, speed, prev/next)
```

**Key features:**
- **No mode switching** — main app stays live; review window is completely isolated
- **No playback_update signal** — playback data never goes to live tabs. The crash source was `_on_playback_update()` pushing snapshots to `_tab_io` and `_tab_all_tags` while live data was also coming in.
- **Catalog-based I/O classification** — uses `io_catalog.KNOWN_IO_TAGS` with `"direction": "INPUT"`/`"OUTPUT"` to split tags correctly. Never use heuristics like `_is_output_tag()`.
- **Alarm markers** — red downward arrows painted by `AlarmOverlay` (transparent sibling widget) above the slider groove at snapshot indices where `snapshot.alarm_events` fired. See Z-order note below.
- **Timeline ruler** — `TimelineRuler` sibling widget above `AlarmOverlay` shows 30-minute tick marks and `H:MM` labels (e.g., `0:00`, `0:30`, `1:00`)
- **Double-click pre-alarm seek** — double-clicking an arrow jumps ~10 seconds before the alarm (computed from actual polling interval estimated from adjacent snapshot timestamps)
- **Click-to-jump** — single-clicking an arrow seeks to the alarm snapshot and auto-pauses
- **Fullscreen/maximized** — `showMaximized()` on a separate `QMainWindow`
- **Speed control** — x1/x2/x4/x8/x16 playback speed

**Critical: Z-order overlay pattern for widgets painting above QSlider**

Drawing alarm markers inside `QSlider.paintEvent()` or the parent window's `paintEvent()` is **invisible** because the slider repaints its groove/handle on top. The correct pattern is a **transparent sibling widget**:

```python
class AlarmOverlay(QWidget):
    """Transparent sibling widget that paints red alarm arrows above the QSlider."""

    def __init__(self, parent: QWidget, slider: QSlider, ...):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)   # pass clicks through
        self.setAutoFillBackground(False)                          # no flickering
        self._slider = slider
        self.resize_to_slider()
        self.show()
        self.raise_()  # paint AFTER slider

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_to_slider()

    def resize_to_slider(self):
        geo = self._slider.geometry()
        self.setGeometry(geo.x(), geo.y(), geo.width(), geo.height())
```

**Anti-pattern:** `WA_TransparentBackground` causes flickering and paint artifacts on some Qt styles. Use `setAutoFillBackground(False)` instead.

**Parent's `resizeEvent()` must align overlays:**
```python
def resizeEvent(self, event) -> None:
    super().resizeEvent(event)
    self._alarm_overlay.resize_to_slider()
    self._ruler.resize_to_slider()
```

**Why the crash happened (and why it was removed):**

The original in-app playback pushed snapshot data to live tabs via `playback_update` signal:
```python
# In _on_playback_update() — REMOVED in v2.23.17:
self._tab_io.set_connected(True)
self._tab_io.update_io_values(bool_values)
self._tab_all_tags.update_io_values(bool_values)
```

Problems:
1. **Race condition** — `setUpdatesEnabled(True/False)` block was interrupted by async poll events
2. **Stability filter fighting live data** — `_playback_last_values` / `_playback_stability_counter` suppressed real ON values
3. **False alarms** — read errors during playback forced `False` into cached `io_values`
4. **No visual isolation** — user couldn't tell if they were looking at live or recorded data

**Fix:** Delete the entire `_on_playback_update()` method, remove `playback_update` signal, remove `PlaybackStrip` widget, and strip `PlaybackRecordTab` to only Load + Review buttons. Playback is **only** in the standalone window.

**Files:**
- `gui/playback_review_window.py` — `PlaybackReviewWindow`, `AlarmOverlay`, `TimelineRuler`, double-click logic
- `gui/tabs/playback_record.py` — simplified to recording controls + review button (270 lines, down from 771)
- `recording/timeline_recorder.py` — `Snapshot.alarm_events` stores I/O Reaction alarms per snapshot
- `gui/main_window.py` — removed `_on_playback_update()`, `_pb_strip` widget, all playback wiring

**Files:**
- `gui/playback_review_window.py` — `PlaybackReviewWindow(QMainWindow)` with DEG tabs, I/O tables, timeline, transport
- `gui/tabs/playback_record.py` — "▶ Playback Recording" button opens the review window
- `recording/timeline_recorder.py` — `Snapshot.alarm_events` stores I/O Reaction alarms per snapshot

**Catalog-based classification in `playback_review_window.py`:**

```python
from plc_tools.catalog.io_catalog import KNOWN_IO_TAGS

_TAG_DIRECTION: dict[str, str] = {}
for entry in KNOWN_IO_TAGS:
    name = entry.get("name", "")
    if name:
        _TAG_DIRECTION[name] = entry.get("direction", "INPUT")

def _get_direction(tag: str) -> str:
    """Return INPUT, OUTPUT, or STATUS from the live catalog."""
    if tag in _TAG_DIRECTION:
        return _TAG_DIRECTION[tag]
    clean = tag.lstrip("_")
    if clean in _TAG_DIRECTION:
        return _TAG_DIRECTION[clean]
    # Fallback only for un-catalogued tags
    upper = tag.upper()
    if "_SOL" in upper:
        return "OUTPUT"
    return "INPUT"
```

**Wiring in `PlaybackRecordTab`:**

```python
def _on_review(self) -> None:
    if not self._recording:
        return
    from plc_tools.gui.playback_review_window import PlaybackReviewWindow
    if hasattr(self, "_review_window") and self._review_window is not None:
        self._review_window.raise_()
        self._review_window.activateWindow()
        return
    self._review_window = PlaybackReviewWindow(self._recording, parent=self)
    self._review_window.closed_requested.connect(self._on_review_closed)
    self._review_window.showMaximized()
```

**Alarm events in snapshots:** Each snapshot stores `alarm_events: list[dict]` with `{severity, source, message, fault_key}`. These are captured from `IOAlarmWatcher.check()` in the poll handler and saved into the recording:

```python
# In main_window.py poll handler
alarms = self._io_alarm_watcher.check(io_values)
alarm_events = alarms  # store for recording
for alarm in alarms:
    self._tab_alarms.log_event(...)

# When recording
self._timeline_recorder.record_snapshot(snapshot_values, alarm_events)
```

### EM Module Outputs: Catalog Direction Fix

Seven tags on the EM module (`Upper_Ready_For_Parts`, `Lower_Ready_For_Parts`, `Upper_Completed_Cuts`, `Lower_Completed_Cuts`, `Tilt_DEG_Pos_Deflector`, `Complete_Runner_Drop`, `DEG_Home_And_Ready`) were originally classified as `"STATUS"` because they are program-level status bits. However, they physically map to `_IO_EM_DO_00` through `_IO_EM_DO_06` — these are **PLC → Robot digital outputs**.

**Fix:** Change their `"direction"` from `"STATUS"` to `"OUTPUT"` in `io_catalog.py`. This makes them appear in the Outputs table of the System Controls tab and the playback review window.

**Verification:** After the fix, `io_catalog.py` has 72 INPUT, 55 OUTPUT, 0 STATUS tags.

### Quality Gate

Before every build, run the full quality gate checklist in `references/quality-gate-checklist.md`:

1. Syntax check all changed files (`py_compile`)
2. Full-project AST parse (all 40 `.py` files)
3. Stale reference hunt (`grep -rn old_symbol src/`)
4. Backward-compat API shims preserved
5. Dead-code removal verified
6. Residual-effect check (QTimer orphan, disconnected signals, etc.)
7. Build verification (EXE size ~46 MB)

Zero-tolerance rule: no build is requested until the gate is green.

### Playback Info Window

The `PlaybackInfoWindow` is shown **after** the nav tab is switched (never before), and it is opened with `.show()` (non-modal) — never `.exec()` (modal). Consolidated in `references/playback-live-mode-toggle.md`.

### Robot Interface Tab in Playback

The Robot Interface tab (DI 185–191 from `robot_interface.py`) must also exist in the standalone playback review window. Build it with `_build_robot_tab()` and update per-snapshot with `_update_robot_tab()`. Import `ROBOT_DI_MAP` from the live tab module — never duplicate the definitions. See `references/session-2026-06-02-playback-robot-interface-tab.md` for full implementation.
---

## Section 8: Production Diagnostics & Crash Handling

When a PySide6 desktop app is deployed on a plant-floor workstation, unhandled exceptions must do more than write to a log file — an operator staring at a frozen screen needs to know what happened and where to find help.

### Crash Log Writer + Thread-Safe Popup

The crash handler writes to a path determined at runtime by whether the app is running as a PyInstaller-bundled EXE or from source:

| State | Crash Log Directory |
|---|---|
| **Frozen (PyInstaller EXE)** | `\dist\crash_logs\` — next to the `.exe` so operators can find it easily |
| **Source / development** | `%LOCALAPPDATA%\\Degater PLC Tool\\crash_logs\\...` |

Detection uses `sys.frozen` + `hasattr(sys, "_MEIPASS")` to prevent false positives from other bundlers.

```python
def _get_crash_dir() -> Path:
    frozen = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
    if frozen:
        exe_dir = Path(sys.executable).resolve().parent
        return exe_dir / "crash_logs"
    # ... fallback to LOCALAPPDATA / .local/share ...
```

**Why this matters:** Operators on the plant floor don't know about `AppData\\Local`. A crash log sitting next to the EXE is trivial to find, copy, and email to support. Development runs keep the old `%LOCALAPPDATA%` path so crash logs don't clutter `dist/` during testing.

Add a user-facing popup that fires from **any thread** after the log is written:

```python
def write_crash_log(exc_type, exc_value, tb) -> None:
    from pathlib import Path
    log_dir = Path(os.environ.get("LOCALAPPDATA", ".")) / "Degater PLC Tool" / "crash_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"crash_{datetime.now():%Y%m%d_%H%M%S}.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("... full traceback, version, platform, memory stats ...")

    # Show popup on main GUI thread regardless of where crash originated
    def _show():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText(f"Unhandled exception: {exc_type.__name__}")
        msg.setInformativeText(
            f"A crash log was saved to:\n{log_path}\n\n"
            f"Version: {__version__}"
        )
        msg.exec()

    if threading.current_thread() is threading.main_thread():
        _show()
    else:
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, _show)
```

**Why `QTimer.singleShot(0, _show)`:**
`QMessageBox.exec()` must run on the GUI (main) thread. Calling it from a background thread can deadlock Qt's event loop. `singleShot(0, ...)` schedules the popup to run in the main thread's next event-loop iteration.

### Pitfall: `SyntaxWarning` in Docstrings

Crash-log paths that contain backslashes trigger Python `SyntaxWarning` if not properly escaped in docstrings:

```python
# BAD — unescaped backslashes in docstring
"""Writes crash_log to %LOCALAPPDATA%\Degater PLC Tool\crash_logs ... """

# GOOD — double-escaped for docstring
"""Writes crash_log to %LOCALAPPDATA%\\Degater PLC Tool\\crash_logs ... """
```

Always audit docstrings that mention Windows paths after any change to the crash handler.

### Bytecode Verification for Suspected Sleep Bugs

When a reviewer (or static analysis) flags a `time.sleep` call as suspicious (e.g., "integer 333333" instead of "float 0.333"), verify the compiled bytecode instead of relying on the source:

```python
# audit_sleep.py — run against the compiled .pyc or the module itself
import dis, time, importlib

mod = importlib.import_module("plc_tools.gui.main_window")
for instr in dis.get_instructions(mod):
    if instr.opname == "LOAD_CONST" and isinstance(instr.argval, float):
        print(f"  line {instr.starts_line}: float constant {instr.argval}")
    if instr.opname == "CALL" or instr.opname == "CALL_FUNCTION":
        # Context needed to associate with LOAD_GLOBAL time.sleep
        pass

# Simpler: grep for magic integers in the compiled file
import marshal
with open("__pycache__/main_window.cpython-311.pyc", "rb") as f:
    f.read(16)  # skip header
    code = marshal.load(f)

for instr in dis.get_instructions(code):
    if instr.opname == "LOAD_CONST":
        val = instr.argval
        if isinstance(val, int) and val > 1000:
            print(f"  line {instr.starts_line}: suspicious int constant {val}")
```

In this session, the suspected `sleep(333333)` turned out to be `sleep(0.02)` — correct. The audit confirmed no integer constants >1000 appeared in the compiled `.pyc`.

---

## Section 9: Simulated Recordings for Offline Testing

Two approaches exist, controlled by how the user wants to work:

| Approach | Use When | Pros | Cons |
|---|---|---|---|
| **Standalone TCP Server** (NEW, preferred) | Testing the full app end-to-end: GUI polling, alarm watcher, diagnostics tab, I/O status, connect/disconnect | Zero GUI code changes; drives real poll worker; 17 fault types; manual writes; auto-fault mode | Requires separate terminal window for the server |
| **In-Process Recording Generator** | Testing playback review window layout, alarm marker rendering, time-seek behavior | Single process, easily batch-generated scenarios | Cannot test live polling, fault injection needs manual JSON editing |

### Approach 1 — Standalone TCP Server (Preferred)

See `references/session-2026-06-04-simulated-plc-server.md` for full architecture.

Quick start:

```bash
# Terminal 1 — start the server
python3 simulated_plc_server.py --timeline deg_timeline_20260525_224802.json --speed 5.0

# In the PLC Tool — File → Connect → Simulated DEG Server → IP 127.0.0.1
```

Fault injection while the server is running:
```
> fault list              # show all 17 faults
> fault inject DEG3_stuck_lower_ext 10
> fault auto on           # random intermittent faults every 15-60s
> speed 10.0              # 10x playback speed
> pause / resume
```

### Approach 2 — In-Process Recording Generator

When testing playback review windows, alarm markers, or UI changes, the user may not have access to the physical PLC or may want to validate behavior at his desk. Generate deterministic `.json` recordings with realistic degating cycles and configurable faults.

`generate_sim_recordings.py` — standalone Python script in project root (not shipped in `.exe`).

```bash
python3 generate_sim_recordings.py
```

Generates `dist/sim_*.json` files with 8 scenarios:

| File | Fault | Alarm Snapshots |
|---|---|---|
| `sim_01_normal_cycle.json` | None (clean) | 0 |
| `sim_02_stuck_sensor_lower_ext.json` | Cylinder extends, sensor stuck FALSE | 36 |
| `sim_03_slow_cylinder_retract.json` | Retract takes ~2.5s instead of 0.5s | 32 |
| `sim_04_grip_failure.json` | Grip solenoid ON, sensors stay FALSE | 26 |
| `sim_05_sensor_unplugged.json` | Both Ext and Ret FALSE simultaneously | 40 |
| `sim_06_opposing_solenoids_both_on.json` | Both extend + retract solenoids ON | 12 |
| `sim_07_mixed_deg1_faulty_deg2_normal.json` | DEG1 stuck, DEG2 clean | 36 |
| `sim_08_multiple_rapid_alarms.json` | Consecutive retract faults | 16 |

### Critical Bug Fix: Step Advancement Order

**Step advancement MUST happen BEFORE `make_alarm_events()`.** If it happens inside `_snapshot_tag_values()`, the alarm builder sees the next step and produces zero alarms.

```python
for i in range(num_snaps):
    for deg, sim in simulators.items():
        # 1. Advance step BEFORE generating snapshot
        if sim.snaps_in_step >= sim.steps[sim.step][1]:
            sim.step = (sim.step + 1) % len(sim.steps)
            sim.snaps_in_step = 0
            sim.step_start_snap = i

        # 2. Generate snapshot
        vals = sim._snapshot_tag_values(i)

        # 3. Generate alarms for CURRENT step
        events = sim.make_alarm_events(i, vals)
```

### Reproducibility

All random state is seeded. Same seed → identical recording. Use different seeds per scenario.

---

## Verification: Does Manual Mode Allow App Output Control?

| Ladder Pattern | App Writes in Manual (Run) | App Writes in Program |
|---|---|---|
| XIO breaks auto + manual uses OTL | ✅ Works in manual | ✅ Always works |
| XIO breaks auto + manual uses OTE + physical PB | ⚠️ Fights if PB not pressed | ✅ Works |
| No mode contact (auto always active) | ❌ Always fights | ✅ Works |
| OTE-only, no bypass | ❌ Always fights | ✅ Works |

> For the Degater project: OTE coils everywhere, no OTL. **Program mode is the correct troubleshooting approach.** Manual mode enables the physical pushbutton path, not app-driven writes.

---

## Pitfalls

1. **Filtering outputs by active degater when ladder checks ALL for home signal.** Do not suppress alarms from unwired stations if the home signal depends on all stations.
2. **Continuous check has zero grace.** Apply Grace Rules 1 + 2 from Section 3.
3. **Sensor unplug never alarms.** Without direction-aware fail-safe reads, INPUT errors cache `True` and hide failures.
4. **Tab-switch glitch alarms.** Require 4+ consecutive poll failures before alarming.
5. **Slow polling creates false "swaps."** 1-second sampling catches sensors mid-transition. Use 250 ms or faster.
6. **Proposing ladder logic fixes.** All fixes must be software-side: polling, filtering, UI tuning.
7. **Silently missing data files in bundle.** JSON catalogs not in `datas` cause empty collections with no error.
8. **Running EXE during rebuild.** Windows locks the `.exe`. Close it first or rename before rebuild.
| **Tag case drift across catalog, mapping, and JSON.** | A single-character case difference causes pycomm3 to return "no response" on every poll. Always rename tags in all three files atomically in one commit. Run `scripts/verify_tag_consistency.py` before every build. See the `plc-tag-case-consistency-guard` skill for the full checklist and detection script. |
| **Auto-reconnect warning threshold mismatch.** | Showing "after 2 attempts" but giving up at 10 creates user confusion. Use one threshold for both message and logic (e.g., warn at ≥5 attempts), or reword the popup to include the actual cap: "(up to 10 attempts)." Always use `self._auto_reconnect_attempts` as the single source of truth for both conditions. |
| **Hardcoded version strings in dialogs / splash screens / window titles.** | The dynamic `__version__` from `plc_tools.version` must be used everywhere UI shows a version. Any hardcoded string (e.g. `Version 1.05` in `QMessageBox.about`) will drift and confuse users after auto-bump increments the build. |
> **Session reference confirming this happened TWICE:** `references/session-2026-06-03-claude-bug-report-fix-and-rebuild.md`

| **Internal underscore drift within numbered tags (Cyl_N vs CylN).** | Catalog and mapping both use the SAME wrong name, so `verify_tag_consistency.py` passes — but the PLC rejects the tag with `"Tag doesn't exist"`. The fail-safe returns `False` for INPUTs, so the alarm watcher never sees the transition and faults go undetected. Verify with `grep -rn 'Cyl_[0-9]' io_catalog.py` after ANY tag addition or catalog edit. **Do not assume `verify_tag_consistency.py` alone catches internal format errors — it only detects MISALIGNMENTS between files.** |
| **Silent fallback to hardcoded catalog tags when pycomm3 cache is empty.** | `get_tag_list()` returns catalog-stored tag names with no user-visible indication. A renamed or deleted PLC tag appears as "live" but was never actually read. Fix: add `is_catalog_fallback: bool = False` to the tag value dataclass, set `True` during fallback, and wire a yellow warning banner in the consuming tab. See `references/session-2026-06-03-claude-bug-report-fix-and-rebuild.md` for full implementation. |
| **Pre-build gate false positives from system status tags.** | Tags like `KM_Command_To_Drop`, `DEG_MAN_AUTO`, and `Home_All_Manual_PB` are INPUTs that exist in the catalog but are NOT monitored by I/O alarm pairs (operator controls, not cylinder sensors). The gate reports them as "missing from alarm_pairs.json" unless you explicitly exclude them. Add an `ALARM_PAIR_EXCLUSIONS` set to `verify_tag_consistency.py` listing all operator-level tags. Only suppress from the "missing" check — NEVER from the "extra" check. |
| **Hardcoded version strings in dialogs / splash screens / window titles.** | The dynamic `__version__` from `plc_tools.version` must be used everywhere UI shows a version. Any hardcoded string (e.g. `Version 1.05` in `QMessageBox.about`) will drift and confuse users after auto-bump increments the build. |
11. **Synchronous CIP calls on the GUI thread.** `_load_diagnostics()` making multiple pycomm3 reads on the main thread stalls the poll loop, causes read errors in the background worker, and triggers false alarms. Always run heavy CIP reads in a background thread or make them manual (Refresh button).
12. **Disconnect without idle wait.** Tearing down the pycomm3 socket while `_PollWorker` has an in-flight read leaves a half-closed TCP session on the Micro870. The PLC rejects the next `open()`. Always wait for `_busy` to clear and add a server-side cooldown before reconnect.
13. **Double underscores from UI generation ternaries.** When the catalog uses single underscore but the UI shows double, the bug is in tab generation code (`f"D{num}__Tag"`), not the catalog. `grep` for `__` in `gui/tabs/` before assuming the catalog is wrong.
14. **Playback review window missing live tabs confuses operators.** The standalone review window must mirror every live tab that carries useful data — not just the I/O status tabs. When adding a live tab (Robot Interface, Alarms, Diagnostics), always add its playback equivalent to `PlaybackReviewWindow`. Import shared data structures (like `ROBOT_DI_MAP`) from the live tab module — never duplicate definitions.
15. **Searching PLC tag catalog for robot controller DI numbers.** A robot alarm like "wait DI-186 Time out" references the robot's internal I/O map, not the PLC's physical tags. DI-186 does not exist in `io_catalog.py` or `physical_mapping.py`. Always ask for the robot's I/O assignment table to map robot DI numbers to PLC output tags.
16. **pycomm3 `Socket.close()` without `shutdown()` on Windows.** pycomm3 only calls `socket.close()`, leaving the TCP connection in `TIME_WAIT` for ~60s. The Micro870 rejects new sessions until the port is released. Bypass pycomm3 and directly call `shutdown(SHUT_RDWR)` + `close()` on the raw `socket.socket` object inside the wrapper (`self._plc._sock.sock`) during `disconnect()`. Always follow with `gc.collect()` before creating a new driver instance to force Windows to reap the closed handle. See `references/session-2026-06-03-tcp-timewait-socket-teardown.md` for full implementation.
| **Overlapping `_ConnectWorker` threads due to uncancellable `QTimer.singleShot`.** | Using `singleShot` for auto-reconnect means the timer cannot be cancelled if the user clicks Connect during the delay window. Two workers collide on shared `ConnectionManager` state. Use a named `QTimer` with `.stop()` at every manual connect entry point (`_quick_connect`, `_show_connect_dialog`, `showEvent`). See `references/session-2026-06-03-overlapping-threads-cancellable-timer.md` for full details. |
| **No `_connect_in_progress` guard.** | Without a boolean flag, a manual click can launch a worker while an auto-reconnect retry is also in flight. Add `_connect_in_progress` and check it in `_try_reconnect()` before starting a new worker. Reset it in `_on_connect_finished()` regardless of success or failure. |
| **Shadowing `QThread.finished`** with a custom signal — PySide6 silently overloads the Python attribute, and Qt's native `finished()` emission leaks through with default-constructed args. Always use unique signal names like `connect_done`. See `references/session-2026-06-03-signal-shadowing-connect-worker.md`. |
| **Auto-reconnect warning threshold mismatch.** | A popup says "after 2 attempts" but the code gives up at 10. Users see the warning and think retrying stopped, but it silently continues. Always use one threshold for both message and logic, or reword the warning to include the actual cap (e.g., "Auto-reconnect will keep trying (up to 10 attempts)."). |
| **Silent fallback to hardcoded catalog tags in `get_tag_list()`.** | When pycomm3's tag cache is empty, the driver returns hardcoded catalog tags without telling the user. Stale or renamed tags show up as "live" but aren't actually read from the PLC. Fix: add `is_catalog_fallback: bool = False` to the `TagValue` dataclass, set `True` when returning catalog data, and surface a yellow warning banner in the UI. |
| **Discarding previous tool output when it contains "irrelevant" text** — Terminal grep/cat output may include hundreds of lines of noisy search results before the single line you actually need. Do NOT treat the entire output as "garbage to reset from." Extract the specific line(s) you need and continue the patch. Resetting aborts valid partial work and wastes the user's time. Better: `grep` with limited context, or use `search_files` with `output_mode=content` and `limit=5`. |
| **Continuing with garbled / hallucinated code after context corruption** — When the assistant's own context window starts producing nonsense output (garbled characters, repeated fragments, made-up method names), **STOP immediately** and ask the user to reset or clear the conversation. Do NOT try to "recover" by writing more code — the corrupted context will produce broken code that fails syntax checks. Thad explicitly expects this: "your getting off coarse", "try agin you not thinking straight", "why do you keep thinking carbled". These are signals to halt, not to push through. |

---

## Section 8: Auto-Connect / Auto-Reconnect Architecture

When a PLC diagnostic app is deployed at a plant-floor workstation, the operator expects it to reconnect automatically after a network hiccup or app restart. Implementing this correctly requires separating **startup auto-connect** from **runtime auto-reconnect**, tracking failure state without blocking the GUI, and surfacing warnings at the right time.

### Requirements

| Requirement | Implementation |
|---|---|
| Auto-connect on first startup | `showEvent()` with one-shot `_startup_connect_done` guard |
| Config source (in order) | Last known `ConnectionConfig` → `ProjectManager` entry → hardcoded default |
| De-selectable | Checkable `QAction` in File menu (`setCheckable(True)`) |
| Persist user preference | `QSettings("OrgName", "AppName")` |
| Auto-reconnect on disconnect | Trigger in `_do_disconnect()` if flag enabled and PLC was connected |
| Retry delay | 3 seconds between attempts (`QTimer.singleShot(3000, ...)`) |
| Warning threshold | After 2 consecutive failures → `QMessageBox.warning()` |
| Safety cap | Give up after 10 attempts to avoid infinite loops |
| State reset on success | Clear retry counter and warning flag so next incident starts fresh |

### Why Not Use a Single Global Timer

Do NOT run a background `QTimer` that periodically pings the PLC. That creates:
- Resource leakage when `_ConnectWorker` instances overlap
- GUI-thread coupling if the timer fires while a dialog is open
- Uncontrolled retry storms if the PLC is offline for hours

Instead, chain retries through the `_on_connect_finished()` callback using a **cancellable named `QTimer`**. Each retry is event-driven: one attempt finishes → schedule the next → only if still not connected. The named timer can be `.stop()`-ed when the user manually clicks Connect, preventing race conditions between auto-retry and manual intervention.

### Startup Auto-Connect (`showEvent`)

The `QMainWindow.showEvent()` is called every time the window is shown (including after being hidden on multi-monitor setups). Use a one-shot boolean flag so auto-connect happens exactly once:

```python
def showEvent(self, event) -> None:
    super().showEvent(event)
    if self._startup_connect_done or not self._auto_connect_enabled:
        return
    if self._conn_mgr.is_connected:
        return
    self._startup_connect_done = True
    cfg = self._resolve_config()   # see helper below
    self._auto_reconnect_attempts = 0
    self._auto_connect_failed_shown = False
    self._conn_bar.set_connecting(True)
    self._status_bar.showMessage(f"Auto-connecting to {cfg.ip_address}...", 5000)
    self._connect_in_progress = True
    self._reconnect_timer.stop()   # cancel any pending retry
    self._worker = _ConnectWorker(self._conn_mgr, cfg)
    self._worker.connect_done.connect(self._on_connect_finished)
    self._worker.start()
```

### Cancellable Reconnect Timer

Use a named `QTimer` instead of `QTimer.singleShot` so manual connect can cancel an armed retry:

```python
self._reconnect_timer = QTimer(self)
self._reconnect_timer.setSingleShot(True)
self._reconnect_timer.timeout.connect(self._try_reconnect)
```

### Runtime Auto-Reconnect (`_do_disconnect` hook)

The disconnect handler should remember whether the PLC was connected before teardown, then schedule a reconnect if auto-reconnect is enabled:

```python
def _do_disconnect(self) -> None:
    was_connected = self._conn_mgr.is_connected
    # ... existing teardown code ...
    self._conn_mgr.disconnect()
    # ...
    if was_connected and self._auto_reconnect_enabled:
        self._auto_reconnect_attempts = 0
        self._reconnect_timer.start(3000)   # named timer, can be cancelled
```

### Unified Retry Handler (`_try_reconnect`)

Use the same method for both startup retries and runtime retries. It resolves the config with a sensible fallback chain:

```python
def _try_reconnect(self) -> None:
    if self._conn_mgr.is_connected or self._connect_in_progress:
        return
    cfg = None
    if self._conn_mgr.config:
        cfg = self._conn_mgr.config          # last successful config
    else:
        entry = self._proj_mgr.get("DEG System BST33/35")
        if entry:
            cfg = entry.to_config()
    if cfg is None:
        cfg = ConnectionConfig(
            ip_address="192.168.1.197",
            slot=0,
            plc_type=PLCType.MICRO870,
            name="DEG System BST33/35",
        )
    self._conn_bar.set_connecting(True)
    self._connect_in_progress = True
    self._worker = _ConnectWorker(self._conn_mgr, cfg)
    self._worker.connect_done.connect(self._on_connect_finished)
    self._worker.start()
```

### Failure Tracking in `_on_connect_finished`

Aggregate both auto-connect and auto-reconnect failures in a single counter. After 2 attempts, show one warning popup. After 10, log and stop retrying:

```python
def _on_connect_finished(self, success: bool, error: str) -> None:
    self._conn_bar.set_connecting(False)
    self._connect_in_progress = False
    if success:
        self._auto_reconnect_attempts = 0
        self._auto_connect_failed_shown = False
        self._update_ui_connected()
    else:
        self._auto_reconnect_attempts += 1
        if self._auto_reconnect_attempts >= 2 and not self._auto_connect_failed_shown:
            self._auto_connect_failed_shown = True
            QMessageBox.warning(self, "Connection Warning",
                                "PLC connection could not be established after 2 attempts...")
        if self._auto_reconnect_enabled and self._auto_reconnect_attempts < 10:
            self._reconnect_timer.start(3000)
        elif self._auto_reconnect_attempts >= 10:
            self._tab_alarms.log_event("WARNING", "Connection",
                                        "Auto-reconnect gave up after 10 attempts.")
    self._worker = None
```

### Menu Integration

```python
self._auto_connect_action = file_menu.addAction("Auto Connect")
self._auto_connect_action.setCheckable(True)
self._auto_connect_action.setChecked(self._auto_connect_enabled)
self._auto_connect_action.triggered.connect(self._toggle_auto_connect)

def _toggle_auto_connect(self, checked: bool) -> None:
    self._auto_connect_enabled = checked
    self._settings.setValue("auto_connect", checked)
    self._status_bar.showMessage(f"Auto Connect {'ENABLED' if checked else 'DISABLED'}", 3000)
```

### Anti-Patterns

| Anti-Pattern | Why Dangerous | What To Do |
|---|---|---|
| Reconnect immediately (0s delay) | PLC needs TCP socket GC time; reconnect storms | Wait 3s between attempts |
| Infinite retry loop | Wastes network + fills log | Cap at 10 attempts |
| Show popup on every failure | Operator fatigue, modal hell | Show once at threshold (≥2) |
| `QTimer` at fixed interval | Overlaps with connect worker, leaks threads | Event-driven `singleShot` chaining |
| No config fallback | App fails if project entry is missing | Hardcoded default IP as last resort |
| `showEvent` without guard | Triggers on every window show/hide | `_startup_connect_done` boolean flag |
| **Shadowing `QThread.finished`** | Qt emits its own `finished()` at thread exit with zero-initialized args, causing phantom failure callbacks | Rename custom signal (`connect_done`) |

### Signal Shadowing: The `_ConnectWorker` Trap

A `_ConnectWorker(QThread)` class that declares:

```python
class _ConnectWorker(QThread):
    finished = Signal(bool, str)   # ❌ shadows QThread.finished()
```

...will receive **two** emissions after `run()` returns:

1. **Your explicit emission:** `self.finished.emit(True, "")` inside `run()` — correct.
2. **Qt's implicit emission:** `QThread` emits its native `finished()` signal when the thread exits. PySide6 maps this through the overloaded Python `finished` signal using **default-constructed values** `(False, "")`. This triggers `_on_connect_finished(False, "")` as a second callback.

**Impact:** Even after a successful connect, the phantom `(False, "")` callback increments `_auto_reconnect_attempts`, disables the connect bar, and schedules a `QTimer.singleShot(3000, self._try_reconnect)` retry. The connect button appears permanently dead because the retry counter keeps climbing.

**Fix:** Rename the custom signal to a unique name that cannot collide with any Qt built-in:

```python
class _ConnectWorker(QThread):
    connect_done = Signal(bool, str)   # ✅ unique name

    def run(self) -> None:
        try:
            ok = self._manager.connect(self._config)
            self.connect_done.emit(ok, "" if ok else "Connection refused")
        except Exception as exc:
            self.connect_done.emit(False, str(exc))
```

Update **all** call sites that connected to `self._worker.finished`:
- `_quick_connect`
- `_show_connect_dialog`
- `_try_reconnect`
- `showEvent` (startup auto-connect)

**Verification:** `grep -rn "finished" src/plc_tools/gui/main_window.py | grep "_worker"` should return zero hits.

> **Session reference:** `references/session-2026-06-03-signal-shadowing-connect-worker.md`

---

## References

### Core Design Documents

- `references/io-reaction-v3-implementation.md` — Full v3 architecture: grace logic, auto-detection, Diagnostics tab wiring
- `references/io-reaction-v3-test-recipes.md` — WSL unit tests (no PLC required)
- `references/io-reaction-polling-rate.md` — Adjustable polling rate, sampling considerations, Micro870 throughput limits
- `references/io-reaction-alarm-watcher.md` — **v1 historical context** (transition + continuous checks without grace periods)
- **`references/session-2026-06-04-simulated-plc-server.md`** — Standalone TCP simulated PLC server: timeline replay, write-aware fault injection, `_PLCShim` for zero-GUI-change integration

### Session-Specific Fix Notes

- `references/session-2026-06-02-tag-case-consistency-and-version-sync.md` — ...
- `references/session-2026-06-03-auto-connect-reconnect.md` — ...
- **`references/session-2026-06-03-claude-bug-report-fix-and-rebuild.md`** — Internal underscore drift: all 3 files share identical wrong names → verifier passes but PLC rejects tags. Reconnect warning threshold mismatch (2 vs 10). Silent `get_tag_list()` fallback: `is_catalog_fallback` flag + yellow UI banner pattern. Bytecode audit for `time.sleep` constant verification. Surgical JSON replacement technique (avoid `replace_all` corruption). Signal shadowing docstring fix with explicit QThread collision explanation.
- **`references/session-2026-06-03-crash-handler.md`** — Adding user-facing `QMessageBox.Critical` popup to existing `write_crash_log()`: thread-safe dispatch via `QTimer.singleShot(0, ...)` when crash originates in background thread; `SyntaxWarning` fix in docstring (double-escape Windows path backslashes).
- **`references/session-2026-06-03-crash-log-dist-path.md`** — Crash logs redirected: when frozen (PyInstaller EXE) write to `dist\crash_logs\` next to the `.exe` so operators can find them easily; when running from source use old `%LOCALAPPDATA%` path. Detection via `sys.frozen + hasattr(sys, "_MEIPASS")`.
- `references/session-2026-06-03-bytecode-audit-sleep.md` — **Bytecode audit technique: using `python -m dis` to verify `time.sleep` constants in compiled `.pyc` when a reviewer flags a suspected integer-vs-float bug**
- `references/session-2026-06-03-signal-shadowing-connect-worker.md` — PySide6 `QThread.finished` signal shadowing: why `_ConnectWorker.finished = Signal(bool, str)` caused phantom failure callbacks after every connect, and the rename-to-`connect_done` fix
- **`references/session-2026-06-02-playback-robot-interface-tab.md`** — Adding Robot Interface tab (DI 185–191) to standalone playback review window; importing `ROBOT_DI_MAP` from live tab module; mirroring all live tabs in playback
- `references/session-km-robot-di186-wait-timeout-investigation.md` — **KM robot "wait DI-186 Time out": full ladder trace showing why the watcher missed a justify sensor failure — Micro870 DO_ address read failures blind transition checks, Sensor Sanity cannot check single-sensor assemblies, and software-side fix options**
- `references/session-2026-06-02-playback-robot-interface-tab.md` — Adding Robot Interface tab (DI 185–191) to standalone playback review window; importing `ROBOT_DI_MAP` from live tab module
- `references/session-2026-06-03-auto-connect-reconnect.md` — Auto-connect on startup + auto-reconnect on disconnect: `showEvent()` guard, `QTimer.singleShot` chaining, 10-attempt safety cap, 2-attempt warning popup, File menu toggle with `QSettings` persistence
- `references/session-2026-06-04-playback-skip-seek.md` — Skip/seek buttons (±1m, ±5m, ±15m, ±1h) in `PlaybackReviewWindow`; time-based wall-clock seek with auto-pause on seek
- `references/session-2026-06-04-45min-simulated-recording.md` — 45-minute simulated recording generator at 500ms polling; step-scaling for compressed polling, fault window sizing anti-pattern
- `references/session-2026-06-01-plain-english-alarms-and-side-button-restraint.md` — Human-readable alarm messages (transition/continuous), blank-tag filtering, side-button popup removal (superseded by session above for side-button behavior)
- `references/session-2026-06-01-double-alarm-fix.md` — Transition/continuous dedup fix and degater filtering removal
- `references/session-2026-06-03-auto-45min-recorder.md` — **Auto 45-min circular recorder: `AutoRecorder` with IDLE/ACTIVE state machine, `deque(maxlen=27000)` circular buffer, first-state-change trigger, idle timeout, instant `copy_recent()` → `PlaybackReviewWindow`**- `references/session-2026-06-01-sensor-unplug-no-off-alarms.md` — Sensor-at-rest limitation: unmonitored when solenoid is OFF, both-sensor-false detection needed
- **`references/dual-solenoid-guard-design.md`** — Initial dual-solenoid false-alarm analysis and guard sketch
- **`references/session-2026-06-02-sensor-sanity-check.md`** — Sensor Sanity design at rest (per-cylinder, dedup, extraction from tag names)
- `references/session-2026-06-02-sensor-sanity-timeout.md` — **Sensor Sanity independent timeout: why sharing `timeout_sec` with I/O Reaction causes false alarms during transitions, and the fix (`sensor_sanity_timeout_sec=4.0`)**
- `references/playback-data-stability-filter.md` — **Updated**: why the 2-snapshot playback stability filter was removed (it blocked real ON values); correct pattern is single-source-of-truth mode toggle + poll discard guard
- `references/playback-review-window.md` — Standalone fullscreen playback review: `PlaybackReviewWindow(QMainWindow)` with I/O view + alarms + alarm-marked timeline, singleton pattern, separate from main app
- `references/session-2026-06-04-playback-skip-seek.md` — Skip/seek buttons (±1m, ±5m, ±15m, ±1h) and Restart in `PlaybackReviewWindow`; time-based seek with auto-pause, transport bar layout
- `references/session-2026-06-04-45min-simulated-recording.md` — 45-minute simulated recording generator at 500ms polling with 3 fault windows, step-scaling for compressed polling, anti-patterns for fault window sizing
- `references/alarm-marker-slider.md` — Custom `QSlider` with red alarm ticks: `paintEvent` overlay, click-to-jump signal, auto-pause on alarm marker click
- `references/playback-live-mode-toggle.md` — Live/playback mode toggle architecture: `_set_data_mode()`, poll discard guard, mode button in PlaybackStrip
- `references/playback-info-window.md` — Floating info dialog on recording load: metadata table, snapshot stats, "Return to Live" button with custom result code 42
- `references/playback-data-stability-filter.md` — Two-layer playback defense: last-known-value caching + 2-snapshot stability threshold
- `references/proactive-playback-mode.md` — **Proactive mode switch on Play click: set playback mode before timer starts to prevent live data leak**
- `references/timeline-subsampling-for-recording.md` — Decouple poll rate from record rate to bound 12-hour recording size

### PLC & Ladder Logic

- `references/degater-project-notes.md` — Session-specific findings: tag names, rung structure, OTE behavior, EMF conversion
- `references/ladder-logic-analysis-from-python.md` — Tracing the Python signal chain and verifying ladder supports manual writes

### Safety Patterns

- `references/manual-mode-popup-final.md` — Production Manual Mode dialog: photo, button layout, caching
- `references/manual-button-photo-popup.md` — Early popup pattern (superseded by final)
- `references/top-row-manual-status-button.md` — Mode banner and top-row status button

### Bundling

- `references/pyinstaller-datas-mapping.md` — Mapping table for images and JSON/CSV data files
- `references/pyinstaller-bloat-cleanup.md` — Dead-code/asset scanner and spec-pruning checklist

### Validation Scripts

- `scripts/convert_ladder_emf_to_png.py` — Batch-convert EMF ladder images from .docx to PNG via PowerShell
- `references/validate_io_alarm_pairs.py` — Pre-build validation: checks physical/logical tags in JSON pairs against the live catalog, flags zero-padding and missing tags

---

## Related Skills

- `pyinstaller-desktop-app` — Generic PyInstaller build guidance (this skill is domain-specific for PLCs)
- `elite-coder-toolkit` — General coding practices
- `systematic-debugging` — Debugging methodology
