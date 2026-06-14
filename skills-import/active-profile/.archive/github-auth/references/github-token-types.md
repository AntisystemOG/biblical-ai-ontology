# GitHub Token Types — Reference

Quick reference for which GitHub token type to use for what, and how to pass them to git correctly.

## Token Types

| Prefix | Type | Works for `git push`? | Works for API? |
|---|---|---|---|
| `ghp_` | Classic Personal Access Token | **No** (deprecated 2024) | Yes |
| `github_pat_` | Fine-grained Personal Access Token | **Yes** | Yes |
| `gho_` | GitHub OAuth token (from `gh auth`) | Yes | Yes |

**Rule:** If you're doing `git push` or `git pull` from a repo, use a **fine-grained PAT** (`github_pat_...`). Classic tokens (`ghp_`) will fail with:
```
remote: Invalid username or token. Password authentication is not supported.
fatal: Authentication failed
```

## Generating a Fine-Grained PAT

1. Go to https://github.com/settings/tokens/new (or GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens)
2. Click **Generate new token** (fine-grained)
3. Set expiration (90 days recommended)
4. **Repository access:** Select repositories → pick your repo(s)
5. **Permissions:**
   - `Contents` → **Read and write** (required for `git push`)
   - `Metadata` → **Read** (auto-selected)
   - Optional: `Pull requests` → Read/write, `Issues` → Read/write, `Actions` → Read/write
6. Generate and copy the token immediately (won't be shown again)

## Passing Token to Git — Do and Don't

### ✅ Correct: Credential Helper Store

```bash
# 1. Set helper
git config --global credential.helper store

# 2. Do one operation that prompts for credentials
git ls-remote https://github.com/OWNER/REPO.git
#   Username: your-github-username
#   Password: paste the fine-grained PAT (not your GitHub password)

# 3. Token is now saved in ~/.git-credentials, future ops reuse it
git push origin main
```

### ❌ Incorrect: Embed in Remote URL

```bash
# DON'T — shell escaping mangles the URL, token may leak to logs
git remote set-url origin https://ghp_REDACTED_EXAMPLE_TOKEN@github.com/...
```

The URL-with-token approach:
- Fails when the token contains characters that need URL-encoding
- Shows up in `git remote -v` output (leaks to logs, screen captures, etc.)
- Gets permanently saved in `.git/config`
- Hard to rotate (must edit `.git/config` for every repo)

### ✅ Alternative: GIT_ASKPASS Script (Headless)

When no TTY is available (automated agents, CI):

```bash
# Create a temporary askpass script
cat > /tmp/git_askpass.sh << 'EOF'
#!/bin/bash
if [ "$1" = "Username for 'https://github.com':" ]; then
  echo "your-github-username"
else
  echo "github_pat_...YOUR_FINE_GRAINED_TOKEN"
fi
EOF
chmod +x /tmp/git_askpass.sh

# Use it for one operation
GIT_ASKPASS=/tmp/git_askpass.sh git push origin main

# Clean up
rm /tmp/git_askpass.sh
```

### ✅ Alternative: Export as Env Var (API calls only)

For `curl` API calls, not for `git`:

```bash
export GITHUB_TOKEN="github_pat_..."
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
```

## WSL-Specific

In WSL, Git on the Windows side (e.g., Git Bash, PowerShell) may already be authenticated. The WSL git is a **separate environment** — it does not share credentials with Windows.

Options ranked:
1. **Set up credential helper in WSL** (fastest): `git config credential.helper store`, authenticate once
2. **Use Windows Git from PowerShell** (if already authenticated there)
3. **Copy Windows SSH keys into WSL**: `cp /mnt/c/Users/<you>/.ssh/id_* ~/.ssh/` + `chmod 600`
4. **Generate WSL-specific SSH key**: `ssh-keygen -t ed25519` + add to GitHub

## Troubleshooting Token Errors

| Error | Cause | Fix |
|---|---|---|
| `Invalid username or token` | Using classic `ghp_` token for git | Generate fine-grained `github_pat_` |
| `Password authentication not supported` | Same as above | Same as above |
| `could not read Username for 'https://github.com': No such device or address` | No credential helper configured | `git config credential.helper store` then authenticate once |
| `Authentication failed` after correct token | Token lacks `Contents:write` scope | Regenerate with correct permissions |
| `remote: Repository not found` | Token lacks access to that specific repo | Add repo to token's access list |
| Token works on API but not git | Using fine-grained PAT without `Contents:write` | Add `Contents: Read and write` permission |

## Quick Checklist Before Push

- [ ] Token is fine-grained (`github_pat_...`) not classic (`ghp_`)
- [ ] Token has `Contents: Read and write` for the repo
- [ ] Token is not expired
- [ ] `git config credential.helper` returns `store` or `cache`
- [ ] `git config user.name` and `user.email` are set
- [ ] `git remote -v` shows HTTPS URL (not SSH unless SSH key is configured)
