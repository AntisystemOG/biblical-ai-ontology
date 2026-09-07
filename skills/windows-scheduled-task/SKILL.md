---
name: "windows-scheduled-task"
description: "Scheduled task flashes a powershell window; create, re-register, or update Windows scheduled tasks that run scripts - hidden WScript launcher procedure"
---

# Windows Scheduled Task Script Launcher

## When to use
- A scheduled task flashes/pops a PowerShell console window on every run.
- Creating or re-registering a Windows scheduled task that runs a PowerShell script.
- Swapping a scheduled task's action without disturbing its trigger/settings.

## Why this pattern exists
Task Scheduler allocates the console window BEFORE powershell.exe parses `-WindowStyle Hidden`, so a direct `powershell.exe` action flashes a window on every run. Launching PowerShell through WScript with `WScript.Shell.Run ..., 0, True` creates the window hidden from the first millisecond and keeps the task instance spanning the script run.

## Steps

1. Inspect the task: run `schtasks /query /tn "<name>" /fo LIST /v` and read Task To Run, Repeat cadence, Power Management, and Logon Mode. A direct `powershell.exe ... -File` action is the flash cause; "No Start On Batteries" is a silent-failure cause on laptop hosts. Completion: cadence, action, and power restrictions known.

2. Write a hidden launcher `<script>_launcher.vbs` next to the target script in scripts/:
   `CreateObject("WScript.Shell").Run "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""<absolute script path>""", 0, True`
   - `0` = window hidden from the start (kills the flash); `True` = wait, so the task instance spans the script run and MultipleInstances IgnoreNew keeps overlap protection.
   - Double the quotes around the script path (VBS string escaping).
   Completion: launcher file exists and quotes/paths are exact.

3. Point the task at the launcher:
   - Full re-register (task you own and can rebuild): run the task's setup .ps1 using `Register-ScheduledTask -Force`; battery-safe laptop settings: `-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)`.
   - In-place swap (must not disturb trigger/settings/principal): `$a = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument '//B "<launcher path>"'; Set-ScheduledTask -TaskName "<name>" -Action $a`.
   - `//B` suppresses wscript script-error dialogs.
   - Any snippet using variables goes into a .ps1 file first - inline exec strips PowerShell $-variables on this host.
   Completion: `schtasks /query /v` shows `wscript.exe //B "<launcher>"` as Task To Run.

4. Test and verify: trigger a run (`Start-ScheduledTask` or the setup script's built-in test run), then query Last Run Time/Last Result (expect 0) and confirm the guarded service stayed healthy (e.g., curl its health endpoint). Last Result is wscript's exit code - PowerShell exit codes are NOT propagated through the launcher; treat the script's own log file as the failure signal. Completion: Result 0 recorded and service verified healthy.
