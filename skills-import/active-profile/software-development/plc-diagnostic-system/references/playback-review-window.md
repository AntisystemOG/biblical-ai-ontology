# Standalone Playback Review Window

## Purpose

A separate `QMainWindow` that opens when the user clicks "Review" on a loaded recording. Shows I/O status, alarm log, and alarm-marked timeline. The main app stays live — this window is completely isolated from the main app's polling.

## When to Use

Use this pattern **instead of** a live/playback mode toggle on the main window when:
- The user needs to review recordings while the main app continues live PLC monitoring
- Live data leaks into playback during mode transitions (timer stop/start latency)
- Outputs don't stay on reliably during playback
- Switching modes back and forth is confusing

The Degater project abandoned the mode-toggle approach after user feedback: "this doesn't seem to be working." The separate window pattern solved all three problems.

## Architecture

```
MainWindow (live PLC, always running)
    └── PlaybackRecordTab
            └── "🔍 Review" button (enabled only when recording loaded)
                    └── PlaybackReviewWindow (separate QMainWindow)
                            ├── AlarmMarkerSlider (top, with red alarm ticks)
                            ├── QSplitter
                            │       ├── SnapshotIOView (left) — I/O values from snapshot
                            │       └── AlarmsLogTab (right) — pre-populated alarms
                            └── Transport controls (bottom)
                                    ├── ▶ Play / ⏸ Pause
                                    ├── ◀ Prev / Next ▶
                                    ├── Speed: x1/x2/x4/x8/x16
                                    ├── ⛶ Fullscreen toggle
                                    └── ✕ Close
```

## Files

| File | Purpose |
|---|---|
| `gui/playback_review_window.py` | `PlaybackReviewWindow(QMainWindow)` + `SnapshotIOView` |
| `gui/widgets/alarm_marker_slider.py` | `AlarmMarkerSlider(QSlider)` with red paintEvent ticks |
| `gui/tabs/playback_record.py` | Adds "🔍 Review" button + `_on_review()` handler |

## Key Implementation Details

### Opening the Window

```python
def _on_review(self) -> None:
    if not self._recording:
        return
    from plc_tools.gui.playback_review_window import PlaybackReviewWindow
    # Singleton: raise existing window instead of opening duplicate
    if hasattr(self, "_review_window") and self._review_window is not None:
        self._review_window.raise_()
        self._review_window.activateWindow()
        return
    self._review_window = PlaybackReviewWindow(self._recording, parent=self)
    self._review_window.closed_requested.connect(self._on_review_closed)
    self._review_window.showMaximized()

def _on_review_closed(self) -> None:
    self._review_window = None
```

**Singleton pattern:** prevents multiple review windows from stacking up. If the window already exists, `raise_()` brings it to front.

### Window Contents

**AlarmMarkerSlider** at top — custom `QSlider` that paints red rectangles on the groove at alarm snapshot indices. Clicking near a red tick jumps to that snapshot and auto-pauses. See `references/alarm-marker-slider.md`.

**SnapshotIOView** (left pane) — simplified I/O display showing tag values from a single snapshot:
- Timestamp label
- Snapshot index / total
- Grid of bool tags with 🟢/⚪ indicators
- Alarm details if `snapshot.fault_detected`

**AlarmsLogTab** (right pane) — an actual `AlarmsLogTab` instance, pre-populated with all alarms from the recording at window open time:
```python
def _populate_alarms_from_recording(self) -> None:
    for idx in self._alarm_indices:
        snap = self._recording.snapshots[idx]
        ts_str = snap.timestamp.strftime("%m-%d %H:%M:%S")
        for detail in snap.fault_details:
            self._alarms_tab.log_event(
                severity="CRITICAL",
                source="Playback",
                message=f"[{ts_str}] Snapshot {idx + 1}: {detail}",
            )
```

### Transport Controls

- **Play/Pause** — `QTimer` advances snapshot index; interval calculated from相邻 snapshot timestamps divided by speed multiplier
- **Prev/Next** — single-step through snapshots
- **Speed** — x1/x2/x4/x8/x16 buttons; active button highlighted in indigo
- **Fullscreen** — toggle `showFullScreen()` / `showNormal()`
- **Close** — `close()` destroys window, emits `closed_requested` signal

### Playback Timer

```python
def _update_play_interval(self) -> None:
    if not self._recording or self._current_index >= len(self._recording.snapshots) - 1:
        return
    curr = self._recording.snapshots[self._current_index]
    nxt = self._recording.snapshots[self._current_index + 1]
    if curr and nxt:
        delta_ms = (nxt.timestamp - curr.timestamp).total_seconds() * 1000
        delta_ms = max(delta_ms, 50.0)
        interval = max(16, int(delta_ms / self._play_speed))
        self._play_timer.setInterval(interval)
```

**Adaptive interval:** each snapshot has its own timestamp; playback speed respects the real recording interval between adjacent snapshots.

### Alarm Indices Extraction

```python
self._alarm_indices: list[int] = [
    i for i, snap in enumerate(recording.snapshots)
    if snap.fault_detected
]
```

These indices feed `AlarmMarkerSlider.set_alarm_indices()`.

## Cleanup on Recording Clear

When the recording is cleared in the main tab, close the review window if open:

```python
def clear(self) -> None:
    # ... existing clear logic ...
    if hasattr(self, "_review_window") and self._review_window is not None:
        self._review_window.close()
        self._review_window = None
```

## Anti-Patterns

| Anti-Pattern | Why Bad | Correct Approach |
|---|---|---|
| Mode toggle on main window | Live data leaks, outputs flicker, confusing | Separate `QMainWindow` |
| Modal review window (`.exec()`) | Blocks main app, can't interact with timeline | `.show()` + signal |
| No alarm markers on timeline | User can't see where alarms happened | `AlarmMarkerSlider` with red ticks |
| Multiple review windows | Clutter, confusion | Singleton pattern with `raise_()` |
| Playback speed ignores real intervals | Jumps, stutters | Adaptive interval from snapshot timestamps |

## Testing

1. Load a recording with known alarm snapshots
2. Click "🔍 Review" — window opens maximized
3. Verify red ticks appear on slider at alarm indices
4. Click a red tick — playback pauses, jumps to that snapshot
5. Verify alarm appears in right-side AlarmsLogTab
6. Verify main app continues live polling (LED stays green if connected)
7. Close review window — main app unaffected
8. Clear recording — review window auto-closes

---
*Session: 2026-06-02. User: Thad. Project: Degater PLC Tool BST33 and 35.*
