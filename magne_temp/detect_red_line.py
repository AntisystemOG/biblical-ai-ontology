"""Detect the red guide line in full_track_grid.png and compare to current waypoints."""
import numpy as np
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)
h, w, _ = arr.shape

# Detect red pixels: R high, G and B low-ish
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
red_mask = (r > 150) & (g < 100) & (b < 100)
print('Red pixels:', red_mask.sum())

# Save mask as image
mask_img = Image.fromarray((red_mask * 255).astype(np.uint8))
mask_img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_mask.png')

# Overlay current waypoints on the full grid image
out = img.copy()
draw = ImageDraw.Draw(out)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,128,0)]
for pid, pts in PATH_WAYPOINTS_PX.items():
    color = colors[pid % len(colors)]
    for i, (x, y) in enumerate(pts):
        r = 5 if i % 5 == 0 else 3
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    if len(pts) > 1:
        draw.line(pts, fill=color, width=2)
out.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\waypoints_on_grid.png')
print('Saved waypoints_on_grid.png')

# Compute distance from each current waypoint to nearest red pixel
ys, xs = np.where(red_mask)
red_pts = np.column_stack([xs, ys])
print('Number of red points:', len(red_pts))

# For each path, print nearest red distance for a few waypoints
for pid, pts in PATH_WAYPOINTS_PX.items():
    print(f'\nPath {pid}:')
    for i in [0, len(pts)//2, -1]:
        x, y = pts[i]
        dists = np.hypot(red_pts[:,0] - x, red_pts[:,1] - y)
        nearest = dists.min()
        nx, ny = red_pts[dists.argmin()]
        print(f'  wp[{i:3d}] current=({x:6.1f},{y:6.1f}) nearest_red=({nx:6.1f},{ny:6.1f}) dist={nearest:5.1f}px')
