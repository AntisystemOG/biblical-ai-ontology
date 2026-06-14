#Requires -RunAsAdministrator
# Stop-Bloatware.ps1 - One-click service cleanup
# Place shortcut on desktop pointing to this script

$ErrorActionPreference = 'Stop'

$ServicesToDisable = @(
    # Dell bloatware (major memory hogs)
    "SupportAssistAgent"           # ~380MB
    "DellTechHub"                  # ~87MB + sub-agents
    "DellClientManagementService"  # Dell WMI provider
    
    # Intel DSA (optional driver updater)
    "DSAService"                   # ~108MB
    "DSAUpdateService"             # Updater service
    
    # Intel telemetry
    "esrv_svc"                     # ~216MB
    "ESRV_SVC_QUEENCREEK"
    "SystemUsageReportSvc_QUEENCREEK"
    "SurSvc"                       # SupportAssist sub-service
)

$BackupPath = "$env:USERPROFILE\.openclaw\service-backup.json"

# Ensure backup dir exists
New-Item -ItemType Directory -Path (Split-Path $BackupPath) -Force | Out-Null

# Check for existing backup (prevent double-run)
if (Test-Path $BackupPath) {
    $choice = Read-Host "Services already disabled. Restore them? (y/N)"
    if ($choice -match '^[Yy]') {
        $backups = Get-Content $BackupPath | ConvertFrom-Json
        foreach ($b in $backups) {
            try {
                Set-Service -Name $b.Name -StartupType $b.StartType -ErrorAction SilentlyContinue
                if ($b.Status -eq 'Running') { Start-Service -Name $b.Name -ErrorAction SilentlyContinue }
                Write-Host "Restored: $($b.Name)" -ForegroundColor Green
            } catch {}
        }
        Remove-Item $BackupPath -Force
        Write-Host "`nServices restored. Press any key to exit..." -ForegroundColor Cyan
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        exit
    } else {
        exit
    }
}

Write-Host "Stopping bloatware services..." -ForegroundColor Cyan
Write-Host "(Saves ~1.6GB RAM)`n" -ForegroundColor Gray

$backups = @()
$stopped = 0

foreach ($svcName in $ServicesToDisable) {
    $svc = Get-Service -Name $svcName -ErrorAction SilentlyContinue
    if (-not $svc) { continue }
    
    $backups += @{
        Name = $svc.Name
        Status = $svc.Status.ToString()
        StartType = $svc.StartType.ToString()
    }
    
    try {
        if ($svc.Status -eq 'Running') {
            Stop-Service $svc.Name -Force
            $stopped++
        }
        Set-Service $svc.Name -StartupType Disabled
        Write-Host "  STOPPED: $($svc.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "  FAILED:  $($svc.Name) - $_" -ForegroundColor Red
    }
}

# Kill any lingering Dell processes
Write-Host "`nCleaning up processes..." -ForegroundColor Cyan
$dellProcs = Get-Process | Where-Object { 
    $_.Company -match 'Dell' -or 
    $_.Name -match 'Dell\.(TechHub|CoreServices|UCA|Update|TechHub\..*)' 
} -ErrorAction SilentlyContinue

foreach ($proc in $dellProcs) {
    try {
        $proc | Stop-Process -Force
        Write-Host "  KILLED: $($proc.Name)" -ForegroundColor Green
    } catch {}
}

# Save backup
$backups | ConvertTo-Json -Depth 3 | Set-Content $BackupPath

Write-Host "`nDone! Services disabled." -ForegroundColor Cyan
Write-Host "Backup saved to: $BackupPath" -ForegroundColor Gray
Write-Host "Run again to restore services.`n" -ForegroundColor Gray
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
