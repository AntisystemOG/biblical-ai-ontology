"""Apply manual trace waypoints to the cleaned track image."""
import json
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor\Track Alignment program')
from main import _generate_plc_paths, PATH_ORDER
from PIL import Image, ImageDraw

def _dist2(a, b): return (a[0]-b[0])**2 + (a[1]-b[1])**2

# Use the manual trace control points
path6_ctrl = [(40, 75), (150, 75), (350, 75), (550, 75), (750, 77), (950, 80), (1150, 85), (1320, 92), (1430, 105), (1500, 125), (1545, 150), (1560, 165), (1560, 180)]
path1_ctrl = [(1560, 180), (1550, 190), (1545, 195), (1540, 200)]
path2_ctrl = [(1540, 200), (1538, 250), (1535, 350), (1532, 450), (1530, 540), (1505, 600), (1460, 622), (1410, 625), (1375, 610), (1365, 560), (1362, 460), (1361, 350), (1360, 250), (1360, 200)]
path3_ctrl = [(1360, 200), (1200, 202), (1000, 203), (800, 203), (600, 202), (500, 200)]
path4_ctrl = [(500, 200), (502, 250), (505, 350), (508, 450), (510, 540), (535, 600), (580, 622), (630, 625), (665, 610), (675, 560), (678, 460), (679, 350), (680, 250), (680, 200)]
path5_ctrl = [(680, 200), (500, 195), (300, 190), (150, 185), (40, 180)]

ctrl_by_path = {6: path6_ctrl, 1: path1_ctrl, 2: path2_ctrl, 3: path3_ctrl, 4: path4_ctrl, 5: path5_ctrl}

# Convert to anchors and junctions format expected by _generate_plc_paths
# Build a master loop of anchors: concatenate control points, removing duplicates at junctions
master = []
junction_indices = []
for pid in PATH_ORDER:
    pts = ctrl_by_path[pid]
    if master and _dist2(master[-1], pts[0]) < 1:
        start_idx = len(master) - 1
        master.extend(pts[1:])
    else:
        start_idx = len(master)
        master.extend(pts)
    junction_indices.append(start_idx)

# Remove the last duplicate to make it a closed loop? Actually keep last point same as first
plc = _generate_plc_paths(master, junction_indices, spacing=6.0, smooth=False)

# Draw on cleaned image
img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_levels.png').convert('RGB')
draw = ImageDraw.Draw(img)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
for pid in PATH_ORDER:
    pts = plc[pid]
    color = colors[pid-1]
    draw.line(pts, fill=color, width=2)
    for x, y in pts[::max(1, len(pts)//15)]:
        draw.ellipse([x-4, y-4, x+4, y+4], fill=color)

# Draw control points
all_ctrl = path6_ctrl + path1_ctrl + path2_ctrl + path3_ctrl + path4_ctrl + path5_ctrl
for x, y in all_ctrl:
    draw.ellipse([x-3, y-3, x+3, y+3], fill=(255,255,255), outline=(0,0,0), width=1)

img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\manual_trace_clean_preview.png')
print('Saved manual_trace_clean_preview.png')
print('PLC counts:', {k: len(v) for k, v in plc.items()})

# Save the cleaned image path for reference
# Also save as the new track_photo.png candidate
import shutil
shutil.copy(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_levels.png',
            r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_photo_candidate.png')
print('Saved track_photo_candidate.png')

def _dist2(a, b): return (a[0]-b[0])**2 + (a[1]-b[1])**2
