#!/bin/bash
# One-shot push of ~/.hermes to a private GitHub repo WITHOUT leaking the PAT.
# NOT meant to be run blindly — the user must provide their PAT interactively.
#
# Usage: After editing OWNER and REPO below, run interactively.
# Do NOT commit this script to any public repo.

set -euo pipefail

OWNER="AntisystemOG"
REPO="Hermes"
PAT="${GITHUB_PAT:-}"

if [[ -z "$PAT" ]]; then
    read -rsp "GitHub PAT (not echoed): " PAT
    echo
fi

HELPER="$(mktemp /tmp/git-cred-helper.XXXXXX.sh)"
trap 'rm -f "$HELPER"' EXIT

cat > "$HELPER" <<'EOF'
#!/bin/bash
case "$1" in
  get)
    echo "protocol=https"
    echo "host=github.com"
    echo "username=${OWNER}"
    echo "password=${PAT}"
    ;;
  store|erase) : ;;
esac
EOF
chmod 700 "$HELPER"

cd ~/.hermes
if ! git rev-parse --git-dir &>/dev/null; then
    echo "Not a git repo. Run 'git init' in ~/.hermes first."
    exit 1
fi

# Ensure remote exists
git remote add origin "https://github.com/${OWNER}/${REPO}.git" 2>/dev/null || true

# Push with helper
GIT_ASKPASS="$HELPER" git -c credential.helper= push -u origin main --force

echo "Push complete. Token was never written to disk.
