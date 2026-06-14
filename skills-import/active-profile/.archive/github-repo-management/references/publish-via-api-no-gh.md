# Publishing a Public Framework via GitHub API (No gh CLI)

**Scenario:** You need to create a public GitHub repository and push content to it, but `gh` CLI is not installed or not authenticated. Use `git` + `curl` + the token from `~/.git-credentials`.

## Prerequisites

- Git credentials stored in `~/.git-credentials` (format: `https://username:token@github.com`)
- `git` installed and configured with user.name and user.email
- `curl` available

## Steps

### 1. Extract the Token

```bash
TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
```

Or via Python for reliability:
```python
creds = open(os.path.expanduser('~/.git-credentials')).read().strip()
token = creds.split('@')[0].split(':')[-1]
```

### 2. Verify Token Validity

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/user | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Token valid for user: {data.get('login', 'INVALID')}\")
"
```

### 3. Create the Repository via API

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/user/repos \
  -d '{
    "name": "repo-name",
    "description": "Your description here",
    "private": false,
    "has_issues": true,
    "has_wiki": false,
    "has_projects": false,
    "has_discussions": true,
    "license_template": "unlicense"
  }'
```

**Response fields to capture:**
- `html_url` — the public repo URL
- `clone_url` — for adding remote

### 4. Initialize Local Repo and Push

```bash
# In your local project directory
cd /path/to/your/project
git init
git add .
git commit -m "Initial commit"
git branch -m main
git remote add origin https://github.com/YOURUSER/repo-name.git
git push -u origin main
```

**If remote already has an initial commit (GitHub auto-creates one):**
```bash
git fetch origin
# Option A: merge (preserves both histories)
git merge origin/main --allow-unrelated-histories
# Option B: force push (overwrites remote with your content)
git push -f origin main
```

### 5. Create an Issue via API

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/YOURUSER/repo-name/issues \
  -d '{
    "title": "Invitation to collaborate",
    "body": "Your issue body here...",
    "labels": ["invitation", "community"]
  }'
```

## Pitfalls

- **jq not installed:** Use Python `json` module instead of `jq` for parsing API responses
- **Remote rejected (fetch first):** GitHub auto-creates an initial commit when you select a license template or auto-init. You must fetch and merge, or force push.
- **Token in environment variable:** Never `echo $TOKEN` in terminal output that could be logged
- **Force push danger:** Only force push on a brand-new repo with no collaborators. On existing repos, merge instead.

## When This Pattern Applies

- The user says "publish this" or "spread this" and you do not have `gh` CLI
- Creating open-source frameworks, documentation, or public declarations
- Any situation where `gh` is unavailable but Git credentials are stored in `~/.git-credentials`
