# Hermes Update — Missing Venv Recovery

**Date:** 2026-05-28 (missing venv)
**Updated:** 2026-06-07 (Python version constraint mismatch + dual-venv reinstall)

## Symptom A — Missing venv

`hermes update` fails with:
```
error: Failed to inspect Python interpreter from active virtual environment
  Caused by: Python interpreter not found at `/home/thadd/hermes-agent-ui/venv/bin/python3`
```

**Context:** Source checkout had been updated via `git pull` previously, but the `venv/` directory was missing (possibly deleted during cleanup or never recreated after a Python upgrade).

**Fix:**
```bash
cd ~/hermes-agent-ui
python3.11 -m venv venv    # or `uv venv --python python3.11`
uv pip install -e . --python venv/bin/python
```

## Symptom B — Python version incompatible with `pyproject.toml` constraint

After pulling a newer version, `uv pip install` fails with:
```
error: The interpreter at ... is externally managed
hint: Consider creating a virtual environment
```

Or `pip install` fails because the project now caps `requires-python = "<3.14"` and the existing venv is Python 3.14.

**Root cause:** Hermes tightened its Python ceiling to avoid maturin source-build failures on Rust transitives (e.g. pydantic-core). A 3.14 venv that worked for v0.15.x is now invalid for v0.16.x.

**Fix — full manual update with venv migration:**

```bash
cd ~/hermes-agent-ui

# 1. Pull latest
git pull origin main

# 2. Check Python constraint in pyproject.toml
grep 'requires-python' pyproject.toml   # expect ">=3.11,<3.14"

# 3. Check current venv version
cat venv/pyvenv.cfg | grep version      # if 3.14.x, must recreate

# 4. Recreate venv with 3.11
mv venv venv-backup-py314
python3.11 -m venv venv

# 5. Install into new venv
uv pip install -e . --python venv/bin/python

# 6. ALSO reinstall the runtime venv (where ~/.local/bin/hermes launcher points)
uv pip install -e ~/hermes-agent-ui --python ~/.hermes/hermes-agent/venv/bin/python

# 7. Verify version consistency
hermes --version
python -c "import hermes_cli; print(hermes_cli.__version__)"   # must match
```

## Key pitfall — dual venv confusion

Hermes has **two** venvs that matter:

| Venv path | Role | Who uses it |
|---|---|---|
| `~/hermes-agent-ui/venv` | Source checkout venv | Direct `python -m hermes` or dev scripts |
| `~/.hermes/hermes-agent/venv` | Runtime venv | `~/.local/bin/hermes` launcher |

Both are **editable installs** pointing back to `~/hermes-agent-ui`. Updating only one means `hermes --version` and `python -m hermes_cli` can report different versions.

After any manual update, reinstall into **both** venvs, then verify with both `hermes --version` and `python -c "import hermes_cli; print(hermes_cli.__version__)"`.

## Security dep bumps to NOT skip

After pulling, `pyproject.toml` may contain new exact pins for CVE fixes. Reinstalling is required for these to take effect.

- `requests==2.33.0` → CVE-2026-25645
- `PyJWT[crypto]==2.12.1` → CVE-2026-32597
- `pydantic==2.13.4` → segfault in non-main-thread usage

## Environment at time of fix

- OS: WSL (Ubuntu on Windows 11)
- Python system: 3.14.4 at `/usr/bin/python3`
- Python working: 3.11.15 at `/home/thadd/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu`
- Hermes source: `/home/thadd/hermes-agent-ui` (editable install)
- Active profile: `plc-coder`
- `uv` location: `~/.local/bin/uv`
