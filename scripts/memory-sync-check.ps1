# Memory Sync Check Script
# Runs on gateway start to verify daily memory sync

$date = Get-Date -Format "yyyy-MM-dd"
$markerFile = "C:\Users\thadd\.openclaw\workspace\.memory-sync-marker"
$workspaceDir = "C:\Users\thadd\.openclaw\workspace"

# Check if sync was done today
$lastSync = $null
if (Test-Path $markerFile) {
    $lastSync = Get-Content $markerFile -Raw
}

if ($lastSync -eq $date) {
    Write-Output "Memory sync already done today ($date)"
    exit 0
}

# Sync hasn't been done today - check for today's memory file
$todayMemory = Join-Path $workspaceDir "memory\$date.md"
if (Test-Path $todayMemory) {
    Write-Output "Found today's memory file: $todayMemory"
    Write-Output "ACTION NEEDED: Review memory file and update MEMORY.md"
    Write-Output "Then run: git add . && git commit -m 'daily memory sync' && git push"
} else {
    Write-Output "No memory file for today yet: $todayMemory"
}

Write-Output "Reminder: Daily memory sync required!"
