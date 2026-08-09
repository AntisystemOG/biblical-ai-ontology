"""Reapply final waypoints and update header comment in track_photo.py."""
import json
import re
from pathlib import Path

track_py = Path(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\track_photo.py')
text = track_py.read_text(encoding='utf-8')

# Replace header (the first triple-quoted string)
header_end = text.find('"""', 3)
old_header = text[:header_end+3]
new_header = '"""Pixel-space calibration for the rendered S7000 track layout.\n\nBackground: mm_monitor/data/track_photo.png is a cleaned render of the user\'s\nfreehand full_track_grid.png. The red grid overlay was removed and the image\nwhite-balanced/levelled so the background is neutral and the rails are clear.\n\nWaypoints: PATH_WAYPOINTS_PX was manually traced along the top edge of each\nrail extrusion so carts/pallets ride on the top of the track. The six PLC\npaths are split at the real rail junctions:\n  Path 6 (Process)         -> full top rail incl. both end curves\n  Path 3 (unnamed connector)-> long straight lower rail (HOME / Cleanout)\n  Path 4 (Mold 2)           -> LEFT U-shaped spur\n  Path 2 (Mold 1)           -> RIGHT U-shaped spur\n  Path 1 (Mold 1 Entry/Exit)-> tiny right junction connector\n  Path 5 (Mold 2 Entry/Exit)-> tiny left junction connector / Cleanout stub\n\nREAL_TO_PIXEL_BREAKPOINTS are identity for paths 2 and 4 in this render; the\nwaypoints already encode the U-turn geometry. If cart pacing through the mold\nloops looks wrong compared to the real machine, recalibrate from\ntrack_geometry\'s real segment lengths.\n"""'

text = new_header + text[header_end+3:]

# Load waypoints from manual trace
with open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\manual_trace_applied.json') as f:
    wps = {int(k): v for k, v in json.load(f).items()}

# Replace PATH_WAYPOINTS_PX block
marker = "PATH_WAYPOINTS_PX: dict[int, list[tuple[float, float]]] = {"
start = text.find(marker)
if start == -1:
    raise ValueError("Could not find PATH_WAYPOINTS_PX block")
rest = text[start:]
match = re.search(r"\n\ndef ", rest)
end = start + match.start() if match else len(text)

lines = ["PATH_WAYPOINTS_PX: dict[int, list[tuple[float, float]]] = {"]
for pid in sorted(wps.keys()):
    pts = wps[pid]
    lines.append(f"    {pid}: [")
    for i in range(0, len(pts), 3):
        chunk = pts[i : i + 3]
        lines.append("        " + ", ".join(f"({x:.1f}, {y:.1f})" for x, y in chunk) + ",")
    lines.append("    ],")
lines.append("}")

new_text = text[:start] + "\n".join(lines) + "\n" + text[end:]
track_py.write_text(new_text, encoding='utf-8')
print(f'Updated {track_py}')
