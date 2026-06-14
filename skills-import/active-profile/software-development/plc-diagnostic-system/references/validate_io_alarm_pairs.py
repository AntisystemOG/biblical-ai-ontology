#!/usr/bin/env python3
"""
Validate io_alarm_pairs.json against the PLC I/O tag catalog.

Run before shipping a build to catch:
- Output tags not in KNOWN_IO_TAGS
- Input tags not in KNOWN_IO_TAGS or PHYSICAL_ADDRESS_MAP
- Mismatched physical vs logical tag names
- Missing "direction" metadata (needed for fail-safe read policy)
- Missing zero-padding in physical tag names

Usage:
    python3 validate_io_alarm_pairs.py

Returns non-zero if any mismatch found.
"""
import json
import sys
from pathlib import Path


def _load():
    src = Path(__file__).parent.parent.parent / "src"
    sys.path.insert(0, str(src))

    from plc_tools.catalog.io_catalog import KNOWN_IO_TAGS
    from plc_tools.catalog.physical_mapping import PHYSICAL_ADDRESS_MAP

    pairs_path = src / "plc_tools" / "catalog" / "io_alarm_pairs.json"
    pairs = json.load(open(pairs_path))

    return KNOWN_IO_TAGS, PHYSICAL_ADDRESS_MAP, pairs


def main():
    KNOWN_IO_TAGS, PHYSICAL_ADDRESS_MAP, pairs = _load()

    logical_names = {t["name"] for t in KNOWN_IO_TAGS}
    physical_names = {p for p in PHYSICAL_ADDRESS_MAP.values()}
    tag_dirs = {t["name"]: t.get("direction", "STATUS") for t in KNOWN_IO_TAGS}

    errors = []
    warnings = []

    for p in pairs:
        out_tag = p.get("output_tag", "")
        out_phys = p.get("output_physical", "")

        if out_tag and out_tag not in logical_names:
            errors.append(f"  Output logical tag missing: {out_tag}")
        if out_phys and out_phys not in physical_names:
            errors.append(f"  Output physical tag missing: {out_phys}")

        # Direction check: outputs should be OUTPUT
        if out_tag and tag_dirs.get(out_tag) != "OUTPUT":
            warnings.append(f"  Output tag {out_tag} has direction={tag_dirs.get(out_tag)}, expected OUTPUT")

        for inp in p.get("on_inputs", []) + p.get("off_inputs", []):
            if inp and inp not in logical_names:
                errors.append(f"  Input logical tag missing: {inp} (pair: {out_tag})")
            if inp and tag_dirs.get(inp, "STATUS") != "INPUT":
                warnings.append(
                    f"  Input tag {inp} has direction={tag_dirs.get(inp, 'STATUS')}, expected INPUT"
                )

        for inp_phys in p.get("on_inputs_physical", []) + p.get("off_inputs_physical", []):
            if inp_phys and inp_phys not in physical_names:
                errors.append(f"  Input physical tag missing: {inp_phys} (pair: {out_tag})")

        # Zero-padding check
        for phys_tag in [out_phys] + p.get("on_inputs_physical", []) + p.get("off_inputs_physical", []):
            if phys_tag and not phys_tag.endswith(("00","01","02","03","04","05","06","07","08","09")):
                # Rough heuristic: if it ends in a single digit preceded by underscore, probably not padded
                parts = phys_tag.rsplit("_", 1)
                if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 1:
                    errors.append(f"  Physical tag NOT zero-padded: {phys_tag} (should be ..._{parts[1].zfill(2)})")

    print(f"Pairs validated: {len(pairs)}")
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if warnings:
        for w in warnings:
            print(f"WARN: {w}")
    if errors:
        for e in errors:
            print(f"ERR:  {e}")
        sys.exit(1)

    print("All pairs validated OK.")


if __name__ == "__main__":
    main()
