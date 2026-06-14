#!/usr/bin/env python3
"""Validate that all tags referenced in io_alarm_pairs.json exist in io_catalog.py.

Run this after any catalog or JSON edit to catch typos before they produce
silent failures (missing tags = skipped checks = no alarms)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Adjust path to import your project's catalog
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from plc_tools.catalog.io_catalog import KNOWN_IO_TAGS

ALL_TAGS = {e["name"] for e in KNOWN_IO_TAGS}


def main(json_path: str) -> int:
    exit_code = 0

    with open(json_path, "r") as f:
        pairs = json.load(f)

    print(f"Catalog has {len(ALL_TAGS)} tags")
    print(f"JSON pairs: {len(pairs)}")
    print()

    for pair in pairs:
        output = pair.get("output_tag")
        on_inputs = pair.get("on_inputs", [])
        off_inputs = pair.get("off_inputs", [])

        # Check output
        if output and output not in ALL_TAGS:
            print(f"  [MISSING OUTPUT] {output}")
            exit_code = 1

        # Check inputs
        for tag in on_inputs + off_inputs:
            if tag and tag not in ALL_TAGS:
                print(f"  [MISSING INPUT ] {tag}  (for output {output})")
                exit_code = 1

    if exit_code == 0:
        print("✅ All JSON references present in catalog")
    else:
        print()
        print("❌ Fix typos or add missing tags to io_catalog.py, then re-run.")

    return exit_code


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/io_alarm_pairs.json>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
