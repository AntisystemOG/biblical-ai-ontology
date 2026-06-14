$ErrorActionPreference = "Continue"
$body = @{
    model = "mistral"
    prompt = Get-Content "temp_stock_analysis.txt" -Raw
    stream = $false
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    Write-Output $response.response
} catch {
    Write-Output "Error: $_"
    Write-Output $_.Exception.Response
}
