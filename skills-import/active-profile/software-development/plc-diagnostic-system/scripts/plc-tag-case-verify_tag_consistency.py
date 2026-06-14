#!/usr/bin/env python3
"""verify_tag_consistency.py

Run this from the project root BEFORE building the EXE.
Checks that tag names are identical across three sources:
  1. io_catalog.py      (canonical list)
  2. physical_mapping.py (logical → physical address map)
  3. io_alarm_pairs.json (output/input pairings for I/O Reaction alarm)

Exits with code 1 if any mismatch is found, 0 if clean.
"""
import json
import sys
from pathlib import Path

assert Path("src/plc_tools/catalog").is_dir(), "Run from project root"
src = str(Path("src").resolve())
if src not in sys.path:
    sys.path.insert(0, src)

from plc_tools.catalog.io_catalog import KNOWN_IO_TAGS
from plc_tools.catalog.physical_mapping import PHYSICAL_ADDRESS_MAP

print("=" * 60)
print("Tag Name Case-Consistency Check")
print("=" * 60)

catalog_names = {e["name"] for e in KNOWN_IO_TAGS}
map_names = set(PHYSICAL_ADDRESS_MAP.keys())

# ── Check 1: physical_mapping.py vs io_catalog.py ──────────────────────
missing_map = sorted(catalog_names - map_names)
missing_catalog = sorted(map_names - catalog_names)

if missing_map:
    print(f"\n❌ CATALOG tags with NO physical mapping ({len(missing_map)}):")
    for n in missing_map:
        print(f"   - {n}")

if missing_catalog:
    print(f"\n❌ PHYSICAL mapping keys NOT in catalog ({len(missing_catalog)}):")
    for n in missing_catalog:
        print(f"   - {n}")

# ── Check 2: io_alarm_pairs.json vs io_catalog.py ─────────────────────────
with open("src/plc_tools/catalog/io_alarm_pairs.json") as f:
    pairs = json.load(f)

json_names = set()
for entry in pairs:    # flat list, not dict
    json_names.add(entry["output_tag"])
    json_names.update(entry.get("on_inputs", []))
    json_names.update(entry.get("off_inputs", []))

missing_json = sorted(catalog_names - json_names)
extra_json = sorted(json_names - catalog_names)

if missing_json:
    print(f"\n❌ CATALOG tags missing from alarm_pairs.json ({len(missing_json)}):")
    for n in missing_json:
        print(f"   - {n}")

if extra_json:
    print(f"\n❌ alarm_pairs.json tags NOT in catalog ({len(extra_json)}):")
    for n in extra_json:
        print(f"   - {n}")

# ── Check 3: extra underscore typo in catalog ─────────────────────────────
underscore_typos = sorted(
    n for n in catalog_names if "__" in n or n.startswith("_") or n.endswith("_")
)
if underscore_typos:
    print(f"\n❌ Catalog entries with suspicious underscores ({len(underscore_typos)}):")
    for n in underscore_typos:
        print(f"   - {n}")

# ── Summary ──────────────────────────────────────────────────────────────────
all_ok = not any((missing_map, missing_catalog, missing_json, extra_json, underscore_typos))

if all_ok:
    print("\n✅ All tag names are fully synchronized")
    print(f"   Catalog: {len(catalog_names)} tags")
    print(f"   Physical mapping: {len(map_names)} entries")
    print(f"   Alarm pairs JSON: {len(json_names)} references")
    sys.exit(0)
else:
    print("\n⚠ Fix mismatches before building!")
    sys.exit(1)
