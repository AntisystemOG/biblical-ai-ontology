' load_governor_launcher.vbs - hidden launcher for the OpenClaw Load Governor (no console flash).
' Same pattern as gateway.vbs / gateway_watchdog_launcher.vbs: WScript.Shell.Run(..., 0, True)
' creates the PowerShell console hidden from the start instead of flashing it every 5 minutes.
CreateObject("WScript.Shell").Run "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\thadd\.openclaw\workspace\scripts\load_governor.ps1""", 0, True