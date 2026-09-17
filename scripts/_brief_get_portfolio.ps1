# Daily brief helper: print latest portfolio CSV content
$dir = "C:\Users\thadd\Desktop\Portfolio Positions"
if (-not (Test-Path $dir)) {
    Write-Output "MISSING_DIR: $dir"
    exit 0
}
$latest = Get-ChildItem -Path $dir -Filter *.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $latest) {
    Write-Output "NO_CSV_FILES"
    exit 0
}
Write-Output "LATEST_FILE: $($latest.FullName)"
Write-Output "LAST_WRITE: $($latest.LastWriteTime)"
Write-Output "---BEGIN---"
Get-Content -Path $latest.FullName -TotalCount 80
Write-Output "---END---"