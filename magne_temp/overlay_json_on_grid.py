"""Overlay JSON waypoints on full_track_grid.png for visual check."""
import json
from PIL import Image, ImageDraw

with open(r'C:\AI Projects\MagneMotionMonitor\Track Alignment program\waypoints_from_recording.json') as f:
    wps = json.load(f)

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
draw = ImageDraw.Draw(img)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,128,0)]
for pid_str, pts in wps.items():
    pid = int(pid_str)
    color = colors[pid % len(colors)]
    if len(pts) > 1:
        draw.line([(x, y) for x, y in pts], fill=color, width=3)
    for i, (x, y) in enumerate(pts):
        if i % 10 == 0:
            r = 6
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\json_on_grid.png')
print('Saved json_on_grid.png')
