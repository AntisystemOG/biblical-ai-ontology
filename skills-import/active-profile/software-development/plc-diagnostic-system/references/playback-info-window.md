# Playback Info Window

## Purpose

When a timeline recording is loaded for review, immediately open a **non-modal** `PlaybackInfoWindow` that floats above the main window. The user can interact with playback controls while the info panel stays visible, or close it without affecting playback.

## Dialog Features

- **Controller metadata**: IP address, PLC type, firmware version, catalog code
- **Snapshot stats**: total snapshots, duration, first/last timestamps (ISO 8601)
- **Keep on Top toggle**: checkbox pins the window above the main app with `Qt.WindowStaysOnTopHint`
- **Return to Live button**: emits `return_to_live_requested` signal; parent connects it to `_set_data_mode("live")`
- **Non-modal**: uses `.show()`, not `.exec()` — user can keep using playback controls

## Why Non-Modal?

The original implementation used `.exec()` (modal), which blocked the entire application. The user couldn't interact with the timeline scrubber, play/pause, or any other playback controls until the dialog closed. This was discovered after runtime feedback.

**Conversion pattern:**
1. Change `.exec()` → `.show()`
2. Replace `done(42)` / `result()` detection with a `Signal()` — `return_to_live_requested = Signal()`
3. Add "Keep on Top" checkbox so the dialog can be pinned if desired
4. Store the dialog reference in the parent (`self._playback_info_dialog`) to prevent garbage collection

## Signal-Based Result Delivery

```python
class PlaybackInfoWindow(QDialog):
    return_to_live_requested = Signal()

    def _request_return_to_live(self):
        self.return_to_live_requested.emit()
        self.close()
```

**Handler in MainWindow:**

```python
self._playback_info_dialog = PlaybackInfoWindow(recording, self)
self._playback_info_dialog.return_to_live_requested.connect(
    lambda: self._set_data_mode("live")
)
self._playback_info_dialog.show()   # non-modal
```

## Keep on Top Toggle

```python
def _toggle_on_top(self, state: int):
    flags = self.windowFlags()
    if state:
        self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
    else:
        self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
    self.show()
```

## Lifecycle

```
User clicks Load Recording
    → MainWindow._on_load_recording_clicked()
        → timeline_recorder.load_recording(path)
        → tab_playback.load_recording(recording)
        → pb_strip.arm(recording)
        → nav_list.setCurrentRow(PLAYBACK_TAB_INDEX)
        → _on_recording_loaded(recording)   # NEW in this session
            → close any existing info dialog (prevent duplicates)
            → instantiate PlaybackInfoWindow(recording, self)
            → connect return_to_live_requested → _set_data_mode("live")
            → show()  (non-modal, no blocking)
        → _set_data_mode("playback")
        → show status message
```

## Code Snippet

```python
class PlaybackInfoWindow(QDialog):
    return_to_live_requested = Signal()

    def __init__(self, recording: TimelineRecording, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Playback Info — {recording.title or 'Timeline Recording'}")
        self.setMinimumSize(480, 400)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        self._on_top = False
        self._build_ui(recording)

    def _build_ui(self, recording):
        layout = QVBoxLayout(self)
        # ... controller info table, snapshot stats, timing info ...

        btn_row = QHBoxLayout()
        self._top_ck = QCheckBox("Keep on Top")
        self._top_ck.stateChanged.connect(self._toggle_on_top)
        btn_row.addWidget(self._top_ck)
        btn_row.addStretch()

        live_btn = QPushButton("🔴 Return to Live")
        live_btn.clicked.connect(self._request_return_to_live)
        btn_row.addWidget(live_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _toggle_on_top(self, state: int):
        self._on_top = bool(state)
        flags = self.windowFlags()
        if self._on_top:
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def _request_return_to_live(self):
        self.return_to_live_requested.emit()
        self.close()
```

## Anti-Patterns

| Anti-Pattern | Why Bad | What To Do |
|---|---|---|
| `.exec()` on info window | Blocks all playback controls | `.show()` + `Signal()` for results |
| No parent reference | Dialog garbage-collected, silent disappearance | Store in `self._playback_info_dialog` |
| Modal without Keep on Top | User can't see info while scrubbing | Add checkbox for `WindowStaysOnTopHint` |
| Result code magic numbers (`42`) | Fragile, hard to grep, no type safety | Named `Signal()` with explicit connection |
| Not closing previous dialog on new load | Multiple dialogs stack up | Close existing before creating new |

