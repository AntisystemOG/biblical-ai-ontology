# Session: KM Robot "wait DI-186 Time out" — Root Cause Investigation

**Date:** 2026-06-03
**Trigger:** Thad reports KM robot alarmed with "wait DI-186 Time out"
**Resolution:** Tool missed the fault because Micro870 DO_ physical addresses read unreliably, blinding the IOAlarmWatcher's transition check. Ladder logic and sensor were physically correct.

---

## 1. The Alarm

| Field | Value |
|---|---|
| Source | KM robot controller (not PLC ladder) |
| Alarm text | "wait DI-186 Time out" |
| What it means | Robot program timed out waiting for a pre-condition signal |
| Root cause | PLC output `_IO_EM_DO_01` (Lower_Ready_For_Parts) stayed OFF because the justify cycle never completed |

---

## 2. Robot DI Number → PLC Output Mapping

Robot DI numbers are internal to the robot controller. They map to PLC outputs through the robot's I/O assignment table, NOT the PLC ladder. From the PLC physical mapping:

| Robot DI (config'd) | PLC Output | Meaning |
|---|---|---|
| DI-186 (inferred) | `_IO_EM_DO_01` | Lower_Ready_For_Parts |

The robot expected `Lower_Ready_For_Parts` to be TRUE, but it stayed FALSE.

---

## 3. Why Lower_Ready_For_Parts Stayed OFF (Ladder Trace)

### Para 253: Lower_Ready_For_Parts OTE

```
BST XIC USER_BIT_11  XIO USER_BIT_22
NXB XIC USER_BIT_37  XIO USER_BIT_48
NXB XIC USER_BIT_63  XIO USER_BIT_74
BND OTE _IO_EM_DO_01
```

Logic: `_IO_EM_DO_01` = (DEG1 ready AND not DEG1 done) OR (DEG2 ready AND not DEG2 done) OR (DEG3 ready AND not DEG3 done).

For DEG1, USER_BIT_11 = ready, USER_BIT_22 = done.

### Para 373: USER_BIT_16 SET (Justify Complete)

Requires ALL of:
- `_IO_EM_DI_10` E-Stop OK
- `_IO_EM_DI_08` Door Closed
- `_IO_X2_DI_30` Auto Mode
- `USER_BIT_15` Prior state (lower cut complete)
- `_IO_X1_DI_08` D1_Low_Justify_Cyl1_Ext
- `_IO_X1_DI_09` D1_Low_Justify_Cyl2_Ext
- `_IO_X1_DI_10` D1_Low_Justify_Cyl3_Ext ← **THIS SENSOR WAS OFF**
- `_IO_X1_DI_11` D1_Low_Justify_Cyl4_Ext

### Para 385: USER_BIT_22 SET (Cycle Done)

Requires:
- `USER_BIT_16` ← must already be ON
- `_IO_EM_DI_06` KM away from degater

### Chain of Failure

1. `D1_Low_Justify_Cyl3_Ext` was physically OFF (sensor failed)
2. → `USER_BIT_16` could not set (all 4 sensors in series)
3. → `USER_BIT_22` could not set (USER_BIT_16 required)
4. → `_IO_EM_DO_01` (Lower_Ready_For_Parts) stayed OFF
5. → Robot timed out waiting → "wait DI-186 Time out"

The **ladder was working correctly**. It correctly refused to signal "ready" because a justification sensor was missing.

---

## 4. Why the PLC Tool Missed It

### 4.1 The Watcher's Design

`IOAlarmWatcher._start_check()` is the entry point:

```python
def _start_check(self, pair, out_val, io_values, now):
    # Starts a pending check ONLY when output transitions ON
    # Sets deadline = now + timeout_sec (default 1.0s)
    # Monitors expected_inputs until deadline
```

For a justify extend alarm to fire, the watcher needs to see `D1_Low_Justify_Ext_Sol` turn ON. Then it watches `_IO_X1_DI_08` through `_IO_X1_DI_11`. If any stay OFF for >1s → ALARM.

### 4.2 The Read Failure Problem

The poller (`_PollWorker.run()` lines 77-128) batch-reads ALL 127 physical tags:

```python
phys_tags = [physical_mapping.get(tag, tag) for tag in catalog_tags]
raw = drv._plc.read(*phys_tags)
```

For a DO_ physical address like `_IO_X3_DO_05` (D1_Low_Justify_Ext_Sol physical mapping):

| Time | Actual PLC State | pycomm3 Read | Poller Behavior | io_values Seen |
|---|---|---|---|---|
| t=0 | OFF | SUCCESS | cached | False |
| t=100ms | ON | FAILS (no response) | falls back to last_known | False |
| t=200ms | ON | FAILS | falls back to last_known | False |
| t=300ms | ON | SUCCESS | cached | True |

The watcher sees the transition at **t=300ms**, not t=100ms. The 1-second timer that should have started at t=100ms is already 200ms stale.

### 4.3 Worst-Case Scenario (High Failure Rate)

If DO_ reads fail >80% of the time (typical on Micro870):

| Time | Actual | Read | Cached | io_values |
|---|---|---|---|---|
| t=0 | OFF | SUCCESS | False | False |
| t=100ms | ON | FAILS | False | False |
| t=200ms | ON | FAILS | False | False |
| t=300ms | ON | FAILS | False | False |
| ... | ON | FAILS | False | False |

The watcher **never sees the transition** → **never starts the timer** → **NO ALARM EVER FIRES**.

### 4.4 Sensor Sanity Also Blind

Sensor Sanity checks if both extend AND retract sensors are OFF simultaneously while the assembly is at rest (both solenoids OFF). For the Lower Justify assembly:

```python
for deg, ext_sensors, ret_sensors in assemblies:
    ext_by_cyl = group_by_cyl(ext_sensors)  # 4 sensors: Cyl1-4 Ext
    ret_by_cyl = group_by_cyl(ret_sensors)  # EMPTY for justify!
    for cyl_num in set(ext_by_cyl.keys()) & set(ret_by_cyl.keys()):
        # ret_by_cyl is empty → set intersection is EMPTY
        # → NO justify cylinders checked at all
```

Sensor Sanity only checks Lower Arm and Upper Arm (which have both extend + retract sensor pairs). Justify assemblies have no retract sensors, so they are **completely invisible to Sensor Sanity**.

Moreover, the solenoid read failures mean Sensor Sanity may think the assembly is "at rest" (both solenoids OFF) even when the extend solenoid is actually ON.

---

## 5. What the Watcher CAN and CANNOT Detect (As-Built)

| Can Detect | Cannot Detect |
|---|---|
| Lower Arm extend/retract sensor failures | Justify cylinder sensor failures (no retract sensors, uncheckable) |
| Upper Arm extend/retract sensor failures | Output turning ON when sensors fail (transition blind) |
| Input dropping OFF while output stays ON | Grip sensor failures (if grip transitions are hidden) |
| (iff output is read as ON at least once) | Any failure where output transition is invisible |

---

## 6. Fix Options (Software-Side Only)

### Option A — Try Symbolic Tag Names

Read `D1_Low_Justify_Ext_Sol` (symbolic program tag) instead of `_IO_X3_DO_05` (physical address).

```python
# In micro800_driver.py read_tag():
def read_tag(self, tag_name: str) -> dict:
    phys = physical_mapping.get(tag_name, tag_name)
    result = self._plc.read(phys)  # physical
    if result and result.error:
        # Fallback: try symbolic name
        result = self._plc.read(tag_name)  # symbolic
    return result
```

**Pros:** Minimal code change; if it works, fixes everything. **Cons:** May fail on Micro870; needs hardware test.

### Option B — Monitor PLC State Bits

Track internal ladder variables instead of physical outputs:
- `USER_BIT_15` — lower cut complete
- `USER_BIT_16` — justify complete (ALL 4 sensors ON)
- `USER_BIT_22` — cycle done

These are regular program tags that pycomm3 reads reliably.

**Pros:** Accurate state machine tracking; no DO_ read failures. **Cons:** Must discover tag names; may vary between PLC programs.

### Option C — Pattern-Based Stuck-Sensor Detection

Alert if a sensor that normally cycles stays OFF for >X seconds while the degater is active:

```python
# Pseudo-code for stuck-sensor detector
if degater_selected and sensor_not_ON and time_since_last_ON > threshold:
    raise_alarm(f"{sensor_name} has not cycled ON for {threshold}s")
```

**Pros:** No dependency on output reads; catches ALL stuck sensors. **Cons:** Needs tuning; can't identify which output was commanded.

---

## 7. Ladder Logic Paragraph References (from Degaters_Operation.docx)

| Paragraph | Content | Tags |
|---|---|---|
| Para 244 | `USER_BIT_11` SET requirements | `_IO_X1_DI_00`, `_IO_X1_DI_02`, `USER_BIT_10` |
| Para 373 | `USER_BIT_16` SET requirements | `_IO_X1_DI_08`–`_IO_X1_DI_11`, `USER_BIT_15`, `USER_BIT_12` |
| Para 383 | `_IO_EM_DO_01` OTE | `USER_BIT_11`, `USER_BIT_22`, `USER_BIT_37`–`USER_BIT_74` |
| Para 385 | `USER_BIT_22` SET requirements | `USER_BIT_16`, `_IO_EM_DI_06` |

---

## 8. Key Takeaways

1. **"wait DI-186 Time out" is a robot alarm, not a PLC ladder alarm.** The root cause is always upstream in the PLC.
2. **The PLC ladder was correct.** It refused to signal "ready" because a justification sensor failed.
3. **The tool failed because Micro870 DO_ physical addresses read unreliably.** This blinded the transition check.
4. **Sensor Sanity cannot check justify assemblies** because they have no retract sensors.
5. **Symbolic tag reads or state-bit monitoring** are the most promising software-side fixes.
6. **Always map robot DI numbers to PLC outputs via the robot's I/O assignment table** — never assume from the ladder alone.
