"""Generate final verification image from project files."""
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX
from PIL import Image, ImageDraw

img = Image.open(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\data\track_photo.png').convert('RGB')
draw = ImageDraw.Draw(img)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
for pid in sorted(PATH_WAYPOINTS_PX.keys()):
    pts = PATH_WAYPOINTS_PX[pid]
    color = colors[pid-1]
    draw.line(pts, fill=color, width=2)
    for i, (x, y) in enumerate(pts):
        if i % 30 == 0:
            draw.ellipse([x-4, y-4, x+4, y+4], fill=color)
img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\final_track_verification.png')
print('Saved final_track_verification.png')
