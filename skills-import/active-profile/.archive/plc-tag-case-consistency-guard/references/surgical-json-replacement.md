# Surgical JSON Replacement — Avoiding `replace_all` Corruption

## Problem

The `patch` tool's `replace_all` mode replaces ALL occurrences of a substring across an entire file. In JSON files, this is dangerous because tag names may contain the same substring in unexpected places.

**Real incident (2026-06-03):**

Attempting to fix `D3_Up_Justify_Cyl_2_Ext` → `D3_Up_Justify_Cyl2_Ext` with `replace_all` also corrupted:
- `D2_Up_Justify_Cyl2_Ext` → became `D1_Low_Justify_Cyl2_Ext` (completely wrong tag)

The substring `Cyl2` existed in the replacement string, and `replace_all` matched it again. In a JSON with 55 alarm pair entries, a single `replace_all` corrupted ~12 unrelated lines.

## Correct Technique: Targeted Python String Replace

After reverting the corrupted JSON (`git checkout -- io_alarm_pairs.json`), use a small Python script that replaces ONLY the exact old string:

```python
import json
from pathlib import Path

json_path = Path("src/plc_tools/catalog/io_alarm_pairs.json")
text = json_path.read_text()

# ONLY these 4 exact strings — no regex, no substring matching
replacements = {
    'D1_Low_Justify_Cyl_4_Ext': 'D1_Low_Justify_Cyl4_Ext',
    'D3_Up_Justify_Cyl_2_Ext':  'D3_Up_Justify_Cyl2_Ext',
    'D3_Up_Justify_Cyl_3_Ext':  'D3_Up_Justify_Cyl3_Ext',
    'D3_Up_Justify_Cyl_4_Ext':  'D3_Up_Justify_Cyl4_Ext',
}

for old, new in replacements.items():
    text = text.replace(old, new)

json_path.write_text(text)
```

**Why this works:** `str.replace(old, new)` replaces exact contiguous substrings. It will NOT partial-match inside larger strings. It will NOT recurse into the replacement string.

## When `replace_all` is SAFE

- The old string appears only once in the file (verified with `grep -c 'OLD' file`)
- The replacement string does NOT contain any substring that also appears elsewhere
- You have already run `verify_tag_consistency.py` and confirmed the file loads cleanly

## When `replace_all` is DANGEROUS

- JSON files with arrays of similar objects (I/O pairs, mappings, configs)
- Any tag list where tags share prefixes/suffixes
- Any file where the replacement string contains a known tag fragment

## Verification After Fix

1. `python scripts/verify_tag_consistency.py` must exit 0
2. `git diff src/plc_tools/catalog/io_alarm_pairs.json` must show ONLY the intended lines changed
3. If a line changed that was NOT intended, revert and retry with more specific strings

## Alternative: Load → Mutate → Dump via Python

For complex renames across a JSON structure, load the JSON as objects, mutate, then dump:

```python
import json

with open("io_alarm_pairs.json") as f:
    data = json.load(f)

for pair in data:
    if pair.get("output_tag") == old_name:
        pair["output_tag"] = new_name
    for key in ("on_inputs", "off_inputs"):
        if old_name in pair[key]:
            pair[key] = [new_name if t == old_name else t for t in pair[key]]

with open("io_alarm_pairs.json", "w") as f:
    json.dump(data, f, indent=2)
```

This is immune to substring corruption but requires knowing the JSON schema.
