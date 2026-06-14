# cleanup-services.ps1
# Stops and disables unnecessary background services
# Run as Administrator

param(
    [switch]$DryRun,
    [switch]$Restore
)

$ServicesToDisable = @(
    # Dell Bloatware
    "SupportAssistAgent"
    "DellTechHub"
    "DellClientManagementService"
    
    # Intel Driver & Support Assistant (optional - checks for driver updates)
    "DSAService"
    "DSAUpdateService"
    
    # Intel Energy Server (telemetry)
    "esrv_svc"
    "ESRV_SVC_QUEENCREEK"
    
    # Dell SupportAssist sub-service
    "SurSvc"
    
    # Intel System Usage Report (telemetry)
    "SystemUsageReportSvc_QUEENCREEK"
)

$BackupFile = "$env:TEMP\disabled-services-backup.json"

function Stop-And-Disable {
    param($serviceName)
    
    $svc = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if (-not $svc) {
        Write-Host "  [SKIP] $serviceName not found" -ForegroundColor Gray
        return
    }
    
    $status = $svc.Status
    $startType = $svc.StartType
    
    if ($DryRun) {
        Write-Host "  [DRY-RUN] Would stop/disable: $serviceName (currently: $status, $startType)" -ForegroundColor Yellow
        return @{ Name = $serviceName; Status = $status; StartType = $startType }
    }
    
    # Backup current state
    $backup = @{ Name = $serviceName; Status = $status; StartType = $startType }
    
    try {
        if ($svc.Status -eq 'Running') {
            Stop-Service -Name $serviceName -Force -ErrorAction Stop
            Write-Host "  [STOPPED] $serviceName" -ForegroundColor Green
        }
        
        Set-Service -Name $serviceName -StartupType Disabled -ErrorAction Stop
        Write-Host "  [DISABLED] $serviceName" -ForegroundColor Green
        
        return $backup
    }
    catch {
        Write-Host "  [ERROR] Failed to disable $serviceName`: $_" -ForegroundColor Red
        return $null
    }
}

# Main
Write-Host "`n=== Service Cleanup Script ===" -ForegroundColor Cyan
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN (no changes)' } elseif ($Restore) { 'RESTORE' } else { 'LIVE' })`n"

if ($Restore) {
    if (-not (Test-Path $BackupFile)) {
        Write-Host "ERROR: No backup file found at $BackupFile" -ForegroundColor Red
        exit 1
    }
    
    $backups = Get-Content $BackupFile | ConvertFrom-Json
    Write-Host "Restoring services from backup...`n" -ForegroundColor Cyan
    
    foreach ($b in $backups) {
        try {
            Set-Service -Name $b.Name -StartupType $b.StartType
            if ($b.Status -eq 'Running') {
                Start-Service -Name $b.Name
            }
            Write-Host "  [RESTORED] $($b.Name) -> $($b.StartType)" -ForegroundColor Green
        }
        catch {
            Write-Host "  [ERROR] Failed to restore $($b.Name): $_" -ForegroundColor Red
        }
    }
    
    Remove-Item $BackupFile -ErrorAction SilentlyContinue
    Write-Host "`nDone. Backup file removed." -ForegroundColor Cyan
}
else {
    # Stop and disable
    $backups = @()
    $saved = 0
    
    foreach ($svc in $ServicesToDisable) {
        $result = Stop-And-Disable $svc
        if ($result) {
            $backups += $result
            $saved++
        }
    }
    
    if (-not $DryRun -and $saved -gt 0) {
        $backups | ConvertTo-Json | Set-Content $BackupFile
        Write-Host "`nBackup saved to: $BackupFile" -ForegroundColor Cyan
        Write-Host "To restore: .\cleanup-services.ps1 -Restore" -ForegroundColor Yellow
    }
    
    # Kill lingering Dell processes
    if (-not $DryRun) {
        Write-Host "`nKilling lingering Dell processes..." -ForegroundColor Cyan
        $processes = @('Dell.TechHub*', 'Dell.CoreServices*', 'Dell.UCA*', 'Dell.Update*')
        foreach ($p in $processes) {
            Get-Process -Name $p -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
            if ($?) { Write-Host "  [KILLED] $p" -ForegroundColor Green }
        }
    }
    
    Write-Host "`n=== Done ===" -ForegroundColor Cyan
    Write-Host "Run again with -DryRun to preview changes" -ForegroundColor Gray
}
