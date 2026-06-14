#!/usr/bin/env python3
"""Post-build verification script for Electron app packaging from WSL.

Run this after `npx electron-builder --win dir` to validate:
- The EXE exists and has reasonable size
- CSS bundle contains Tailwind utilities (not just directives)
- The renderer JS bundle exists
- No old app processes are still running (which would lock files)

Usage:
    python3 scripts/verify-electron-build.py /mnt/c/Users/thadd/spock-code
"""
import sys, os, subprocess, struct

def verify(project_dir: str) -> bool:
    ok = True
    release_dir = os.path.join(project_dir, "release", "win-unpacked")
    dist_dir = os.path.join(project_dir, "dist")

    # 1. EXE exists
    exe_name = None
    for f in os.listdir(release_dir) if os.path.isdir(release_dir) else []:
        if f.endswith(".exe"):
            exe_name = f
            break
    if not exe_name:
        print("FAIL: No .exe found in release/win-unpacked/")
        return False
    exe_path = os.path.join(release_dir, exe_name)
    exe_size = os.path.getsize(exe_path)
    print(f"OK: {exe_name} exists ({exe_size / 1e6:.1f} MB)")
    if exe_size < 50_000_000:
        print("WARN: EXE seems small (< 50 MB) — did electron-builder package correctly?")
        ok = False

    # 2. CSS bundle contains utilities
    css_files = [f for f in os.listdir(dist_dir) if f.endswith(".css")] if os.path.isdir(dist_dir) else []
    if not css_files:
        print("FAIL: No CSS files in dist/")
        return False
    css_path = os.path.join(dist_dir, css_files[0])
    css_size = os.path.getsize(css_path)
    with open(css_path, "r", encoding="utf-8", errors="ignore") as f:
        css_content = f.read()
    has_utilities = ".flex" in css_content or ".bg-" in css_content or ".text-" in css_content
    print(f"OK: CSS bundle {css_files[0]} ({css_size / 1024:.1f} kB) utilities={has_utilities}")
    if not has_utilities:
        print("FAIL: CSS bundle missing Tailwind utilities — run tailwindcss pre-build first")
        ok = False

    # 3. JS bundle exists
    js_files = [f for f in os.listdir(dist_dir) if f.endswith(".js")] if os.path.isdir(dist_dir) else []
    if not js_files:
        print("FAIL: No JS files in dist/")
        ok = False
    else:
        print(f"OK: JS bundle {js_files[0]} present")

    # 4. No running old processes
    base_name = exe_name.replace(".exe", "")
    try:
        result = subprocess.run(
            ["cmd.exe", "/C", "tasklist"],
            capture_output=True, text=True, timeout=10
        )
        running = base_name in result.stdout
        if running:
            print(f"WARN: {base_name} is already running — kill it before rebuild: taskkill /F /IM '{exe_name}'")
            ok = False
        else:
            print(f"OK: No running {base_name} processes")
    except Exception as e:
        print(f"SKIP: Could not check running processes ({e})")

    # 5. Icon exists
    icon_paths = [
        os.path.join(project_dir, "resources", "icon.ico"),
        os.path.join(project_dir, "resources", "icon.png"),
    ]
    icon_ok = any(os.path.exists(p) for p in icon_paths)
    if icon_ok:
        print("OK: Icon resource found")
    else:
        print("WARN: No icon.ico or icon.png in resources/")

    return ok

if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "."
    success = verify(project)
    sys.exit(0 if success else 1)
