"""Measure perpendicular offset from current red line to rail top edge."""
import numpy as np
from PIL import Image
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img).astype(float)
h, w, _ = arr.shape

# Red line mask (same HSV method as before)
def rgb_to_hsv(rgb):
    rgb = rgb.astype(float)
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    diff = mx - mn
    v = mx
    s = np.where(mx > 0, diff / mx * 255, 0)
    h = np.zeros_like(mx)
    mask = diff > 0
    mr = mask & (mx == r)
    h[mr] = ((g[mr] - b[mr]) / diff[mr] * 60) % 360
    mg = mask & (mx == g)
    h[mg] = ((b[mg] - r[mg]) / diff[mg] * 60 + 120) % 360
    mb = mask & (mx == b)
    h[mb] = ((r[mb] - g[mb]) / diff[mb] * 60 + 240) % 360
    return h, s, v

hue, sat, val = rgb_to_hsv(arr)
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
red_mask = ((hue < 20) | (hue > 340)) & (sat > 80) & (val > 80)
red_mask &= (r > g + 20) & (r > b + 20)
# Exclude top edge text and very bright labels by requiring not too high V
# Actually the red line is the largest thin component. Let's just keep all and work per-path.

# Rail mask: detect the colored rail. It's not white/gray background.
# Background is light gray/white. Rail colors are green, purple, blue, silver.
# Use saturation: rail has some color (sat > 15) OR it is dark-ish metal.
# More robust: background is very bright and low saturation.
bg_mask = (val > 200) & (sat < 30)
rail_mask = ~bg_mask
# Exclude text labels by size? Hard. Let's just use it for vertical scans near current waypoints.

# For each current waypoint, find the nearest red pixel (red line) and nearest rail top edge
# in the perpendicular direction.
from scipy.ndimage import distance_transform_edt
red_dists, red_nearest = distance_transform_edt(~red_mask, return_distances=True, return_indices=True)
# Actually we want index of nearest red pixel
ys_red, xs_red = np.where(red_mask)
red_pts = np.column_stack([xs_red, ys_red])

def perpendicular(pts, idx):
    n = len(pts)
    a = max(0, idx - 1)
    b = min(n - 1, idx + 1)
    dx = pts[b][0] - pts[a][0]
    dy = pts[b][1] - pts[a][1]
    length = np.hypot(dx, dy)
    if length == 0:
        return (0, -1)
    # Two normals: (dy, -dx) and (-dy, dx). Pick the one pointing toward the rail top edge.
    # For now return both.
    return (dy / length, -dx / length), (-dy / length, dx / length)

# For Path 6, sample at multiple X and find red-line Y and rail-top Y
print('=== Path 6: red line Y vs rail top Y ===')
pts6 = PATH_WAYPOINTS_PX[6]
for idx in range(0, len(pts6), 3):
    x, y = pts6[idx]
    # nearest red
    dists = np.hypot(red_pts[:,0] - x, red_pts[:,1] - y)
    nr_idx = dists.argmin()
    rx, ry = red_pts[nr_idx]
    # Search upward from red line for rail top edge
    # A vertical scan at x=rx, from ry upward until we hit rail_mask
    top_y = None
    for yy in range(int(ry) - 1, 0, -1):
        if rail_mask[yy, int(rx)]:
            # check if it's the top edge: pixel above is background
            if yy > 0 and not rail_mask[yy - 1, int(rx)]:
                top_y = yy
                break
    if top_y is None:
        # find first rail pixel
        for yy in range(int(ry) - 1, 0, -1):
            if rail_mask[yy, int(rx)]:
                top_y = yy
                break
    print(f'  x={x:5.0f} red_y={ry:5.1f} rail_top_y={top_y} offset={top_y-ry if top_y else None}')
