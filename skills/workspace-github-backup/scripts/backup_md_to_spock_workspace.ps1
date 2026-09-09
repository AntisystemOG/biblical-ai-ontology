#!/usr/bin/env powershell
# backup_md_to_spock_workspace.ps1 - Sync ALL current .md files from the OpenClaw
# workspace into the spock-workspace backup repo clone, then prune stale tracked .md.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\backup_md_to_spock_workspace.ps1
# (git add/commit/push are left to the caller)
# v3: exclusion pattern matches FORWARD-slash relative paths (v2 used backslashes ->
# skills-import/ etc. leaked in). skills-import = third-party skill cache, excluded.
# v2 fixes kept: exclusions matched on RELATIVE path; prune compares to copied list.

$ErrorActionPreference = "Stop"
$ws = "C:\Users\thadd\.openclaw\workspace"
$cl = Join-Path $ws ".openclaw\tmp\spock-workspace"

$excludePattern = '^(\.git|\.openclaw|__pycache__|legacy_backup|tmp|temp|magne_temp|logs|cron-logs|media|pictures|node_modules|skills-import|profiles|state)(/|$)'

$all = Get-ChildItem $ws -Recurse -File -Filter *.md
$mds = @()
foreach ($f in $all) {
    $rel = $f.FullName.Substring($ws.Length + 1) -replace '\\','/'
    if ($rel -match $excludePattern) { continue }
    $mds += [pscustomobject]@{ File = $f; Rel = $rel }
}
Write-Output ("workspace .md in scope: {0}" -f $mds.Count)

$copiedRel = @()
foreach ($m in $mds) {
    $dest = Join-Path $cl ($m.Rel -replace '/','\')
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }
    Copy-Item $m.File.FullName $dest -Force
    $copiedRel += $m.Rel
}
Write-Output ("copied .md files: {0}" -f $copiedRel.Count)

Set-Location $cl
$tracked = git ls-files "*.md" | ForEach-Object { $_ -replace '\\','/' }
$stale = @($tracked | Where-Object { $copiedRel -notcontains $_ })
foreach ($t in $stale) {
    $p = Join-Path $cl ($t -replace '/','\')
    if (Test-Path $p) { Remove-Item $p -Force }
}
Write-Output ("pruned stale tracked .md: {0}" -f $stale.Count)

$patterns = 'BEGIN (RSA )?PRIVATE KEY|api[_-]?key\s*[:=]|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-'
$hits = Get-ChildItem $cl -Recurse -File -Filter *.md |
    Where-Object { $_.FullName -notmatch '\\\.git(\\|$)' } |
    Select-String -Pattern $patterns -ErrorAction SilentlyContinue
if ($hits) {
    Write-Output ("SECRET SCAN: {0} matches - review before commit" -f ($hits | Measure-Object).Count)
    $hits | Group-Object Path | Sort-Object Count -Descending | Select-Object -First 10 |
        ForEach-Object { Write-Output ("  {0} hits: {1}" -f $_.Count, $_.Name.Replace($cl + '\', '')) }
} else {
    Write-Output "secret scan: clean"
}