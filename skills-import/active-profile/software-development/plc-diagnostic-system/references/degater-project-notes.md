# Degater BST33/35 Project Notes

Session-specific findings from ladder logic analysis, PLC mode behavior, and build fixes.

## Project
- **PLC:** Allen-Bradley Micro870 (2080-LC70)
- **IP:** 192.168.1.10
- **Logic:** D14 revision — 177 ladder rungs, 28 TON timers (TON_1–TON_28)
- **Mode tag:** DEG_MAN_AUTO (X2 Digital Input 30)
- **Physical switch:** MAN-AUTO selector on the machine

## Findings

### 1. Timers do not exist as individual tags (May 2026 bug)
`pycomm3` cannot read structured timer members on this Micro870 firmware. `read_timers()` throws errors about PRE/ACC/EN/DN/TT not existing.

**Workaround:** The app now falls back to the static `KNOWN_TIMERS` catalog from `timer_catalog.py` (28 TON timers) for display only. Timer values are not polled — only the boolean state is flattened into `io_values` for ladder display logic.

**Fix delivered:** Removed an orphaned `self._poll_worker.set_timer_names(timer_names)` call in `_on_poll_done()` (line 630 of `main_window.py`) that caused `NameError` because `timer_names` was no longer defined after removing the Programs tab.

### 2. Ladder Logic Output Rung Structure
Every solenoid output (verified on rungs ~54-177) has 3-4 parallel branches feeding an OTE coil:

```
Branch 1 (Auto):    USER_BIT_32  --[ ]--+-- TON_24.Q --[ ]--  (Output OTE)
Branch 2 (Manual):   ]/[ DEG_MAN_AUTO   --[ ]--+-- Home All Manual PB --[ ]--  (same OTE)
Branch 3 (Home):     USER_BIT_79 (KM Request Home) --[ ]--  (same OTE)
```

- `]/[` = normally closed (NC) contact
- `[-]` = normally open (NO) contact
- `( )` = OTE coil (output energize)

### 3. DEG_MAN_AUTO is NC
`DEG_MAN_AUTO = FALSE` (manual mode) → NC contact **CLOSES** → manual branch becomes active (but requires `Home All Manual PB` pressed).
`DEG_MAN_AUTO = TRUE` (auto mode) → NC contact **OPENS** → manual branch breaks.

### 4. Outputs Use OTE Only — No OTL/OTU
There are **no latch coils** anywhere in the program. Every output uses OTE `( )` which is re-evaluated and overwritten every PLC scan.

**App write behavior in Run mode:**
1. App writes `IO_X4_DO_07 = TRUE`
2. Next scan evaluates auto branch (likely FALSE if machine down)
3. OTE coil evaluates to FALSE
4. PLC overwrites tag back to FALSE
5. **Physical output flickers ON for ~1-20ms**

### 5. Program Mode is the Correct Approach
For troubleshooting a down machine:
1. Press **Run/Stop button** on PLC front panel until "Program" appears
2. (Or use CCW → right-click PLC → Mode → Program Mode)
3. Use app to toggle solenoid outputs
4. Ladder still evaluates but **OTE does not drive physical I/O**
5. App writes **stick** — no flicker

### 6. Cannot Accidentally Change the Program
- pycomm3 `write_tag()` only writes **data values**
- CIP tag read/write services are completely separate from program download services
- Only CCW download can modify ladder instructions
- Safe to put in Program mode and test outputs — program is not modified

## Tag Naming Conventions

### Inputs (from physical_mapping.py and ladder analysis)
- `DEG_MAN_AUTO` — X2 DI 30 (MAN-AUTO switch)
- `DEG_SEQ` — X0 DI 06
- `DEG_GO` — X0 DI 07
- `DEG1_PRESENT` — X3 DI 37 / DI 38
- `DEG2_PRESENT` — X3 DI 39 / DI 40
- `DEG1_IN_POSITION` — X2 DI 24 / DI 25
- `DEG2_IN_POSITION` — X2 DI 26 / DI 27

### Outputs (solenoids)
- `Output_Deg1_FeedSol`
- `Output_Deg1_JustifySol`
- `Output_Deg1_CutSol`
- `Output_Deg2_FeedSol`
- `Output_Deg2_JustifySol`
- `Output_Deg2_UpperCutSol`
- `Output_Deg2_LowerCutSol`
- `Output_Deg2_GripSol`
- `Output_Deg2_NipperSol`
- `Output_Deg2_ExtendSol`
- `Output_Deg2_RetractSol`

### Digital I/O module tags
- `IO_X4_DO_07` through `IO_X4_DO_20` (Deg1 outputs)
- `IO_X5_DO_01` through `IO_X5_DO_12` (Deg2 outputs)
- `IO_X0_DI_06` through `IO_X0_DI_22`
- `IO_X2_DI_24` through `IO_X2_DI_35`
- `IO_X3_DI_36` through `IO_X3_DI_47`
- `IO_X6_DI_48` through `IO_X6_DI_59`
- `IO_X7_AI_00` through `IO_X7_AI_03`

## EMF-to-PNG Conversion Notes
CCW's print-to-Word function generates EMF images (not PNG/JPG). Linux tools cannot render EMF. Conversion path:
1. Extract .docx: `python3 -m zipfile -e doc.docx extracted/`
2. EMFs at `extracted/word/media/image*.emf`
3. Convert via PowerShell: `System.Drawing.Imaging.Metafile::FromFile(...).Save(...)`
4. Run PowerShell via WSL's `/mnt/c/Windows/System32/cmd.exe /c "powershell ..."`
5. Analyze resulting PNG with `vision_analyze`

This is required because the ladder logic is embedded as vector images with no extractable text.

## I/O Reaction Alarm Watcher (May 2026)
A background engine monitors every PLC output transition and verifies expected input sensors react within **1.0 second**. If not, a deduplicated fault alarm is raised.

### Architecture
- `IOAlarmWatcher.check(io_values)` called synchronously inside `_on_poll_complete()` — no extra threads
- 55 alarm pairs loaded from `catalog/io_alarm_pairs.json`
- Each pair defines: `output_physical`, `on_inputs_physical` (expected HIGH when output turns ON), `off_inputs_physical` (expected HIGH when output turns OFF)
- `_PendingCheck` tracks deadline per transition; composite `fault_key` prevents duplicate spam
- `watcher.clear()` on disconnect to avoid phantom alarms across reconnections

### Critical Tag Format Pitfall
Physical Micro870 I/O tags use **zero-padded two-digit suffixes**:
- ✅ `_IO_X1_DI_01` through `_IO_X1_DI_19`
- ✅ `_IO_X3_DO_00` through `_IO_X3_DO_15`
- ❌ `_IO_X1_DI_1` (non-padded) — **silently fails to match** live values

The initial JSON mapping used non-padded tags and the watcher never fired. Regenerating with `f"_IO_X1_DI_{n:02d}"` fixed it.

## Recent Bug Fixes
| Commit | What | Why |
|---|---|---|
| `7f8f217` | Removed `self._poll_worker.set_timer_names(timer_names)` | Orphaned reference after Programs tab removal caused `NameError` |
| `fef8191` | Widened sidebar 180→200px; restored 🔴 emoji | 🔴 was clipped at 180px |
| `93d8023` | I/O Reaction Alarm Watcher + 55 alarm pairs | Real-time output→input timeout validation with deduplication |
| `4c34aee` | Bundled `io_alarm_pairs.json` in PyInstaller `datas` | EXE loaded 0 pairs — permanently silent |
| `4c34aee` | Reset `_fault_keys` on reconnect | Dedup suppressed all repeated alarms across reconnects |
| `2c90754` | Poll alarm suppression: 4 consecutive failures | Single read errors on tab switch spammed Alarms & Logs |
| `10:36` | Fail-safe read policy by direction | INPUT→False on failure (sensor alarm), OUTPUT→cached (no flicker) |
| `10:36` | Alarm detail dialog (double-click row) | QTableWidget truncated long alarm messages — couldn't read full text |

## Known Issues & Behaviors

### Poll Error "Spam" When Switching Tabs
When the user switches to the Diagnostics tab, a **one-off** pycomm3 read may fail (contention between poll cycle and tab-initiated read). Before `2c90754`, this fired an alarm immediately on a single error. After `2c90754`, only 4+ consecutive errors alarm.

### Timeout Button Label
The timeout control is labeled **`Apply`** (not Accept). Located in the ALARM SETTINGS group inside the Diagnostics tab. A `QLabel` displays the current timeout after it is applied.

### Output Forcing vs. True Force
App writes in Run mode are **not true forces** — the PLC ladder overwrites OTE coils every scan. For troubleshooting a down machine, the correct workflow is:
1. **Program mode** (front panel button or CCW)
2. App toggle → tag writes stick → verify physical solenoid
3. **Run mode** to resume production

### "Both Sensors OFF But No Alarm" — Root Cause
When a sensor is unplugged and the poller hits a read error, the *old* code preserved the last-known TRUE value for ALL tags (inputs and outputs alike). The alarm watcher saw sensor = TRUE and did not fire. The fix (`10:36`) forces INPUT/STATUS tags to `False` on read failure while keeping OUTPUT tags cached.

---

## Build Environment
- WSL Ubuntu
- Python 3.14 (Windows build), 3.11 (WSL dev/test)
- PySide6, pycomm3, texttable, py7zr
- Build: `/mnt/c/Users/thadd/AppData/Local/Programs/Python/Python314/python.exe build_exe.py`
- Output: `dist/Degater PLCTool BST33 and 35.exe`