"""Draw current PATH_WAYPOINTS_PX on current track_photo.png to verify alignment."""
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX
from PIL import Image, ImageDraw

img = Image.open(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\data\track_photo.png').convert('RGB')
draw = ImageDraw.Draw(img)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
for pid in sorted(PATH_WAYPOINTS_PX.keys()):
    pts = PATH_WAYPOINTS_PX[pid]
    color = colors[(pid-1) % len(colors)]
    if len(pts) > 1:
        draw.line([(x, y) for x, y in pts], fill=color, width=3)
    for i, (x, y) in enumerate(pts):
        if i % 10 == 0:
            r = 6
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\waypoints_verification.png')
print('Saved waypoints_verification.png')
