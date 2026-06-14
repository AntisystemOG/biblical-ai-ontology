"""Sensor Sanity check implementation pattern.

Detects unplugged/broken sensors when a cylinder is at rest (both solenoids OFF).

Key insight: at rest, a healthy cylinder has at least one position sensor TRUE
(either Extended or Retracted). If BOTH sensors are FALSE simultaneously for
the configured duration, at least one sensor is unplugged or dead.

This check runs INDEPENDENTLY of the I/O Reaction watcher. It does NOT check
solenoid state — only sensor health."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class AlarmEvent:
    source: str
    severity: str
    message: str
    timestamp: datetime


def sensor_sanity_check(
    io_values: dict,
    now: datetime,
    pairs: list[dict],
    timeout_sec: float = 4.0,
    timers: dict | None = None,
    fired: set | None = None,
) -> list[AlarmEvent]:
    """
    Returns any Sensor Sanity alarms for this poll cycle.

    Args:
        io_values: current snapshot of all I/O tags
        now: current timestamp
        pairs: alarm pair definitions (with on_inputs/off_inputs per cylinder)
        timeout_sec: how long both sensors must stay FALSE before alarm (default 4.0)
        timers: mutable dict tracking per-cylinder fault-start times
        fired: mutable set of already-fired sanity faults (deduplication)

    Usage:
        timers = {}
        fired = set()
        for snapshot in snapshots:
            alarms = sensor_sanity_check(snapshot, now, pairs, 4.0, timers, fired)
            # ...handle alarms...
    """
    if timers is None:
        timers = {}
    if fired is None:
        fired = set()

    alarms: list[AlarmEvent] = []

    # Build per-cylinder sensor groups from the alarm pairs
    for pair in pairs:
        on_tags = pair.get("on_inputs", [])
        off_tags = pair.get("off_inputs", [])
        if not on_tags or not off_tags:
            continue  # Not a dual-solenoid cylinder — skip

        # Group by cylinder number (e.g. "Cyl_1_Ext" → cyl=1, pos=Ext)
        # Adapt this to your tag naming convention
        cyl_groups = defaultdict(dict)  # cyl_num -> {"Ext": tag, "Ret": tag}
        for tag in on_tags:
            parts = tag.split("_")
            for i, p in enumerate(parts):
                if p.startswith("Cyl"):
                    num = int(parts[i + 1]) if i + 1 < len(parts) else 1
                    pos = "Ext" if "Ext" in tag else "Ret"
                    cyl_groups[num][pos] = tag

        for cyl_num, pos_map in cyl_groups.items():
            ext_tag = pos_map.get("Ext")
            ret_tag = pos_map.get("Ret")
            if not ext_tag or not ret_tag:
                continue

            ext_val = bool(io_values.get(ext_tag, False))
            ret_val = bool(io_values.get(ret_tag, False))

            ckey = f"{pair.get('output_tag', 'unknown')}_cyl{cyl_num}"

            if ext_val or ret_val:
                # At least one sensor is TRUE → cylinder at a known position, OK
                timers.pop(ckey, None)
                fired.discard(ckey)
            else:
                # Both FALSE → timer starts
                if ckey not in timers:
                    timers[ckey] = now

                elapsed = (now - timers[ckey]).total_seconds()
                if elapsed >= timeout_sec and ckey not in fired:
                    fired.add(ckey)
                    alarms.append(
                        AlarmEvent(
                            source="Sensor Sanity",
                            severity="INFO",
                            message=(
                                f"Cylinder {cyl_num}: Both position sensors are "
                                f"OFF while at rest. Unplugged or broken sensor. "
                                f"Expected at least one of {ext_tag} or "
                                f"{ret_tag} to be ON."
                            ),
                            timestamp=now,
                        )
                    )

    return alarms
