$task = Get-ScheduledTask -TaskName "OpenClaw Gateway"
$task.Settings.RestartCount = 3
$task.Settings.RestartInterval = [TimeSpan]::FromMinutes(1)
Register-ScheduledTask -Force -TaskName "OpenClaw Gateway" -InputObject $task
Write-Host "Gateway task updated - will restart 3 times on failure"
