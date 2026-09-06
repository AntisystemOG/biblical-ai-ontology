# load_governor.ps1 - idle-aware gateway load governor (every 5 min via Task Scheduler)
# Rule: when Thad is actively using the PC (input idle < 5 min) the gateway node
# process is demoted to BelowNormal CPU priority so his apps always win.
# When the PC is idle >= 10 min the gateway returns to Normal (full speed).
# Logs one line only on priority CHANGES.
$ErrorActionPreference = 'SilentlyContinue'

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class GatewayLoadGovernor {
  [StructLayout(LayoutKind.Sequential)]
  public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
  [DllImport("user32.dll")]
  public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
  public static uint IdleSeconds() {
    LASTINPUTINFO lii = new LASTINPUTINFO();
    lii.cbSize = (uint)Marshal.SizeOf(typeof(LASTINPUTINFO));
    if (!GetLastInputInfo(ref lii)) return 0;
    uint now = (uint)Environment.TickCount;
    uint last = lii.dwTime;
    return (now >= last) ? (now - last) / 1000 : 0;
  }
}
"@

$idleSec = [GatewayLoadGovernor]::IdleSeconds()

$gw = Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match 'openclaw' } | Select-Object -First 1
if (-not $gw) { exit 0 }
$p = Get-Process -Id $gw.ProcessId -ErrorAction SilentlyContinue
if (-not $p) { exit 0 }

$target = $null
if ($idleSec -lt 300) { $target = [System.Diagnostics.ProcessPriorityClass]::BelowNormal }      # user active
elseif ($idleSec -ge 600) { $target = [System.Diagnostics.ProcessPriorityClass]::Normal }        # PC idle 10+ min

if ($target -and $p.PriorityClass -ne $target) {
    $p.PriorityClass = $target
    $line = (Get-Date -Format 'M/d/yyyy h:mm tt') + " - load governor: user idle " + $idleSec + "s -> gateway priority " + $target
    Add-Content -LiteralPath "$env:USERPROFILE\.openclaw\workspace\.openclaw\tmp\load_governor.log" -Value $line -Encoding utf8
}
exit 0