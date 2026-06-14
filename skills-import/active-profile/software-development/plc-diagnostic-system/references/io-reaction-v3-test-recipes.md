# I/O Reaction Alarm Watcher v3 — Unit Test Recipes

Complete test suite runnable in WSL without a PLC.

> **Prerequisites:** `IOAlarmWatcher` must be importable from the project path.

---

## Test 1: Grace Period Suppresses Continuous Check

**Goal:** When output turns ON and sensors haven't moved yet, continuous check must be silent until `timeout_sec` after the output changed.

```python
from datetime import datetime, timedelta

def test_grace_period_suppresses():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)

    # Poll A: output turns ON, both sensors still OFF (cylinder hasn't moved yet)
    values_a = {
        "_IO_X4_DO_07": True,
        "_IO_X1_DI_01": False,
        "_IO_X1_DI_02": False,
    }
    alarms = watcher.check(values_a, now)
    assert len(alarms) == 0, "Grace period should suppress continuous check"

    # Poll B: 0.5s later, sensors still OFF
    alarms = watcher.check(values_a, now + timedelta(seconds=0.5))
    assert len(alarms) == 0, "Still within grace period"

    # Poll C: 1.5s later, sensors OFF → continuous should fire NOW
    alarms = watcher.check(values_a, now + timedelta(seconds=1.5))
    assert len(alarms) == 1, f"Expected 1 continuous alarm, got {len(alarms)}"
    assert "continuous" in alarms[0].message.lower()
    assert "_IO_X1_DI_01" in alarms[0].message or "_IO_X1_DI_02" in alarms[0].message
```

---

## Test 2: No Double Alarm — Transition Owns the Window

**Goal:** Transition alarm fires at deadline, but continuous check stays silent for the same `timeout_sec` after transition alarm fires.

```python
def test_transition_owns_window():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)

    # Transition: output ON, sensors OFF → pending check created
    values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": False, "_IO_X1_DI_02": False}
    alarms = watcher.check(values, now)
    assert len(alarms) == 0   # grace suppresses

    # At deadline (1.0s), transition fires alarm
    alarms = watcher.check(values, now + timedelta(seconds=1.0))
    assert len(alarms) == 1
    assert "within 1.0s" in alarms[0].message   # transition wording

    # Immediately next poll: continuous should be suppressed by Grace Rule 2
    alarms = watcher.check(values, now + timedelta(seconds=1.01))
    assert len(alarms) == 0, "Continuous suppressed after transition alarm"

    # After full timeout passes from transition: continuous can fire again
    alarms = watcher.check(values, now + timedelta(seconds=2.1))
    assert len(alarms) == 1
    assert "continuous" in alarms[0].message.lower()
```

---

## Test 3: Per-Degater Filtering

**Goal:** Disabling a degater stops all its pairs, clears pending checks, and suppresses transition_fired entries.

```python
def test_degater_filter():
    watcher = IOAlarmWatcher(timeout_sec=1.0)

    # Verify pair with degater "DEG1" exists
    deg1_pairs = [p for p in watcher._pairs if p.degater == "DEG1"]
    assert len(deg1_pairs) > 0, "Need at least one DEG1 pair to test"
    pair = deg1_pairs[0]

    now = datetime(2026, 6, 1, 12, 0, 0)
    values = {pair.output_physical: True}
    for inp in pair.on_inputs_physical:
        values[inp] = False

    # With all enabled: transition + pending created
    watcher.check(values, now)
    assert pair.output_physical in watcher._pending

    # Disable DEG1
    watcher.set_active_degaters(["DEG2", "DEG3", "SYS"])
    assert pair.output_physical not in watcher._pending
    assert pair.output_physical not in watcher._transition_fired

    # Re-enable DEG1, verify it works again
    watcher.set_active_degaters(["DEG1", "DEG2", "DEG3", "SYS"])
    watcher.clear()   # clean slate
    watcher.check(values, now)
    assert pair.output_physical in watcher._pending
```

---

## Test 4: Runtime Timeout Change Affects In-Flight Pending

**Goal:** Changing timeout from 1.0s to 2.5s while a check is pending must extend the deadline.

```python
def test_runtime_timeout_change():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)

    # Create pending check at T=0, deadline = T+1.0
    values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": False, "_IO_X1_DI_02": False}
    watcher.check(values, now)
    check = watcher._pending["_IO_X4_DO_07"]
    assert check.deadline == now + timedelta(seconds=1.0)

     # Change timeout to 2.5s while pending
    watcher.set_timeout_sec(2.5)
    assert check.deadline == now + timedelta(seconds=2.5)
    # Note: do NOT assert a stale `now` variable here. The deadline is absolute.

    # Verify it still fires after new deadline
    alarms = watcher.check(values, now + timedelta(seconds=2.6))
    assert len(alarms) == 1

    # Verify it does NOT fire at old deadline
    watcher2 = IOAlarmWatcher(timeout_sec=1.0)
    watcher2.check(values, now)   # create pending
    watcher2.set_timeout_sec(2.5)
    alarms = watcher2.check(values, now + timedelta(seconds=1.1))
    assert len(alarms) == 0, "Old deadline should be extended, not fire"
```

---

## Test 5: Sensor Unplug Detection (Fail-Safe)

**Goal:** Simulate a sensor cable vibration loose: output stays ON, sensor goes FROM True TO False while output unchanged.

```python
def test_sensor_unplug_after_motion():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)

    # Poll A: motion complete, sensors all ON
    values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": True, "_IO_X1_DI_02": True}
    alarms = watcher.check(values, now)
    assert len(alarms) == 0

    # Poll B: 5.0s later, sensor 1 drops (cable loosens)
    values["_IO_X1_DI_01"] = False
    alarms = watcher.check(values, now + timedelta(seconds=5.0))
    assert len(alarms) == 1, "Sensor drop must trigger continuous alarm"
    assert "continuous" in alarms[0].message.lower()
    assert "_IO_X1_DI_01" in alarms[0].message
```

---

## Test 6: Clear on Disconnect

**Goal:** `clear()` must reset all state so reconnect doesn't see stale pending/acked/fired entries.

```python
def test_clear_on_disconnect():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)

    values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": False, "_IO_X1_DI_02": False}
    watcher.check(values, now)
    assert len(watcher._pending) > 0

    watcher.clear()
    assert len(watcher._pending) == 0
    assert len(watcher._acked_faults) == 0
    assert len(watcher._transition_fired) == 0
    assert len(watcher._output_states) == 0
```

---

## Test 7: Zero-Padded Tag Matching

**Goal:** Watcher must correctly match physical addresses with zero-padded suffixes.

```python
def test_zero_padded_tags():
    # This is more of a catalog validation test
    import json, os

    json_path = "src/plc_tools/catalog/io_alarm_pairs.json"
    with open(json_path) as f:
        pairs = json.load(f)

    for pair in pairs:
        out_tag = pair["output_physical"]
        # e.g., "_IO_X4_DO_07" — verify suffix is zero-padded
        parts = out_tag.rsplit("_", 1)
        assert parts[1].isdigit() and len(parts[1]) == 2, \
            f"Tag {out_tag} should use zero-padded suffix"

        for inp in pair.get("on_inputs_physical", []):
            parts = inp.rsplit("_", 1)
            assert parts[1].isdigit() and len(parts[1]) == 2, \
                f"Input tag {inp} should use zero-padded suffix"
```

---

## Test 8: Deduplication Stays Active After Grace

**Goal:** Once a transition alarm fires, the same output→input combo should not fire again until the output toggles.

```python
def test_transition_dedup_across_polls():
    watcher = IOAlarmWatcher(timeout_sec=1.0)
    now = datetime(2026, 6, 1, 12, 0, 0)

    values = {"_IO_X4_DO_07": True, "_IO_X1_DI_01": False, "_IO_X1_DI_02": False}

    # Fire once
    watcher.check(values, now)   # create pending
    alarms = watcher.check(values, now + timedelta(seconds=1.1))
    assert len(alarms) == 1

    # Same cycle: immediately next poll should dedup
    alarms = watcher.check(values, now + timedelta(seconds=1.2))
    assert len(alarms) == 0, "Dedup should suppress repeat alarm"
```

---

## Running All Tests

```python
import sys
sys.path.insert(0, "src")

from plc_tools.polling.io_alarm_watcher import IOAlarmWatcher

tests = [
    test_grace_period_suppresses,
    test_transition_owns_window,
    test_degater_filter,
    test_runtime_timeout_change,
    test_sensor_unplug_after_motion,
    test_clear_on_disconnect,
    test_zero_padded_tags,
    test_transition_dedup_across_polls,
]

for test in tests:
    try:
        test()
        print(f"PASS: {test.__name__}")
    except AssertionError as e:
        print(f"FAIL: {test.__name__}: {e}")
    except Exception as e:
        print(f"ERR:  {test.__name__}: {e}")
```

---

## Pitfall: Stale `now` in Test Scripts

One test failed with `AssertionError: Expected 1 alarm after grace, got 2` because the test script declared `now = datetime.now()` once and re-used it across multiple test calls. If `watcher._transition_fired` stores absolute timestamps from `datetime.now()` inside `_evaluate_pending_check`, using a stale `now` for subsequent assertions breaks grace calculations.

**Fix:** Either:
- Pass `now` explicitly to every `check()` call (recommended for test determinism)
- Or re-declare `now = datetime.now()` before every check in integration tests
