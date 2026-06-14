# PyInstaller `datas` → `_MEIPASS` Path Mapping

## The Rule

In your `.spec` file, each `datas` entry is a tuple: `(source_path, bundle_path)`.

When the EXE runs, `sys._MEIPASS` is the root of the extracted bundle. The **bundle path** (second element) is the directory structure inside `_MEIPASS`. Your `_asset_path()` function must reconstruct the full path using that bundle path.

## Worked Example: Degater PLC Tool

### `.spec` file

```python
datas=[
    ('src/plc_tools/assets',        'plc_tools/assets'),       # banner.png, micro850.jpg
    ('src/plc_tools/gui/assets',    'plc_tools/gui/assets'),   # Manual.jpg
],
```

### Correct `_asset_path()` (fixed in session)

```python
from pathlib import Path
import sys

def _asset_path(filename: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        # Match the SECOND element of the datas tuple exactly
        return Path(sys._MEIPASS) / "plc_tools" / "assets" / filename
    # Development fallback
    return Path(__file__).parent.parent.parent / "assets" / filename
```

### Why this broke originally

```python
# WRONG — missing the package prefix
return Path(sys._MEIPASS) / "assets" / filename

# CORRECT — includes the full bundle path
return Path(sys._MEIPASS) / "plc_tools" / "assets" / filename
```

The broken path looked for `MEIPASS/assets/banner.png`, but the actual file was at `MEIPASS/plc_tools/assets/banner.png`.

## Data files (JSON, CSV, XML) — same rule, worse failure mode

Data files receive **no visual feedback** when missing. They fail silently.

### Add JSON/CSV to `datas`

```python
datas=[
    ('src/plc_tools/assets',           'plc_tools/assets'),      # images
    ('src/plc_tools/catalog/pairs.json','plc_tools/catalog'),    # runtime data
],
```

### Runtime loading must use bundle path

```python
def _json_path(filename: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "plc_tools" / "catalog" / filename
    return Path(__file__).parent.parent / "catalog" / filename
```

### Critical pitfall: silent 0-record loads

If your code does this:

```python
try:
    with open(path) as f:
        return json.load(f)
except FileNotFoundError:
    return []  # silently returns empty, alarm never fires
```

When the JSON is missing from the bundle, the EXE runs fine but the data is empty. **Always warn on 0-record loads:**

```python
data = json.load(f)
if not data:
    logger.warning("Loaded 0 records from %s — check .spec datas", path)
```

## Mapping Table

| `datas` source | `datas` bundle path | Correct `_MEIPASS` access |
|---|---|---|
| `('src/my_app/assets', 'my_app/assets')` | `my_app/assets` | `sys._MEIPASS / "my_app" / "assets"` |
| `('src/gui/icons', 'gui/icons')` | `gui/icons` | `sys._MEIPASS / "gui" / "icons"` |
| `('data/config.json', '.')` | `.` (root) | `sys._MEIPASS / "config.json"` |
| `('src/pkg/fonts', 'pkg/fonts')` | `pkg/fonts` | `sys._MEIPASS / "pkg" / "fonts"` |
| `('src/pkg/config.json', 'pkg')` | `pkg` | `sys._MEIPASS / "pkg" / "config.json"` |

## Visual layout inside `_MEIPASS`

```
sys._MEIPASS/
├── my_app/
│   ├── assets/
│   │   ├── banner.png
│   │   └── micro850.jpg
│   └── gui/
│       └── assets/
│           └── Manual.jpg
├── plc_tools/
│   └── catalog/
│       └── pairs.json
└── ... (other bundled files)
```

## Pitfall: Multiple asset directories

When you have multiple `datas` entries, each has its own bundle path. Do NOT assume a single `_MEIPASS / "assets"` root:

```python
# BAD — one-size-fits-all
return Path(sys._MEIPASS) / "assets" / filename

# GOOD — match each entry
if filename in {"banner.png", "micro850.jpg"}:
    return Path(sys._MEIPASS) / "plc_tools" / "assets" / filename
if filename == "Manual.jpg":
    return Path(sys._MEIPASS) / "plc_tools" / "gui" / "assets" / filename
if filename == "pairs.json":
    return Path(sys._MEIPASS) / "plc_tools" / "catalog" / filename
```

## Verification

Add this to any `_asset_path()` function for a one-time sanity check:

```python
path = _asset_path("banner.png")
print(f"DEBUG: asset={path}, exists={path.exists()}")
```

Build with `console=True` temporarily to see the output, then switch back to `console=False` for production.
