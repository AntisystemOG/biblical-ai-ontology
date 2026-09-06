# Gateway Watchdog Launcher
# Usage: .\scripts\gateway-watchdog.ps1
# Or: powershell -File .\scripts\gateway-watchdog.ps1

param(
    [switch]$CheckOnly,
    [switch]$AutoFix,
    [switch]$Silent
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logFile = "$env:USERPROFILE\.openclaw\workspace\logs\gateway-health.log"

# Ensure log directory exists
$logDir = Split-Path $logFile -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry
    if (-not $Silent) {
        switch ($Level) {
            "ERROR" { Write-Host $logEntry -ForegroundColor Red }
            "WARN"  { Write-Host $logEntry -ForegroundColor Yellow }
            "OK"    { Write-Host $logEntry -ForegroundColor Green }
            default { Write-Host $logEntry }
        }
    }
}

function Check-GatewayStatus {
    Write-Log "Checking gateway status..."
    try {
        $status = openclaw status 2>&1
        if ($status -match "running|ready") {
            Write-Log "Gateway is RUNNING" "OK"
            return $true
        } else {
            Write-Log "Gateway appears STOPPED or not responding" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Failed to check gateway status: $_" "ERROR"
        return $false
    }
}

function Check-CronHealth {
    Write-Log "Checking cron job health..."
    try {
        $cronList = openclaw cron list --json 2>&1 | ConvertFrom-Json
        $total = $cronList.jobs.Count
        $enabled = ($cronList.jobs | Where-Object { $_.enabled }).Count
        $disabled = $total - $enabled
        $recentErrors = $cronList.jobs | Where-Object { $_.state.lastRunStatus -eq "error" }
        
        Write-Log "Total cron jobs: $total ($enabled enabled, $disabled disabled)"
        
        if ($recentErrors) {
            Write-Log "Jobs with recent errors: $($recentErrors.Count)" "WARN"
            foreach ($job in $recentErrors) {
                Write-Log "  - $($job.name): $($job.state.lastError)" "WARN"
            }
        } else {
            Write-Log "No recent cron errors" "OK"
        }
        
        return $recentErrors
    } catch {
        Write-Log "Failed to check cron health: $_" "ERROR"
        return @()
    }
}

function Check-Sessions {
    Write-Log "Checking session health..."
    try {
        # This would need to be run via OpenClaw - checking is limited from PowerShell
        Write-Log "Session check requires OpenClaw API access" "WARN"
        return @()
    } catch {
        Write-Log "Failed to check sessions: $_" "ERROR"
        return @()
    }
}

function Check-DiskSpace {
    Write-Log "Checking disk space..."
    try {
        $workspaceDrive = (Get-Item $env:USERPROFILE).PSDrive
        $freeGB = [math]::Round($workspaceDrive.Free / 1GB, 2)
        $totalGB = [math]::Round(($workspaceDrive.Free + $workspaceDrive.Used) / 1GB, 2)
        $percentFree = [math]::Round(($freeGB / $totalGB) * 100, 1)
        
        Write-Log "Disk space: $freeGB GB free of $totalGB GB ($percentFree%)"
        
        if ($percentFree -lt 10) {
            Write-Log "LOW DISK SPACE - Only $percentFree% remaining!" "ERROR"
        } elseif ($percentFree -lt 20) {
            Write-Log "Disk space getting low - $percentFree% remaining" "WARN"
        } else {
            Write-Log "Disk space OK" "OK"
        }
        
        return $percentFree
    } catch {
        Write-Log "Failed to check disk space: $_" "ERROR"
        return 0
    }
}

function Check-LogSizes {
    Write-Log "Checking log file sizes..."
    try {
        $logPath = "$env:USERPROFILE\.openclaw\logs"
        if (Test-Path $logPath) {
            $logs = Get-ChildItem $logPath -File | Sort-Object Length -Descending | Select-Object -First 5
            $totalSize = (Get-ChildItem $logPath -File | Measure-Object -Property Length -Sum).Sum
            $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
            
            Write-Log "Total log size: $totalSizeMB MB"
            
            foreach ($log in $logs) {
                $sizeMB = [math]::Round($log.Length / 1MB, 2)
                if ($sizeMB -gt 100) {
                    Write-Log "  Large log: $($log.Name) ($sizeMB MB)" "WARN"
                }
            }
        }
    } catch {
        Write-Log "Failed to check log sizes: $_" "WARN"
    }
}

# Main execution
Write-Log "=== Gateway Watchdog Started ==="

$issues = @()

# Run checks
$gatewayOk = Check-GatewayStatus
if (-not $gatewayOk) { $issues += "Gateway not running" }

$cronErrors = Check-CronHealth
if ($cronErrors.Count -gt 0) { $issues += "$($cronErrors.Count) failed cron jobs" }

$sessions = Check-Sessions

$diskFree = Check-DiskSpace
if ($diskFree -lt 10) { $issues += "Low disk space ($diskFree%)" }

Check-LogSizes

# Summary
Write-Log "=== Watchdog Complete ==="
if ($issues.Count -eq 0) {
    Write-Log "✅ All systems healthy" "OK"
} else {
    Write-Log "⚠️  Found $($issues.Count) issue(s):" "WARN"
    foreach ($issue in $issues) {
        Write-Log "   - $issue" "WARN"
    }
}

# Offer auto-fix if requested and issues found
if ($AutoFix -and $issues.Count -gt 0) {
    Write-Log "Auto-fix requested but requires OpenClaw approval" "WARN"
}

# Always log completion
Write-Log "Watchdog run complete"

# Return exit code for automation
exit ($issues.Count)
