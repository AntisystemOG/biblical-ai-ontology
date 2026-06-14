# Case-Mismatch Examples from Degater PLC Tool Sessions

Real case-mismatch incidents that caused polling errors in production. Use these as a checklist when debugging "no response" on known tags.

## Incident 1: D3_Low_justify_Ret_Sol (2026-06-01)

**Symptom:** Alarm log flooded with `Read failure #510: D3_Low_Justify_Ret_Sol: no response` every ~6 seconds.

**Root cause cascade:**
1. `io_catalog.py` had tag named `D3_Low_justify_Ret_Sol` (lowercase j)
2. User corrected it to `D3_Low_Justify_Ret_Sol` (capital J)
3. `io_catalog.py` was fixed in commit `128a93e`
4. `physical_mapping.py` was NOT updated — still had old `D3_Low_justify_Ret_Sol`
5. `io_alarm_pairs.json` was NOT updated either

**Result:** Driver built tag list from corrected catalog, then looked up physical address in stale mapping. Key mismatch → no physical address found → pycomm3 fell back to logical tag name → "no response".

**Fix:** Same commit must update ALL three files atomically. Never leave them out of sync.

## Incident 2: D3_low_Nip_Open_Sol (2026-06-01)

Same pattern as Incident 1. `io_catalog.py` was fixed from `D3_low_Nip_Open_Sol` to `D3_Low_Nip_Open_Sol`, but `physical_mapping.py` retained the old lowercase `l`.

## Incident 3: D1__Low_Grip_Close_Sol (2026-06-02)

**Symptom:** No immediate polling error (the typo existed in both catalog AND mapping, so they matched each other). However, `io_alarm_pairs.json` was out of sync.

**Root cause:** Double underscore (`__`) between `D1` and `Low`. Likely introduced by a search-and-replace operation.

**Fix:** The `verify_tag_consistency.py` script now detects double-underscore typos as a separate check.

## Incident 4: D3_Up_Justify_Cyl_2_Ext (2026-06-03)

**Symptom:** I/O Reaction Alarm Watcher never detected faults for D3 Upper Justify Cylinders 2, 3, and 4. Operator reported "Cylinder 2 keeps faulting but I get no alarm."

**Root cause cascade:**
1. Tag names in `io_catalog.py` had an extra underscore before the cylinder number:
   - `D3_Up_Justify_Cyl_2_Ext` (should be `Cyl2_Ext`)
   - `D3_Up_Justify_Cyl_3_Ext` (should be `Cyl3_Ext`)
   - `D3_Up_Justify_Cyl_4_Ext` (should be `Cyl4_Ext`)
   - `D1_Low_Justify_Cyl_4_Ext` (same bug, different station)
2. The PLC's actual tag list uses `Cyl2_Ext`, `Cyl3_Ext`, `Cyl4_Ext` (no underscore before the number)
3. The poller looked up the tag in `physical_mapping.py` using the wrong name
4. pycomm3 batch read for those tags returned `"Tag doesn't exist"`
5. The direction-aware fail-safe returned `False` (fail-safe for INPUT tags)
6. The Alarm Watcher never saw the sensor transition because the tag read failed silently

**Impact:** Three out of four D3 Upper Justify cylinder sensors were completely invisible to the alarm system. A mechanical fault would produce "0 alarms" on the tool while the machine faulted.

**Fix:** Changed all four names to match the PLC convention (`Cyl2_Ext`, `Cyl3_Ext`, `Cyl4_Ext`, and `D1_Low_Justify_Cyl4_Ext`). Updated both `io_catalog.py` and `physical_mapping.py` in a single commit.

## Pattern: Internal Underscore Drift (Cyl_N vs CylN)

This is a different class from case-mismatch (Incident 1) and double-underscore (Incident 3). It is an **inconsistency in naming convention within a single tag** — one part uses `Cyl_1` and another uses `Cyl1`. These are especially dangerous because:
- The tag "looks right" at a glance
- `verify_tag_consistency.py` will pass if both catalog and mapping have the SAME wrong name
- The PLC silently rejects the read → fail-safe FALSE → no alarm

**Detection:**
```bash
# Look for mixed patterns in justify/extend/grip tags
grep -En 'Cyl_[0-9]+_' io_catalog.py
grep -En 'Cyl[0-9]+_'  io_catalog.py

# Count lines per pattern — they should match. If Cyl_N has more lines than CylN, drift exists.
```

**Prevention:** When adding new tags that contain numbered elements, pick ONE format (`Cyl1` or `Cyl_1`) and enforce it everywhere. Do not mix.

**Verification after fix:** `grep -rn 'Cyl_[0-9]' io_catalog.py` should return zero hits.

## Detection Pattern

Any time a tag produces "no response" but:
- The PLC is otherwise communicating fine
- Other tags read successfully
- The tag IS in the catalog

→ Run `verify_tag_consistency.py`. If it prints mismatches, that's the cause.

## Prevention Rule

When renaming/correcting a tag name:
1. Update `io_catalog.py`
2. Update `physical_mapping.py`
3. Update `io_alarm_pairs.json` (flat list, fields: `output_tag`, `on_inputs[]`, `off_inputs[]`)
4. Run `python scripts/verify_tag_consistency.py`
5. Only then commit
