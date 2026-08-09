"""Check if HSV red mask captures the guide line, overlay waypoints."""
import numpy as np
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)

# Load mask from previous script
mask = np.array(Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_hsv_np_mask.png')) > 0

out = Image.fromarray(arr)
draw = ImageDraw.Draw(out)
ys, xs = np.where(mask)
for x, y in zip(xs, ys):
    draw.point((x, y), fill=(255, 255, 0))

colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,128,0)]
for pid, pts in PATH_WAYPOINTS_PX.items():
    color = colors[pid % len(colors)]
    for i, (x, y) in enumerate(pts):
        r = 5 if i % 5 == 0 else 3
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    if len(pts) > 1:
        draw.line(pts, fill=color, width=2)
out.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\waypoints_on_red_mask.png')
print('Saved waypoints_on_red_mask.png')

# Count pixels per horizontal band
for yband in [(0,100),(100,200),(200,400),(400,600),(600,672)]:
    cnt = mask[yband[0]:yband[1], :].sum()
    print(f'Y {yband[0]}-{yband[1]}: {cnt} red pixels')
