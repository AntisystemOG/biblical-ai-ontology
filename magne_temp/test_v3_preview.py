"""Generate final preview of v3 tool defaults."""
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor\Track Alignment program')
from main import load_waypoints, _build_anchors_from_paths, _generate_plc_paths, PATH_ORDER
from PIL import Image, ImageDraw

wps = load_waypoints(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\track_photo.py')
anchors, junctions = _build_anchors_from_paths(wps, epsilon=4.0)
plc = _generate_plc_paths(anchors, junctions, spacing=6.0, smooth=False)

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
draw = ImageDraw.Draw(img)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
for pid in PATH_ORDER:
    pts = plc[pid]
    color = colors[pid-1]
    draw.line(pts, fill=color, width=2)
for i, (x, y) in enumerate(anchors):
    is_junction = i in junctions
    r = 8 if is_junction else 5
    draw.ellipse([x-r, y-r, x+r, y+r], fill=(255,255,0), outline=(0,0,0), width=2)
img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\v3_final_preview.png')
print('Saved v3_final_preview.png')
print('Anchors:', len(anchors), 'Junctions:', junctions)
