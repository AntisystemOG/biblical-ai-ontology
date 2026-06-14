# Session: TCP TIME_WAIT Socket Teardown for Micro870 Reconnect — 2026-06-03

## Problem

After a **manual disconnect** or any TCP session teardown, attempting to reconnect to the Allen-Bradley Micro870 PLC would **fail indefinitely**. The only way to recover was to close the entire application.

Disabling auto-reconnect did **not** fix the issue. The problem was fundamentally at the OS network layer.

## Root Cause: Windows TIME_WAIT

pycomm3's `Socket.close()` only calls `socket.close()`:

```python
# socket_.py (pycomm3)
def close(self):
    self.sock.close()
```

On Windows, `close()` without `shutdown(SHUT_RDWR)` leaves the TCP connection in `TIME_WAIT` state for approximately **60 seconds**. During this window, the Micro870 rejects new CIP/TCP session attempts because the previous session is still recorded as half-open.

Unlike ControlLogix, the Micro870 does **not** aggressively garbage-collect half-closed sessions.

## Fix: Force Socket Shutdown Before Close

In `micro800_driver.py:disconnect()`, bypass pycomm3's wrapper and directly call `shutdown(SHUT_RDWR)` + `close()` on the underlying `socket.socket`:

```python
import socket

def disconnect(self) -> None:
    if self._plc is not None:
        try:
            self._plc.close()
        except Exception:
            pass

        # Force raw socket teardown to avoid TIME_WAIT on Windows
        raw = (
            self._plc._sock.sock
            if (
                getattr(self._plc, "_sock", None)
                and getattr(self._plc._sock, "sock", None)
            )
            else None
        )
        if raw is not None:
            try:
                raw.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                pass
            try:
                raw.close()
            except (OSError, socket.error):
                pass

        try:
            self._plc._sock = None
        except (OSError, AttributeError):
            pass

        try:
            del self._plc
        except AttributeError:
            pass
        self._plc = None
```

**Key steps explained:**

| Step | Purpose |
|---|---|
| `self._plc.close()` | Graceful pycomm3 cleanup (CIP Close service) |
| `raw.shutdown(socket.SHUT_RDWR)` | Sends FIN to remote host → immediate release from TIME_WAIT |
| `raw.close()` | Actually frees the socket descriptor |
| `self._plc._sock = None` | Cuts pycomm3's internal reference to dead socket |
| `del self._plc` | Removes the `LogixDriver` instance from memory |
| `self._plc = None` | Clears the driver reference |

## Complementary Fix: gc.collect() Before New Connection

Even after `shutdown()`/`close()`, the OS socket handle may still be held by the process's kernel reference table until Python's garbage collector reaps the object. Adding `gc.collect()` inside `ConnectionManager.connect()` forces immediate handle release:

```python
import time
import gc

def connect(self, ip, slot=0, plc_type="micro800"):
    if self.is_connected():
        self.disconnect()
        time.sleep(0.8)   # let Micro870 GC old TCP/CIP session
        gc.collect()      # force Windows to reap closed socket handle
    self._driver = self._create_driver(ip, slot, plc_type)
    return self._driver.open()
```

**Why both `_do_disconnect` idle wait and `gc.collect()`?**
- `_do_disconnect` waits for in-flight reads to finish → prevents half-closed socket creation
- `gc.collect()` forces handle release AFTER the 0.8s cooldown → ensures the new `socket.socket()` call gets a fresh Windows handle

## Verification

Without the fix:
1. Connect → succeed
2. Disconnect → succeed
3. Click Connect again → "Connection Failed" every time
4. Wait 60s → still fails (socket handle is cached by Python, not just TIME_WAIT)
5. Restart app → succeeds immediately (fresh process = fresh state)

With the fix:
1. Connect → succeed
2. Disconnect → succeed
3. Click Connect again → succeed immediately
4. Repeat connect/disconnect 10+ times → consistent success

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|---|---|
| Only call `self._plc.close()` | pycomm3 `Socket.close()` lacks `shutdown()` → TIME_WAIT |
| Only call `socket.close()` on wrapper | Windows still holds the handle in the kernel |
| Add `SO_REUSEADDR` on client socket | Not applicable to client sockets; only works for `bind()` |
| Retry immediately without delay | Micro870 needs sub-second cooldown to GC old CIP instance |
| Rely on pycomm3 default cleanup | pycomm3 does not call `shutdown()` — verified by reading `socket_.py` |

## Related Skill References

- `SKILL.md` Section 6.2 "Disconnect Must Wait for In-Flight CIP Reads"
- `references/session-2026-06-02-diagnostics-freeze-reconnect.md` — earlier idle-wait + cooldown analysis
- `references/session-2026-06-03-signal-shadowing-connect-worker.md` — overlapping threads also prevented reconnect
