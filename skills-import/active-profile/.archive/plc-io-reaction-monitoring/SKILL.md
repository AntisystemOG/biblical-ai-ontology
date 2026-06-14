---
name: plc-io-reaction-monitoring
description: >-
  Industrial PLC I/O reaction alarm patterns — monitoring outputs (solenoids)
  and verifying expected inputs (sensors) respond within a timeout. Covers
  dual-solenoid cylinder guards, transition vs continuous checks, and
  catalog-to-mapping validation.
triggers:
  - I/O reaction alarm system
  - output-to-input verification
  - solenoid sensor monitoring
  - PLC alarm false positives
  - cylinder extend/retract alarm
keywords:
  - io_alarm_watcher
  - timeout_sec
  - off_inputs
  - on_inputs
  - opposing_solenoid
  - transition check
  - continuous check
  - dual-solenoid guard
  - degater
---

# PLC I/O Reaction Monitoring

Industrial automation pattern: monitor every output (solenoid) and verify its
associated inputs (position sensors) react within a configured timeout. When an
output commands motion but sensors don't confirm it, raise a FAULT alarm.

This skill covers the complete lifecycle: design → implement → debug false
alarms → produce documentation.

## Table of Contents

1. [Before Writing Code — Visual Mapping](#1-before-writing-code--visual-mapping)
2. [Two Check Types](#2-two-check-types)
3. [Dual-Solenoid Cylinder Guard](#3-dual-solenoid-cylinder-guard)
4. [Catalog ↔ Mapping Validation](#4-catalog--mapping-validation)
5. [Implementation Checklist](#5-implementation-checklist)
6. [Pitfalls](#6-pitfalls)
7. [References](#references)

## 1. Before Writing Code — Visual Mapping

**User preference: produce a table mapping outputs → inputs BEFORE any code.**

Create a visual reference (HTML table, markdown, or PDF) showing:
- Output tag (solenoid)
- Function name (e.g. "Lower Extend")
- Expected ON sensors (`on_inputs`)
- Expected OFF sensors (`off_inputs`) — only for dual-solenoid cylinders
- Physical addresses if available

This table becomes the contract. Review it with the user before implementing.

Example row:

| Function | Output | on_inputs (ON) | off_inputs (OFF) |
|---|---|---|---|
| Lower Extend | DEG1_Lower_Ext_Sol | D1_Low_Ext_Cyl_1_Ext, D1_Low_Ext_Cyl_2_Ext | D1_Low_Ext_Cyl_1_Ret, D1_Low_Ext_Cyl_2_Ret |
<br>

## 2. Two Check Types

| Check | Trigger | What It Verifies | Fires When |
|---|---|---|---|
| **Transition** | Output changes state (ON → OFF or OFF → ON) | Expected inputs become TRUE within `timeout_sec` | Deadline passes without all inputs ON |
| **Continuous** | Every poll cycle while output is steady | Expected inputs stay TRUE while output is ON | Any input drops OFF while output remains ON |

Key design rule: **transition owns the grace window.** Once a transition alarm
fires, suppress the continuous check for the same `timeout_sec` to avoid
double-alarming on the same fault.

## 3. Dual-Solenoid Cylinder Guard

**The #1 source of false alarms in this pattern.**

A dual-solenoid cylinder has two outputs: Extend and Retract. Only one is ON
at a time. When Extend turns OFF, the PLC may not command Retract ON for a few
hundred milliseconds.

**Problem:** If you start checking `off_inputs` (Retract sensors) the instant
Extend turns OFF, those sensors are still FALSE — the cylinder hasn't started
retracting yet. FALSE ALARM.

**Fix — Opposing Solenoid Guard:**

```
When solenoid turns OFF:
    Look up the PAIRED solenoid (Extend ↔ Retract)
    Read the opposing solenoid's current value
    IF opposing solenoid is ON:
        Cylinder IS actively moving → verify off_inputs
    ELSE:
        Cylinder is at rest → SKIP off_inputs check
```

**Also:** Continuous check should only validate `on_inputs` (solenoid ON).
`off_inputs` describe the DESTINATION position — the transition check already
verified the cylinder arrived there. Checking `off_inputs` continuously would
false-alarm when the opposing solenoid later commands motion.

## 4. Catalog ↔ Mapping Validation

In PySide6/pycomm3 apps, I/O tags typically live in two places:
1. **Catalog** (`io_catalog.py`) — the "single source of truth" tag list
2. **Alarm pairs JSON** (`io_alarm_pairs.json`) — which tags are outputs vs inputs for each function

**These MUST stay in sync.** A tag name typo in either place breaks the watcher
silently (the alarm check just skips missing tags, producing no alarm at all).

**Validation script:** Run after any JSON edit or catalog update. See
`references/tag_crosscheck.py` in this skill.

If a JSON `output_tag` is not in the catalog → alarm check silently skips it.
If a JSON `on_inputs`/`off_inputs` entry is not in the catalog → those sensors
never get checked. Both are silent failures.

## 5. Implementation Checklist

- [ ] Produce visual input/output mapping table for user review
- [ ] Define `timeout_sec` per function (default 1.0s, adjustable from UI)
- [ ] Mark dual-solenoid pairs in JSON (`function` uses "Extend" / "Retract")
- [ ] Implement `_opposing_solenoid()` lookup by degater + opposite function name
- [ ] Add guard in `_start_check()` for OFF transitions of dual-solenoid outputs
- [ ] Restrict `_continuous_check()` to `on_inputs` only
- [ ] Add transition-fired suppression to avoid double alarms
- [ ] Write catalog ↔ JSON cross-check script and run it
- [ ] Simulate: normal cycle → verify 0 alarms
- [ ] Simulate: sensor stuck during motion → verify alarm fires within timeout
- [ ] Simulate: sensor unplugged at rest → verify 0 false alarms (expected)
- [ ] Build EXE and test on hardware

## 7. Catalog Pattern Validation — Cross-degater Consistency

When multiple identical machines (degaters) share the same physical I/O layout, the JSON alarm-pair entries MUST follow a consistent numeric pattern. A single entry that drifts out of the pattern is almost always wrong.

### The consistency rule

For each function ("Up Justify Extend", "Low Grip Close", etc.), the physical input addresses should form a **contiguous block** that shifts predictably across degaters. If DEG1 uses 12-15, DEG2 uses 00-03, and DEG3 uses 20-23, the DEG3 value is the anomaly — it should follow the same offset progression.

### Cross-check every edit

Before AND after modifying any `on_inputs_physical` or `off_inputs_physical` entries, run this mental verification:

1. **Extend ↔ Retract parity check**
   - For a given function (e.g., "Up Justify Extend"), read its paired retract entry ("Up Justify Retract")
   - Both entries MUST reference the **same 4 physical sensors** (the extend sensors)
   - Extend has them as `on_inputs_physical`; Retract has them as `off_inputs_physical`
   - If the two lists differ, one is wrong — by definition they monitor the same cylinders

2. **No overlap check**
   - Scan all entries in the same degater and I/O module (e.g., DEG3 on X2)
   - No two functions should claim the same physical address
   - If "Up Justify Extend" says 24-27 AND "Low Grip Open" also says 24-25, you have a collision
   - The one that breaks the contiguous-block pattern is the wrong one

3. **Pattern drift check**
   - List the `on_inputs_physical` for the same function across all degaters
   - If DEG1 and DEG2 follow a clear progression (08-11, 28-31) but DEG3 jumps to 24-27, that is a red flag
   - Example: see `references/multidegater-pattern-analysis.md` for the Degater DEG1/2/3 actual numbers showing how DEG3 Up Justify Extend was wrong.

### Why this matters

PyInstaller-bundled apps rarely show warnings for JSON data errors — the alarm watcher simply sees the wrong addresses and either false-alarms (sensors mismatch) or stays silent (sensors not found). The error is invisible until you compare the physical layout across entries.

### Pitfall: odd-even pairing in `off_inputs_physical`

Some catalog entries store `off_inputs_physical` as pairs of odd-even addresses (e.g., `_IO_X1_DI_21` and `_IO_X1_DI_23`). This pattern is correct when it matches the wiring — the two sensors are on physically adjacent but electrically separate channels. Do NOT "fix" these to be sequential unless the wiring doc actually changes. Always validate against the `on_inputs_physical` of the RETRACT entry to confirm the pairing is intentional.

## Pitfalls

| Pitfall | Why It Happens | Prevention |
|---|---|---|
| **Removing `off_inputs` to fix false alarms** | Thinking `off_inputs` cause the problem | The problem is TIMING, not existence. Keep `off_inputs` and add the opposing-solenoid guard. |
| **Transition + continuous both fire for same fault** | Grace period not suppressed | After transition alarm, suppress continuous for `timeout_sec`. Track in `_transition_fired`. |
| **First poll treated as state change** | Startup logic starts pending check on initial values | Skip `_start_check` if `changed_at is None` (first observation). |
| **Tag name drift between catalog and JSON** | Typo like `D3_Up_Justify_Cyl_2_Ext` vs `D3_Up_Justify_Cyl2_Ext` | Run the cross-check script after every JSON or catalog edit. |
| **Tag name drift between catalog and JSON** | Capitalization drift: `D3_low_Nip_Open_Sol` vs `D3_Low_Nip_Open_Sol` | The cross-check script catches this too, but also visually audit all DEG* entries in the catalog for casing consistency after any bulk edit. |
| **Sensor Sanity false-alarms during normal transition** | Shared `timeout_sec` between I/O Reaction and Sensor Sanity | Sensor Sanity needs its **own independent timeout** (e.g., 4.0 s vs 1.0 s). During motion the magnet passes between reed switches for ~2–3 s; a 1-second timeout would false-alarm. Keep `sensor_sanity_timeout_sec` separate. |
| **Sensor Sanity false-alarms during normal transition** | Shared `timeout_sec` between I/O Reaction and Sensor Sanity | Sensor Sanity needs its **own independent timeout** (e.g., 4.0 s vs 1.0 s). During motion the magnet passes between reed switches for ~2–3 s; a 1-second timeout would false-alarm. Keep `sensor_sanity_timeout_sec` separate. |
| **Sensor Sanity checks impossible sensor combo** | Assemblies with only one sensor type (e.g., justify cylinders with Ext sensors but no Ret sensors) | Sensor Sanity requires matched Ext+Ret sensor pairs. Single-sensor assemblies are silently SKIPPED by the cyl-number matching logic. Design a separate "stuck sensor" detector that watches for sensors staying OFF longer than their normal cycle time, regardless of solenoid state. |
| **Sensor unplugged at rest not detected** | Both solenoids OFF = no checks run | This is BY DESIGN. To catch at-rest sensor failures, implement a separate **Sensor Sanity** check that looks for impossible states (e.g. both Ext AND Ret sensors FALSE simultaneously) regardless of solenoid state. |
| **Physical address range collision in JSON catalog** | Editing one entry without checking overlap with adjacent entries | Before changing any `*_inputs_physical` array, grep the entire JSON for each address you are assigning. If another function already claims it, you have a collision. Also compare extend vs retract entries for the same function — they must match exactly. |
| **Degater pattern drift (contiguous block anomaly)** | One degater's address block jumps out of sequence with the others | After every JSON edit, run the "pattern drift check" in `references/multidegater-pattern-analysis.md`. Contiguous-block anomalies are almost always wrong entries. |

## References

- `references/tag_crosscheck.py` — Python script to verify every tag referenced in `io_alarm_pairs.json` exists in the catalog. Run after every JSON edit.
- `references/sensor_sanity_dedup.py` — Standalone Sensor Sanity implementation showing timer + dedup patterns. Copy/paste starting point for new projects.
- `references/dual_solenoid_guard_snippet.py` — Minimal implementation of the opposing-solenoid guard
- `references/DEG_mapping_example.md` — Full DEG1/2/3 input/output mapping table from the Degater BST33/35 project
- `references/multidegater-pattern-analysis.md` — **Cross-degater physical address pattern validation.** Shows the correct contiguous-block layout across all degaters, the 3-step verification method (Extend-Retract match, No-overlap, Pattern drift), and concrete example of the DEG3 Up Justify Extend collision that was caught using these checks.