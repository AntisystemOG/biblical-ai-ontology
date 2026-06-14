# Parallel Workspace Pattern: Claude Code + Hermes WebUI

Thad maintains three distinct but related workspace locations for coding projects:

## 1. Hermes WebUI "CODE Projects"
**Path (WSL)**: `/home/thadd/.hermes/profiles/devteam/CODE Projects`
**Access**: Hermes WebUI file manager (browser-based)
**Purpose**: Upload/receive files via WebUI, temporary staging area
**Characteristics**: 
- Files uploaded via chat attachments land here first
- User expects files to be mirrored to other locations
- Visible in WebUI sidebar under "Home / CODE Projects"

## 2. Claude Code Dev Agent Projects
**Path (Windows)**: `C:\Users\thadd\.claude\projects`
**WSL equivalent**: `/mnt/c/Users/thadd/.claude/projects`
**Purpose**: Active coding workspaces for Claude Code CLI
**Characteristics**:
- Claude Code stores project checkouts here automatically
- Prior projects may already exist (check before copying)
- Large projects should use `rsync` with `--exclude='node_modules' --exclude='.git' --exclude='build' --exclude='dist'`

## 3. Claude Code Backups
**Path (Windows)**: `C:\Users\thadd\.claude\backups`
**WSL equivalent**: `/mnt/c/Users/thadd/.claude/backups`
**Purpose**: Archive location for zip files, backups, and exported data
**Characteristics**:
- User explicitly directs archive files here (confirmed via screenshot)
- Already contains `.claude.json.backup.*` files and prior project folders
- The zip file was moved here AND copied back to CODE Projects (user wants dual presence)

## Operational Pattern

When user uploads files and says "the Dev Agent will be using this":

1. **Stage in CODE Projects** — file arrives via upload
2. **Copy to .claude\projects** — Dev Agent working directory
3. **Archive in .claude\backups** — permanent storage (if user explicitly requests)
4. **Create Desktop shortcut** — if user requests quick access

## Cross-Location File Operations

### Moving from CODE Projects to .claude\backups
```bash
mv "/home/thadd/.hermes/profiles/devteam/CODE Projects/file.zip" \
    "/mnt/c/Users/thadd/.claude/backups/"
```

### Copying from CODE Projects to .claude\projects
```bash
cp -r "/home/thadd/.hermes/profiles/devteam/CODE Projects/MyProject" \
    "/mnt/c/Users/thadd/.claude/projects/"
```

### Large project with exclusions
```bash
rsync -av --exclude='node_modules' --exclude='.git' --exclude='build' --exclude='dist' \
    "/home/thadd/.hermes/profiles/devteam/CODE Projects/MyProject/" \
    "/mnt/c/Users/thadd/.claude/projects/MyProject/"
```

### Dual-presence (CODE Projects + backups)
```bash
# Move to backups (primary)
mv "/home/thadd/.hermes/profiles/devteam/CODE Projects/file.zip" \
    "/mnt/c/Users/thadd/.claude/backups/"

# Copy back to CODE Projects (dual presence)
cp "/mnt/c/Users/thadd/.claude/backups/file.zip" \
    "/home/thadd/.hermes/profiles/devteam/CODE Projects/"
```

## Screenshot Communication

The user references locations via the Hermes WebUI file manager screenshots (e.g., "see photo" showing `Home / CODE Projects`). When the user shares a screenshot of the WebUI:
1. Read the breadcrumb path carefully (e.g., "Home / CODE Projects")
2. Note the exact case of folder names ("CODE" not "Code")
3. Map to WSL path: `Home / CODE Projects` → `/home/thadd/.hermes/profiles/devteam/CODE Projects`