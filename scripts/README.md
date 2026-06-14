# Spock Git Scripts

## Setup (run once on primary machine)

```powershell
.\setup-git.ps1
```

Creates the Git repo, .gitignore, and initial commit.

## Daily Sync

### Start of day (pull latest)
```powershell
.\sync.ps1 -Pull
```

### End of day (push changes)
```powershell
.\sync.ps1 -Push
```

### Quick status check
```powershell
.\sync.ps1 -Status
```

## Auto-sync (optional - for automation)

```powershell
# At startup
.\autosync.ps1 -Mode startup

# At shutdown
.\autosync.ps1 -Mode shutdown
```

---

## Setup Remote (Optional - for cloud sync)

1. Create a **private** repo at https://github.com/new
2. Connect it:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/spock-workspace.git
git push -u origin main
```

3. On other machines, clone instead of using OneDrive folder:

```powershell
git clone https://github.com/YOUR_USERNAME/spock-workspace.git
```

---

## Workflow with Multiple Machines

1. **Machine A** (e.g., home PC): `git pull` → work → `git push`
2. **Machine B** (e.g., laptop): `git pull` → work → `git push`

Git handles merging automatically. If both machines edited the same file, Git will prompt you to resolve conflicts.

---

**No remote?** The scripts still work locally — just skip the remote commands. Each machine has its own repo history.