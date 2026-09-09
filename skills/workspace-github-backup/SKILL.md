---
name: "workspace-github-backup"
description: "Backup or push workspace memory/.md files to the private spock-workspace GitHub repo — private check, secret scan, clone refresh, verified push."
---

# Workspace GitHub Backup (spock-workspace)

Mirror the OpenClaw workspace's markdown knowledge — memory, soul, identity, agents, reports — to the private GitHub repo `github.com/AntisystemOG/spock-workspace`.

## Steps
1. Confirm the target repo is PRIVATE before moving anything personal: `gh repo view AntisystemOG/spock-workspace --json isPrivate`. If it is public, stop and ask Thad.
2. Refresh the local clone at `.openclaw\tmp\spock-workspace`: `git -C .openclaw\tmp\spock-workspace pull origin main` (clone it first if missing: `git clone https://github.com/AntisystemOG/spock-workspace.git .openclaw\tmp\spock-workspace`).
3. Sync + secret scan: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\backup_md_to_spock_workspace.ps1`. The script copies every in-scope workspace `.md` into the clone, prunes tracked `.md` that no longer exist in the workspace, and prints either `secret scan: clean` or `SECRET SCAN: N matches`.
4. If the scan alerts: do NOT commit. Kill the session, inspect the hits, fix the script's `$excludePattern`, and re-run. Placeholder keys inside third-party skill docs (e.g. `skills-import\`) are false positives; that directory stays excluded.
5. Commit and push from inside the clone: `git add -A`, `git commit -m "..."`, `git push origin main`.
6. Verify the push landed: `git rev-parse --short origin/main` must equal local HEAD, and `git ls-files "*.md" | Measure-Object` should equal the script's copied count.

## Pitfalls (learned 2026-09-09)
- File-exclusion regexes MUST match the workspace-RELATIVE path with FORWARD slashes, never the absolute `FullName` — the base path itself contains `.openclaw`, so an absolute-path match silently excludes every file (v1 copied 0 files and pruned the whole mirror). Regex directory separators must be `/` after relative-path normalization, not `\`.
- `skills-import\` is a third-party skill-doc cache full of DOCUMENTED example keys (`api_key="your-api-key"`, `sk-...`, `"EMPTY"`). Its scan hits are false positives; the directory is excluded from the backup.
- `git status --short` collapses untracked directories into one line, so the pending count under-reports; `git add -A` still stages everything.
- Long git chains on this 2-core host must run as background sessions and be polled; after any interrupted chain, re-verify HEAD vs `origin/main` before retrying — an exit code 1 can mean the push alone failed while earlier commits landed.
