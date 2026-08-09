"""Apply waypoints_from_recording.json to mm_monitor/track_photo.py and replace the track photo."""
import json
import re
import shutil
from pathlib import Path

project_dir = Path(r'C:\AI Projects\MagneMotionMonitor')
track_photo_src = project_dir / 'Pictures and graphics' / 'full_track_grid.png'
track_photo_dst = project_dir / 'mm_monitor' / 'data' / 'track_photo.png'
track_py = project_dir / 'mm_monitor' / 'track_photo.py'
waypoints_json = project_dir / 'Track Alignment program' / 'waypoints_from_recording.json'

# Backup old photo
if track_photo_dst.exists():
    backup = track_photo_dst.with_suffix('.png.previous')
    shutil.copy2(track_photo_dst, backup)
    print(f'Backed up old photo to {backup}')

# Copy new photo
shutil.copy2(track_photo_src, track_photo_dst)
print(f'Copied {track_photo_src.name} to {track_photo_dst}')

# Load waypoints
with open(waypoints_json) as f:
    wps = json.load(f)

# Read current track_photo.py
text = track_py.read_text(encoding='utf-8')

# Update header comment to reflect new photo
old_header = 'Pixel-space calibration for the real S7000 track photo'
new_header = 'Pixel-space calibration for the rendered S7000 track layout (full_track_grid.png)'
text = text.replace(old_header, new_header, 1)
old_sub = 'so the Live Track view can draw stations/carts directly on the actual hardware photo'
new_sub = 'so the Live Track view can draw stations/carts directly on the rendered track layout'
text = text.replace(old_sub, new_sub, 1)

# Replace PATH_WAYPOINTS_PX block
marker = "PATH_WAYPOINTS_PX: dict[int, list[tuple[float, float]]] = {"
start = text.find(marker)
if start == -1:
    raise ValueError("Could not find PATH_WAYPOINTS_PX block")
rest = text[start:]
match = re.search(r"\n\ndef ", rest)
end = start + match.start() if match else len(text)

lines = ["PATH_WAYPOINTS_PX: dict[int, list[tuple[float, float]]] = {"]
for pid in sorted(wps.keys(), key=int):
    pts = wps[pid]
    lines.append(f"    {pid}: [")
    # 3 points per line to keep file compact but readable
    for i in range(0, len(pts), 3):
        chunk = pts[i : i + 3]
        lines.append("        " + ", ".join(f"({x:.1f}, {y:.1f})" for x, y in chunk) + ",")
    lines.append("    ],")
lines.append("}")

new_text = text[:start] + "\n".join(lines) + "\n" + text[end:]
track_py.write_text(new_text, encoding='utf-8')
print(f'Updated {track_py} with {sum(len(v) for v in wps.values())} waypoints')
