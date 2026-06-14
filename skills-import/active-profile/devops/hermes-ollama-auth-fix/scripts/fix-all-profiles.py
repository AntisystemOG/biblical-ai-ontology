#!/usr/bin/env python3
"""Scan all Hermes profiles and switch ollama-cloud → ollama-launch."""
import yaml, os, glob, pwd

home = pwd.getpwuid(os.getuid()).pw_dir

OLLAMA_LAUNCH = {
    "api": "http://127.0.0.1:11434/v1",
    "default_model": "kimi-k2.6:cloud",
    "models": ["kimi-k2.6:cloud"],
    "name": "Ollama",
}

fixed = []
for cfg in sorted(glob.glob(f"{home}/.hermes/profiles/*/config.yaml")):
    profile = os.path.basename(os.path.dirname(cfg))
    with open(cfg) as f:
        config = yaml.safe_load(f) or {}

    current_provider = config.get("model", {}).get("provider", "")
    current_url = config.get("model", {}).get("base_url", "")

    changed = False
    if current_provider in ("ollama-cloud", ""):
        config.setdefault("model", {})
        config["model"]["provider"] = "ollama-launch"
        if current_url == "https://ollama.com/v1":
            config["model"]["base_url"] = "http://127.0.0.1:11434"
            config["model"]["default"] = "kimi-k2.6:cloud"
        changed = True

    if "providers" not in config:
        config["providers"] = {}
    if "ollama-launch" not in config.get("providers", {}):
        config["providers"]["ollama-launch"] = OLLAMA_LAUNCH
        changed = True

    if changed:
        with open(cfg, "w") as f:
            yaml.dump(config, f, sort_keys=False, default_flow_style=False)
        fixed.append(profile)
        print(f"FIXED: {profile}")
    else:
        print(f"OK:    {profile}")

print(f"\nTotal fixed: {len(fixed)}")
