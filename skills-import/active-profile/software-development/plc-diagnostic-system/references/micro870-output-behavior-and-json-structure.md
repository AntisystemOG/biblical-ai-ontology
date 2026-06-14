# Micro870 Output Read Behavior & Alarm Pairs JSON Structure

## Micro870 DO_ Addresses Are Write-Only

On the Allen-Bradley Micro870 (Micro800 series), digital output addresses (`_IO_X*_DO_*`) are write-only from the pycomm3 perspective. Attempting to read them back with `plc.read()` returns `"no response"`. This is **expected behavior**, not a communication error. The `_PollWorker` must NOT log these as alarm-worthy poll failures.

### Implementation in `_PollWorker`

```python
if direction == "OUTPUT":
    io_values[logical_name] = self._last_known_values.get(logical_name, False)
    # OUTPUT read errors are normal — do NOT log as first_error
else:
    io_values[logical_name] = False
    if not first_error:
        err = res.error if res else "no response"
        first_error = f"{logical_name}: {err}"
```

| Error Type | Tag Direction | Action | Log?
|---|---|---|---|
| `res.error` | INPUT | Force `False` (fail-safe) | Yes |
| `res.error` | STATUS | Force `False` | Yes |
| `res.error` | OUTPUT | Keep last-known value | No — expected |
| Exception on bulk read | — | Fall through by direction | Yes |

## Alarm Pairs JSON Structure

`io_alarm_pairs.json` is a **flat array** of dictionaries, NOT a dict-of-lists.

**Traversal code (correct):**
```python
for entry in pairs:
    output = entry["output_tag"]       # singular key name
    inputs = entry.get("on_inputs", [])  # not "inputs"
    off_inputs = entry.get("off_inputs", [])
```

**Wrong assumption (initially made this session):**
```python
for group in pairs.values():  # pairs is NOT a dict
    for ent in group:
        json_names.add(ent["output"])  # key is "output_tag", not "output"
        json_names.update(ent.get("inputs", []))  # key is "on_inputs", not "inputs"
```

## Tags Expected to NOT Appear in Alarm Pairs

Status bits and robot kinematics tags exist in the catalog but are not cylinder output/sensor pairs:

- `DEG_MAN_AUTO`
- `Home_All_Manual_PB`
- `KM_*` (all robot kinematics)
- `Upper_Ready_For_Parts`
- `Lower_Ready_For_Parts`
- `DEG_Home_And_Ready`
- `Complete_Runner_Drop`
- `Tilt_DEG_Pos_Deflector`

The consistency checker should tolerate catalog-only entries when verifying against alarm pairs, but flag physical-mapping-only entries as errors.

## Case Mismatch Patterns Found in This Session

| File | Before | After |
|---|---|---|
| `io_catalog.py` | `D3_Low_justify_Ret_Sol` | `D3_Low_Justify_Ret_Sol` |
| `physical_mapping.py` | `D3_Low_justify_Ret_Sol` | `D3_Low_Justify_Ret_Sol` |
| `physical_mapping.py` | `D3_low_Nip_Open_Sol` | `D3_Low_Nip_Open_Sol` |
| `io_alarm_pairs.json` | `D3_Up_Justify_Cyl2_Ext` | `D3_Up_Justify_Cyl_2_Ext` |
| `io_catalog.py` | `D1__Low_Grip_Close_Sol` | `D1_Low_Grip_Close_Sol` |

**Rule:** When renaming a tag, update ALL THREE files in ONE commit. Never split across commits.
