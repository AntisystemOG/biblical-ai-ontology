# Session: Auto 45-Minute Circular Recorder — v2.24.x

**Date:** 2026-06-10
**Scope:** Add a background circular buffer that auto-records the last 45 min of PLC state, triggered on first I/O state change, overwrites old data continuously, survives disconnect/reconnect, and offers instant playback via "Playback Last 45min" button.

---

## Problem

User wanted:
1. **Always-on background recording** that continuously buffers the last 45 min of I/O data
2. **No manual start/stop** — arms automatically on app start, triggered by first state change
3. **Overwrite old data** — when buffer fills past 45 min, oldest snapshots are dropped
4. **Idle timeout** — if no state changes for 45 min, clear buffer and go idle (does not auto-fire -> saves CPU when PLC idle)
5. **Playback without file loading** — a "Playback Last 45min" button opens the same review window as loaded recordings
6. **12-hour manual recording still exists** and is unaffected
7. **Survive disconnect** — auto-recorder doesn't die when PLC disconnects; resumes when reconnect happens

---

## Architecture

```
MainWindow
    ├── _auto_recorder: AutoRecorder()   # <-- NEW
    ├── _timeline_recorder: TimelineRecorder()  # manual 12-hr, unchanged
    └── _on_poll_done(io_values)
            ├── _timeline_recorder.record_snapshot(...)   # manual recording
            └── _auto_recorder.record_snapshot(io_values, alarm_events)   # always

PlaybackRecordTab
    ├── "▶  Playback Recording"  → _on_review() (from loaded recording)
    └── "⏪  Playback Last 45min" → _on_auto_review() → auto_review_requested Signal

PlaybackReviewWindow
    └── Works identically with TimelineRecording from AutoRecorder.copy_recent()
```

---

## Files Changed

### New: `src/plc_tools/recording/auto_recorder.py`

```python
from collections import deque
from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import Any

from plc_tools.recording.timeline_recorder import Snapshot, TimelineRecording

AUTO_BUFFER_MINUTES = 45
INACTIVITY_MINUTES = 45
MAX_SNAPSHOTS = 27000   # 45 min @ 100 ms

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
        """Begin auto-recording. Safe to call at app startup."""
        self._buffer.clear()
        self._last_values = {}
        self._last_snapshot_time = None
        self._state = _State.IDLE
```

**Key design decisions:**

1. **State machine (IDLE → ACTIVE)** — Waiting uses negligible CPU/memory. Only buffers snapshots after a real state change (not every poll).
2. **`deque(maxlen=MAX_SNAPSHOTS)`** — Python's `collections.deque` automatically drops oldest entries on append when `maxlen` is set. No manual rotation logic.
3. **Idle timeout check runs inside `record_snapshot()`** — No separate timer thread. Every poll tick checks `(now - last_snapshot_time).total_seconds() > 45*60`. If true → IDLE → clear buffer.
4. **`copy_recent()` deep-copies snapshots** — PlaybackReviewWindow keeps its own copy; live buffer is unaffected.
5. **Fault snapshot indexes rebuilt from `snapshot.alarm_events`** — Unlike manual recordings where indexes are tracked during write, the auto buffer rebuilds them during `copy_recent()` to stay accurate after circular rotation.

### Modified: `src/plc_tools/gui/tabs/playback_record.py`

- Added `_auto_review_btn` with text "⏪  Playback Last 45min"
- Emits `auto_review_requested = Signal()` when clicked
- Button enabled when `_auto_recorder` has data (wired from MainWindow)

### Modified: `src/plc_tools/gui/main_window.py`

- Instantiate `self._auto_recorder = AutoRecorder()`
- Import + wire signal: `_tab_playback.auto_review_requested.connect(self._on_auto_review)`
- In `_on_poll_done()` — always call `self._auto_recorder.record_snapshot(io_values, alarm_events)`
- Added `_on_auto_review()` method:

```python
def _on_auto_review(self) -> None:
    rec = self._auto_recorder.copy_recent()
    if not rec:
        QMessageBox.information(self, "Auto Playback", "No recent data in buffer yet.")
        return
    from plc_tools.gui.playback_review_window import PlaybackReviewWindow
    self._review_window = PlaybackReviewWindow(rec, parent=self)
    self._review_window.closed_requested.connect(self._on_review_closed)
    self._review_window.showMaximized()
```

---

## User Requirements vs. Implementation

| User Requirement | What I first tried | What it should be |
|---|---|---|
| Auto-start on connect | Start buffering immediately on PLC connect | **Start on first state change** — saves memory when PLC idle |
| Button label "Auto Playback" | Label "Auto Playback" | **Label "Playback Last 45min"** — matches user's exact wording |
| Survives disconnect | Stop recorder on disconnect, start on reconnect | **Survives** — recorder is independent of connection state. Only data flow stops when no values arrive |
| Overwrite every 45 min | File-based circular files | **In-memory `deque` with `maxlen`** — no disk I/O, instant playback, no file management |

---

## Testing Checklist

- [ ] Auto-recorder starts IDLE with 0 snapshots
- [ ] First state change transitions to ACTIVE, buffer fills
- [ ] 45 min of no changes → IDLE, buffer cleared
- [ ] Buffer wraps automatically after 27000 snapshots (~45 min @ 100ms)
- [ ] "Playback Last 45min" opens review window with correct snapshot count
- [ ] Disconnect doesn't crash auto-recorder; reconnect resumes
- [ ] Manual 12-hr recording unaffected

---

## Related Session References

- `references/session-2026-06-03-remove-in-app-playback-crash-fix.md` — Why playback was moved to standalone window (pre-requisite for this)
- `references/session-2026-06-02-playback-review-window.md` — PlaybackReviewWindow architecture (this re-uses it)
