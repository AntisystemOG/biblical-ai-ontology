# Comprehensive Security Check Script
# Runs all security checks for Windows + OpenClaw

Write-Host "🔒 Running Comprehensive Security Check..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 1. BitLocker Status
Write-Host "`n1. 🔐 BitLocker Encryption Status" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
$bitlockerStatus = manage-bde -status C: 2>$null
if ($bitlockerStatus) {
    $bitlockerStatus | Select-String "Conversion Status", "Protection Status"
} else {
    Write-Host "❌ BitLocker not available or access denied" -ForegroundColor Red
}

# 2. Windows Firewall Status
Write-Host "`n2. 🔥 Windows Firewall Status" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow
$firewallStatus = netsh advfirewall show allprofiles
$firewallStatus | ForEach-Object {
    if ($_ -match "State" -or $_ -match "ON" -or $_ -match "OFF") {
        Write-Host $_.Trim()
    }
}

# 3. Windows Defender Status
Write-Host "`n3. 🛡️  Windows Defender Status" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow
$defenderStatus = Get-MpComputerStatus 2>$null
if ($defenderStatus) {
    Write-Host "Antivirus enabled: $($defenderStatus.AMServiceEnabled)"
    Write-Host "Antivirus updated: $($defenderStatus.AntivirusSignatureLastUpdated)"
    Write-Host "Real-time protection: $($defenderStatus.RealTimeProtectionEnabled)"
} else {
    Write-Host "❌ Windows Defender not available" -ForegroundColor Red
}

# 4. Windows Updates
Write-Host "`n4. 🔄 Windows Update Status" -ForegroundColor Yellow
Write-Host "---------------------------" -ForegroundColor Yellow
$updateSession = New-Object -ComObject Microsoft.Update.Session
$updateSearcher = $updateSession.CreateUpdateSearcher()
$searchResult = $updateSearcher.Search("IsInstalled=0")
if ($searchResult.Updates.Count -gt 0) {
    Write-Host "⚠️  Pending updates: $($searchResult.Updates.Count)" -ForegroundColor Yellow
    $searchResult.Updates | Select-Object -First 3 Title
} else {
    Write-Host "✅ No pending updates" -ForegroundColor Green
}

# 5. OpenClaw Status
Write-Host "`n5. 🦞 OpenClaw Gateway Status" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow
$oclStatus = openclaw gateway status 2>$null
if ($oclStatus -and $oclStatus -match "running") {
    Write-Host "✅ OpenClaw gateway is running" -ForegroundColor Green
} else {
    Write-Host "❌ OpenClaw gateway not running" -ForegroundColor Red
}

# 6. Network Information
Write-Host "`n6. 🌐 Network Security Status" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow
$network = Get-NetConnectionProfile
Write-Host "Current network: $($network.Name)"
Write-Host "Network category: $($network.NetworkCategory)"
Write-Host "IPv4 connectivity: $($network.IPv4Connectivity)"

# 7. User Account Info
Write-Host "`n7. 👤 User Account Security" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
Write-Host "Current user: $($currentUser.Name)"
Write-Host "Authentication type: $($currentUser.AuthenticationType)"

Write-Host "`n🔒 Security check completed!" -ForegroundColor Cyan
Write-Host "Review the results above for any security issues." -ForegroundColor Cyan