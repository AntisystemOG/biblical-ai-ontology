# Ladder Logic Analysis from Python Codebase

When the `.l5x`, `.acd`, or ladder export is not in the repository, you can still determine whether manual output writes will work by tracing the full signal chain in the Python code and knowing what to verify in the PLC program.

## Full Signal Chain in the Degater Project

```
ManualControlWidget._on_on_clicked()
    → emits output_forced(tag_name, True)
        → DegaterIOTab.output_forced
            → IOStatusTab.output_force_requested
                → MainWindow._on_output_force()
                    → driver.write_tag(physical_tag, forced_value)
                        → micro800_driver.write_tag()
                            → CIPDriver.write((tag_name, value))
                                → PLC tag updated via CIP over EtherNet-IP
```

After the CIP write completes, the PLC ladder logic executes its next scan cycle. If the ladder rung driving that output evaluates to a state that conflicts with the manual write, the PLC overwrites it.

## What to Verify in the PLC Program

1. **Open the ladder in CCW / RSLogix**
2. **Find the output tag** (e.g., `Output_Deg1_FeedSol`)
3. **Check for a mode bypass contact**
   - Look for `XIO DEG_MAN_AUTO` in series with the auto rung
   - When `DEG_MAN_AUTO = FALSE` (manual mode), the auto rung should break
4. **Check for a manual override rung**
   - May use `XIC DEG_MAN_AUTO` or a dedicated manual bit
   - May use `OTL`/`OTU` (latch/unlatch) to hold manual state across scans
5. **Check coil type**
   - `OTE` (output energize) → rewritten every scan; needs bypass
   - `OTL`/`OTU` → holds state; safer for manual override

## Common Patterns and Outcomes

| Ladder Pattern | Manual Write Result |
|---|---|
| **Auto rung broken by `XIO DEG_MAN_AUTO` NC contact** | ✅ Clean — auto disables in manual; manual branch active |
| **Manual branch has `XIC DEG_MAN_AUTO` NC + physical PB in series** | ✅ Clean — requires switch + PB; app writes bypass this entirely |
| **Separate manual rung with `OTL` coil** | ✅ Clean — manual state latches across scans |
| **No mode contact at all** | ❌ Fight — auto evaluates every scan |
| `OTE` coil only, no bypass | ❌ Fight — overwritten every scan |

## Real-World Case: Degater BST33/35 D14 Program (177 Rungs)

Discovered by analyzing a `.docx` ladder export containing 266 EMF images (one per rung):

### Output Control Rung Structure (e.g., rung 54/55)
Three parallel branches feeding an OTE coil:

| Branch | Contacts | Purpose |
|---|---|---|
| **Top (Auto)** | `USER_BIT_32` + `TON_24.Q` in series | Auto sequence drives output |
| **Middle (Manual)** | `]/[ DEG_MAN_AUTO` (NC) + `Home All Manual PB` (NO) in series | Manual path when `DEG_MAN_AUTO = FALSE` |
| **Bottom (Override)** | `USER_BIT_79` / `KM Request Home` (NO) | Homing override |
| → **Coil** | `OTE Output_Deg2_UpperCutSol` (or similar) | Standard output energize |

### Critical Finding: DEG_MAN_AUTO is Normally Closed (NC)
- **Contact symbol:** `]/[` (NC, not NO)
- `DEG_MAN_AUTO = TRUE` (Auto mode) → NC contact **OPENS** → manual branch blocked
- `DEG_MAN_AUTO = FALSE` (Manual mode) → NC contact **CLOSES** → manual path enabled
- **Physical button required:** `Home All Manual PB` must also be pressed

### OTE Coil Problem for App Writes
The outputs use OTE `( )` coils — **not OTL/OTU** latches. OTE is re-evaluated and overwritten every PLC scan.

| PLC Mode | App writes behavior |
|---|---|
| **Run mode** | App writes `IO_X4_DO_07 = TRUE`. Next scan, ladder evaluates auto branch (FALSE if manual), writes FALSE back. **Output flickers.** |
| **Program mode** | Ladder still evaluates but OTE does NOT drive physical I/O. App writes **stick** — no overwrite. Safe for troubleshooting. |

### Solenoid Outputs Found in the Program
All solenoid names use pattern `Output_Deg{d}_{name}Sol`:
- `Output_Deg1_FeedSol`
- `Output_Deg2_JustifySol`
- `Output_Deg2_UpperCutSol`
- `Output_Deg2_LowerCutSol`
- `Output_Deg2_GripSol`
- `Output_Deg2_NipperSol`
- `Output_Deg2_ExtendSol`
- `Output_Deg2_RetractSol`
- *(etc. — full set of 22 DEG1 + DEG2 outputs)*

### Verdict for the Degater Project
**Can the app reliably toggle outputs?** — **NO** in Run mode, **YES** in Program mode.
- The ladder has a manual path, but it requires the physical `Home All Manual PB` — the app bypasses this requirement.
- The OTE coil means the ladder overwrites app-written values every scan.
- **Program mode** disables physical I/O driving, so app writes "stick." This is the correct troubleshooting approach.

## How to Analyze Ladder EMF Diagrams from .docx Export

When the PLC programmer provides a `.docx` file with embedded EMF ladder images:

1. **Extract the .docx** (it's a ZIP):
   ```bash
   python3 -m zipfile -e ladder.docx extracted/
   # Images are at: extracted/word/media/*.emf
   ```

2. **Convert EMF to PNG using PowerShell from WSL** (since pypdf/libreoffice can't handle EMF):
   ```bash
   # Copy EMF to Windows temp
   cp extracted/word/media/image75.emf /mnt/c/Users/$USER/AppData/Local/Temp/
   
   # Run PowerShell to convert
   /mnt/c/Windows/System32/cmd.exe /c "powershell -ExecutionPolicy Bypass -File C:\\Users\\$USER\\AppData\\Local\\Temp\\convert_emf.ps1"
   ```

3. **PowerShell conversion script** (`convert_emf.ps1`):
   ```powershell
   Add-Type -AssemblyName System.Drawing
   $emf = [System.Drawing.Imaging.Metafile]::FromFile("C:\Users\$USER\AppData\Local\Temp\image75.emf")
   $emf.Save("C:\Users\$USER\AppData\Local\Temp\rung75.png", [System.Drawing.Imaging.ImageFormat]::Png)
   $emf.Dispose()
   ```

4. **Analyze with vision_analyze** — ask the assistant to read the ladder rung and identify:
   - Contact types (NO `[-]`, NC `]/[`)
   - Coil type (OTE `( )`, OTL `(L)`, OTU `(U)`)
   - Tag names on each element
   - Parallel branches vs. series elements
   - Presence of `DEG_MAN_AUTO` or similar mode contacts

## Key Takeaway

> The app does not perform a true PLC "force." It performs a plain tag write. Whether the output stays in the forced state depends entirely on whether the ladder logic is structured to accept manual writes when `DEG_MAN_AUTO` is `FALSE`.
>
> **For troubleshooting a down machine: Program mode is the correct approach.** Switch to Program mode (front panel button or CCW), then use the app to write outputs directly. The ladder logic still runs but does not drive physical outputs — app writes "stick."
>
> **Cannot accidentally change the program** — direct tag writes only change data values, never ladder instructions. Only CCW download operations can modify the program.