$latest = "C:\Users\thadd\Desktop\Portfolio Positions\Portfolio_Positions_Jul-31-2026 (1).csv"
$lines = Get-Content -Path $latest
Write-Output ("TOTAL_LINES: " + $lines.Count)
$lines | Select-Object -Skip 39 | ForEach-Object { $_ }