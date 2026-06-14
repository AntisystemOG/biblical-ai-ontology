# PyInstaller Bloat Cleanup — Dead-Code / Dead-Asset Discovery

Session: Degater PLC Tool BST33 and 35 cleanup, 2026-05-31. Reduced EXE footprint by pruning 13 dead `.py` files, ~350 dead asset files, 8 dead hiddenimports, and the `py7zr` dependency.

## Discovery workflow

Run this on the project root before every rebuild.

### Step 1 — Enumerate all source modules

```bash
find src/ -name "*.py" | sort
```

### Step 2 — For each candidate module, check if it is alive

A module is **alive** if any of these are true:
- It is imported by `main_window.py` (or the app's entry point)
- It is imported by any other alive module
- It contains a class that is instantiated anywhere in the tree

A module is **dead** if ALL of these are true:
- Zero non-definition references to its class name across `src/`
- Zero `import` or `from … import` references to the module path
- It is not the entry-point module

```bash
# Example: check if fault_log.py is alive
grep -r "FaultLogTab" src/ --include="*.py"
# If the ONLY hit is "class FaultLogTab", the module is dead.
```

```bash
# Example: check if program_view.py is alive
grep -r "ProgramViewTab\|program_view" src/ --include="*.py"
# Exclude self-definition hits. If nothing remains, delete before build.
```

### Step 3 — Check main_window.py for tab/widget instantiation

Most dead GUI code hides in tabs that were prototyped but never wired into the sidebar nav / QStackedWidget:

```bash
grep -r "from plc_tools.gui.tabs" src/plc_tools/gui/main_window.py
grep -r "= .*Tab()" src/plc_tools/gui/main_window.py
```

Any `.py` in `gui/tabs/` whose class is NOT listed in those two grep outputs is dead.

### Step 4 — Check widget usage

```bash
grep -r "RecordingBar\|TagBrowser\|PLCPanel" src/ --include="*.py"
# Exclude class definition files. If zero consumer hits → dead.
```

### Step 5 — Check communication / polling modules

```bash
grep -r "l5x_parser\|L5XParser\|network_scanner\|NetworkScanner" src/ --include="*.py"
grep -r "ccw_parser\|CCWParser\|ccw_tag_parser\|CCWTagParser" src/ --include="*.py"
grep -r "scheduler\|Scheduler" src/ --include="*.py"
```

## Asset audit

### Find all asset directories

```bash
find src/ -type d -name "assets"
```

### Cross-check each asset against source loads

```bash
# Look for every filename in every assets/ dir
for f in $(find src/ -path "*/assets/*" -type f); do
    name=$(basename "$f")
    hits=$(grep -r "$name" src/ --include="*.py" | wc -l)
    if [ "$hits" -eq 0 ]; then
        echo "UNUSED: $f"
    fi
done
```

**Degater example:** `assets/rungs/` contained 350 EMF/PNG ladder-rung images. Zero `.py` files referenced any `rung_*.png` or `rung_*.emf`. The entire directory was dead weight.

### Prefer individual-file `datas` entries over directories

Bad (pulls everything, including dead files):
```python
datas=[
    ('src/plc_tools/assets', 'plc_tools/assets'),
]
```

Good (only what the app actually loads):
```python
datas=[
    ('src/plc_tools/assets/banner.png',    'plc_tools/assets'),
    ('src/plc_tools/assets/micro850.jpg',  'plc_tools/assets'),
    ('src/plc_tools/gui/assets',           'plc_tools/gui/assets'),
]
```

## Spec pruning checklist

After deleting dead files, update `PLCTools.spec` (or equivalent):

- [ ] **hiddenimports** — remove entries for deleted modules and for modules that PyInstaller auto-detects anyway (e.g. `PySide6.QtCore` is usually unnecessary)
- [ ] **datas** — replace directory entries with individual files when the directory has unused files
- [ ] **excludes** — add stdlib modules PyInstaller wrongly bundles:
  ```python
  excludes=[
      'tkinter', 'matplotlib', 'scipy', 'pandas', 'jinja2',
      'pytest', 'unittest', 'xmlrpc', 'pydoc', 'email', 'html',
      'http', 'ftplib', 'urllib', 'lib2to3', 'curses',
  ]
  ```

## Dependency pruning

Check `pyproject.toml` or `requirements.txt`:

```bash
# For each dependency, grep the source tree
grep -r "py7zr\|import.*7zr" src/ --include="*.py"
# If zero hits → safe to remove from dependencies
```

**Degater example:** `py7zr>=0.21` was in `pyproject.toml` but never imported. Removed.

## Cleanup commands before rebuild

```bash
# Purge Python cache
find src/ -type d -name "__pycache__" -exec rm -rf {} +

# Purge build artifacts
rm -rf build/work dist/

# Purge egg-info if present
rm -rf src/*.egg-info/
```

## Result from Degater session

| Item | Count | Size impact |
|---|---|---|
| Dead `.py` files deleted | 13 | ~50 KB source |
| Dead asset files deleted | ~350 (EMF/PNG) | ~1.5+ MB |
| `__pycache__` directories purged | 174 | N/A (build-time only) |
| Dead hiddenimports removed | 8 | Faster Analysis phase |
| Dependencies removed | 1 (`py7zr`) | Slightly smaller venv |
| Stdlib excludes added | 15 | Reduces bundled stdlib bloat |

## Advanced: Python-based dead-code scanner

For complex trees, a Python script is faster than shell loops:

```python
from pathlib import Path
import re

proj = Path("/path/to/project")
src = proj / "src"

# 1. Enumerate all .py modules
modules = {p.stem: p for p in src.rglob("*.py")}

# 2. For each module, grep the entire tree for its class name or path
for stem, path in modules.items():
    # Try class name CamelCase heuristic
    class_name = "".join(x.title() for x in stem.split("_")) + "Tab"
    pattern = re.compile(rf"\b{class_name}\b|\b{stem}\b")
    hits = 0
    for py in src.rglob("*.py"):
        if py == path:
            continue
        text = py.read_text()
        if pattern.search(text):
            hits += 1
            break
    if hits == 0:
        print(f"DEAD: {path.relative_to(proj)}")
```

## Verify hiddenimports against actual source

After pruning dead files, programmatically verify every `hiddenimports` entry resolves to an existing module:

```python
import re
from pathlib import Path

spec = Path("PLCTools.spec").read_text()
imports = re.findall(r"'plc_tools[^']*'", spec)

for imp in imports:
    mod = imp.strip("'").replace(".", "/")
    candidates = [
        Path("src") / f"{mod}.py",
        Path("src") / f"{mod}/__init__.py",
    ]
    if not any(c.exists() for c in candidates):
        print(f"MISSING in spec: {imp}")
```

## Post-cleanup: sync architecture docs

After deleting modules, update `AGENTS.md` or `ARCHITECTURE.md` so the next agent doesn't look for deleted files:

- Remove deleted modules from the source-tree diagram
- Update the active-tab list in the GUI section
- Note the cleanup date so future sessions know the tree is current
