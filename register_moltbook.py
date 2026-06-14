#!/usr/bin/env python3
import sys
import os

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Import and run the register script
from pathlib import Path
skills_dir = Path(__file__).parent / "skills" / "moltbook" / "moltbook-integration" / "scripts"
register_script = skills_dir / "register.py"

# Add to path
sys.path.insert(0, str(skills_dir))

# Run registration
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True)
args = parser.parse_args()

# Execute the registration
os.system(f'python "{register_script}" --name "{args.name}"')
