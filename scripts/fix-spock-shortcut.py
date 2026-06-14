import os
import sys

try:
    import win32com.client
except ImportError:
    print("pywin32 not installed. Install with: pip install pywin32")
    sys.exit(1)

desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
bat_path = os.path.join(desktop, "Start Hermes WebUI.bat")
icon_path = os.path.join(desktop, "spock-icon.ico")
lnk_path = os.path.join(desktop, "Spock WebUI.lnk")

if not os.path.exists(bat_path):
    print(f"ERROR: Batch file not found: {bat_path}")
    sys.exit(1)

if not os.path.exists(icon_path):
    print(f"ERROR: Icon not found: {icon_path}")
    sys.exit(1)

shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(lnk_path)
shortcut.TargetPath = bat_path
shortcut.WorkingDirectory = desktop
shortcut.IconLocation = icon_path
shortcut.Description = "Start Spock WebUI Server & Open Browser"
shortcut.WindowStyle = 7  # Minimized window
shortcut.Save()

print(f"✓ Created: {lnk_path}")
print(f"  Target: {bat_path}")
print(f"  Icon:   {icon_path}")
