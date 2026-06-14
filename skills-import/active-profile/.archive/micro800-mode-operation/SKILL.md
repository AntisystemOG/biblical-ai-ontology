---
name: micro800-mode-operation
description: "Allen-Bradley Micro800/Micro870 PLC mode operation for desktop diagnostic apps — status detection, mode switching limitations, Program-mode troubleshooting workflow, and OTE coil implications."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
    hermes:
      tags: [plc, micro800, micro870, pycomm3, troubleshooting, diagnostics, mode, program, run, cip, output-force]
      related_skills: [plc-output-force-safety, pyinstaller-desktop-app, plc-io-reaction-validation]
---

# Micro800 Mode Operation & Troubleshooting

How to read PLC mode, why Micro800s can't switch modes remotely from the app (unlike ControlLogix), when to use Program mode for troubleshooting, and how to determine if app-driven output writes will actually work.

## Scope

- **Read-only mode detection** from the PLC Identity Object / status word
- **Why you cannot switch Micro800 modes remotely** via CIP/pycomm3
- **Program mode troubleshooting** — when and how it's safe
- **OTE vs OTL/OTU coils** — does the ladder logic overwrite your app writes?
- **Analyzing ladder logic from .docx EMF exports** when you don't have the CCW file

## 1. Detecting PLC Mode (Read-Only)

The Micro870 exposes a status word via the Identity Object. Decode it to determine Run / Program / Faulted mode.

### Status Word Decoding

```python
from pycomm3 import Services, ClassCode

def get_controller_mode(self) -> dict:
    """Read PLC status word via CIP Identity Object (read-only)."""
    try:
        result = self._plc.generic_message(
            service=Services.get_attribute_single,
            class_code=ClassCode.identity_object,
            instance=1,
            attribute=5,  # Status word
            connected=False,
            unconnected_send=True,
            route_path=True,
        )
        if result and not result.error and result.value:
            status_word = int.from_bytes(result.value[:2], 'little')
            return self._decode_status_word(status_word)
    except Exception as e:
        return {"mode": "Unknown", "flags": [str(e)], "raw": 0}

def _decode_status_word(self, word: int) -> dict:
    modes = {
        0x00: "Program",
        0x01: "Run",
        0x02: "Run",        # redundant on Micro800
        0x03: "Faulted",
        0x04: "Booting",
    }
    mode = modes.get(word & 0x0F, f"Unknown({word & 0x0F})")
    flags = []
    if word & 0x10:   flags.append("Minor Fault Non-Recoverable")
    if word & 0x40:   flags.append("Major Recoverable Fault")
    if word & 0x80:   flags.append("Major Non-Recoverable Fault")
    if word & 0x100: flags.append("Minor Recoverable Fault")
    return {"mode": mode, "flags": flags or ["None"], "raw": word}
```

### Key Point

> **Status word is read-only. There is no CIP service to switch Micro800 modes remotely.**
> pycomm3 has `Services.start` and `Services.reset` (CIP 0x01, 0x05) but they do not work on Micro800 Identity Object. The only way to switch modes is:
> - Physical front panel **Run/Stop button**
> - **Connected Components Workbench (CCW)** → right-click PLC → Mode → Program/Run

---

## 2. Program Mode for Troubleshooting

### When to Use It

| Scenario | Action |
|---|---|
| Machine is **down** for maintenance | Switch to **Program mode**, force outputs via app |
| Testing solenoid wiring / air supply | Program mode + app tag writes |
| Verifying output LED on I/O module | Program mode + toggle output |
| Production is running | **STAY in Run mode** — fixtures are holding |

### What Program Mode Does vs. Run Mode

| | Run Mode | Program Mode |
|---|---|---|
| Ladder logic scan | Evaluates AND drives physical outputs | Evaluates internally, does **not** drive physical outputs |
| App tag writes (e.g. `IO_X4_DO_07 = TRUE`) | PLC overwrites on next scan (OTE coils) | **Value sticks** — no physical output driving |
| Input readings | Normal | Normal |
| Tag value reads | Normal | Normal |
| Expansion modules | Active | Active |

### The OTE Coil Problem

The Micro800/Degater program uses **OTE (Output Energize) coils** everywhere:

```
(Auto branch)   OR
(Manual branch) OR  --[ ]--  (Output coil OTE)
(Home branch)   OR
```

**OTE is rewritten every single scan.** In Run mode:

1. App writes `IO_X4_DO_07 = TRUE`
2. Next PLC scan evaluates the rung
3. If auto branch evaluates to FALSE, the OTE coil evaluates to FALSE
4. PLC **overwrites the tag back to FALSE**
5. Result: output **flickers** ON for ~1–20 ms, then OFF

In **Program mode**, the ladder still evaluates but the OTE **does not drive physical I/O** — so the app write "sticks" in the tag value, and you can read it back to verify.

### Safety Checklist Before Switching

- [ ] Machine is **down** — no production cycle running
- [ ] No personnel in the cell
- [ ] You have **verified** `DEG_MAN_AUTO` is in manual (FALSE) _or_ you are in Program mode
- [ ] You have a **Release plan** for every forced output before switching back to Run

---

## 3. Can the App Accidentally Change the Program?

**No. Absolutely not.** Direct tag writes via pycomm3 only change **data values**, never ladder logic instructions.

| What the app does | Affects ladder logic? |
|---|---|
| `read_tag("DEG_MAN_AUTO")` | ❌ No — read-only |
| `write_tag("IO_X4_DO_07", True)` | ❌ No — only changes the tag's current value |
| `write_tag("TON_24.PRE", 500)` | ❌ No — changes timer preset, not the program |
| **CCW download** | ✅ Yes — only way to change ladder instructions |
| Firmware update | ✅ Yes — but requires explicit action |
| Factory reset | ✅ Yes — requires explicit action |

The CIP protocol services for **tag read/write** are entirely different from the services for **program download/upload**. pycomm3 does not expose program download capabilities for Micro800.

---

## 4. How to Analyze Ladder Logic When You Don't Have CCW

When the PLC programmer provides a `.docx` ladder export (e.g., from CCW print function) instead of the `.l5x` file:

### Step 1: Extract the .docx

```bash
python3 -m zipfile -e ladder.docx extracted/
# Images are at: extracted/word/media/*.emf
```

### Step 2: Convert EMF to PNG

Use PowerShell from WSL (Linux tools cannot render EMF properly):

```bash
# Build a PowerShell conversion script
cat > /mnt/c/Users/$USER/AppData/Local/Temp/convert_emf.ps1 <<'EOF'
Add-Type -AssemblyName System.Drawing
$emf = [System.Drawing.Imaging.Metafile]::FromFile("C:\Users\$USER\AppData\Local\Temp\image75.emf")
$emf.Save("C:\Users\$USER\AppData\Local\Temp\rung75.png", [System.Drawing.Imaging.ImageFormat]::Png)
$emf.Dispose()
Write-Host "Done"
EOF

# Execute via cmd.exe
/mnt/c/Windows/System32/cmd.exe /c \"powershell -ExecutionPolicy Bypass -File C:\\Users\\$USER\\AppData\\Local\\Temp\\convert_emf.ps1\"
```

### Step 3: Analyze Individual Rungs

Use `vision_analyze` to read the ladder diagram. Ask for:

1. Number of parallel branches
2. Contacts in series within each branch
3. Coil type: OTE `( )`, OTL `(L)`, or OTU `(U)`
4. Presence of `DEG_MAN_AUTO` or mode-related contacts
5. Contact type: NO `[-]` vs NC `]/[`

```
vision_analyze("/mnt/c/Users/$USER/AppData/Local/Temp/rung75.png",
    "List all tag names, identify parallel branches, identify NO vs NC contacts, trace full logic flow.")
```

### What You're Looking For

| Feature | Meaning |
|---|---|
| `]/[ DEG_MAN_AUTO` (NC) in auto rung | Auto rung breaks when manual mode active ✅ |
| `(L)` OTL coil | Latches — holds state across scans ✅ |
| `( )` OTE coil | Rewritten every scan — app writes fight ladder ❌ in Run mode |
| `[-] Home All Manual PB` (NO) in manual branch | Physical button required for manual path |

---

## 5. PyChecker/Upgrading & Micro800 Gotchas

- **pycomm3 services that don't work on Micro800:** `Start(0x01)`, `Reset(0x05)`, `Stop` on Identity Object. These are ControlLogix-specific. Always verify before using.
- **Identity Object instances 2-8** are reserved for expansion modules — scan these to find I/O modules.
- **Assembly Object (Class 0x04)** on Micro800 is limited. Some firmware versions don't expose full I/O data. Fall back to `discover_tags()` + `read_tag()` when Assembly fails.
- **Tag names are ASCII only** — no spaces, no special chars. CCW auto-converts to underscores.
- **Zero-padded I/O tags** — Physical tags use `_IO_X1_DI_01` format (not `_IO_X1_DI_1`). Mismatching silently fails tag matching. See `references/degater-project-notes.md` §I/O Reaction Alarm Watcher.

---

## 6. I/O Reaction Alarm Watcher Pattern

When building real-time validation that checks if outputs cause expected input reactions within a timeout, follow the pattern from the Degater project:

1. **Load alarm pairs from JSON** — `output_physical`, `on_inputs_physical`, `off_inputs_physical`, `timeout_sec`
2. **Check synchronously in poll cycle** — call `watcher.check(io_values)` inside `_on_poll_complete()` with live tag dict
3. **Deduplicate by `fault_key`** — composite key like `"DEG1_Lower_Extend_timeout"`; suppress repeats until output toggles back
4. **Clear on disconnect** — `watcher.clear()` when PLC disconnects to prevent stale pending checks
5. **Zero-padded tag format** — ensure JSON physical addresses match PLC exactly (`_DI_01`, not `_DI_1`)
6. **Continuous validation** — in addition to transition checks, scan every active output every poll cycle and alarm immediately if expected inputs are not ON. Catches sensor disconnects that happen *after* the transition.
7. **Runtime-mutable timeout** — expose `set_timeout_sec(float)` so the Diagnostics tab can change the grace period without restarting the program
8. **Zero-padded tag format** — ensure JSON physical addresses match PLC exactly (`_DI_01`, not `_DI_1`)
9. **Poll error throttling** — require 4 consecutive read failures before logging a Poll Error alarm; prevents tab-switch spikes from spamming the log
10. **Fault key clear on reconnect** — call `watcher.clear()` and `alarms_log.clear()` on every connect to reset dedup state
11. **Automatic degater detection (v3.1)** — When a KM robot selects stations via PLC inputs (e.g., `KM_Selected_DEG1_Or_3` = `_IO_EM_DI_00`, `KM_Selected_DEG2_Or_3` = `_IO_EM_DI_01`), read these inputs every poll cycle and automatically set `_active_degaters`. This eliminates false alarms from unwired stations whose outputs are commanded ON by PLC ladder but are not physically in use. See `references/io-reaction-v3-implementation.md` §Auto-Degater Detection from KM Robot Inputs for the decoding matrix and wiring pattern.
12. **Do NOT filter by selected degater if ladder has global dependencies** — If the "Home" signal or any safety interlock depends on ALL degaters being home simultaneously, remove any `if pair.degater not in _active_degaters: continue` logic. Keep `_active_degaters` for UI display only. See `references/io-reaction-alarm-watcher.md` §When NOT to Filter by Selected Degater for the decision matrix.
13. **Poll rate selector** — Add a QComboBox (100/250/500/1000 ms) to Diagnostics tab so operators can speed up polling to catch sensor transitions. Wire `poll_rate_changed` signal to `QTimer.setInterval()`. See `references/io-reaction-alarm-watcher.md` §Poll Rate Selection UI Pattern.
14. **Suppress continuous check during grace period** — When an output changes state, the transition check owns the timeout window. Suppress continuous validation for `timeout_sec` after `state.changed_at` AND after `_transition_fired` to avoid double-alarming during normal cylinder motion. See `references/io-reaction-alarm-watcher.md` §Grace Period.

Full implementation notes and the zero-padding pitfall are in `references/io-reaction-alarm-watcher.md`.

Full implementation notes and the zero-padding pitfall are in `references/io-reaction-alarm-watcher.md`.

---

## 7. Alarm Log Detail Dialog Pattern

When alarm messages are long, the QTableWidget `Message` column truncates with `…` — users cannot read the full text. Implement a double-click detail dialog.

### Implementation

1. Store the log entry `id` in each row’s `Qt.UserRole`:
   ```python
   item.setData(Qt.UserRole, entry.id)
   ```

2. Wire `cellDoubleClicked` on both Active and Acknowledged tables:
   ```python
   table.cellDoubleClicked.connect(self._on_cell_double_clicked)
   ```

3. Open a dark-themed QDialog with a read-only QPlainTextEdit:
   ```python
   from PySide6.QtWidgets import QDialog, QDialogButtonBox, QPlainTextEdit
   from PySide6.QtCore import Qt

   def _on_cell_double_clicked(self, row, col, table):
       entry_id_item = table.item(row, 0)
       if not entry_id_item:
           return
       entry_id = entry_id_item.data(Qt.UserRole)
       entry = self._find_entry_by_id(entry_id)  # look in _active or _acknowledged
       if not entry:
           return

       dlg = QDialog(self)
       dlg.setWindowTitle(f"Alarm Detail — {entry.severity}")
       dlg.setStyleSheet("""QDialog { background-color: #1a1a2e; color: #e0e0e0; }
                           QPlainTextEdit { background-color: #16213e; color: #e0e0e0;
                                            border: 1px solid #0f3460; }""")

       layout = QVBoxLayout(dlg)
       meta = QPlainTextEdit(
           f"Timestamp: {entry.timestamp:%Y-%m-%d %H:%M:%S}\n"
           f"Severity:  {entry.severity}\n"
           f"Source:    {entry.source}\n"
           f"Acked:     {entry.acknowledged}")
       meta.setReadOnly(True)
       meta.setMaximumBlockCount(4)
       layout.addWidget(meta)

       msg = QPlainTextEdit(entry.message)
       msg.setReadOnly(True)
       msg.setLineWrapMode(QPlainTextEdit.WidgetWidth)
       layout.addWidget(msg)

       btns = QDialogButtonBox(QDialogButtonBox.Close)
       btns.rejected.connect(dlg.reject)
       layout.addWidget(btns)

       dlg.exec()
   ```

### Design Notes

- `QPlainTextEdit` is preferred over `QLabel` because it handles word wrap at widget width and scrolls naturally for very long messages.
- `WidgetWidth` line wrap mode breaks lines at the dialog width, not at fixed character columns.
- Store `entry.id` (a UUID or integer) in `Qt.UserRole` — never store the full message in the item data; keep models lightweight.
- This pattern applies to any QTableWidget that displays truncated text and needs a detail view.

## 8. Direction-Aware Fail-Safe Read Policy

A "playback glitch fix" that caches last-known values on pycomm3 read failures will **hide sensor failures** from the alarm watcher if applied blindly to all tags.

### The Bug

In the poller (`_PollWorker.poll()`), if pycomm3 returns a read error:
```python
# BEFORE (broken): every tag returns cached TRUE on failure
io_values[tag] = self._last_known_values.get(tag, False)
```

| What happened | What poller reported | Watcher saw | Result |
|-------------|---|---|---|
| Sensor ON, gets unplugged | Read fails → cached **True** | Sensor still ON | **No alarm** |
| Both sensors unplugged | Both cached **True** | Both ON | **No alarm** |
| Output solenoid, transient read glitch | Cached **True** | Output still ON | ✅ OK (avoid flicker) |

### The Fix

Check `direction` from the I/O catalog (`drv._io_tags`) before deciding the fallback value:

```python
tag_dir = {
    t: (drv._io_tags.get(t, {}).get("direction", "STATUS")
        if drv._io_tags else "STATUS")
    for t in catalog_tags
}

for logical_name, res in zip(catalog_tags, raw):
    if res and not res.error:
        io_values[logical_name] = res.value
        self._last_known_values[logical_name] = res.value
    else:
        direction = tag_dir.get(logical_name, "STATUS")
        if direction == "OUTPUT":
            # Transient glitch — keep last known to avoid flicker
            io_values[logical_name] = self._last_known_values.get(
                logical_name, False)
        else:
            # INPUT or STATUS — fail-safe: disconnected sensor = False
            io_values[logical_name] = False
```

**Same logic applies to the total-read-failure (`except Exception`) path.**

### Why This Works

| Direction | Read Failure Behavior | Rationale |
|---|---|---|
| **INPUT** | Force `False` | Sensor unplugged → PLC can't read → should alarm |
| **OUTPUT** | Keep last known | Transient comm spike shouldn't flicker solenoid display |
| **STATUS** | Force `False` | Status bits should always be readable; failure means fault |

The `KNOWN_IO_TAGS` catalog already contains `"direction": "INPUT"` / `"OUTPUT"` / `"STATUS"` for every tag — no schema change needed.

## 9. Visual I/O Association Verification Before Implementation

Before writing the background watcher logic, present a visual table of the loaded output→input alarm pairs so the user can confirm the mapping is correct. This catches:
- Missing or extra pairs in `io_alarm_pairs.json`
- Physical tag name mismatches (e.g. `_DI_1` vs `_DI_01`)
- Outputs with no expected inputs defined
- Wrong degater associations (e.g. DEG2 pair pointing to DEG1 inputs)

Use `QTableWidget` or `QTreeWidget` with columns: **Output** | **Action** | **Expected ON Inputs** | **Expected OFF Inputs** | **Timeout**. Populate from the JSON after loading. Only proceed to background implementation once the user confirms the table looks correct.

---

## Verification: Does Manual Mode Allow App Output Control?

After analyzing the ladder, you can answer this definitively:

| Ladder Pattern | App Writes in Manual Mode (Run) | App Writes in Program Mode |
|---|---|---|
| `XIO DEG_MAN_AUTO` breaks auto rung + manual branch uses OTL | ✅ Works in manual | ✅ Always works |
| `XIO DEG_MAN_AUTO` breaks auto + manual branch uses OTE + physical PB | ⚠️ Fights if PB not pressed | ✅ Works |
| No mode contact at all (auto always active) | ❌ Always fights | ✅ Works |
| OTE-only throughout, no bypass | ❌ Always fights | ✅ Works |

> For the Degater project: OTE coils everywhere, no OTL. **Program mode is the correct troubleshooting approach.** Manual mode on the ladder enables the _physical pushbutton path_, not app-driven writes.

---

## References

- `references/degater-project-notes.md` — Session-specific findings from D14 analysis: tag names, rung structure, OTE behavior, EMF conversion notes, and recent bug fixes
- `references/micro800-mode-status-decoder.md` — Status word bit field breakdown for every Micro800 model
- `references/ladder-emf-conversion.md` — Step-by-step EMF to PNG workflow with sample PowerShell scripts
- `references/io-reaction-alarm-watcher.md` — Real-time output→input timeout validation pattern: architecture, JSON pair format, deduplication, zero-padding pitfall, integration points, and test recipes
- `references/io-reaction-alarm-watcher.md#direction-aware-fail-safe-read-policy` — INPUT=Fail-safe (False on error), OUTPUT=last-known cached (prevent flicker)
- `references/validate_io_alarm_pairs.py` — Pre-build validation script: checks all physical/logical tags in JSON pairs against the live catalog, flags zero-padding issues, missing tags, and wrong direction metadata

## Support Scripts

- `scripts/convert_ladder_emf_to_png.py` — Python script to batch-convert EMF ladder images from a .docx export to PNG using PowerShell. Run: `python3 scripts/convert_ladder_emf_to_png.py /path/to/ladder.docx`

## Related Skills

- `plc-output-force-safety` — Safety patterns for manual/auto interlocks, GUI dimming, and force/release workflows
- `pyinstaller-desktop-app` — Bundling diagnostic apps into single-file Windows .exe
