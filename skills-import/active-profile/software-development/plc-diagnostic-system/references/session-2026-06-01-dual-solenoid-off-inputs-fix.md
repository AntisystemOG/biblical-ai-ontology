# Session 2026-06-01 — Dual-Solenoid `off_inputs` False Alarm Fix

## Problem

Pneumatic degater cylinders use **dual solenoids** (separate Extend and Retract solenoids). The alarm table `io_alarm_pairs.json` had `off_inputs` defined for each output:

```json
// DEG2 Lower Extend
{
  "output_tag": "DEG2_Lower_Ext_Sol",
  "on_inputs": ["D2_Low_Ext_Cyl_1_Ext", "D2_Low_Ext_Cyl_2_Ext"],
  "off_inputs": ["D2_Low_Ext_Cyl_1_Ret", "D2_Low_Ext_Cyl_2_Ret"],
  ...
}
```

When **Extend solenoid turns OFF**, the watchdog fires a transition check for out_val=False using `off_inputs` = Ret sensors. But the Retract solenoid hasn't turned ON yet → FALSE ALARM.

Same on every cylinder cycle. 2 false alarms per motion.

## Evidence

User alarm log showed messages **flipping between "Expected Ext" and "Expected Ret"** — the key clue that two different checks were firing.

Timeline trace:
```
Snap 48:  ExtSol=1, Ext=[0,0], Ret=[1,1]  <- Extend solenoid JUST turned ON
Snap 49:  ExtSol=0, Ext=[1,1], Ret=[0,0]  <- Ext solenoid OFF, sensors swapped
Snap 69:  ExtSol=0, Ext=[1,1], Ret=[0,0]  <- ALARM fires "Expected Ret" <- WRONG
```

## Root Cause

Dual-solenoid design: each solenoid handles ONE direction. When Extend is OFF, the cylinder is NOT being commanded (Retract solenoid handles the other direction if/when it turns ON). Checking sensors on solenoid OFF is wrong because the opposing solenoid may not have energized yet.

## Fix

Removed `off_inputs` from all **12 dual-solenoid entries** (Lower/Upper Extend+Retract × DEG1/2/3):

```json
"off_inputs": [],
"off_inputs_physical": [],
"note_off": "Lower Extend solenoid OFF. Cylinder position not monitored.",
```

## What NOT to Change

- **Grip solenoids** (open/close use separate outputs/sensors; on_inputs for BOTH directions is correct — they're single-solenoid for each action)
- **Justify** (already correct — extend and retract use separate entries)
- **Nip solenoids** (no sensors mapped)

## Testing After Fix

Timeline showed clean cycle:
- Snap 58: Ext_Sol=ON → transition check starts (on_inputs=Ext sensors)
- Snap 59: Ext sensors ON → passed, no alarm
- Snap 64: Ext_Sol=OFF → **no check** (off_inputs empty)
- Snap 69: Ext_Sol=0, Ext=[1,1] → **no off-state alarm**

## Takeaway

For **dual-solenoid cylinders**, only validate `on_inputs`. Leave `off_inputs` empty. The opposing solenoid handles its own validation when IT turns ON.

For **single-solenoid spring-return**, `off_inputs` is semantically valid — verify sensors on de-energize, but allow longer settle time for gravity/pneumatic exhaust.
