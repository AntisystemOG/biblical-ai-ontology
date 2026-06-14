# Session 2026-06-03: Signal Shadowing in `_ConnectWorker`

## Problem

After a connect operation succeeded, the **Connect** button became permanently disabled.
Clicking it had no effect. Reconnect attempts fired automatically every 3 seconds,
incrementing a retry counter that eventually showed a warning popup even though the
initial connect had worked.

## Root Cause

The `_ConnectWorker(QThread)` helper declared a custom signal:

```python
class _ConnectWorker(QThread):
    finished = Signal(bool, str)   # ❌ shadows QThread.finished()
```

This shadowed `QThread.finished` — a built-in signal Qt emits automatically when a `QThread`
finishes execution. After `run()` returned, Qt emitted its native `finished()` signal.
PySide6 mapped this through the overloaded Python `finished` attribute, delivering it with
**default-constructed** `(False, "")` arguments.

The GUI had connected `_on_connect_finished` to this signal:

```python
self._worker.finished.connect(self._on_connect_finished)
```

So `_on_connect_finished` fired **twice** per connect:
1. Once with `(True, "")` from the explicit `emit` inside `run()`.
2. Once with `(False, "")` from Qt's implicit thread-exit emission.

The second call treated the successful connect as a failure, incrementing
`_auto_reconnect_attempts` and scheduling `QTimer.singleShot(3000, self._try_reconnect)`.
After any manual or programmatic disconnect, the counter was already elevated, and the
connect button was stuck in a "retrying" state.

## Fix

Renamed the custom signal to a unique name that cannot collide with any Qt built-in:

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

Updated **all four** call sites in `main_window.py`:

| Method | Old | New |
|---|---|---|
| `_quick_connect` | `self._worker.finished.connect(...)` | `self._worker.connect_done.connect(...)` |
| `_show_connect_dialog` | `self._worker.finished.connect(...)` | `self._worker.connect_done.connect(...)` |
| `_try_reconnect` | `self._worker.finished.connect(...)` | `self._worker.connect_done.connect(...)` |
| `showEvent` (startup auto-connect) | `self._worker.finished.connect(...)` | `self._worker.connect_done.connect(...)` |

## Verification

- `grep -rn "_worker.finished" src/` → zero hits
- `grep -rn "finished" src/plc_tools/gui/main_window.py` → only `QThread` references, none tied to `_worker`
- `python3 -m py_compile src/plc_tools/gui/main_window.py` → exit code 0

## Impact on Auto-Connect / Auto-Reconnect

The signal shadowing bug was masked by the auto-reconnect feature. Without auto-reconnect,
the connect button would still have appeared disabled after a single connect, but the user
might have noticed it immediately. With auto-reconnect enabled, the phantom failure callback
kept the retry loop alive and made the button seem permanently broken.

This fix makes the auto-connect / auto-reconnect architecture (Section 8 of `SKILL.md`)
actually functional. Before this fix, every successful connect was immediately followed
by a false failure event.

## Lessons

- **Never name a custom QThread signal `finished`**, `started`, `running`, or any other
  `QThread` built-in signal name.
- **PySide6 does not raise errors on signal shadowing.** It silently overloads the Python
  attribute, and Qt's native emissions leak through with default args.
- **Always grep for the old signal name** after a rename to catch stale references in
  `.connect()`, `.disconnect()`, and `.emit()` calls.
