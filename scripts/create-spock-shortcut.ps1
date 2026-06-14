# Create Spock WebUI shortcut with icon
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut('C:\Users\thadd\Desktop\Spock WebUI.lnk')
$shortcut.TargetPath = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$shortcut.Arguments = 'http://172.24.60.180:8648/'
$shortcut.IconLocation = 'C:\Users\thadd\Desktop\spock-icon.ico'
$shortcut.Description = 'Spock WebUI - Hermes Agent Interface'
$shortcut.WorkingDirectory = 'C:\Users\thadd\Desktop'
$shortcut.Save()
Write-Host "✓ Spock WebUI shortcut created on Desktop" -ForegroundColor Green
