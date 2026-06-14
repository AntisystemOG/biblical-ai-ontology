# PyInstaller Windows EXE Build from WSL

## Context
You are developing a Python desktop application (PySide6/pycomm3) on WSL (Windows Subsystem for Linux) but need to produce a Windows `.exe` via PyInstaller. The PyInstaller package is installed on the **Windows Python** side, not the WSL Linux Python side.

## Windows Python Location

Common paths to check:
```bash
# Most common (Python installed from python.org or Windows Store)
ls /mnt/c/Users/thadd/AppData/Local/Programs/Python/Python*/python.exe

# Alternative locations
ls /mnt/c/Python*/python.exe
ls /mnt/c/ProgramData/Anaconda3/python.exe

# Ask Windows itself
/mnt/c/Windows/System32/cmd.exe /c "where python"
```

Thad's Windows Python: `/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe`

## Verify PyInstaller Availability

```bash
/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe -m PyInstaller --version
```

Expected output: `6.x.x` (or whatever version is installed)

## Build Command

```bash
cd "/mnt/c/Users/thadd/.claude/projects/Degater PLC Tool BST33 and 35"
/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe build_exe.py
```

## Clean Rebuild

When you want a completely fresh build (not incremental):
```bash
rm -rf build/work
/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe build_exe.py
```

PyInstaller caches heavily in `build/work/`. Clean rebuilds eliminate stale artifacts but take longer (~3-5 min vs ~2 min incremental).

## Build Script Anatomy (`build_exe.py`)

```python
import subprocess
import sys

subprocess.run(
    [
        sys.executable, "-m", "PyInstaller",
        "PLCTools.spec",
        "--distpath", "dist",
        "--workpath", "build/work",
        "--noconfirm",
    ],
    check=True,
)
print("\nBuild complete: dist/Degater PLCTool BST33 and 35.exe")
```

Note: `sys.executable` resolves to whichever Python interpreter runs `build_exe.py`. When called from Windows Python, it's the Windows Python executable. When called from WSL via the Windows Python path, it's still the Windows Python executable.

## Pitfalls

### 1. `python` command not found in WSL
```
/usr/bin/bash: line 3: python: command not found
```
**Fix:** Use `python3` for WSL Python, or the full Windows Python path for Windows Python.

### 2. `No module named PyInstaller` in WSL Python
WSL Python doesn't have PyInstaller installed (and even if it did, it can't build Windows PE executables from Linux).
**Fix:** Always invoke the **Windows Python** executable directly.

### 3. SyntaxWarning during build
```
app.py:5: SyntaxWarning: "\D" is an invalid escape sequence
```
**Fix:** Convert docstrings containing Windows backslash paths to raw strings (`r"""`). See `elite-coder-toolkit` SKILL.md "Tool Pitfalls" section.

### 4. Build timeout in foreground
PyInstaller builds take 3-5 minutes. Foreground `terminal()` calls may timeout.
**Fix:** Use `background=true` with `notify_on_complete=true`, then `process(action="wait")` to poll for completion.

### 5. PySide6/Qt version mismatch between WSL dev and Windows build environments
**Symptom:** EXE builds successfully but crashes at launch with:
```
ImportError: cannot import name 'QAction' from 'PySide6.QtWidgets'
```
(or similar for `QActionGroup`, `QShortcut`, `QUndoCommand`, etc.)

**Root cause:** PySide6 relocated several classes from `QtWidgets` to `QtGui` in version 6.8+. Your WSL development environment may have an older PySide6 where the old import path still works, but the Windows Python used by PyInstaller has the newer version where those classes are only available in `QtGui`.

**Affected classes (PySide6 6.8+):**
- `QAction` → `PySide6.QtGui`
- `QActionGroup` → `PySide6.QtGui`
- `QShortcut` → `PySide6.QtGui`
- `QUndoCommand` → `PySide6.QtGui`
- `QUndoStack` → `PySide6.QtGui`
- `QFileSystemModel` → `PySide6.QtGui`

**Fix:** Update all affected imports to use `PySide6.QtGui` instead of `PySide6.QtWidgets`:
```python
# Before (breaks on PySide6 6.8+):
from PySide6.QtWidgets import QAction, QActionGroup

# After (works on all PySide6 versions):
from PySide6.QtGui import QAction, QActionGroup
```

**Prevention:** After any PySide6 code change that works in WSL, verify the same import paths work in the Windows Python environment:
```bash
/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe -c \
  "from PySide6.QtGui import QAction, QActionGroup; print('OK')"
```

**Detection:** If the WSL `python3` has an older PySide6 than Windows Python, you won't catch this during development. The error only surfaces in the frozen EXE. Always do a test build and launch after any import changes.

## Build Output Verification

```bash
ls -lh "/mnt/c/Users/thadd/.claude/projects/Degater PLC Tool BST33 and 35/dist/Degater PLCTool BST33 and 35.exe"
file "/mnt/c/Users/thadd/.claude/projects/Degater PLC Tool BST33 and 35/dist/Degater PLCTool BST33 and 35.exe"
```

Expected:
```
-rwxrwxrwx 1 thadd thadd 50M May 29 18:22 .../dist/Degater PLCTool BST33 and 35.exe
.../dist/Degater PLCTool BST33 and 35.exe: PE32+ executable for MS Windows 6.00 (GUI), x86-64
```

## Automation Pattern

For fully automated rebuilds from a WSL session:
```bash
# 1. Clean old build artifacts
rm -rf "/mnt/c/Users/thadd/.claude/projects/Degater PLC Tool BST33 and 35/build/work"

# 2. Run build with Windows Python
/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe \
  "/mnt/c/Users/thadd/.claude/projects/Degater PLC Tool BST33 and 35/build_exe.py"

# 3. Verify output exists and is valid PE
ls -lh "/mnt/c/Users/thadd/.claude/projects/Degater PLC Tool BST33 and 35/dist/"
```

### 6. Images missing in the EXE bundle (wrong `_MEIPASS` path)

**Symptom:** The EXE launches fine but images (banner.png, Manual.jpg, etc.) are not displayed — only text fallbacks or placeholders show.

**Root cause:** The `datas` directive in the `.spec` file maps source directories to bundle directories. The mapping is not 1:1 — it creates a subdirectory structure inside `sys._MEIPASS`.

Example spec:
```python
datas=[
    ('src/plc_tools/assets', 'plc_tools/assets'),
    ('src/plc_tools/gui/assets', 'plc_tools/gui/assets'),
],
```

This means the source file `src/plc_tools/assets/banner.png` is extracted at runtime to:
```
sys._MEIPASS / "plc_tools" / "assets" / "banner.png"
```

NOT to:
```
sys._MEIPASS / "assets" / "banner.png"     ← WRONG
```

**Fix:** Update `_asset_path()` to include the correct bundle prefix:
```python
def _asset_path(filename: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        # The spec maps src/plc_tools/assets  →  plc_tools/assets in the bundle
        return Path(sys._MEIPASS) / "plc_tools" / "assets" / filename
    return Path(__file__).parent.parent.parent / "assets" / filename
```

**Detection:** Test the EXE on a clean machine (no source tree). If images load from the source tree during development but not from the EXE, the `_MEIPASS` path is wrong.

**Prevention:** After adding any `datas` entry to the spec, verify the runtime path matches `sys._MEIPASS / <target_dir> / <filename>`.
- `elite-coder-toolkit` SKILL.md — "Tool Pitfalls" section for raw docstring fix
- `PROJECT_MEMORY.md` in project root — latest build timestamp and feature list
