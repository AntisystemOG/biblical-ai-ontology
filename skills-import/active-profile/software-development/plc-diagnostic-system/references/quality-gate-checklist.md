# Quality Gate Checklist — Pre-Build & Post-Refactor

Mandatory quality gate. Do not skip. Run before every PyInstaller build and after every refactor of the Degater PLC Tool.

---

## 1. Syntax Check All Changed Files

For every `.py` file that was modified in this session:

```bash
python -m pycompile src/plc_tools/gui/main_window.py src/plc_tools/gui/widgets/connection_bar.py ...
```

Alternatively, use Python stdlib directly in the shell:

```python
import py_compile
import sys
files = [
    'src/plc_tools/gui/main_window.py',
    'src/plc_tools/gui/tabs/playback_info_window.py',
]
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"✓ {f}")
    except py_compile.PyCompileError as e:
        print(f"✗ {f}: {e}")
        sys.exit(1)
```

Pass criterion: every changed file compiles with `doraise=True`

---

## 2. Full-Project AST Parse

Re-parse every `.py` source file in the tree. A syntax error in a file you didn't touch (a stale import, a deleted class that still gets referenced elsewhere) can still break the build silently.

```python
import ast, os
base = "src/"
all_ok = True
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    ast.parse(fh.read())
            except SyntaxError as e:
                all_ok = False
                print(f"SYNTAX ERROR: {os.path.relpath(path, base)}\n  {e}")
if all_ok:
    print("All Python files parsed successfully — no syntax errors.")
```

Pass criterion: zero syntax errors across the entire `src/` tree

---

## 3. Stale Reference Hunt

After moving, renaming, or deleting a class, method, or signal, search the entire codebase for old names still referenced. PyInstaller won't catch NameError for dynamically-constructed names inside strings or lambdas.

Search patterns to run for every renamed/deleted entity:

```bash
# Example: after removing PlaybackStrip.set_mode() and show_mode_button()
grep -rn "_pb_strip\.set_mode"    src/ --include="*.py"
grep -rn "_pb_strip\.show_mode"   src/ --include="*.py"
grep -rn "mode_toggle_requested"   src/ --include="*.py"
```

**Pass criterion:** grep returns zero hits for every removed/renamed symbol.

**Common stale reference sources after refactor:**
- `MainWindow.__init__` signal connections
- `_set_data_mode()` sync calls
- `_on_recording_loaded()` / `_on_recording_clear()` UI calls
- Tab-switch handlers (`_on_nav_changed`)
- Event handler lambdas

---

## 4. Backward-Compatibility API Shims

If a public method or signal was renamed, keep a shim until all callers are updated.

Example:

```python
def set_playback_mode(self, playback: bool) -> None:
    """Legacy shim for callers still using the old API.

    New code should call set_mode("playback") or set_mode("live").
    This shim will be removed after a migration period.
    """
    self.set_mode("playback" if playback else "live")
```

**Rule:** Keep the shim until the next major version bump, or until a full-repo grep confirms all callers use the new API.

---

## 5. Dead-Code Removal

After completing a feature, remove all variables, state, imports, and methods that are no longer read or used.

Common dead-code types to audit:

| Type | Audit command | Files |
|---|---|---|
| `__init__` state variables | grep `_old_var_name` src/ --include="*.py" | `main_window.py`, `playback_record.py` |
| Unused imports | `flake8 --select=F401 src/` | any |
| Methods never called | Search class name + method name | any tab widget |
| Signal connections with no target | Search `connect(old_signal)` then grep target | `main_window.py` |
| QTimer, QTimer remaining after stop | Check for orphan `.start()` without `.stop()` | `main_window.py`, tabs |

**Pass criterion:** `grep -rn <dead_symbol> src/` returns zero hits

**Note on dead-code risk:** Do not remove unused imports that are needed by downstream plugins, eval'd strings, or dynamic imports. Only remove what you know is dead.

---

## 6. Residual-Effect Check

Some changes leave invisible state. After a refactor, verify no invisible state has leaked:

| Change type | Residual effect to check | How |
|---|---|---|
| Tab removed | `main_window.py` still imports and instantiates it? | grep for removed tab's class name in `_build_ui()` |
| Signal removed | `disconnect()` called in cleanup? | Just removing the signal is fine if no connect remains |
| QTimer removed | Was it properly stopped before deletion? | Check `__init__` for `.start()` without matching `.stop()` |
| StyleSheet removed | Are inherited widget styles still applied? | Visual check, or inspect via `widget.styleSheet()` |
| File deleted | Is it listed in `datas` / `hiddenimports`? | Review `PLCTools.spec` for stale entries |

---

## 7. Build Verification

After PyInstaller succeeds, verify:

```bash
ls -lh dist/Degater\ PLCTool\ BST33\ and\ 35.exe
```

- Size should be ~46 MB (+/- 3 MB)
- EXE should have today's timestamp
- If size drops by > 5 MB, a large dependency may have been silently excluded → audit

---

## Zero-Tolerance Rule

**No build is requested until the quality gate is green.** This is not optional polish. Skipping it guarantees a broken build or silent runtime crash.

Fluency is not an excuse to skip the gate. The gate is the fluency.
