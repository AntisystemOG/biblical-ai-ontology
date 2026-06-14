#!/usr/bin/env python3
"""
Secure Hermes → GitHub Backup Script
Usage: python3 backup.py [repo_url] [branch]
"""
import os, re, sys, subprocess

HERMES = os.environ.get('HERMES_HOME', '/home/thadd/.hermes')
ENV_PATH = f'{HERMES}/.env'
CFG_PATH = f'{HERMES}/config.yaml'
CFG_BAK = f'{HERMES}/config.yaml.bak'

REPO = sys.argv[1] if len(sys.argv) > 1 else 'https://github.com/AntisystemOG/Hermes.git'
BRANCH = sys.argv[2] if len(sys.argv) > 2 else 'main'

print(f'[+] Target: {REPO}')

# 1. Ensure .env is complete
backups = sorted(
    [f for f in os.listdir(HERMES) if f.startswith('.env') and os.path.isfile(f'{HERMES}/{f}')],
    key=lambda x: os.path.getmtime(f'{HERMES}/{x}'),
    reverse=True
)

if len(backups) > 1 and os.path.getsize(ENV_PATH) < 200:
    print(f'[!] .env is small ({os.path.getsize(ENV_PATH)} bytes), merging from {backups[1]}')
    with open(f'{HERMES}/{backups[1]}', 'r') as f:
        base = {k: v for k, v in (l.strip().split('=', 1) for l in f if '=' in l and not l.strip().startswith('#'))}
    with open(ENV_PATH, 'r') as f:
        overrides = {k: v for k, v in (l.strip().split('=', 1) for l in f if '=' in l and not l.strip().startswith('#'))}
    base.update(overrides)
    with open(ENV_PATH, 'w') as f:
        for k, v in base.items():
            f.write(f'{k}={v}\n')
    print('[+] .env merged')

# 2. Backup and sanitize config.yaml
with open(CFG_PATH, 'r') as f:
    real = f.read()
with open(CFG_BAK, 'w') as f:
    f.write(real)

with open(CFG_PATH, 'w') as f:
    f.write(re.sub(r'(api_key|session_key|brave_api_key|token|password|secret_key):\s*"[^"]*"', r'\1: ""', real))
print('[+] config.yaml sanitized for commit')

# 3. Initialize/push
git = lambda *args: subprocess.run(['git'] + list(args), cwd=HERMES, capture_output=True, text=True)

if not os.path.exists(f'{HERMES}/.git'):
    git('init')
    print('[+] git init')

git('remote', 'add', 'origin', REPO)
result = git('commit', '-am', f'Backup {os.popen("date +%Y-%m-%d_%H-%M").read().strip()}')
if 'nothing to commit' in result.stdout.lower() and 'nothing to commit' in result.stderr.lower():
    print('[0] No changes to commit')
else:
    print(f'[+] Committed: {result.stdout.strip()}')

# 4. Push via cred helper
helper = '/tmp/hermes-git-cred-helper.sh'
with open(helper, 'w') as f:
    f.write("#!/bin/bash\ncase \"$1\" in\nget)\n  . /home/thadd/.hermes/.env 2>/dev/null\n  echo \"protocol=https\"\n  echo \"host=github.com\"\n  echo \"username=AntisystemOG\"\n  echo \"password=$GITHUB_PAT\"\n;;\nstore|erase)\n  :;;\nesac\n")
os.chmod(helper, 0o700)

env = {**os.environ, 'GIT_ASKPASS': helper, 'GIT_USERNAME': 'AntisystemOG'}
result = subprocess.run(['git', 'push', '-u', 'origin', BRANCH], cwd=HERMES, env=env, capture_output=True, text=True)
print(f'[+] Push: {result.stdout.strip()}')
if result.returncode != 0:
    print(f'[!] Error: {result.stderr.strip()}')

# 5. Restore config.yaml and cleanup
with open(CFG_BAK, 'r') as f:
    real = f.read()
with open(CFG_PATH, 'w') as f:
    f.write(real)
if os.path.exists(helper):
    os.remove(helper)
print('[+] config.yaml restored, credential helper cleaned')
print('[+] Done')
