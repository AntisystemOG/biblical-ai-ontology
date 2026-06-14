# Session: Auto 45-Min Circular Recorder (June 3, 2026)

## Problem

The user needed a background recorder that:
- Runs continuously while the app is live
- Captures the last 45 minutes of PLC data into a circular buffer
- Only starts recording on first I/O state change (not before)
- Goes idle and clears buffer if no state changes for 45 minutes
- Survives disconnect/reconnect without losing the buffer architecture
- Can be played back instantly via one button click — no file loading needed
- Coexists with the existing manual 12-hour recording

## Architecture Decision

**Two independent recording systems:**
1. **Manual TimelineRecorder** — user-initiated, JSON file, 12-hour cap, every-poll saved
2. **AutoRecorder (new)** — background, in-memory circular buffer, 45-min cap, triggered by first state change

Never combine them — separate instances, separate code paths, separate UI controls.

## Implementation

### `recording/auto_recorder.py` (121 lines)

```python
from collections import deque
from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import Any

MAX_SNAPSHOTS = 27000       # 45 min @ 100 ms polling
INACTIVITY_SECONDS = 45 * 60

class _State(Enum):
    IDLE = "idle"
    ACTIVE = "active"

class AutoRecorder:
    def __init__(self):
        self._state = _State.IDLE
        self._buffer: deque[Snapshot] = deque(maxlen=MAX_SNAPSHOTS)
        self._last_values: dict[str, Any] = {}
        self._last_snapshot_time: datetime | None = None

    def arm(self) -> None:
        self._state = _State.IDLE
        self._buffer.clear()
        self._last_values = {}
        self._last_snapshot_time = None

    def disarm(self) -> None:
        self._state = _State.IDLE
        self._buffer.clear()
        self._last_values = {}
        self._last_snapshot_time = None

    def record_snapshot(self, values, alarm_events=None):
        now = datetime.now()
        # Idle timeout: no activity for 45 min
        if self._state is _State.ACTIVE and self._last_snapshot_time:
            if (now - self._last_snapshot_time).total_seconds() > INACTIVITY_SECONDS:
                self._state = _State.IDLE
                self._buffer.clear()
                self._last_values = {}
                self._last_snapshot_time = None

        has_change = self._has_changed(values)

        if self._state is _State.IDLE:
            if not has_change and not alarm_events:
                return
            # First state change (or alarm) → start recording
            self._state = _State.ACTIVE
            self._buffer.clear()
            self._last_values = values.copy()
            # Fall through to ACTIVE below

        if self._state is _State.ACTIVE:
            snapshot = Snapshot(
                timestamp=now,
                values=values.copy(),
                fault_detected=bool(alarm_events),
                fault_details=[a.get("message", "") for a in (alarm_events or [])],
                alarm_events=alarm_events or [],
            )
            self._buffer.append(snapshot)
            self._last_snapshot_time = now
            self._last_values = values.copy()

    def copy_recent(self, project_name="DEG System (Auto)"):
        if not self._buffer:
            return None
        snapshots = [deepcopy(s) for s in self._buffer]  # isolation
        fault_indices = [i for i, s in enumerate(snapshots) if s.alarm_events]
        return TimelineRecording(
            project_name=project_name,
            start_time=snapshots[0].timestamp,
            end_time=snapshots[-1].timestamp,
            snapshots=snapshots,
            fault_snapshots=fault_indices,
        )

    def _has_changed(self, values) -> bool:
        if not self._last_values:
            return True
        if set(values.keys()) != set(self._last_values.keys()):
            return True
        return any(values.get(k) != v for k, v in self._last_values.items())
```

### PlaybackRecordTab Changes

- New button: `⏪  Playback Last 45min` (grayed out until buffer has data)
- New signal: `auto_review_requested = Signal()`
- New public methods:
  - `set_auto_ready(enabled: bool)` — enables/disables the auto playback button
  - `set_status(text: str)` — general status text display

### MainWindow Wiring

```python
# In __init__
self._auto_recorder = AutoRecorder()

# On PLC connect
self._auto_recorder.arm()          # start waiting for first state change

# On every poll (in _on_poll_done)
if io_values:
    self._auto_recorder.record_snapshot(io_values, alarm_events)
    if self._auto_recorder.snapshot_count > 0:
        self._tab_playback.set_auto_ready(True)

# On disconnect
self._auto_recorder.disarm()
self._tab_playback.set_auto_ready(False)

# On button click
self._on_auto_review():
    recording = self._auto_recorder.copy_recent()
    if recording:
        self._review_window = PlaybackReviewWindow(recording, parent=self)
        self._review_window.showMaximized()
```

## Key Design Decisions

1. **State-change trigger, not timer trigger**: The buffer doesn't start filling until the PLC actually does something. This saves memory during idle periods and makes "Playback Last 45min" meaningful — it always shows the most recent activity.

2. **Deep copy on `copy_recent()`**: Returns an isolated `TimelineRecording` so the `PlaybackReviewWindow`'s timeline scrubbing and snapshot inspection cannot corrupt the live circular buffer.

3. **Survives disconnect/reconnect**: `disarm()` on disconnect, `arm()` on connect. Buffer architecture is re-established without code duplication.

4. **Coexists with manual recording**: Both recorders receive the same `io_values` dict on every poll. No shared state. Manual recorder writes to JSON file; auto recorder writes to `deque`.

5. **No `closed_requested` signal for auto review window**: Unlike the loaded-recording review window, the auto review window does not store a reference that needs cleanup on close. The review window is created fresh each time and garbage-collected by Qt.

## Anti-Patterns Avoided

| Anti-Pattern | Why Not | What We Did |
|---|---|---|
| Auto-recording to file every poll | Writes 1.5 GB/hr to disk unnecessarily | Circular in-memory buffer, only read on demand |
| Start recording on app launch (before PLC connect) | Would record zeros/empty dicts until state change | `arm()` only called on PLC connect |
| Shared TimelineRecording object | Review window mutations affect live buffer | `deepcopy()` every snapshot on export |
| Single recorder for both modes | Manual and auto have different lifecycle needs | Two separate recorder instances |
| Buffer survives app restart | Not possible with in-memory deque; file-based persistence needed | Buffer cleared on app start — acceptable for 45-min rolling window |

## Files Modified

- `src/plc_tools/recording/auto_recorder.py` — NEW
- `src/plc_tools/gui/tabs/playback_record.py` — Added `⏪ Playback Last 45min` button, `set_auto_ready()`, `set_status()`
- `src/plc_tools/gui/main_window.py` — Wired `AutoRecorder`, added `_on_auto_review()`

## Build

Version 2.23.25 — 46 MB EXE. No changes to PyInstaller spec needed (all files in `src/`).
