# Gateway Restart Monitor
# Run this AFTER closing the gateway to detect if it restarts unexpectedly
# Usage: .\gateway-monitor.ps1 -DurationMinutes 60

param(
    [int]$DurationMinutes = 60,
    [string]$LogPath = "$env:USERPROFILE\.openclaw\workspace\logs\gateway-monitor.log"
)

$startTime = Get-Date
$endTime = $startTime.AddMinutes($DurationMinutes)

"=== Gateway Monitor Started at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $LogPath -Append
"Monitoring for $DurationMinutes minutes (until $($endTime.ToString('HH:mm:ss')))" | Out-File -FilePath $LogPath -Append
"" | Out-File -FilePath $LogPath -Append

while ((Get-Date) -lt $endTime) {
    $now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $clawProcess = Get-Process -Name "claw" -ErrorAction SilentlyContinue
    $nodeProcess = Get-Process -Name "node" | Where-Object { $_.CommandLine -like "*openclaw*" } -ErrorAction SilentlyContinue
    $portListening = Test-NetConnection -ComputerName 127.0.0.1 -Port 18789 -WarningAction SilentlyContinue
    
    $status = "CLOSED"
    if ($clawProcess -or $nodeProcess -or $portListening.TcpTestSucceeded) {
        $status = "⚠️ RUNNING"
        
        # Capture process details
        if ($clawProcess) {
            "[$now] ALERT: claw.exe process detected! PID: $($clawProcess.Id), Started: $($clawProcess.StartTime)" | Out-File -FilePath $LogPath -Append
        }
        if ($nodeProcess) {
            "[$now] ALERT: node.exe (openclaw) detected! PID: $($nodeProcess.Id), Started: $($nodeProcess.StartTime)" | Out-File -FilePath $LogPath -Append
        }
        if ($portListening.TcpTestSucceeded) {
            "[$now] ALERT: Port 18789 is LISTENING!" | Out-File -FilePath $LogPath -Append
        }
        
        # Check Task Scheduler
        $nextRun = Get-ScheduledTask -TaskName "*openclaw*" -ErrorAction SilentlyContinue | 
                   Get-ScheduledTaskInfo | 
                   Select-Object -First 1
        if ($nextRun) {
            "[$now] Scheduled Task Found: $($nextRun.TaskName) - Next Run: $($nextRun.NextRunTime)" | Out-File -FilePath $LogPath -Append
        }
        
        # Check Windows Services
        $services = Get-Service | Where-Object { $_.Name -like "*claw*" -or $_.DisplayName -like "*openclaw*" }
        if ($services) {
            foreach ($svc in $services) {
                "[$now] Service Found: $($svc.Name) - Status: $($svc.Status) - StartType: $($svc.StartType)" | Out-File -FilePath $LogPath -Append
            }
        }
        
        # Check startup items
        $startupItems = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue | 
                         Get-Member -MemberType NoteProperty | 
                         Where-Object { $_.Name -like "*claw*" -or $_.Definition -like "*openclaw*" }
        if ($startupItems) {
            "[$now] Startup Item Found in Registry: $($startupItems.Name)" | Out-File -FilePath $LogPath -Append
        }
        
        $startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
        $startupFiles = Get-ChildItem $startupFolder -Filter "*claw*" -ErrorAction SilentlyContinue
        if ($startupFiles) {
            foreach ($file in $startupFiles) {
                "[$now] Startup File Found: $($file.FullName)" | Out-File -FilePath $LogPath -Append
            }
        }
    } else {
        "[$now] Status: CLOSED (no gateway processes detected)" | Out-File -FilePath $LogPath -Append
    }
    
    # Check every 30 seconds
    Start-Sleep -Seconds 30
}

"" | Out-File -FilePath $LogPath -Append
"=== Monitor ended at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $LogPath -Append
"Log saved to: $LogPath"
