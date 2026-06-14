$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut('C:\Users\thadd\Desktop\Spock WebUI.lnk')
$shortcut.TargetPath = 'C:\Users\thadd\Desktop\Start Hermes WebUI.bat'
$shortcut.WorkingDirectory = 'C:\Users\thadd\Desktop'
$shortcut.IconLocation = 'C:\Users\thadd\Desktop\spock-icon.ico,0'
$shortcut.Description = 'Start Spock WebUI Server & Open Browser'
$shortcut.WindowStyle = 7
$shortcut.Save()
Write-Host "Shortcut fixed - now starts server + opens browser" -ForegroundColor Green
