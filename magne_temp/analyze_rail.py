"""Analyze track_photo.png rail edges and propose shifted waypoints."""
import numpy as np
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_photo.png').convert('RGB')
arr = np.array(img)
print('Image size:', arr.shape)


def perpendicular_direction(pts, idx):
    """Return unit normal vector pointing to the LEFT of travel direction
    (i.e., toward 'top' of rail if travel is left-to-right; but we need top,
    which is screen-up = -Y, so we may need to flip based on section)."""
    n = len(pts)
    if n < 2:
        return (0, -1)
    a = max(0, idx - 1)
    b = min(n - 1, idx + 1)
    dx = pts[b][0] - pts[a][0]
    dy = pts[b][1] - pts[a][1]
    length = np.hypot(dx, dy)
    if length == 0:
        return (0, -1)
    # perpendicular to travel: (-dy, dx) is 90 deg CCW (left of travel)
    return (-dy / length, dx / length)


def sample_line(arr, x0, y0, nx, ny, length=60, step=1.0):
    """Sample RGB values along a line from (x0,y0) in direction (nx,ny) for +/- length."""
    pts = []
    vals = []
    for d in np.arange(-length, length + 1e-6, step):
        x = int(round(x0 + nx * d))
        y = int(round(y0 + ny * d))
        if 0 <= x < arr.shape[1] and 0 <= y < arr.shape[0]:
            pts.append((x, y, d))
            vals.append(arr[y, x].mean())
    return pts, np.array(vals)


def find_top_edge(vals, pts, direction_sign):
    """Find the transition from dark background to bright rail top edge.
    direction_sign: +1 means increasing d is the search direction, -1 means decreasing d.
    We want the first bright edge in the search direction."""
    # Smooth
    from scipy.ndimage import gaussian_filter1d
    smooth = gaussian_filter1d(vals.astype(float), sigma=2)
    # Take derivative
    grad = np.gradient(smooth)
    # Search from center outward in the specified direction
    if direction_sign > 0:
        idxs = range(len(grad) // 2, len(grad) - 3)
    else:
        idxs = range(len(grad) // 2, 2, -1)
    for i in idxs:
        # strong positive gradient = entering bright rail
        if grad[i] > 8 and grad[i + 1] > 5:
            return pts[i][2]  # return signed distance d
    return None


def shift_waypoints_to_top(pts, target_d_offset=-18):
    """Shift each waypoint along its local perpendicular by target_d_offset pixels.
    Negative d means toward 'left' of travel. We need to determine the correct sign
    per path/section so that it goes to the top edge."""
    new_pts = []
    for i, (x, y) in enumerate(pts):
        nx, ny = perpendicular_direction(pts, i)
        new_pts.append((x + nx * target_d_offset, y + ny * target_d_offset))
    return new_pts


# Let's first just look at samples for Path 6
print('\n=== Path 6 samples (top horizontal rail) ===')
pts6 = PATH_WAYPOINTS_PX[6]
for idx in [0, 4, 8, 12, 16]:
    x, y = pts6[idx]
    nx, ny = perpendicular_direction(pts6, idx)
    sample_pts, vals = sample_line(arr, x, y, nx, ny, length=50)
    # Find bright edge in both directions
    edge_pos = find_top_edge(vals, sample_pts, +1)
    edge_neg = find_top_edge(vals, sample_pts, -1)
    print(f'  idx={idx:2d} center=({x:.0f},{y:.0f}) normal=({nx:+.2f},{ny:+.2f}) pos_edge_d={edge_pos} neg_edge_d={edge_neg}')
    print(f'    val range: {vals.min():.0f}-{vals.max():.0f}, center={vals[len(vals)//2]:.0f}')

# Quick visualization: draw current centerline and a shifted version
out = img.copy()
draw = ImageDraw.Draw(out)
for pid, pts in PATH_WAYPOINTS_PX.items():
    # draw original centerline
    draw.line([(x, y) for x, y in pts], fill=(255, 0, 0), width=2)
    # draw shifted "left of travel" by 18px
    shifted = shift_waypoints_to_top(pts, -18)
    draw.line([(x, y) for x, y in shifted], fill=(0, 255, 0), width=2)
out.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\shift_preview_left18.png')

# Also try +18
out2 = img.copy()
draw2 = ImageDraw.Draw(out2)
for pid, pts in PATH_WAYPOINTS_PX.items():
    draw2.line([(x, y) for x, y in pts], fill=(255, 0, 0), width=2)
    shifted = shift_waypoints_to_top(pts, +18)
    draw2.line([(x, y) for x, y in shifted], fill=(0, 255, 255), width=2)
out2.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\shift_preview_right18.png')

print('\nSaved shift_preview_left18.png and shift_preview_right18.png')
