#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

audio_file = r"C:\Users\thada\.openclaw\media\inbound\file_7---4de7f9dc-bf06-40d0-b88e-0e4403335457.ogg"
output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

# Try to download ffmpeg if not available
try:
    import yt_dlp
    # ffmpeg might be bundled with yt-dlp
except ImportError:
    pass

# Try direct whisper transcription
try:
    from whisper import transcribe
    result = transcribe(audio_file, model="tiny", device="cpu", language="en")
    print(result["text"])
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
