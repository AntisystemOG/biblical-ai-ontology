# Session: Crash Handler Popup — Thread-Safe QMessageBox for Unhandled Exceptions

**Date:** 2026-06-03
**Issue:** Existing `write_crash_log()` saved files silently; operators had no indication the app crashed.
**Fix:** Add `QMessageBox.Critical` popup with exception name, message, log path, and version.

## Problem Statement

The Degater PLC Tool already had a crash log writer (`%LOCALAPPDATA%\Degater PLC Tool\crash_logs\crash_YYYYMMDD_HHMMSS.txt`) triggered by `sys.excepthook` and `QtFatalHandler`. However, an operator staring at a frozen GUI had no idea a crash occurred — they might restart the PC unnecessarily or call IT for a non-issue. A user-facing popup is required.

## Implementation

### Existing Infrastructure (No Changes)

- `install_excepthook()` — wraps `sys.excepthook`
- `install_qt_fatal_handler()` — intercepts qInstallMessageHandler critical/fatal messages
- `write_crash_log(exc_type, exc_value, tb)` — writes timestamp, version, Python/platform info, memory stats (if psutil), active threads, full traceback

### New: Popup Dialog

Inserted inside `write_crash_log()` after the file is written:

```python
import threading
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer

def _show_crash_popup(exc_type, exc_value, log_path):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Application Error")
    msg.setText(f"Unhandled exception: {exc_type.__name__}")
    msg.setInformativeText(
        f"A crash log was saved to:\n{log_path}\n\n"
        f"Version: {__version__}\n\n"
        f"Please report this to your PLC technician with the log file."
    )
    msg.exec()

def write_crash_log(exc_type, exc_value, tb):
    # ... existing log writing code ...
    if threading.current_thread() is threading.main_thread():
        _show_crash_popup(exc_type, exc_value, log_path)
    else:
        QTimer.singleShot(0, lambda: _show_crash_popup(exc_type, exc_value, log_path))
```

### Thread-Safety Rationale

If a crash originates in a background `QThread` (e.g., `_PollWorker`), calling `QMessageBox.exec()` directly can deadlock Qt's event loop because `exec()` starts a nested event loop on the wrong thread. The fix:

- **Crashes on main thread:** Call `_show_crash_popup()` directly.
- **Crashes on background thread:** Use `QTimer.singleShot(0, ...)` to schedule the popup on the main thread's event loop.

## Secondary Fix: Docstring SyntaxWarning

The crash log path contains backslashes. An existing docstring used single backslashes, triggering Python's `SyntaxWarning`:

```python
# BAD — produces SyntaxWarning: invalid escape sequence '\D'
"""Writes crash_log to %LOCALAPPDATA%\Degater PLC Tool\crash_logs ..."""

# GOOD — no warning
"""Writes crash_log to %LOCALAPPDATA%\\Degater PLC Tool\\crash_logs ..."""
```

Always verify with `python -m py_compile` after modifying docstrings that mention Windows paths.

## Verification

1. `python -m py_compile src/plc_tools/utils/__init__.py` → clean
2. `python -m py_compile src/plc_tools/app.py` → clean
3. `python scripts/verify_tag_consistency.py` → passes
4. Build EXE to include changes (done in follow-up step)

## Files Modified

- `src/plc_tools/utils/__init__.py` — added popup, fixed docstring escaping
- `src/plc_tools/app.py` — no changes (already called `install_excepthook()`)
