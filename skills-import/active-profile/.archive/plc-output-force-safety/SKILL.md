---
name: plc-output-force-safety
description: "Safety patterns for output forcing in industrial PLC monitoring applications — manual mode interlocks, visual state feedback, and preventing accidental writes in auto mode."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [plc, industrial, safety, pycomm3, pyside6, micro800, output-force, interlock]
    related_skills: [elite-coder-toolkit, systematic-debugging, micro800-mode-operation]
---

# PLC Output Force Safety Patterns

Industrial desktop applications that allow manual override of PLC outputs must implement safety interlocks. Writing to an output while the machine is in auto mode can cause collisions, equipment damage, or injury.

## Core Principle

> **Output forcing is only permitted when the PLC program is in manual mode.** The GUI must detect the mode from the PLC in real time, lock controls in auto mode, and provide unambiguous visual feedback.

> **User preference (Degater project): Keep original ON/OFF/Release buttons always visible.** When in auto mode, dim the buttons (gray text, muted borders) so they look inactive. Any click on ON, OFF, or Release opens the Manual Mode dialog with a photo of the MAN-AUTO switch. This preserves the familiar layout while preventing accidental forces. Only in manual mode do the buttons brighten to full color and become functional.

## Detecting Manual Mode from the PLC

Most PLC programs expose a mode selector as a digital input tag. For the Degater project, the tag is **`DEG_MAN_AUTO`** (X2 Digital Input 30):
- `DEG_MAN_AUTO = FALSE` → **Manual mode** → output controls **ACTIVE**
- `DEG_MAN_AUTO = TRUE`  → **Auto mode**   → output controls **LOCKED**

The tag is polled alongside all other I/O values. The GUI reacts within one poll cycle.

## Architecture

```
┌─────────────────────────────────────┐
│  PLC (Micro870)                     │
│  • DEG_MAN_AUTO  (BOOL input)     │
│  • Output tags     (BOOL outputs)   │
└────────────┬────────────────────────┘
             │ pycomm3 CIP read/write
             ▼
┌─────────────────────────────────────┐
│  GUI (PySide6)                      │
│  • IOStatusTab reads all tag values │
│  • Checks DEG_MAN_AUTO first        │
│  • Enables/disables controls        │
│  • Shows colored mode banner        │
└─────────────────────────────────────┘
```

## Implementation

### Pattern A: Dimmed Original Buttons (Final — User Requested)

**User preference (Degater project, May 2026):** Always show the original ON / OFF / Release buttons. In auto mode, dim them (gray text, muted borders) so they look inactive. Clicking any button opens the Manual Mode dialog. Only in manual mode do the buttons brighten to full color and actually force outputs.

**Critical implementation details learned in production:**

1. **Button sizing — prevent text clipping.** A 100px-wide button with 11px bold text clips descenders (the left edge of "M" in "Manual"). Fix: increase width to 112px, reduce font to 10px, add 2px internal padding:
   ```python
   self._manual_btn.setFixedSize(112, 28)
   # stylesheet: font-size: 10px; padding: 2px 4px;
   ```

2. **Mode banner cache — prevent flicker during playback.** The `DEG_MAN_AUTO` tag appears in every I/O snapshot during timeline playback. Re-setting the banner and re-styling all controls on every frame causes visible flicker. Cache the last mode and only update on change:
   ```python
   cached = getattr(self, "_cached_man_auto", None)
   if cached != is_auto:
       self._cached_man_auto = is_auto
       self._set_manual_mode_banner(not is_auto)
       for ctrl in self._output_controls.values():
           ctrl.set_manual_mode(not is_auto)
   ```

3. **Status indicator early-return.** `StatusIndicator.set_on()` must check `if on == self._is_on: return` before calling `update()` to avoid repainting every frame during playback.

```python
class ManualControlWidget(QWidget):
    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setAlignment(Qt.AlignCenter)

        # ON button — always visible
        self._on_btn = QPushButton("ON")
        self._on_btn.setFixedSize(45, 24)
        self._on_btn.setCheckable(True)
        self._on_btn.clicked.connect(self._on_on_clicked)

        # OFF button — always visible
        self._off_btn = QPushButton("OFF")
        self._off_btn.setFixedSize(45, 24)
        self._off_btn.setCheckable(True)
        self._off_btn.setChecked(True)
        self._off_btn.clicked.connect(self._on_off_clicked)

        # Release button — always visible
        self._release_btn = QPushButton("Release")
        self._release_btn.setFixedSize(55, 24)
        self._release_btn.setEnabled(False)
        self._release_btn.clicked.connect(self._on_release)

        layout.addWidget(self._on_btn)
        layout.addWidget(self._off_btn)
        layout.addWidget(self._release_btn)
        self.set_manual_mode(False)

    def set_manual_mode(self, enabled: bool) -> None:
        """enabled=True → PLC in Manual mode (buttons ACTIVE)
        enabled=False → PLC in Auto mode  (buttons dimmed, click shows dialog)
        """
        self._manual_enabled = enabled
        self._update_button_states()

    def _update_button_states(self) -> None:
        """Dim buttons in auto mode so the user sees they are locked."""
        if not self._manual_enabled:
            self._on_btn.setStyleSheet(
                "QPushButton { background: #f3f4f6; color: #9ca3af; "
                "border: 2px solid #d1d5db; border-radius: 4px; "
                "font-weight: bold; font-size: 10px; }"
                "QPushButton:checked { background: #10b981; color: white; border-color: #059669; }"
                "QPushButton:hover { border-color: #10b981; }"
            )
            self._off_btn.setStyleSheet(
                "QPushButton { background: #f3f4f6; color: #9ca3af; "
                "border: 2px solid #d1d5db; border-radius: 4px; "
                "font-weight: bold; font-size: 10px; }"
                "QPushButton:checked { background: #ef4444; color: white; border-color: #dc2626; }"
                "QPushButton:hover { border-color: #ef4444; }"
            )
            self._release_btn.setEnabled(False)
        else:
            # Bright normal styles
            self._on_btn.setStyleSheet(
                "QPushButton { background: #e5e7eb; color: #374151; "
                "border: 2px solid #d1d5db; border-radius: 4px; "
                "font-weight: bold; font-size: 10px; }"
                "QPushButton:checked { background: #10b981; color: white; border-color: #059669; }"
                "QPushButton:hover { border-color: #10b981; }"
            )
            self._off_btn.setStyleSheet(
                "QPushButton { background: #e5e7eb; color: #374151; "
                "border: 2px solid #d1d5db; border-radius: 4px; "
                "font-weight: bold; font-size: 10px; }"
                "QPushButton:checked { background: #ef4444; color: white; border-color: #dc2626; }"
                "QPushButton:hover { border-color: #ef4444; }"
            )
            self._release_btn.setEnabled(self._forced)

    def _show_manual_dialog(self) -> None:
        if self._dialog is None:
            self._dialog = ManualModeDialog(self)
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def _on_on_clicked(self, checked: bool) -> None:
        if not self._manual_enabled:
            self._show_manual_dialog()
            return
        if checked:
            self._off_btn.setChecked(False)
            self._forced = True
            self._release_btn.setEnabled(True)
            self.output_forced.emit(self._tag_name, True)

    def _on_off_clicked(self, checked: bool) -> None:
        if not self._manual_enabled:
            self._show_manual_dialog()
            return
        if checked:
            self._on_btn.setChecked(False)
            self._forced = True
            self._release_btn.setEnabled(True)
            self.output_forced.emit(self._tag_name, False)

    def _on_release(self) -> None:
        if not self._manual_enabled:
            self._show_manual_dialog()
            return
        self._forced = False
        self._on_btn.setChecked(False)
        self._off_btn.setChecked(True)
        self._release_btn.setEnabled(False)
        self.output_released.emit(self._tag_name)
```

### Pattern B: "⚠ Manual" Button Swap (Historical — Replaced by Pattern A)

For reference, the previous approach swapped the widget entirely between a single "⚠ Manual" button (auto mode) and the full ON/OFF/Release group (manual mode). This was clearer than disabled controls but user feedback preferred keeping the original buttons visible at all times.

### Manual Mode Dialog with Photo

A non-modal dialog showing a picture of the physical MAN-AUTO switch:

```python
class ManualModeDialog(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Switch to Manual Mode")
        self.setFixedSize(640, 540)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("⚠  Manual Mode Required")
        title.setStyleSheet("QLabel { color: #92400e; font-size: 18px; font-weight: bold; }")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Instruction
        instr = QLabel(
            "Switch to Manual on the line to enable output controls.\n"
            "Input: X2 Digital Input 30  (Degator is in Auto = FALSE → Manual mode)"
        )
        instr.setStyleSheet("QLabel { color: #4b5563; font-size: 12px; }")
        instr.setAlignment(Qt.AlignCenter)
        layout.addWidget(instr)

        # Photo of the physical switch
        self._img_lbl = QLabel()
        self._img_lbl.setAlignment(Qt.AlignCenter)
        self._load_image()
        layout.addWidget(self._img_lbl)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(100, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6; color: white;
                border: none; border-radius: 6px;
                font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background: #2563eb; }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

    def _load_image(self) -> None:
        """Load photo from bundled assets (handles both source tree and PyInstaller EXE)."""
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "assets", "Manual.jpg"),
            os.path.join(os.path.dirname(__file__), "..", "..", "gui", "assets", "Manual.jpg"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Manual.jpg"),
        ]
        # PyInstaller _MEIPASS for bundled resources
        if getattr(sys, "_MEIPASS", None):
            candidates.insert(0, os.path.join(
                sys._MEIPASS, "plc_tools", "gui", "assets", "Manual.jpg"
            ))

        for path in candidates:
            if os.path.isfile(path):
                pm = QPixmap(path)
                if not pm.isNull():
                    scaled = pm.scaled(580, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self._img_lbl.setPixmap(scaled)
                    return

        self._img_lbl.setText("[Manual.jpg not found — image missing from bundle]")
```

### Bundling the Photo into PyInstaller

Add the assets directory to `datas` in the `.spec` file so the image is extracted alongside the EXE:

```python
datas=[
    ('src/plc_tools/gui/assets', 'plc_tools/gui/assets'),
],
```

The image will be extracted at runtime to `sys._MEIPASS/plc_tools/gui/assets/Manual.jpg`.

---

### Pattern B: Disable ON/OFF/Release in Place (Legacy)

If swapping widgets is not feasible, keep the controls visible but disable them. This is less intuitive because users don't know *why* the controls are grayed out.

```python
def set_manual_mode(self, enabled: bool) -> None:
    self._on_btn.setEnabled(enabled)
    self._off_btn.setEnabled(enabled)
    if not enabled and not self._forced:
        self._release_btn.setEnabled(False)
    elif not enabled and self._forced:
        self._release_btn.setEnabled(True)
```

---

### 1. Mode Banner Widget

A colored banner at the top of every I/O tab that shows the current mode:

```python
def _set_manual_mode_banner(self, manual_enabled: bool) -> None:
    """Show mode banner: green = Manual (controls active), amber = Auto (locked)."""
    if manual_enabled:
        self._mode_banner.setText("🟢 MANUAL MODE — Output controls are ACTIVE")
        self._mode_banner.setStyleSheet("""
            QLabel {
                background-color: #d1fae5;
                color: #065f46;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
    else:
        self._mode_banner.setText(
            "🟡 AUTO MODE — Click ⚠ Manual on any output to see how to switch to Manual mode"
        )
        self._mode_banner.setStyleSheet("""
            QLabel {
                background-color: #fef3c7;
                color: #92400e;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
    self._mode_banner.setVisible(True)
```

### Per-Control Enable/Disable (Legacy Pattern)

Each `ManualControlWidget` (ON/OFF/Release button group) receives the mode state. In the **preferred pattern**, the widget is swapped between a "⚠ Manual" button and the full control group. In the legacy pattern, controls are disabled in place:

```python
class ManualControlWidget(QWidget):
    def set_manual_mode(self, enabled: bool) -> None:
        """
        enabled=True  → PLC in Manual → controls ACTIVE
        enabled=False → PLC in Auto   → controls DISABLED
        """
        self._on_btn.setEnabled(enabled)
        self._off_btn.setEnabled(enabled)

        if not enabled and not self._forced:
            self._release_btn.setEnabled(False)
        elif not enabled and self._forced:
            # Keep release enabled so user can clear an active force in auto mode
            self._release_btn.setEnabled(True)
```

**Key safety behavior:** If a user forces an output and then the PLC switches to auto mode, the force remains active but new forces cannot be issued. The Release button stays enabled so the user can clear the force.

### 3. Wiring in the I/O Update Loop

The `update_io_values()` method in each I/O tab checks `DEG_MAN_AUTO` before updating anything else:

```python
def update_io_values(self, tag_values: dict[str, bool]) -> None:
    # ── Safety interlock: check DEG_MAN_AUTO first ─────────────────────
    if "DEG_MAN_AUTO" in tag_values:
        is_auto = bool(tag_values["DEG_MAN_AUTO"])
        self._set_manual_mode_banner(not is_auto)
        manual_enabled = not is_auto
        for ctrl in self._output_controls.values():
            ctrl.set_manual_mode(manual_enabled)

    # ── Now update input/output indicators (always safe to display) ────
    for i, inp in enumerate(self._inputs):
        ...
    for i, out in enumerate(self._outputs):
        ...
```

### 4. Disconnect Handling

On disconnect, hide the banner and release all forces:

```python
def clear(self) -> None:
    ...
    self._mode_banner.setVisible(False)
    for ctrl in self._output_controls.values():
        ctrl.release_force()
```

## Important Notes

- **Tag polling frequency:** The mode detection is only as fast as the I/O poll. If polling is slow (e.g., 2-second interval), the mode change won't appear instantly. Consider a faster poll for safety-critical tags.
- **Mode tag naming:** `DEG_MAN_AUTO` is project-specific. Other projects may use `MANUAL_MODE`, `AUTO_MODE`, `MAN_AUTO_SW`, etc. Always verify the exact tag name with the PLC programmer.
- **True vs False meaning:** In this project, `TRUE = Auto` and `FALSE = Manual`. This is conventional for many Rockwell programs but not universal. Document the polarity clearly.
- **Release in auto mode:** Allowing release in auto mode is a deliberate safety feature. A user may have accidentally forced an output and then the machine went into auto. They must be able to clear the force without switching back to manual.

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Dangerous | What To Do Instead |
|-------------|-------------------|-------------------|
| Let the GUI decide the mode | GUI state can drift from PLC reality | Always read mode from PLC |
| Show a one-time warning | User may miss it, or mode changes later | Persistent banner + live control state |
| Disable the entire tab | User still needs to see I/O values in auto | Only disable the force controls |
| Force without any interlock | Direct tag writes in any mode | Always check mode first |
| Rely on PLC-side interlock only | GUI gives false confidence | Defense in depth: GUI + PLC both enforce |

## PLC-Side Verification: Will Manual Writes Win?

The GUI can send manual output writes, but whether they actually control the physical output depends on the PLC ladder logic. In Run mode, the PLC re-evaluates every rung every scan. If the ladder logic driving that output evaluates to a different state, it overwrites the tag value immediately.

### Tracing the Write Path

To determine if manual writes will work when the ladder file is not in the repository, trace the full signal chain in the Python codebase:

1. **Widget click** → `ManualControlWidget._on_on_clicked()` emits `output_forced(tag_name, True)`
2. **Tab forwarding** → `DegaterIOTab.output_forced` → `IOStatusTab.output_force_requested`
3. **MainWindow handler** → `_on_output_force()` calls `driver.write_tag(physical_tag, forced_value)`
4. **Driver layer** → `micro800_driver.write_tag()` → `CIPDriver.write((tag_name, value))`
5. **PLC scan cycle** → The tag is updated via CIP, then the ladder logic runs on the next scan

### What to Look for in the Ladder Logic

| Pattern | Result |
|---|---|
| **Manual bypass** — `XIO DEG_MAN_AUTO` in series with auto rung coils | Auto rungs break when manual. App writes win cleanly. |
| **Manual override rung** — separate rung with `XIC DEG_MAN_AUTO` that latches output | App writes feed the manual rung. Must verify latching holds across scans. |
| **No bypass** — auto rungs always active regardless of mode | App writes fight ladder logic every scan. Output flickers or follows program. |
| **OTL/OTU (latch/unlatch) coils** | Manual set/reset holds state across scans. Safe if manual rung uses OTL. |
| **OTE (output energize) only** | State is rewritten every scan. Unsafe unless auto rung is broken in manual mode. |

### Verification Steps

1. Open the PLC program in CCW / RSLogix
2. Find the rung for the output tag (e.g., `Output_Deg1_FeedSol`)
3. Check if `DEG_MAN_AUTO` appears as a normally-closed (`XIO`) contact on the auto rung
4. Check for a separate manual rung or manual set/reset coils
5. If unsure, test physically: force an output in manual mode and watch if it holds steady or flickers

### Key Insight

> **The app does not perform a "force" in the PLC sense.** It performs a plain `write_tag()`. True forcing requires Remote/Program mode and special CIP force commands that the Micro800 does not support. The app relies entirely on the ladder logic being structured to accept manual writes when in manual mode.

## References

- `references/plc-safety-interlock-example.md` — Full annotated example from the Degater project
- `references/ladder-logic-analysis-from-python.md` — How to trace the Python signal chain and verify ladder logic supports manual writes
- `references/playback-data-stability-filter.md` — Two-layer defense against false OFF values in timeline recordings: last-known-value caching in poll workers + 2-snapshot stability threshold during playback
