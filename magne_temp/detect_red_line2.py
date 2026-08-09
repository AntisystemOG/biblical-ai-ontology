"""Better red line detection using color ratios and connected components."""
import numpy as np
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX
from scipy.ndimage import label

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img).astype(float)
h, w, _ = arr.shape
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

# red-ish: R dominant, R-G high, R-B high, and R above moderate threshold
red_mask = (r > 120) & (r > g + 30) & (r > b + 30)
# Exclude top edge: only keep pixels below y=60
red_mask[:60, :] = False
# Exclude very bottom too (grid labels)
red_mask[-50:, :] = False

# Label connected components, keep the largest
labeled, num = label(red_mask)
print('Components:', num)
sizes = np.bincount(labeled.ravel())[1:]
print('Component sizes:', sorted(sizes, reverse=True)[:10])
largest = np.argmax(sizes) + 1
red_mask = (labeled == largest)
print('Largest component pixels:', red_mask.sum())

# Save refined mask
mask_img = Image.fromarray((red_mask * 255).astype(np.uint8))
mask_img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_mask_refined.png')

# Overlay current waypoints
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
out.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\waypoints_on_grid2.png')
print('Saved waypoints_on_grid2.png')

# Compute distances to refined red line
ys, xs = np.where(red_mask)
red_pts = np.column_stack([xs, ys])
print('Number of red points:', len(red_pts))

for pid, pts in PATH_WAYPOINTS_PX.items():
    print(f'\nPath {pid}:')
    for i in [0, len(pts)//2, -1]:
        x, y = pts[i]
        dists = np.hypot(red_pts[:,0] - x, red_pts[:,1] - y)
        nearest = dists.min()
        nx, ny = red_pts[dists.argmin()]
        print(f'  wp[{i:3d}] current=({x:6.1f},{y:6.1f}) nearest_red=({nx:6.1f},{ny:6.1f}) dist={nearest:5.1f}px')
