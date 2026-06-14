#!/usr/bin/env python3
"""
Convert EMF ladder logic images from a .docx export to PNG for analysis.
Use PowerShell from WSL (since Linux tools can't render EMF properly).

Usage:
    python3 scripts/convert_ladder_emf_to_png.py /path/to/ladder.docx

Outputs rung_NNN.png files in the current directory. Run this on Windows
with WSL access to the .docx file, or from WSL with the file mounted
under /mnt/c/.
"""

import os
import sys
import shutil
import subprocess
import tempfile


def convert_docx_emf_to_png(docx_path: str, output_dir: str | None = None) -> list[str]:
    """
    Extract all EMF images from a .docx file and convert each one to PNG
    using PowerShell's System.Drawing from WSL.

    Returns list of output PNG paths.
    """
    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Extract .docx (it's a ZIP)
    tmpdir = tempfile.mkdtemp(prefix="docx_")
    extract_dir = os.path.join(tmpdir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    print(f"Extracting {docx_path}...")
    subprocess.run(
        [sys.executable, "-m", "zipfile", "-e", docx_path, extract_dir],
        check=True,
        capture_output=True,
    )

    emf_dir = os.path.join(extract_dir, "word", "media")
    if not os.path.isdir(emf_dir):
        print(f"No media directory found in {docx_path}")
        return []

    emf_files = sorted(
        [f for f in os.listdir(emf_dir) if f.lower().endswith(".emf")],
        key=lambda x: int(os.path.splitext(x)[0].replace("image", "")),
    )

    if not emf_files:
        print("No EMF files found in document.")
        return []

    print(f"Found {len(emf_files)} EMF images to convert...")

    # Step 2: Convert each EMF to PNG using PowerShell via WSL's cmd.exe
    windows_temp = r"C:\Users\thadd\AppData\Local\Temp"
    png_paths: list[str] = []

    for emf_name in emf_files:
        emf_src = os.path.join(emf_dir, emf_name)
        idx = os.path.splitext(emf_name)[0].replace("image", "")

        # Copy to Windows temp
        win_temp_emf = os.path.join("/mnt/c/Users/thadd/AppData/Local/Temp", emf_name)
        shutil.copy2(emf_src, win_temp_emf)

        # Build PowerShell one-liner
        ps_cmd = (
            f'Add-Type -AssemblyName System.Drawing; '
            f'$emf = [System.Drawing.Imaging.Metafile]::FromFile('
            f'"C:\\Users\\thadd\\AppData\\Local\\Temp\\{emf_name}"); '
            f'$emf.Save('
            f'"C:\\Users\\thadd\\AppData\\Local\\Temp\\rung{idx}.png", '
            f'[System.Drawing.Imaging.ImageFormat]::Png); '
            f'$emf.Dispose(); Write-Host "Done"'
        )

        cmd = [
            "/mnt/c/Windows/System32/cmd.exe",
            "/c",
            f'powershell -ExecutionPolicy Bypass -Command "{ps_cmd}"',
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            win_png = f"/mnt/c/Users/thadd/AppData/Local/Temp/rung{idx}.png"
            dst = os.path.join(output_dir, f"rung{idx}.png")
            if os.path.exists(win_png):
                shutil.copy2(win_png, dst)
                png_paths.append(dst)
            else:
                print(f"  Warning: PNG not created for {emf_name}")
        else:
            print(f"  Error converting {emf_name}: {result.stderr.strip()}")

    return png_paths


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} /path/to/ladder.docx [output_dir]")
        sys.exit(1)

    docx_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    pngs = convert_docx_emf_to_png(docx_path, output_dir)
    if pngs:
        print(f"\n✓ Converted {len(pngs)} images to {output_dir}/")
        print(f"  Run: vision_analyze('{output_dir}/rung75.png', '...') to analyze individual rungs")
    else:
        print("\n✗ No images were converted.")


if __name__ == "__main__":
    main()
