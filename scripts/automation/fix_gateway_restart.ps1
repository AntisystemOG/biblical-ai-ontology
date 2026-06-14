$task = Get-ScheduledTask -TaskName 'OpenClaw Gateway'
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$task.Settings = $settings
Set-ScheduledTask -InputObject $task
Write-Host "Done - gateway will now restart up to 3 times on failure, 1 minute apart"
