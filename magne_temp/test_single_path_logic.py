"""Test the single-master-path logic without GUI."""
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor\Track Alignment program')
from main import (
    load_waypoints, _build_master_from_paths, _reduce_to_anchors,
    _resample, _split_master_into_paths, PATH_ORDER, _poly_length,
)
from PIL import Image, ImageDraw

wps = load_waypoints(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\track_photo.py')
print('Loaded paths:', {k: len(v) for k, v in wps.items()})

master, splits = _build_master_from_paths(wps)
print('Master points:', len(master), 'splits:', splits)
print('Master length:', _poly_length(master))

anchors = _reduce_to_anchors(master, splits, epsilon=8.0)
print('Anchor indices:', len(anchors))

# Resample master
master2 = _resample(master, 6.0)
print('Resampled master:', len(master2))

# Recompute splits in resampled master
def dist2(a, b): return (a[0]-b[0])**2 + (a[1]-b[1])**2
old_junctions = [master[idx] for idx in splits]
splits2 = [min(range(len(master2)), key=lambda i: dist2(master2[i], j)) for j in old_junctions]
print('New splits:', splits2)

plc = _split_master_into_paths(master2, splits2)
print('PLC points:', {k: len(v) for k, v in plc.items()})

# Draw preview
img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
draw = ImageDraw.Draw(img)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
for pid in PATH_ORDER:
    pts = plc[pid]
    color = colors[pid-1]
    draw.line(pts, fill=color, width=2)
    for x, y in pts[::max(1, len(pts)//10)]:
        draw.ellipse([x-4, y-4, x+4, y+4], fill=color)

# Draw anchor points
for idx in anchors:
    x, y = master[idx]
    is_split = idx in splits
    r = 8 if is_split else 5
    draw.ellipse([x-r, y-r, x+r, y+r], fill=(255,255,0), outline=(0,0,0), width=2)

img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\single_path_preview.png')
print('Saved single_path_preview.png')
