"""Apply the manual trace waypoints and cleaned image to the project."""
import json
import re
import shutil
from pathlib import Path

project_dir = Path(r'C:\AI Projects\MagneMotionMonitor')
img_src = Path(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_levels.png')
img_dst = project_dir / 'mm_monitor' / 'data' / 'track_photo.png'
track_py = project_dir / 'mm_monitor' / 'track_photo.py'

# Backup old photo
if img_dst.exists():
    backup = img_dst.with_suffix('.png.previous_v2')
    shutil.copy2(img_dst, backup)
shutil.copy2(img_src, img_dst)
print(f'Copied cleaned image to {img_dst}')

# Build waypoints from manual trace control points
path6_ctrl = [(40, 75), (150, 75), (350, 75), (550, 75), (750, 77), (950, 80), (1150, 85), (1320, 92), (1430, 105), (1500, 125), (1545, 150), (1560, 165), (1560, 180)]
path1_ctrl = [(1560, 180), (1550, 190), (1545, 195), (1540, 200)]
path2_ctrl = [(1540, 200), (1538, 250), (1535, 350), (1532, 450), (1530, 540), (1505, 600), (1460, 622), (1410, 625), (1375, 610), (1365, 560), (1362, 460), (1361, 350), (1360, 250), (1360, 200)]
path3_ctrl = [(1360, 200), (1200, 202), (1000, 203), (800, 203), (600, 202), (500, 200)]
path4_ctrl = [(500, 200), (502, 250), (505, 350), (508, 450), (510, 540), (535, 600), (580, 622), (630, 625), (665, 610), (675, 560), (678, 460), (679, 350), (680, 250), (680, 200)]
path5_ctrl = [(680, 200), (500, 195), (300, 190), (150, 185), (40, 180)]

ctrl_by_path = {6: path6_ctrl, 1: path1_ctrl, 2: path2_ctrl, 3: path3_ctrl, 4: path4_ctrl, 5: path5_ctrl}

# Resample each path at ~6px spacing
def resample(pts, spacing=6.0):
    if len(pts) < 2:
        return list(pts)
    out = [pts[0]]
    remain = 0.0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        seg = (dx*dx+dy*dy)**0.5
        if seg == 0:
            continue
        ux, uy = dx/seg, dy/seg
        d = remain
        while d < seg:
            out.append((a[0]+ux*d, a[1]+uy*d))
            d += spacing
        remain = d - seg
    if (out[-1][0]-pts[-1][0])**2 + (out[-1][1]-pts[-1][1])**2 > 1:
        out.append(pts[-1])
    return out

waypoints = {pid: resample(ctrl) for pid, ctrl in ctrl_by_path.items()}

# Ensure junctions match exactly
waypoints[6][-1] = waypoints[1][0]
waypoints[1][-1] = waypoints[2][0]
waypoints[2][-1] = waypoints[3][0]
waypoints[3][-1] = waypoints[4][0]
waypoints[4][-1] = waypoints[5][0]
waypoints[5][-1] = waypoints[6][0]

# Update track_photo.py
text = track_py.read_text(encoding='utf-8')
marker = "PATH_WAYPOINTS_PX: dict[int, list[tuple[float, float]]] = {"
start = text.find(marker)
if start == -1:
    raise ValueError("Could not find PATH_WAYPOINTS_PX block")
rest = text[start:]
match = re.search(r"\n\ndef ", rest)
end = start + match.start() if match else len(text)

lines = ["PATH_WAYPOINTS_PX: dict[int, list[tuple[float, float]]] = {"]
for pid in sorted(waypoints.keys()):
    pts = waypoints[pid]
    lines.append(f"    {pid}: [")
    for i in range(0, len(pts), 3):
        chunk = pts[i : i + 3]
        lines.append("        " + ", ".join(f"({x:.1f}, {y:.1f})" for x, y in chunk) + ",")
    lines.append("    ],")
lines.append("}")

new_text = text[:start] + "\n".join(lines) + "\n" + text[end:]
track_py.write_text(new_text, encoding='utf-8')
print(f'Updated {track_py} with {sum(len(v) for v in waypoints.values())} waypoints')

# Save JSON backup for reference
with open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\manual_trace_applied.json', 'w') as f:
    json.dump({str(k): [[round(x,1), round(y,1)] for x, y in v] for k, v in waypoints.items()}, f, indent=2)
