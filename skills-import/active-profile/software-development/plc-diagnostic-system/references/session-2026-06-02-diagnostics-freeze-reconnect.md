# Session: Diagnostics Tab Freeze + False Alarms, Disconnect/Reconnect Failure (June 2, 2026)

## Bug 1 — Double Underscore: `D1__Low_Grip_Close_Sol`

**Symptom:** I/O Status tab shows `D1__Low_Grip_Close_Sol` (double underscore).

**Root cause:** `io_status.py` line 1410 had a ternary special-case:
```python
output_name = f"D{degater_num}__Low_Grip_Close_Sol" if degater_num == 1 else f"D{degater_num}_Low_Grip_Close_Sol"
```
The catalog (`io_catalog.py`), `physical_mapping.py`, and `io_alarm_pairs.json` all used single underscore `D1_Low_Grip_Close_Sol`. Only the UI generation logic was wrong.

**Fix:** Removed the special case. All three degaters now use the same naming convention.

**Lesson:** A double underscore in the UI that is NOT present in the catalog means the bug is in **UI generation code** (string formatting), not the catalog. Search for ternaries or f-strings with `__` before assuming the catalog is wrong.

---

## Bug 2 — Diagnostics Tab Switch Causes Freeze + False Alarms

**Symptom:** Switching to the Diagnostics tab causes a 2-5 second freeze. During/after the freeze, I/O Reaction Alarms fire falsely.

**Root cause:** `main_window.py` `_on_nav_changed()` auto-called `_load_diagnostics()` every time the Diagnostics tab was selected. `_load_diagnostics()` makes multiple **synchronous** pycomm3 CIP calls:
- `get_controller_info()` → Identity Object
- `get_controller_mode()` → Status word
- `get_expansion_modules()` → Slots 1-8 probe
- `get_motion_data()` → PTO axis reads
- `get_system_diagnostics()` → Fault object

These calls block the **GUI thread** for seconds. Meanwhile, the background `_PollWorker` (on its own QThread) continues running on the same pycomm3 instance. Its reads now error because the synchronous calls are hogging the CIP session. Read errors force outputs to `False` in the cached `io_values`, which trips the `IOAlarmWatcher` → false alarms fire.

**Fix:** Removed the auto-load from `_on_nav_changed()`. Diagnostics now only loads:
1. **Once on initial connect** (line 579 in `main_window.py`)
2. **When the user clicks the ↻ Refresh button** (already wired at line 339)

**Verification:** After removal, grep confirmed only two call sites for `_load_diagnostics()` remained: line 579 (initial connect) and line 339 (refresh button click).

---

## Bug 3 — Disconnect → Cannot Reconnect Without Restart

**Symptom:** Disconnecting while the degater is in cycle, then trying to reconnect, fails. Must close and restart the EXE.

**Root cause:** `_do_disconnect()` in `main_window.py` stopped the poll timer and immediately called `driver.disconnect()`. But `_PollWorker` could have an in-flight CIP read at that exact moment. Tearing down the TCP socket mid-read leaves it in a **half-closed state** on the Micro870. The PLC still thinks the old CIP/TCP session is alive, so it rejects the new `open()` attempt with "session already exists" behavior (implicit in Micro870 TCP/CIP stack).

**Fix:** Two-layer approach:

### Layer 1 — Client-side idle wait (`main_window.py`)
Rewrote `_do_disconnect()` to:
1. Stop the poll timer
2. Spin up to **0.3 s** while `_poll_worker._busy` is True
3. Only then set `self._driver = None` and call `disconnect()`

```python
def _do_disconnect(self):
    if self._poll_timer and self._poll_timer.isActive():
        self._poll_timer.stop()
    # Wait for in-flight poll to finish before tearing down socket
    waited = 0.0
    while self._poll_worker and getattr(self._poll_worker, "_busy", False) and waited < 0.3:
        time.sleep(0.05)
        waited += 0.05
    self._driver = None
    self._connection_manager.disconnect()
```

### Layer 2 — Server-side cooldown (`connection_manager.py`)
Inserted `time.sleep(0.8)` after `self.disconnect()` inside `ConnectionManager.connect()` before instantiating the new driver:

```python
def connect(self, ip, slot=0, plc_type="micro800"):
    if self.is_connected():
        self.disconnect()
        time.sleep(0.8)  # Let Micro870 GC old TCP/CIP session
    self._driver = self._create_driver(ip, slot, plc_type)
    return self._driver.open()
```

**Why both layers?** Either alone was insufficient in testing. The idle wait prevents mid-read teardown; the cooldown gives the PLC time to garbage-collect. Together they make reconnect reliable under live PLC load.

---

## Verification Steps Applied

| Check | Method | Result |
|---|---|---|
| Double underscore removed | `grep -n '__' src/plc_tools/gui/tabs/io_status.py` | No hits in tag generation |
| Diagnostics auto-load removed | `grep -n '_load_diagnostics' src/plc_tools/gui/main_window.py` | Only lines 579, 339 |
| Sleep placement correct | `grep -n 'time.sleep' src/plc_tools/communication/connection_manager.py` | Line 33, after disconnect |
| Tag consistency | `grep 'D1_Low_Grip_Close_Sol' src/plc_tools/catalog/*.py src/plc_tools/catalog/*.json` | Single underscore everywhere |

---

## Key Takeaways

1. **Never auto-load data-heavy tabs on tab switch.** If a tab requires synchronous CIP reads, make it manual (Refresh button) or run it in a dedicated background thread with result delivery via signal.
2. **Synchronous pycomm3 calls on the GUI thread stall the poll loop.** The poll worker continues on its thread but shares the pycomm3 instance, so reads error and cached values go stale → false alarms.
3. **Disconnect must wait for in-flight CIP reads.** pycomm3 is not thread-safe for concurrent operations on the same connection. Always check a `_busy` flag or equivalent before socket teardown.
4. **Micro870 needs TCP/CIP session cooldown.** Unlike ControlLogix, the Micro870 does not aggressively garbage-collect half-closed sessions. A sub-second sleep after disconnect is required for reliable reconnect.
