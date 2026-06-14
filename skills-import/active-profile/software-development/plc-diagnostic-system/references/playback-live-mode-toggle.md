# Playback Live / Playback Mode Toggle

## Problem

When the user loads a recording for review, three bad things happen simultaneously:

1. **Live polls continue** — the background `QTimer` keeps firing, and `_on_poll_done()` overwrites the playback display with fresh live PLC data
2. **Outputs don't stay on** — an aggressive stability filter in `_on_playback_update()` suppresses boolean values that haven't been stable for 2 snapshots, making solenoids appear to flicker off
3. **No visual mode indicator** — the user can't tell whether they're looking at live data or a recording

## Architecture: Single Source of Truth

Introduce one central flag in `MainWindow`:

```python
self._data_mode: str = "live"   # or "playback"
```

All components derive their behavior from this flag. `MainWindow._set_data_mode(target)` is the only place that changes it.

```
MainWindow._data_mode  (single source of truth)
    ├── _poll_timer     start/stop
    ├── _conn_bar       mode toggle button (top-left)
    ├── _tab_playback   _mode attr + _update_mode_button()
    └── _on_poll_done() early return when "playback"
```

## `_set_data_mode()` Pattern

```python
def _set_data_mode(self, mode: str) -> None:
    if self._data_mode == mode:
        return   # same-mode guard
    self._data_mode = mode

    # Timer
    if mode == "playback":
        if self._poll_timer and self._poll_timer.isActive():
            self._poll_timer.stop()
    else:
        if self._poll_timer and not self._poll_timer.isActive():
            self._poll_timer.start(self._poll_rate_ms)

    # Connection bar (where the mode toggle lives now)
    if self._conn_bar is not None:
        self._conn_bar.set_mode(mode)

    # Playback tab
    if hasattr(getattr(self, "_tab_playback", None), "_mode"):
        self._tab_playback._mode = mode
    if hasattr(getattr(self, "_tab_playback", None), "_update_mode_button"):
        self._tab_playback._update_mode_button()

    # Signal for other tabs
    self.mode_changed.emit(mode)
```

## Connection Bar Mode Toggle Button (2026-06-02 Update)

The mode toggle lives in the **top-left connection bar**, not the bottom strip. It is visible on **every** page:

```python
class ConnectionBar(QWidget):
    mode_toggle_requested = Signal()   # emits when user clicks the playback button

    def set_mode(self, mode: str) -> None:
        if mode == "playback":
            self._playback_btn.setVisible(True)
            self._playback_btn.setText("  ▶ PLAYBACK")  # click once to toggle back
            self._playback_btn.setStyleSheet("""
                font-size: 10px; font-weight: bold;
                background: #e0e7ff; color: #4338ca;
                padding: 2px 10px; border-radius: 4px;
            """)
        else:
            self._playback_btn.setVisible(False)

    def show_mode_button(self, show: bool) -> None:
        self._playback_btn.setVisible(show)
```

**Wiring in MainWindow._build_ui():**

```python
self._conn_bar.mode_toggle_requested.connect(self._toggle_data_mode)
```

**Recording load sequence:**
1. Switch nav to Playback tab (`setCurrentRow(4)`)
2. Open `PlaybackInfoWindow` via `_on_recording_loaded()` — non-modal
3. Show mode button via `_conn_bar.show_mode_button(True)` (only when `recording is not None`)
4. If recording was cleared, call `_conn_bar.show_mode_button(False)`

## Poll Discard Guard

Even after stopping the timer, a poll may already be in flight. Guard `_on_poll_done()`:

```python
def _on_poll_done(self, io_values: dict[str, Any]) -> None:
    if self._data_mode == "playback":
        return   # discard queued live polls
    ...
```

**Why needed:** `QTimer.stop()` only prevents new timeouts. A timeout that already fired may still have a queued event on the event loop, especially with fast polling (100 ms).

## Stability Filter Removal

Remove the playback stability filter from `_on_playback_update()`. Let booleans pass through unfiltered:

```python
# OLD — suppresses legitimate ON values
if tag in self._playback_last_values:
    if value == self._playback_last_values[tag]:
        stable = True
    else:
        stable = False

# NEW — pass through directly
snapshot = frame["values"]
self._update_io_display(snapshot)
```

**Clean up dead state:** Remove `_playback_last_values`, `_playback_stability_counter`, `_playback_stability_threshold` from `MainWindow.__init__`.

## Playback Info Window (Non-Modal)

When a recording is loaded, immediately open a floating `PlaybackInfoWindow` with:
- Controller metadata (IP, PLC type, recorded at, version)
- Snapshot stats (total snapshots, duration, avg interval, tags / snapshot)
- **"Keep on Top" checkbox** — pins the window above the main app
- **"🔴 Return to Live" button** — emits `return_to_live_requested` signal
- **"Close" button** — closes info window only, no mode change

```python
class PlaybackInfoWindow(QDialog):
    return_to_live_requested = Signal()

    # ... build controller info table, stats table, timing labels ...

    def _request_return_to_live(self):
        self.return_to_live_requested.emit()
        self.close()
```

**Handler in MainWindow:**

```python
def _on_recording_loaded(self, recording) -> None:
    if self._playback_info_dialog is not None:
        self._playback_info_dialog.close()
        self._playback_info_dialog = None

    if recording is not None:
        self._playback_info_dialog = PlaybackInfoWindow(recording, self)
        self._playback_info_dialog.return_to_live_requested.connect(
            lambda: self._set_data_mode("live")
        )
        self._playback_info_dialog.show()   # non-modal

    if self._conn_bar:
        self._conn_bar.show_mode_button(recording is not None)
```

**Why non-modal:** Modal `.exec()` blocks the entire app — user can't interact with timeline scrubber or transport controls. Non-modal `.show()` + `Signal()` is the correct pattern.

## Anti-Patterns (2026-06-02 Update)

| Anti-Pattern | Why Bad | What To Do |
|---|---|---|
| Keep live timer running during playback | Polls overwrite playback data | Stop timer + discard guard |
| Playback stability filter on booleans | Suppresses real ON values | Remove filter; trust recording |
| No visual mode indicator | User confusion | Top-left mode toggle button in connection bar |
| Hardcoded nav index for playback tab | Breaks when tabs reordered | Named constant (`NAV_PLAYBACK`) |
| Dead code left after refactoring | Adds noise, confuses future readers | Remove unused state variables |
| Modal info window blocking playback | User can't interact with controls | Non-modal `.show()` with `Signal()` |
| Info window showing before tab switch | User sees playback on wrong page | Switch nav, then open window, then set mode |
| Redundant mode buttons in both strip and bar | Two sources of truth, sync issues, confusing layout | Single toggle button in connection bar; strip handles transport only |
| `.exec()` blocking app during playback review | Cannot scrub timeline or pause | Always use `.show()` + signal |
| Cross-stream live data during playback | Poll callbacks overwrite playback state | Guard `_on_poll_done()` with `if _data_mode == "playback": return` |
| Reactive mode switch after timer tick | Live data leaks before playback starts | **Proactive emit in `_play()` before `_play_timer.start()`** |

## Proactive Mode Switch on Play Click

See `references/proactive-playback-mode.md` for full details:
- Set `_mode = "playback"` and emit `mode_changed` **before** `_play_timer.start()`
- This guarantees no live poll leaks in during the window between Play click and first frame
