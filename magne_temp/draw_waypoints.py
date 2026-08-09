from PIL import Image, ImageDraw
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_photo.png')
print('Size:', img.size)
draw = ImageDraw.Draw(img, 'RGBA')
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,128,0)]
for pid, pts in PATH_WAYPOINTS_PX.items():
    color = colors[pid % len(colors)]
    for i, (x, y) in enumerate(pts):
        r = 5 if i % 5 == 0 else 3
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    if len(pts) > 1:
        draw.line(pts, fill=color, width=2)
img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\waypoints_overlay.png')
print('saved overlay')
