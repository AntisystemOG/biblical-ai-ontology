# Confusion: PyInstaller `noarchive=True` vs PySide6 Shared Libraries

**Date:** 2026-05-30
**Project:** Degater PLC Tool BST33 and 35
**Skill:** elite-coder-toolkit

## The Pitfall

In a session focused on "RAM residency" performance optimization, the agent
assumed `noarchive=True` was the right setting for PyInstaller to keep Python
modules inside the EXE instead of extracting them to a temporary directory at
runtime.

However, the project's `PLCTools.spec` already had a comment explaining that
`noarchive=False` was intentional — PySide6 and PIL shared libraries need to
unpack into `sys._MEIPASS` so the Windows loader can resolve DLL dependencies.
Setting `noarchive=True` would actually *break* the frozen EXE by preventing
those shared libraries from being extracted.

## What Actually Works

For performance on a PySide6 + PyInstaller Windows app, the correct levers are:

1. **`upx=False`** — Disable UPX compression so EXE pages stay uncompressed.
   This reduces CPU at startup and keeps pages mappable directly.
   Already applied in `PLCTools.spec`.

2. **`noarchive=False`** — Keep this as-is. PySide6/PIL DLLs need extraction.

3. **Pre-load shared assets** — Cache `QPixmap` immediately after PLC connect
   so tab switching is instant, not on first view.
   Already applied in `main_window.py` (`preload_shared_assets()`).

4. **Batch disk I/O** — Don't write JSON on every log event. Use a deferred
   flush timer (e.g., 5-second single-shot QTimer) for event logs.
   Applied to `alarms_log.py`.

## Lesson

When a user asks to "finish what you were doing," verify what was actually done
before hallucating additional changes. Read the actual spec diff before claiming
a change was made. `git diff --cached` or `git diff` is free — use it.

## Correct Commit Message Template for This Project

```
perf: did X and Y

- Actually did X: changed line N in file.py (not what the previous
  commit claimed)
- Actually did Y: adjusted foo.py to do bar
- Did NOT do Z: noarchive remains False because PySide6 DLLs need it
```
