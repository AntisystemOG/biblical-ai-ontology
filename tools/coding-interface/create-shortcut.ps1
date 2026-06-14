# Create Desktop Shortcut for Coder Interface
$WshShell = New-Object -ComObject WScript.Shell

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Coder Interface.lnk"
$BatchPath = "C:\Users\thadd\.openclaw\workspace\tools\coding-interface\start-coder.bat"

# Create the shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $BatchPath
$Shortcut.WorkingDirectory = "C:\Users\thadd\.openclaw\workspace\tools\coding-interface"
$Shortcut.WindowStyle = 1
$Shortcut.Description = "OpenClaw Coder Interface"
$Shortcut.IconLocation = "powershell.exe,0"

$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $ShortcutPath" -ForegroundColor Cyan
