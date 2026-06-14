# Silent Data-Loading Failure and Deduplication Traps

Two independent hidden causes from a single PLC alarm-watcher session.

## Case 1: Bundled JSON file silently loads 0 records

### Symptom
Controller alarm module runs, produces no alarms, no errors in UI, tests pass in dev.

### Investigation (Phase 1)
1. Code review: `IOAlarmWatcher.__init__()` opens a JSON file, catches `OSError`, loads 0 pairs.
2. Check `.spec` file `datas` list — JSON file was never declared.
3. In dev (`python -m app`), relative path works. In EXE (`sys._MEIPASS`), path doesn't exist.

### Root cause
PyInstaller only bundles items listed in the `.spec` `datas` array. Data files are NOT auto-discovered. When the file is missing at runtime, the fallback (`except FileNotFoundError: pass`) silently produces an empty collection.

### Fix
Add the JSON path explicitly to `datas`:

```python
datas=[
    ('src/plc_tools/catalog/io_alarm_pairs.json', 'plc_tools/catalog'),
    # ... existing assets
],
```

Then verify `_asset_path()` inside the app uses the exact bundle path:

```python
if hasattr(sys, "_MEIPASS"):
    base = Path(sys._MEIPASS) / "plc_tools" / "catalog"
```

### Prevention
- Any file read at runtime must be declared in `.spec` `datas`
- Don't `try/except OSError: pass` on critical data loads; at minimum log a warning when 0 records load

## Case 2: Set-based dedup never cleared, suppressing repeat events

### Symptom
Alarm fires once, then never again across reconnects / days. UI log still receives events, but dedup set keeps growing.

### Investigation (Phase 1)
1. Traced `AlarmsLogTab.log_event()` — checks `if fault_key in self._fault_keys: return`
2. Traced `clear()` method — literally `pass` (no-op)
3. Traced where `clear()` is called on reconnect — `main_window.py` explicitly excluded alarms tab from clear loop

### Root cause
Two independent bugs:
- `clear()` was a no-op, so `_fault_keys` accumulated forever
- The alarms tab was excluded from connect-time resets, so even if `clear()` worked, it never got called

### Fix
1. Make `clear()` reset the dedup set: `self._fault_keys.clear()`
2. Include the alarms tab in the connect-time `for tab in tabs: tab.clear()` loop
3. Preserve history (`_entries`) separately from dedup guard

```python
def clear(self):
    self._fault_keys.clear()   # reset dedup so alarms can fire again
    # do NOT clear _entries — history is preserved
```

### Prevention
- Any stateful guard (`_seen`, `_fault_keys`, `_processed_ids`) must have a clear reset path that's exercised on the expected lifecycle event (reconnect, session start, etc.)
- When a tab/widget has separate "display state" and "dedup guard," clear only the guard, not the display data

## Cross-File Data-Flow Verification Pattern

Before declaring a data pipeline correct, verify the entire chain end-to-end:

```python
# 1. Source data (JSON catalog)
"output_tag": "DEG1_Lower_Ext_Sol"

# 2. Logical tag catalog (Python dict)
"DEG1_Lower_Ext_Sol": {"addr": "O:1/1", "desc": "..."}

# 3. Physical address mapping
"DEG1_Lower_Ext_Sol": "0001H0001"

# 4. PollWorker builds io_values with logical names
io_values = {"DEG1_Lower_Ext_Sol": True, ...}

# 5. Watcher receives logical names and matches against JSON
```

If any layer mismatches keys (e.g., JSON uses snake_case, catalog uses CamelCase), the watcher sees no matches and silently produces 0 alarms.

### Verification command (one-shot)

```python
# After loading all three files, assert every alarm pair tag exists in the mapping
for pair in alarm_pairs:
    assert pair["output_tag"] in physical_map, pair["output_tag"]
    for inp in pair["on_inputs"] + pair["off_inputs"]:
        assert inp in physical_map, inp
```
