' gateway_watchdog_launcher.vbs - hidden launcher for the gateway watchdog (no console flash).
' Task Scheduler allocates a console window for powershell.exe before -WindowStyle Hidden
' can apply; launching via WScript.Shell.Run(..., 0, True) creates the window hidden from
' the start. Same pattern as gateway.vbs -> gateway.cmd. True = wait, so the task instance
' spans the full script run and MultipleInstances IgnoreNew keeps overlap protection.
CreateObject("WScript.Shell").Run "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\thadd\.openclaw\workspace\scripts\gateway_watchdog.ps1""", 0, True