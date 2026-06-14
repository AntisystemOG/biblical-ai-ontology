# Degater PLC Tool — Playback I/O Blink Fix

## Reproduction
During timeline playback, digital I/O indicators (StatusIndicator LEDs) and manual-control buttons blinked on every snapshot even though the recorded values were steady true/false.

## Environment
- PySide6 desktop app
- `pycomm3`-based PLC communication
- `QTimer`-driven playback emitting `playback_update(dict)` signals
- No deduplication in recorder — every snapshot fires the signal

## Root Causes Found (3 simultaneous)

### 1. `StatusIndicator.set_on()` unconditional repaint
```python
# BEFORE — flickered every snapshot
self._is_on = on
self.repaint()

# AFTER
if on == self._is_on:
    return
self._is_on = on
self.repaint()
```

### 2. `ManualControlWidget.set_manual_mode()` unconditional stylesheet reapply
```python
# BEFORE — stylesheet thrash every frame
self._manual_enabled = enabled
self._update_button_states()

# AFTER
if enabled == self._manual_enabled:
    return
self._manual_enabled = enabled
self._update_button_states()
```

### 3. `ManualControlWidget.update_from_plc()` unconditional `setChecked()`
```python
# BEFORE
self._on_btn.setChecked(want_on)
self._off_btn.setChecked(want_off)

# AFTER
if self._on_btn.isChecked() != want_on:
    self._on_btn.setChecked(want_on)
if self._off_btn.isChecked() != want_off:
    self._off_btn.setChecked(want_off)
```

### 4. `DEG_MAN_AUTO` banner processed every snapshot (both I/O tabs)
```python
# BEFORE
is_auto = snapshot.get("DEG_MAN_AUTO", True)
self._set_manual_mode_banner(not is_auto)

# AFTER
cached = getattr(self, "_cached_man_auto", None)
if cached != is_auto:
    self._cached_man_auto = is_auto
    self._set_manual_mode_banner(not is_auto)
    self._update_manual_controls_visibility()
```

## Why Downstream Idempotency Was Chosen
The alternative was adding snapshot deduplication in `recorder.py`. That was rejected because:
- It would couple UI flicker logic into the data layer
- Future recorder changes could re-introduce duplicates
- Guards in widgets are defensive regardless of source

## Files Changed
- `src/plc_tools/gui/tabs/io_status.py` — guards in `StatusIndicator`, `ManualControlWidget`, `DegaterIOTab`, `SystemControlsTab`
- `src/plc_tools/gui/widgets/connection_bar.py` — added `set_playback_mode()`
- `src/plc_tools/gui/main_window.py` — `_set_data_mode()` toggles badge
