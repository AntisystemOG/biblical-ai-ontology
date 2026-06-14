# How to Trim Unnecessary Services

## Quick Start

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**

2. **Navigate to the script folder**
   ```powershell
   cd "C:\Users\thadd\OneDrive\Desktop\Spocks Reports"
   ```

3. **Run the trimmer**
   ```powershell
   .\disable_services.ps1
   ```

4. **Verify it worked**
   ```powershell
   .\get_services_status.ps1
   ```

## What Gets Disabled?

| Service | Why Disable? |
|---------|--------------|
| **Adobe ARM Service** | Acrobat auto-updater. Updates can be done manually when needed. |
| **Intel DSA Service** | Driver update checker. Use Windows Update or manual checks instead. |
| **Intel DSA Updater** | Background updater for Intel software. |
| **Intel Dynamic Tuning** | Power/thermal management. Windows handles this fine without it. |
| **Intel System Usage Report** | Telemetry service. Not needed for normal operation. |
| **Intel Energy Server** | Power management reporting. Not essential. |

## Before You Run

### ⚠️ IMPORTANT

- These services are **safe to disable** for most users
- **Do NOT disable** if you rely on Intel Driver & Support Assistant
- Adobe Acrobat will still work — just won't auto-update
- Your drivers won't stop working — Windows Update still handles critical ones

### Memory Savings

Expected savings: **~150-400 MB RAM**
Expected CPU savings: **Less background polling**

## What If Something Breaks?

### Restore Everything

```powershell
# Run as Administrator
cd "C:\Users\thadd\OneDrive\Desktop\Spocks Reports"
.\restore_services.ps1
```

### Restore Individual Service

```powershell
# Run as Administrator
Set-Service -Name "DSAService" -StartupType Automatic
Start-Service -Name "DSAService"
```

## How to Check Current Status

```powershell
# Quick check
.\get_services_status.ps1

# Full service list
Get-Service | Where-Object {$_.Status -eq 'Running'} | Sort-Object DisplayName
```

## Services That Are SAFE to Keep Disabled

These are background updaters/telemetry that don't affect functionality:

- ✅ Adobe ARM (manual updates still work)
- ✅ Intel DSA (drivers still work)
- ✅ Intel telemetry/reporting services
- ✅ Most "helper" services from hardware vendors

## Services You Should NOT Disable

Don't touch these without knowing what you're doing:

- ❌ Windows Defender services
- ❌ Audio services (Windows Audio)
- ❌ Network services (DHCP Client, DNS Client)
- ❌ Storage services
- ❌ Critical Windows services

## Troubleshooting

### "Access Denied" Error

You didn't run as Administrator. Close PowerShell and reopen as Admin.

### Service Still Running After Script

Some services restart themselves. Check again after reboot:

```powershell
.\get_services_status.ps1
```

### Want Updates Back?

Run `restore_services.ps1` to re-enable everything.

## Questions?

Ask Spock. He'll help.

---

**Created:** May 2, 2026  
**Last Updated:** May 2, 2026  
**Files in this folder:**
- `disable_services.ps1` - The main trimmer script
- `get_services_status.ps1` - Check what's running
- `restore_services.ps1` - Undo changes (auto-created)
- `HOW_TO_TRIM_SERVICES.md` - This file