# Session: Crash Log Path — Write Next to EXE When Frozen

**Date:** 2026-06-03
**Issue:** Crash logs were written to `%LOCALAPPDATA%\\Degater PLC Tool\\crash_logs\\...`, which operators struggled to locate on production floor PCs.
**Fix:** Detect PyInstaller frozen state at runtime and redirect crash logs to a `crash_logs/` subfolder next to the `.exe`.

## The Change

Modified `_get_crash_dir()` in `plc_tools/utils/__init__.py`:

```python
def _get_crash_dir() -> Path:
    """..."""
    global _CRASH_DIR
    if _CRASH_DIR is not None:
        return _CRASH_DIR

    frozen = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
    if frozen:
        exe_dir = Path(sys.executable).resolve().parent
        _CRASH_DIR = exe_dir / "crash_logs"
    else:
        if sys.platform == "win32":
            base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        else:
            base = Path.home() / ".local" / "share"
        _CRASH_DIR = base / "Degater PLC Tool" / "crash_logs"

    _CRASH_DIR.mkdir(parents=True, exist_ok=True)
    return _CRASH_DIR
```

## Why It Matters

- **Production floor**: Operators running the `.exe` don't know about `AppData\\Local`.
- **IT support**: Crash logs are right next to the EXE — easy to find, copy to USB, or attach to emails.
- **Development**: Source runs still go to `%LOCALAPPDATA%` so devs aren't cluttering `dist/` with crash logs during testing.

## Detection Details

`sys.frozen` is set by PyInstaller (and cx_Freeze, PyOxidizer, etc.). `_MEIPASS` is PyInstaller-specific — the temp extraction directory. Checking **both** prevents false positives from other bundlers that set `frozen` but use a different layout.

## Docstring SyntaxWarning Fix

When updating the module docstring to advertise the new paths, old single-backslash Windows paths triggered:

```
SyntaxWarning: invalid escape sequence '\D'
```

Fix: always double-escape backslashes in docstrings (`\\\\`) or use `r"""` raw strings.

## Files Modified

- `src/plc_tools/utils/__init__.py` — `_get_crash_dir()` + docstring
