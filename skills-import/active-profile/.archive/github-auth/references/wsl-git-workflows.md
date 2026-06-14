# WSL Git Workflows — References

Common WSL + Git + GitHub patterns that trip up automated agents.

## 1. Massive unstaged working tree with ignored directories already tracked

**Symptom:** `git status` shows thousands of files from a directory listed in `.gitignore` (e.g., `D14/`, CAD models). `git rm --cached` times out on huge trees.

**Workaround:** Stage only what you actually want. Ignore the noise.

```bash
# Get the real source files that changed (exclude ignored dir noise)
git status --short | grep "^ M" | grep -v D14 | awk '{print $2}' | xargs -I{} git add {}

# Stage new untracked files selectively
git add src/ build_exe.py pyproject.toml PLCTools.spec AGENTS.md scripts/
```

**Long-term fix (destructive — use only if the ignored dir was never meant to be tracked):**
```bash
# git filter-repo or BFG to rewrite history and remove the directory entirely
# Install: pip install git-filter-repo
git filter-repo --path D14 --invert-paths
```

## 2. Git identity missing in fresh WSL session

**Symptom:** `git commit` fails with `fatal: empty ident name` even though commits work on Windows side.

**Quick fix — derive from last commit in repo:**
```bash
git config user.name  "$(git log --format='%an' -1)"
git config user.email "$(git log --format='%ae' -1)"
```

## 3. No GitHub auth in WSL — Windows has it, WSL doesn't

**Symptom:** `git push` → `could not read Username for 'https://github.com': No such device or address`

**Options ranked by effort:**
1. **Give agent a PAT** → `git config credential.helper store`, authenticate once, push. Fastest.
2. **Use Windows Git from PowerShell** → Open terminal on Windows side where GitHub auth is already configured.
3. **Set up SSH in WSL** → Generate key, add to GitHub, configure remote to SSH. Slower but permanent.
4. **Copy Windows .ssh keys into WSL** → `cp /mnt/c/Users/<user>/.ssh/id_* ~/.ssh/`, `chmod 600`.

## 4. Stale PROJECT_MEMORY.md vs. git reality

**Symptom:** `PROJECT_MEMORY.md` describes work from weeks ago; git log shows newer commits.

**Agent should:** Read git log to get actual recent changes, then update `PROJECT_MEMORY.md` to match before presenting project state to user.
