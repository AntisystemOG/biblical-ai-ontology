$Wsh = New-Object -ComObject WScript.Shell
$Lnk = $Wsh.CreateShortcut('C:\Users\thadd\Desktop\Hermes WebUI.lnk')
$Lnk.TargetPath = 'C:\Windows\System32\wsl.exe'
$Lnk.Arguments = 'bash -c "cd /mnt/c/Users/thadd/hermes-web-ui \u0026\u0026 node bin/hermes-web-ui.mjs start"'
$Lnk.IconLocation = 'C:\Users\thadd\hermes-web-ui\packages\client\public\favicon.ico,0'
$Lnk.WorkingDirectory = 'C:\Users\thadd\hermes-web-ui'
$Lnk.Description = 'Launch Hermes Web UI (port 8648)'
$Lnk.Save()
Write-Host 'Shortcut created'
