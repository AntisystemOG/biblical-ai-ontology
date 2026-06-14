---
name: hermes-ollama-auth-fix
description: |
  Diagnostic and fix tool for Hermes profiles using Ollama Cloud with empty API
  keys. Detects the common pattern where the Ollama desktop app is running on
  Windows (127.0.0.1:11434) but Hermes profiles are pointed at the cloud
  endpoint with no key, causing HTTP 401 errors.
  
  Also includes a batch script to scan all profiles and auto-fix the misconfiguration.
triggers:
  - "HTTP 401 unauthorized ollama"
  - "API key rejected"
  - "OLLAMA_API_KEY"
  - "ollama-cloud empty key"
  - "switching to webui profile"
  - Profile shows provider ollama-cloud with no api_key
---

# Hermes Ollama Auth Fix

## Problem Pattern

User has the Ollama desktop app running on Windows, which starts a local API at
`http://127.0.0.1:11434`. Hermes profiles are configured with:

```yaml
model:
  provider: ollama-cloud
  base_url: https://ollama.com/v1
```

But no `api_key` is set. Result: `AuthenticationError HTTP 401 unauthorized`

The fix is usually to switch to the local provider.

## Quick Fix (Single Profile)

### 1. Diagnose current profile

```bash
python3 ~/.local/bin/hermes-auth-fix.py 3
```

### 2. Switch to local Ollama (auto)

```bash
python3 ~/.local/bin/hermes-auth-fix.py 1
```

### 3. Enter cloud key instead (manual)

```bash
python3 ~/.local/bin/hermes-auth-fix.py 2
# (will prompt for key)
```

## Batch Fix (All Profiles)

Run the batch scanner if you want to fix every profile:

```bash
python3 ~/.local/bin/hermes-auth-fix-all.py
```

This scans every `~/.hermes/profiles/*/config.yaml`:
- Detects `provider: ollama-cloud` with empty key
- Detects `providers: {}` empty block
- Switches each to `ollama-launch`
- Adds `ollama-launch` provider config block
- Sets base_url to `http://127.0.0.1:11434`
- Sets default model to `kimi-k2.6:cloud`

## Files

- `~/.local/bin/hermes-auth-fix.py` — single-profile diagnostic + fix
- `~/.local/bin/hermes-auth-fix-all.py` — batch fixer
- Alias added to `.bashrc`: `hermes-auth-fix`

## Env Var for Auto Mode

If you want to set the cloud key via environment var instead of interactive prompt:

```bash
export OLLAMA_API_KEY="sk-....hon3 ~/.local/bin/hermes-auth-fix.py 2
```

## Dependencies

Tool uses `pyyaml` for reading/writing Hermes config YAML. Reinstall if needed:

```bash
pip3 install pyyaml --user
```
