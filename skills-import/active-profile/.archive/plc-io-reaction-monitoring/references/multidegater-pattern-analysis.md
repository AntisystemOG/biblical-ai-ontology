# Multi-Degater Physical I/O Pattern Analysis

Reference pattern table from the Degater BST33/35 project showing the correct contiguous-block physical address layout across all three degaters (DEG1, DEG2, DEG3).

## X1 Digital Inputs (DEG1 + DEG2 share X1)

| Function | DEG1 | DEG2 | Notes |
|---|---|---|---|
| Lower Extend ON | 01, 03 | 21, 23 | Odd pairs (extend sensors) |
| Lower Retract ON | 00, 02 | 20, 22 | Even pairs (retract sensors) |
| Upper Extend ON | 05, 07 | 25, 27 | Odd pairs |
| Upper Retract ON | 04, 06 | 24, 26 | Even pairs |
| Low Justify Ext | 08–11 | 28–31 | 4 contiguous |
| **Up Justify Ext** | **12–15** | — | DEG1 only on X1 |
| Low Grip Open | 16–17 | — | DEG1 |
| Up Grip Open | 18–19 | — | DEG1 |

## X2 Digital Inputs (DEG2 + DEG3 share X2)

| Function | DEG2 | DEG3 | Notes |
|---|---|---|---|
| Up Justify Ext | 00–03 | **20–23** | 4 contiguous ✓ |
| Low Grip Open | 04–05 | 24–25 | 2 contiguous |
| Up Grip Open | 06–07 | 26–27 | 2 contiguous |
| Lower Ext ON | — | 09, 11 | Odd (extend) |
| Lower Ret ON | — | 08, 10 | Even (retract) |
| Upper Ext ON | — | 13, 15 | Odd (extend) |
| Upper Ret ON | — | 12, 14 | Even (retract) |
| Low Justify Ext | — | 16–19 | 4 contiguous |

## Critical Checks

1. **Extend-Retract parity**: Within each function, ON sensors are ODD-numbered, OFF sensors are EVEN-numbered (for dual-solenoid cylinders with paired reed switches). Justify cylinders have no retract sensors (single-solenoid) so only Ext sensors exist.

2. **Extend-Retract matching**: For "Up Justify Extend" vs "Up Justify Retract" within the same degater, the physical addresses MUST be identical — Extend has them as `on_inputs_physical`, Retract has them as `off_inputs_physical`.

3. **Contiguous-block rule**: No function's `on_inputs_physical` should skip addresses or overlap with another function's block. The only exception is odd-even skip (e.g., `DI_01`, `DI_03` for paired sensors on separate channels).

4. **Degater progression**: DEG1 on X1 → DEG2 starts on X1 but overflows to X2 → DEG3 continues on X2 at a higher offset. The progression is monotonic, not random.

## How to spot a bad entry (example: DEG3 Up Justify Extend)

**What it was (WRONG):** `24, 25, 26, 27`

**What it should be (FIXED):** `20, 21, 22, 23`

**Why the wrong one was detectable:**
- Collides with DEG3 Low Grip Open (`24–25`) and DEG3 Up Grip Open (`26–27`) — same addresses
- Does NOT match its own retract entry [39] (`20–23`) — contradiction
- Breaks the contiguous-block rule — the prior block ends at 19, so the next should start at 20

If you see an entry that overlaps another function or contradicts its own retract pair, it is wrong.

## Cross-check after every JSON edit

```bash
# 1. Extend vs Retract match (same degater, same function)
grep -A4 '"function": "Up Justify Extend"' io_alarm_pairs.json  # check on_inputs_physical
grep -A4 '"function": "Up Justify Retract"' io_alarm_pairs.json  # check off_inputs_physical
# These two 4-address lists must be identical

# 2. Overlap scan within same I/O module (e.g., DEG3 on X2)
grep -o '"_IO_X2_DI_[0-9]*"' io_alarm_pairs.json | sort | uniq -d
# Any duplicates = collision
```
