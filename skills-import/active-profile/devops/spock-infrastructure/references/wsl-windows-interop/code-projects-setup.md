# Session Reference: CODE Projects Setup — May 23, 2026

## Context
User created a `CODE Projects` folder and wanted files organized across multiple locations for the Dev Agent (Claude Code).

## Locations Discovered

1. **CODE Projects folder** (WSL): `/home/thadd/.hermes/profiles/devteam/CODE Projects`
   - Created via Hermes WebUI file manager
   - Case-sensitive: must search with exact case or `-iname`

2. **Claude Code projects**: `C:\Users\thadd\.claude\projects`
   - Already existed with prior project backups
   - Used by Claude Code CLI for active coding workspaces

3. **Claude Code backups**: `C:\Users\thadd\.claude\backups`
   - Existing `.claude.json.backup.*` files
   - Prior project folders already present

## Operations Performed

### Move zip file to CODE Projects
```bash
mv "/home/thadd/.hermes-web-ui/upload/ab27ab6372054036.zip" \
    "/home/thadd/.hermes/profiles/devteam/CODE Projects/"
```

### Copy project folders to .claude\projects
```bash
cp -r "/mnt/c/Users/thadd/Documents/Degater PLC Tool BST33 and 35" \
    "/mnt/c/Users/thadd/.claude/projects/"

cp -r "/mnt/c/Users/thadd/Documents/PLCTools" \
    "/mnt/c/Users/thadd/.claude/projects/"

# For Thompson Family App (large, with node_modules) — used rsync
rsync -av --exclude='node_modules' --exclude='.git' --exclude='build' --exclude='dist' \
    "/mnt/c/Users/thadd/Documents/Thompson Family App/" \
    "/mnt/c/Users/thadd/.claude/projects/Thompson Family App/"
```

### Move zip to .claude\backups (user's preferred archive location)
```bash
mv "/home/thadd/.hermes/profiles/devteam/CODE Projects/C--Users-thadd-Documents-Degater-PLC-Tool-BST33-and-35.zip" \
    "/mnt/c/Users/thadd/.claude/backups/"
```

### Create Desktop shortcut
```bash
# Write script to Windows-accessible path
cat > "/mnt/c/Users/thadd/Desktop/create_shortcut_temp.ps1" << 'EOF'
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\thadd\Desktop\Claude Projects.lnk")
$Shortcut.TargetPath = "C:\Users\thadd\.claude\projects"
$Shortcut.Save()
EOF

# Execute
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
    -ExecutionPolicy Bypass \
    -File "C:\Users\thadd\Desktop\create_shortcut_temp.ps1"

# Clean up temp script
rm "/mnt/c/Users/thadd/Desktop/create_shortcut_temp.ps1"
```

## Verification
```bash
ls -la "/mnt/c/Users/thadd/Desktop/Claude Projects.lnk"
ls -la "/mnt/c/Users/thadd/.claude/backups/"
ls -la "/home/thadd/.hermes/profiles/devteam/CODE Projects/"
```

## Key Lessons
- `find` on `/mnt/c/` can timeout on large filesystems — use `ls` + `grep` for targeted searches
- Always use `-iname` for case-insensitive directory searches across WSL/Windows
- PowerShell scripts must live under `/mnt/c/` to be visible to `powershell.exe -File`
- `rsync` with excludes is essential for Node.js projects with `node_modules`
- The user's "backups" folder preference was discovered via screenshot (Capture.PNG)