# Session: Auto-Connect/Reconnect Bug — Overlapping Threads + Cancellable Timer — 2026-06-03

## Problem

The auto-reconnect feature worked on the first connect, but after any disconnect (manual or network hiccup), clicking **Connect** again had no effect. The only recovery was closing and restarting the app.

Disabling auto-reconnect did not fix the issue. The root cause was a set of three layered bugs, all in `main_window.py`.

---

## Bug 1: Signal Shadowing on `_ConnectWorker.finished`

**Description:** `_ConnectWorker(QThread)` declared `finished = Signal(bool, str)`, which shadowed `QThread.finished()` — a built-in signal Qt emits automatically when a thread exits.

**Effect:** After `run()` returned, Qt emitted `finished()` with default-constructed args `(False, "")`. The `_on_connect_finished(False, "")` callback treated a successful connect as a failure, incremented `_auto_reconnect_attempts`, and scheduled a retry timer.

**Verification:** `grep -rn "_worker.finished" src/` returned zero hits after fix.

**Fix:** Rename signal to `connect_done = Signal(bool, str)`. Update all 4 call sites.

---

## Bug 2: Uncancellable `QTimer.singleShot`

**Description:** Auto-reconnect used `QTimer.singleShot(3000, self._try_reconnect)` to schedule a retry 3 seconds after disconnect.

**Effect:** If the user clicked **Connect** during that 3-second window, a new `_ConnectWorker` started while the old retry timer was still armed. Two workers ran simultaneously, sharing `ConnectionManager` state. The second worker's `connect()` call raced with the first, producing inconsistent results.

**Verification:** After fix, manual connect entry points call `self._reconnect_timer.stop()` before starting a new worker.

**Fix:** Replace `singleShot` with a named `QTimer`:

```python
self._reconnect_timer = QTimer(self)
self._reconnect_timer.setSingleShot(True)
self._reconnect_timer.timeout.connect(self._try_reconnect)
```

All manual connect entry points (`_quick_connect`, `_show_connect_dialog`, `showEvent`) now call `self._reconnect_timer.stop()` before creating a new worker.

---

## Bug 3: No Guard Against Overlapping Workers

**Description:** Without a connect-in-progress flag, two workers could start simultaneously — one from a manual click, one from an auto-reconnect timer.

**Effect:** `ConnectionManager.connect()` was called by two threads, both trying to create a new `Micro800Driver` while the old one was still tearing down. Result: "Connection Failed" every time.

**Fix:** Added `_connect_in_progress` boolean flag:

```python
def _quick_connect(self) -> None:
    self._reconnect_timer.stop()
    self._connect_in_progress = True
    # ... create worker ...

def _on_connect_finished(self, success: bool, error: str) -> None:
    self._connect_in_progress = False
    # ...
```

`_try_reconnect` also checks `if self._connect_in_progress: return` as an early-exit guard.

---

## Combined Verification

After all three fixes:
1. Connect -> succeed
2. Disconnect -> succeed, auto-reconnect timer starts (if enabled)
3. Click Connect immediately -> timer is cancelled, new worker starts, succeeds
4. Let auto-reconnect run -> succeeds after 3s delay
5. Disable auto-reconnect in File menu -> disconnect stays disconnected
6. Repeated connect/disconnect -> consistent success without app restart

## Anti-Patterns

| Anti-Pattern | Why It Fails | What To Do |
|---|---|---|
| `QTimer.singleShot` for retries | Cannot cancel if user intervenes | Use named `QTimer` + `.stop()` |
| No in-progress guard | Two workers collide on shared state | `_connect_in_progress` boolean |
| Shadow `QThread.finished` | Phantom failure callback after success | Rename to `connect_done` |
| Manual entry point doesn't stop retry timer | Race between manual connect and auto-retry | Call `_reconnect_timer.stop()` at every entry point |

## Related References

- `references/session-2026-06-03-signal-shadowing-connect-worker.md` — deep-dive on Qt signal shadowing
- `references/session-2026-06-03-tcp-timewait-socket-teardown.md` — Windows TIME_WAIT fix that uncovered the real problem
- `references/session-2026-06-02-diagnostics-freeze-reconnect.md` — idle-wait + cooldown from June 2
