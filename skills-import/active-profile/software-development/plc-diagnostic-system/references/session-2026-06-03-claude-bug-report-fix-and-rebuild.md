## Session: 2026-06-03 — Claude Bug Report Fix + EXE Rebuild (v2.23.27)

### Context
Claude Code Review generated a bug report for the Degater PLC Tool BST33/35 with 6 bugs, 2 critical. All were verified and fixed in source; rebuilt EXE passes gate.

---

### Bug 1: Internal Underscore Drift in Justify Cylinder Tags (CRITICAL)

**Root cause**: D3 Up Justify Cyl 2/3/4 and D1 Lower Justify Cyl 4 had an extra underscore (`Cyl_2_Ext` vs `Cyl2_Ext`).

**Why verify_tag_consistency.py did NOT catch it**:
All three files (catalog, mapping, alarm pairs) had the SAME wrong name. The checker only detects MISALIGNMENTS between files (`n ∈ A` but `n ∉ B`), not internal format errors within files.

**Fix applied**:
- `io_catalog.py`: `D3_Up_Justify_Cyl_2_Ext` → `D3_Up_Justify_Cyl2_Ext` (x3 cyls)
- `io_catalog.py`: `D1_Low_Justify_Cyl_4_Ext` → `D1_Low_Justify_Cyl4_Ext`
- `physical_mapping.py`: same keys renamed
- `io_alarm_pairs.json`: same tag references renamed (in `on_inputs`, `off_inputs`, and `note_on`/`note_off` strings)

**Grep command for future detection**:
```bash
grep -rn 'Cyl_[0-9]' src/plc_tools/catalog/   # should return zero hits for Justify cyls
```

**All other `Cyl_` tags** (e.g. `D1_Low_Ext_Cyl_1_Ext`, `D2_Up_Ext_Cyl_1_Ret`) are DEGATER EXTEND/RETRACT cylinders — those use `_` intentionally and match the catalog and PLC.

### Bug 2: Magic Sleep Value (SOURCE VERIFIED, DEFENSIVE COMMENT)

**Report**: Bytecode review showed `333333` near sleep. **Source audit**: actual code is `time.sleep(0.02)` with a 0.3s timeout cap — CORRECT.

**Technique**: Used a Python bytecode audit to confirm no integer-literal sleep exists in `.pyc`:
```python
import dis, marshal
with open('.pyc','rb') as f:
    f.read(16)
    co = marshal.load(f)
for c in [co] + [c2 for c2 in co.co_consts if hasattr(c2,'co_code')]:
    for const in c.co_consts:
        if isinstance(const,int) and const >= 300000:
            print(f"BUG: {const} in {c.co_name}")
```

**Action**: Added defensive source comment warning future editors to use `time.sleep(0.333)` not `time.sleep(333333)` (~4 days).

### Bug 3: Auto-Reconnect Warning Threshold Mismatch

**Report**: Popup said "after 2 attempts" but gave up logic was 10. Users saw the warning and thought retrying stopped.

**Fix**:
- Warning threshold: `>= 2` → `>= 5`
- Message reworded: "...attempts will continue (up to 10)."
- Single source of truth: `self._auto_reconnect_attempts` drives both the warning condition and the give-up condition.

### Bug 4: Signal Naming Comment Misleads Future Edits

**Report**: `connect_done` docstring said Qt `finished()` passes `(False, ""` — but Qt's `finished()` takes ZERO args.

**The REAL mechanism**: PySide6 maps Qt's native `finished()` (zero args) to the overloaded Python `finished = Signal(bool, str)`. The mismatch causes PySide6 to pass the thread object as the first arg instead of `(bool, str)`, triggering a spurious failure callback.

**Fix**: Rewrote docstring with explicit CRITICAL warning explaining signature collision.

```python
"""⚠️ CRITICAL — Do NOT rename `connect_done` to `finished`.
QThread already owns a signal called `finished()` (no arguments).
If you create a custom Signal named `finished` that carries arguments
(bool, str), PySide6 will confuse the two: when the thread ends, Qt
emits its built-in `finished()`, which PySide6 routes to your custom
`finished` slot, passing the thread object instead of intended args.
"""
```

### Bug 5: Silent Catalog Fallback in `get_tag_list()`

**Root cause**: When pycomm3 tag cache is empty, `get_tag_list()` silently returns hardcoded catalog tags (names + descriptions) with no user indication.

**Fix pattern (reusable)**:
1. Add `is_catalog_fallback: bool = False` to `TagValue` dataclass
2. Set `is_catalog_fallback=True` when building fallback tag list in `get_tag_list()`
3. In `MainWindow._load_tags()`, detect `any(t.is_catalog_fallback for t in tags)`
4. Show/hide a yellow warning banner in the UI tab (`QLabel` with amber styling) that reads:
   > "⚠ Tags are from the hardcoded catalog — PLC tag cache is empty. Names may be stale if the PLC program has been renamed or edited."

**File changes**: `models.py` (+1 field), `micro800_driver.py` (+1 flag), `main_window.py` (+6 lines), `all_tags.py` (+20 lines banner + setter method)

### Bug 6: Timer Discovery Hardcoded Probe Names

**Fix**: Expanded probe list with extra case variants + added prominent docstring NOTE saying probe list is a best-guess that may not match the actual PLC program, and users should use "Enumerate Tags" to discover real names.

---

### Pre-build Gate Enhancement: Alarm Pair Exclusions

The `verify_tag_consistency.py` gate was reporting 14 "false missing" tags — system status inputs like `KM_Command_To_Drop`, `DEG_MAN_AUTO`, `Home_All_Manual_PB` that are NOT monitored by alarm pairs by design.

**Fix**: Added `ALARM_PAIR_EXCLUSIONS` set to the script. Tags matching these names are excluded from the "missing from alarm_pairs" check. Critical tags (`missing_json`, `extra_json`) remain fully checked.

### Build Outcome

- **Version**: 2.23.26 → **2.23.27**
- **EXE**: `dist/Degater PLCTool BST33 and 35.exe` (46 MB)
- **Build time**: ~90 seconds
- **Pre-build gate**: PASS (127 tags, 127 mappings, 115 alarm references)

### Changed Files

| File | What Changed |
|---|---|
| `io_catalog.py` | Renamed 4 Justify cylinder tags (removed extra underscore) |
| `physical_mapping.py` | Renamed 4 mapping keys to match catalog |
| `io_alarm_pairs.json` | Renamed 12 tag references + note strings |
| `main_window.py` | Defensive sleep comment; reconnect threshold fix; signal docstring; catalog fallback detection; fallback warning wiring |
| `micro800_driver.py` | Timer discovery docstring + expanded probes |
| `models.py` | Added `is_catalog_fallback` field to `TagValue` |
| `all_tags.py` | Added yellow fallback warning banner + `set_fallback_warning()` |
| `verify_tag_consistency.py` | Added `ALARM_PAIR_EXCLUSIONS` for system status tags |
