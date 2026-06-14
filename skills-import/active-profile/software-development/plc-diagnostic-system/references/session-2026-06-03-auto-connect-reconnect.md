# Session: Auto-Connect / Auto-Reconnect Implementation — 2026-06-03

## Context

Feature request: automatically connect to the PLC when the app starts, and automatically reconnect when disconnected. Both behaviors must be toggleable from the File menu and ON by default. After 2 failed attempts, show a warning popup.

## Files Changed

- `src/plc_tools/gui/main_window.py` — all changes
- `src/plc_tools/communication/micro800_driver.py` — raw socket teardown fix
- `src/plc_tools/communication/connection_manager.py` — `gc.collect()` before new driver
- `PROJECT_MEMORY.md` — documentation update

## Implementation Detail

### New Imports

```python
from PySide6.QtCore import QSettings  # added to existing QtCore imports
```

### New State in `__init__`

```python
self._settings = QSettings("Intralox", "DegaterPLCTool")
self._auto_connect_enabled = bool(self._settings.value("auto_connect", True, type=bool))
self._auto_reconnect_enabled = bool(self._settings.value("auto_reconnect", True, type=bool))
self._auto_reconnect_attempts = 0
self._auto_connect_failed_shown = False
self._startup_connect_done = False  # one-shot guard for showEvent
self._connect_in_progress = False    # overlapping worker guard
self._reconnect_timer = QTimer(self)  # cancellable timer
self._reconnect_timer.setSingleShot(True)
self._reconnect_timer.timeout.connect(self._try_reconnect)
```

### Menu Items Added (`_build_menu`)

Two checkable `QAction`s under File menu:
- **Auto Connect** — controls startup behavior
- **Auto Reconnect** — controls runtime retry behavior

### Startup Auto-Connect (`showEvent`)

```python
def showEvent(self, event) -> None:
    super().showEvent(event)
    if self._startup_connect_done or not self._auto_connect_enabled:
        return
    if self._conn_mgr.is_connected:
        return
    self._startup_connect_done = True
    cfg = ...  # resolve last-known / project-entry / hardcoded fallback
    self._reconnect_timer.stop()   # cancel any pending retry
    self._connect_in_progress = True
    self._worker = _ConnectWorker(self._conn_mgr, cfg)
    self._worker.connect_done.connect(self._on_connect_finished)
    self._worker.start()
```

**Guard:** `_startup_connect_done` prevents re-trigger on window hide/show (multi-monitor setups, window manager restore).

### Runtime Auto-Reconnect (`_do_disconnect`)

```python
def _do_disconnect(self) -> None:
    was_connected = self._conn_mgr.is_connected  # remember BEFORE teardown
    # ... teardown ...
    if was_connected and self._auto_reconnect_enabled:
        self._auto_reconnect_attempts = 0
        self._reconnect_timer.start(3000)   # cancellable named timer
```

**Why `was_connected` is needed:** If the app starts disconnected and auto-connect is disabled, a manual disconnect should NOT trigger auto-reconnect. Only disconnections that break an active connection should retry.

### Unified Retry Handler (`_try_reconnect`)

Resolves config with a 3-level fallback:
1. `self._conn_mgr.config` (last successful)
2. `self._proj_mgr.get("DEG System BST33/35")` (project entry)
3. Hardcoded `ConnectionConfig(ip="192.168.1.197", slot=0, PLCType.MICRO870)`

Early-exit guard: `if self._connect_in_progress: return`

### Failure Tracking (`_on_connect_finished`)

Both auto-connect failures (startup) and auto-reconnect failures (runtime) increment the same counter:

| Attempts | Behavior |
|---|---|
| 1 | Log error to alarm tab, retry via named timer |
| 2 | Same + show `QMessageBox.warning()` once |
| 3–9 | Retry via named timer, no popup |
| 10 | Log "gave up" to alarm tab, stop retrying |

**State reset:** Success sets `_auto_reconnect_attempts = 0` and `_auto_connect_failed_shown = False` so the next incident starts fresh.

**Connecting-in-progress reset:** `_connect_in_progress = False` is set at the TOP of `_on_connect_finished`, before any success/failure branching.

### Warning Popup Text

```
PLC connection could not be established after 2 attempts.

Error: {error}

Auto-connect and auto-reconnect are active — attempts will continue.
Disable them in  File → Auto Connect  if you want to remain offline.
```

### Why Not `QMessageBox.critical` on Every Failure

The original code showed `QMessageBox.critical(self, "Connection Failed", error)` on every connect failure. With auto-reconnect enabled, this would create a modal popup every 3 seconds — unusable. Changed to a single warning at the 2-attempt threshold.

### Cancellable Timer (Critical Fix)

Originally used `QTimer.singleShot(3000, self._try_reconnect)`. This cannot be cancelled. If the user clicked Connect during the 3-second window, a new `_ConnectWorker` started while the old retry timer was still armed → two workers collided.

**Fix:** Replaced with named `QTimer` + `.stop()` at every manual connect entry point:
- `_quick_connect`
- `_show_connect_dialog`
- `showEvent`

## Pitfall: `showEvent` Without One-Shot Guard

Without `_startup_connect_done`, `showEvent()` fires on every window show (minimize→restore, multi-monitor window move, OS wake). This would spawn multiple concurrent `_ConnectWorker` threads. Always use a boolean guard.

## Pitfall: Overlapping `_ConnectWorker` Threads

`_ConnectWorker` is a `QThread`. If `_try_reconnect` runs while a previous `_ConnectWorker` is still running, two threads share the same `ConnectionManager` state. The event-driven named timer + `_connect_in_progress` guard prevents overlap.

## Pitfall: Signal Shadowing (`finished` vs `connect_done`)

`_ConnectWorker.finished = Signal(bool, str)` shadowed `QThread.finished()`, causing a phantom `(False, "")` callback after every successful connect. Renamed to `connect_done`. See `references/session-2026-06-03-signal-shadowing-connect-worker.md` for deep-dive.

## Testing Without PLC (WSL)

```bash
cd "/mnt/c/Users/thadd/.claude/projects/Degater PLC Tool BST33 and 35"
python3 -m py_compile src/plc_tools/gui/main_window.py
```

PySide6 is not available in WSL Python, so a full import test requires Windows Python:

```bash
/mnt/c/Users/thad/AppData/Local/Programs/Python/Python314/python.exe \
  -m py_compile src/plc_tools/gui/main_window.py
```
