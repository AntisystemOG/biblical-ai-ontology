---
description: PyInstaller single-file EXE builds for PySide6 desktop apps on Windows — asset bundling, _MEIPASS path mapping, and common pitfalls.
title: PyInstaller Desktop App Bundling
name: pyinstaller-desktop-app
tags: [pyinstaller, pyside6, desktop, windows, exe, bundling]
version: 1.0.0
---

# PyInstaller Desktop App Bundling

Build single-file Windows executables from Python/PySide6 projects. Covers asset inclusion, `_MEIPASS` runtime path resolution, and the most common bundling failure modes.

## When to use this skill

- Building a `.exe` from a PySide6 / Qt / tkinter desktop app using PyInstaller
- Images, icons, fonts, or data files are missing from the built executable
- `_asset_path()` or resource loading works in `python -m app` but fails in the `.exe`
- Adding new static assets (images, JSON, CSV) to the bundle

## Prerequisites

- Python 3.x with `pyinstaller` installed (`pip install pyinstaller`)
- A working `.spec` file or `build_exe.py` script
- Project uses `sys._MEIPASS` (or `hasattr(sys, "_MEIPASS")`) for runtime path resolution

## Step-by-step

### 1. Verify assets are declared in the `.spec` file

The `datas` list in the `.spec` maps source directories to bundle paths:

```python
datas=[
    ('src/my_app/assets',   'my_app/assets'),     # images, icons
    ('src/my_app/gui/assets', 'my_app/gui/assets'),
    ('src/my_app/data',     'my_app/data'),       # JSON, CSV
],
```

**Rule:** The second string is the **bundle-relative path** inside `_MEIPASS`. All code that loads bundled files must use this exact path.

### 1b. Data files (JSON, CSV, XML) — same rule, silent failure

Data files fail **silently** when missing — no visual error, just empty results.

**Specific example from I/O alarm pairs JSON:**
The `io_alarm_pairs.json` catalog lives at `src/plc_tools/catalog/io_alarm_pairs.json`. If it is not added to the `.spec` `datas` list, the EXE loads zero alarm pairs at startup. The app runs fine but the background alarm watcher is permanently silent. No visual symptom — the user just never sees I/O Reaction alarms.

```python
datas=[
    ('src/plc_tools/assets',              'plc_tools/assets'),    # images
    ('src/plc_tools/gui/assets',          'plc_tools/gui/assets'),
    ('src/plc_tools/catalog/io_alarm_pairs.json', 'plc_tools/catalog'),  # MUST be here
],
```

**Critical:** Never `try/except FileNotFoundError: pass` on data loads in bundled apps. When the file is missing inside `_MEIPASS`, the EXE runs fine but produces empty data. Always warn on 0 records:

```python
try:
    with open(_json_path("config.json")) as f:
        data = json.load(f)
    if not data:
        logger.warning("Loaded 0 records — check .spec datas")
except FileNotFoundError:
    logger.error("Missing bundled data file — add to .spec datas")
    data = []
```

### 2. Write `_asset_path()` correctly

```python
from pathlib import Path
import sys

def _asset_path(filename: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "my_app" / "assets" / filename
    return Path(__file__).parent.parent.parent / "assets" / filename
```

**Critical pitfall:** Using `sys._MEIPASS / "assets"` directly is wrong — the bundle path includes the second element of the `datas` tuple (`my_app/assets`). Always match:

| `datas` entry | Correct `_MEIPASS` path |
|---|---|
| `('src/my_app/assets', 'my_app/assets')` | `sys._MEIPASS / "my_app" / "assets"` |
| `('src/my_app/gui/assets', 'my_app/gui/assets')` | `sys._MEIPASS / "my_app" / "gui" / "assets"` |

### 3. Test the bundle before declaring victory

1. Run `python -m my_app.app` — verify images load
2. Build: `pyinstaller MyApp.spec --distpath dist --workpath build/work --noconfirm`
3. Run the `.exe` directly (not through IDE)
4. Visually confirm every image, icon, and asset renders

### 4. Diagnosing missing assets

If assets work in development but not the `.exe`:

1. Add debug logging in `_asset_path()`:
   ```python
   path = _asset_path("banner.png")
   print(f"Asset path: {path}, exists={path.exists()}")
   ```
2. Build with `--debug` temporarily to see console output
3. Or extract the `.exe` with `pyi-archive_viewer` to inspect bundled files

### 5. Common `hiddenimports`

For PySide6 apps, add to `.spec`:

```python
hiddenimports=[
    'PySide6.QtWidgets',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.sip',
]
```

### 6. The running-EXE lockfile problem (2026-06-02 update)

Windows locks the `.exe` while it is running, including an old version still running on the taskbar. If you try to rebuild while the app is open (or a previous build is still alive), PyInstaller throws:

```
PermissionError: [WinError 5] Access is denied: 'dist\\MyApp.exe'
```

**Fix options (in order of preference):**

1. **Close the running application first** (cleanest, prevents user data loss)
2. **Rename the locked `.exe` to free the dist directory** — works even when the app is still running or the file is held by Windows Defender / antivirus:
   ```bash
   mv dist/MyApp.exe dist/MyApp.exe.locked
   # then rebuild
   rm -f dist/MyApp.exe.locked   # clean up after successful new build
   ```
3. **Kill the process** in Task Manager (last resort)

**Why rename-not-delete:** In a WSL terminal, `rm` of a locked Windows `.exe` may silently fail or return an error. Renaming always succeeds because Windows permits renaming locked files. After the rename, the dist directory is free for PyInstaller to write a new `.exe`.

**Anti-pattern:** Do NOT retry `pyinstaller` blindly without first freeing the lock. It fails 100% of the time.

---

### Build-verified quality gate (2026-06-02 update)

A repeatable gate script for builds. Integrates with the `plc-diagnostic-system` quality gate:

```bash
#!/usr/bin/env bash
# run_quality_gate.sh
set -e

# 1. Syntax check changed files
python3 -m py_compile src/plc_tools/gui/tabs/playback_record.py $\ ...

# 2. Full-project AST parse
python3 -c "
import ast, os
base = 'src/'
ok = True
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    ast.parse(fh.read())
            except SyntaxError as e:
                ok = False
                print(f'SYNTAX ERROR: {path} line {e.lineno}')
print('All OK' if ok else 'FAILED')
"

# 3. Stale reference hunt (dynamic: add recent removed symbols here)
# After a refactor that removes a class/attr, grep for any leftover references.
# Example: after removing PlaybackStrip, grep for any remaining _pb_strip usage.
# for sym in old_symbol1 old_symbol2; do
#     if grep -rn "$sym" src/ --include="*.py"; then
#         echo "STALE REFERENCE: $sym"
#         exit 1
#     fi
# done

# 4. Build
/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe build_exe.py

# 5. Verify
ls -lh dist/Degater\ PLCTool\ BST33\ and\ 35.exe
```

**Exit condition:** gate script exits 0 with EXE present → deploy.

## Verification checklist

- [ ] **All data files (JSON, CSV, XML) listed in `datas`**
- [ ] `_asset_path()` uses the bundle path matching `datas` second element
- [ ] `.exe` tested standalone (not from IDE terminal)
- [ ] No hardcoded `C:\` or absolute paths in asset loading code
- [ ] `console=False` set in `.spec` for production builds
- [ ] **No running `.exe`** (or renamed) before rebuild — Windows locks the file. Use `mv dist/MyApp.exe dist/MyApp.exe.old` if an old build is still running.
- [ ] Zero-record data loads emit a warning (not silently empty)
- [ ] Dead-code / dead-asset audit completed before build
- [ ] `AGENTS.md` / `ARCHITECTURE.md` synced with current source tree
- [ ] Zero syntax errors (run gate script or `python -m py_compile`)
- [ ] Zero stale references after refactor

## Pitfalls

1. **Path mismatch #1** — `_MEIPASS / "assets"` when `datas` maps to `"my_app/assets"`
2. **Path mismatch #2** — Using `__file__` parent chain that differs between dev and bundle layout
3. **Missing hiddenimports** — PySide6 submodules (`QtCore`, `QtGui`) may not auto-detect
4. **Console window** — Forgetting `console=False` leaves a black terminal behind the GUI
5. **UPX corruption** — If icons render as blank squares, try `upx=False` in the `.spec`
6. **Silent 0-record data loads** — JSON/CSV missing from `datas` produces no error, just empty collections. Always warn when loading 0 records.
7. **Bundling entire directories that contain dead weight** — `('src/assets', 'assets')` pulls every file in the folder, including 350+ unused EMF/PNG rung images. Prefer individual-file entries or dead-code pruning before build.

## Bloat Cleanup — Keeping the EXE Lean

Before every rebuild, audit for dead code/assets. Leftover files inflate the EXE and hiddenimports list, slowing startup and tab switching.

### Dead-code discovery workflow

```bash
# 1. Find all Python source files
find src/ -name "*.py"

# 2. For each module, grep the entire tree for its class name / import
# If ZERO non-class-definition hits, the module is dead
grep -r "FaultLogTab\|fault_log\.py" src/ --include="*.py" | grep -v "class FaultLogTab"

# 3. Check the main entry point / main_window for instantiation
grep -r "FaultLogTab(" src/plc_tools/gui/main_window.py

# 4. If never instantiated AND never imported → delete before build
```

### Asset audit

```bash
# List files in each assets/ dir and cross-check against actual loads
# Look for _asset_path(), QPixmap(), or open() calls in source
grep -r "banner\.png\|micro850\.jpg" src/ --include="*.py"
```

### Spec pruning checklist

- [ ] Remove dead `hiddenimports` (modules deleted or never auto-imported)
- [ ] Replace directory `datas` entries with individual files when the directory has dead weight
- [ ] Add `excludes` for stdlib modules PyInstaller wrongly includes:
  ```python
  excludes=[
      'tkinter', 'matplotlib', 'scipy', 'pandas', 'jinja2',
      'pytest', 'unittest', 'xmlrpc', 'pydoc', 'email', 'html',
      'http', 'ftplib', 'urllib', 'lib2to3', 'curses',
  ]
  ```
- [ ] Remove unused dependencies from `pyproject.toml` / `requirements.txt`
- [ ] Purge `__pycache__` and `.egg-info` before build

## References

- `references/pyinstaller-datas-mapping.md` — Mapping table and worked example from Degater project. Covers images AND JSON/CSV data files with silent-failure analysis.
- `references/pyinstaller-debug.md` — Quick debug script to inspect `_MEIPASS` contents at runtime
- `references/pyinstaller-bloat-cleanup.md` — Full dead-code/asset discovery workflow, spec-pruning checklist, Python-based scanner, and architecture-doc sync steps.
- `references/auto-version-bump.md` — Automatic `MAJOR.WEEKLY.BUILD` version bumping integrated into the build script. Every PyInstaller rebuild auto-increments the build number.