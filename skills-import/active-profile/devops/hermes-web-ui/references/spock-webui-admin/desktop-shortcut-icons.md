# Desktop Shortcut Icons (Spock WebUI)

Thad's desktop has three shortcuts related to the Hermes WebUI. When "icons are
messed up" is reported, the `.lnk` files may have reverted to generic Windows
icons after an OpenClaw uninstall/reinstall or a Windows icon cache reset.

## Shortcuts to Manage

| Shortcut File | Target | Expected Icon |
|---------------|--------|---------------|
| `Launch Hermes WebUI.lnk` | `Launch Hermes WebUI.bat` | `spock-icon.ico` |
| `Start Hermes Watchdog.lnk` | `Hermes\Start Hermes Watchdog.bat` | `spock-icon.ico` |
| `Stop Hermes Watchdog.lnk` | `Hermes\Stop Hermes Watchdog.bat` | `spock-icon.ico` |

The icon source file is at `C:\Users\thadd\Desktop\spock-icon.ico` (2 sizes: 16×16
and 32×32 PNG inside an ICO container).

## Setting the Icon from WSL

Use PowerShell `-Command` with **escaped `\$`** so bash doesn't interpolate
PowerShell variables as empty strings.

```bash
# Single shortcut — update icon only
powershell.exe -Command "\
  \$WshShell = New-Object -ComObject WScript.Shell; \
  \$lnk = \$WshShell.CreateShortcut('C:\\Users\\thadd\\Desktop\\Launch Hermes WebUI.lnk'); \
  \$lnk.IconLocation = 'C:\\Users\\thadd\\Desktop\\spock-icon.ico,0'; \
  \$lnk.Save()"
```

**Verify the change:**
```bash
powershell.exe -Command "\
  \$WshShell = New-Object -ComObject WScript.Shell; \
  \$lnk = \$WshShell.CreateShortcut('C:\\Users\\thadd\\Desktop\\Launch Hermes WebUI.lnk'); \
  Write-Output ('Icon: ' + \$lnk.IconLocation)"
```

Expected output: `Icon: C:\Users\thadd\Desktop\spock-icon.ico,0`

## Bulk Icon Refresh

When multiple shortcuts need the same icon, run all three in sequence:

```bash
for name in "Launch Hermes WebUI" "Start Hermes Watchdog" "Stop Hermes Watchdog"; do
  powershell.exe -Command "\
    \$WshShell = New-Object -ComObject WScript.Shell; \
    \$lnk = \$WshShell.CreateShortcut('C:\\Users\\thadd\\Desktop\\${name}.lnk'); \
    \$lnk.IconLocation = 'C:\\Users\\thadd\\Desktop\\spock-icon.ico,0'; \
    \$lnk.Save()"
done
```

## Why `.bat` Files Can't Have Custom Icons

Windows `.bat` files always display the generic batch-file icon. To show a custom
icon, create a `.lnk` shortcut that points to the `.bat`, then set
`IconLocation` on the `.lnk`.

## Icon Cache Refresh

If the desktop still shows the old icon after updating `.lnk` files, the Windows
icon cache needs refreshing. The user can press `F5` on the desktop or restart
Explorer. From PowerShell (admin):

```powershell
# Kill and restart Explorer to clear icon cache
Stop-Process -Name explorer -Force
Start-Process explorer
```
