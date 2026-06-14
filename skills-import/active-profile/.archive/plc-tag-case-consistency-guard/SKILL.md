---
title: "Tag Name Case-Consistency Guard for PLC Projects"
description: "Prevent and detect uppercase/lowercase and internal-format mismatches between catalog tag names, JSON alarm pairs, and physical mapping names in a PLC tooling project. Covers case drift (Justify vs justify) AND number formatting (Cyl2 vs Cyl_2)."
name: plc-tag-case-consistency-guard
triggers:
  - "plc tag name mismatch"
  - "uppercase lowercase typo"
  - "catalog and mapping out of sync"
  - "no response on known tag"
  - "read failure on existing tag"
  - "tag appears in alarm log but exists in catalog"
  - "internal underscore drift"
  - "numbered tag format inconsistency"
  - "surgical json replacement bug"
---

# Tag Name Case-Consistency Guard

## Problem
Tag names live in multiple files:
1. `catalog/io_catalog.py` — canonical list (`KNOWN_IO_TAGS`)
2. `catalog/physical_mapping.py` — maps logical name → physical address (`PHYSICAL_ADDRESS_MAP`)
3. `catalog/io_alarm_pairs.json` — pairs outputs with expected inputs

When a tag is renamed (camelCase fix, typo correction, number format fix), **every file must be updated simultaneously**. If one file is missed, the PLC driver cannot find the physical address → `"no response"` on every poll → floods the alarm log with false errors.

## Two Kinds of Drift

| Type | Example | How it hides |
|---|---|---|
| **Case drift** | `D3_Low_justify_Ret_Sol` vs `D3_Low_Justify_Ret_Sol` | Dict lookup fails. File-level verifiers catch it. |
| **Internal format drift** | `D3_Up_Justify_Cyl_2_Ext` vs `D3_Up_Justify_Cyl2_Ext` | **All three files share the SAME wrong name.** File-to-file verifiers pass. pycomm3 returns `"Tag doesn't exist"`. The fail-safe returns `False` for INPUTs, so alarms are silently swallowed. |

### Why internal-format drift is nastier than case drift

When ALL files (catalog, mapping, JSON) contain `Cyl_2`, the `verify_tag_consistency.py` script exits 0 because every cross-reference matches. But the **PLC itself** rejects the tag. On read failure for an INPUT, the direction-aware fail-safe returns `False`. The `IOAlarmWatcher` never sees the sensor transition, so a real cylinder fault goes completely undetected.

**Prevention:** After any tag addition or catalog edit, run:
```bash
grep -rn 'Cyl_[0-9]' src/plc_tools/catalog/
```
If ANY numbered tag shows `Cyl_1`, `Cyl_2`, `Cyl_3`, or `Cyl_4`, verify against the actual PLC tag list. Do not assume the verifier catches everything.

## Detection Script

Before building the EXE, run this check **and commit only when it passes**:

```bash
python scripts/verify_tag_consistency.py
```

The script checks:
1. Catalog tags ↔ Physical mapping keys (bidirectional)
2. Catalog tags ↔ Alarm pairs `output_tag`, `on_inputs`, `off_inputs`
3. Extra underscores in catalog names (`D1__Low_Grip_Close_Sol` typo)
4. Exclusion handling for system status tags that correctly do NOT appear in alarm pairs

If the script exits with code 1, **do not build**. Fix the mismatches first.

### Handling system tags correctly absent from alarm pairs

Tags like `KM_Command_To_Drop`, `DEG_MAN_AUTO`, and `Home_All_Manual_PB` are INPUTs that exist in the catalog but are operator-level controls, not cylinder sensors. The verifier reports them as "missing from alarm_pairs.json" unless explicitly excluded. Add an `ALARM_PAIR_EXCLUSIONS` set to the verifier listing all operator/system tags. Only suppress from the "missing" check — NEVER from the "extra" check.

## What to Do When a New Poll Error Appears on a Known Tag

1. **Run the detection script above** — if it prints mismatches, that's the cause.
2. **Identify the drift** — one file was updated, another wasn't.
3. **Fix ALL affected files in one commit** — never leave them out of sync.
4. **Commit with a scoped message**:
   ```
   fix: rename D3_Low_justify_Ret_Sol -> D3_Low_Justify_Ret_Sol
   - io_catalog.py
   - physical_mapping.py
   - io_alarm_pairs.json
   ```
5. **Re-verify** with the script before building.

## Common Symptoms

| Symptom | Cause |
|---------|-------|
| `"no response"` every poll for a tag that IS in the catalog | `physical_mapping.py` has a different case or internal format |
| Alarm log flooded with poll errors, but PLC is otherwise fine | OUTPUT tag read failure logged as alarm-worthy (DO_ addresses are write-only → suppress in `_PollWorker`) |
| `"no response"` on a solenoid | Attempted read on DO_ address — outputs are write-only |
| Sensor Sanity alarm fires correctly, but I/O Reaction is silent | Tag name in JSON pairs doesn't match catalog (case or format mismatch) |

## Prevention Checklist (before every build)

- [ ] Detection script passes clean
- [ ] grep for any `\b[A-Z][a-z]+_[a-z]+[A-Z]` vs `\b[A-Z][a-z]+_[A-Z]` patterns
- [ ] grep for `Cyl_[0-9]` in catalog and mapping — verify against PLC tag list
- [ ] `physical_mapping.py` keys exactly match catalog `name` fields
- [ ] `io_alarm_pairs.json` tags exactly match catalog `name` fields
- [ ] No single-commit fixes without updating all three sources
- [ ] System tags excluded in verifier, not suppressed from "extra" check

## References

- `scripts/verify_tag_consistency.py` — Runnable pre-build gate (exits 0/1)
- `references/case-mismatch-examples.md` — Real incidents from the Degater project (D3_Low_justify_Ret_Sol, D1__Low_Grip_Close_Sol, Cyl_2→Cyl2) with full root-cause analysis
- `references/surgical-json-replacement.md` — Why `patch replace_all` on JSON files corrupts unrelated strings, and the targeted Python-string-replace alternative

## Maintenance Notes

- **Case-sensitive imports / dict keys:** Python dict lookups are case-sensitive by default. If the driver builds a tag list from `io_catalog.py` and then looks up physical addresses from `physical_mapping.py`, a single character case difference (`Justify` vs `justify`) causes a missing key.
- **OUTPUT tags:** On Micro870, DO_ (digital output) addresses are write-only. A `"no response"` is expected behavior. The `_PollWorker` in `main_window.py` should **not** log these as errors — it should keep the last-known value and remain silent.
- **Surgical JSON edits after corruption:** If a broad `replace_all` patch corrupts a JSON file (e.g. replacing `Cyl_2` catches `Cyl_2` inside `D2_Up_Justify_Cyl2_Ext` too), revert via git and use a targeted Python script that replaces only the exact 4 broken strings. See `references/surgical-json-replacement.md`.

## Hardcoded Version Strings

A separate but related pre-build quality gate: any version shown in UI (About dialog, splash screen, window title) must use the dynamic `__version__` from `plc_tools.version`, never a hardcoded string.

**Why:** Auto-bump increments `BUILD` on every PyInstaller rebuild. A hardcoded `Version 1.05` in `QMessageBox.about()` will show stale data while the window title shows `v2.23.4`.

**Scan for hardcoded versions:**
```bash
grep -rn "Version [0-9]\+\." src/ --include="*.py" | grep -v "__version__"
```

**Correct pattern:**
```python
from plc_tools.version import __version__
QMessageBox.about(self, "About...", f"<p><b>Version {__version__}</b></p>...")
```

## Reference: Micro870 Output Read Behavior & JSON Structure

See `references/micro870-output-behavior-and-json-structure.md` for:
- Expected `"no response"` behavior for DO_ addresses
- Correct traversal code for the flat-array `io_alarm_pairs.json`
- Full table of tags expected to NOT appear in alarm pairs (status/robot/KM tags)
- Historical case-mismatch and format-drift patterns found in this session
