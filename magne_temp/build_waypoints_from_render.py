"""Build top-edge waypoints from full_track_grid.png using rail segmentation + skeletonization."""
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_opening, binary_closing, distance_transform_edt
from skimage.morphology import skeletonize
from skimage.measure import label as sk_label


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


img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)
h, w, _ = arr.shape
hue, sat, val = rgb_to_hsv(arr)

# Background: very bright, low saturation
bg_mask = (val > 210) & (sat < 35)
non_bg = ~bg_mask

# Rail color masks
teal_mask = ((hue > 140) & (hue < 210)) & (sat > 25) & (val > 60) & non_bg
purple_mask = ((hue > 250) & (hue < 330)) & (sat > 30) & (val > 60) & non_bg
blue_mask = ((hue > 200) & (hue < 260)) & (sat > 40) & (val > 80) & non_bg
gray_mask = (sat < 55) & (val > 70) & (val < 190) & non_bg

# Clean each
for m in [teal_mask, purple_mask, blue_mask, gray_mask]:
    m[:] = binary_closing(binary_opening(m, iterations=1), iterations=2)

rail_mask = teal_mask | purple_mask | blue_mask | gray_mask
rail_mask = binary_closing(rail_mask, iterations=2)

# Remove grid border labels by removing top 60px and left/right edges from rail
rail_mask[:60, :] = False
rail_mask[-40:, :] = False
rail_mask[:, :30] = False
rail_mask[:, -30:] = False

Image.fromarray((rail_mask * 255).astype(np.uint8)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\rail_final_mask.png')
print('Final rail pixels:', rail_mask.sum())

# Skeletonize
skel = skeletonize(rail_mask)
# Distance from background (for width measurement)
dist = distance_transform_edt(rail_mask)
Image.fromarray((skel * 255).astype(np.uint8)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\rail_skeleton.png')
print('Skeleton pixels:', skel.sum())

# Approximate rail width = median of 2*dist on skeleton
widths = dist[skel] * 2
print(f'Median rail width: {np.median(widths):.1f}px, mean={widths.mean():.1f}')

# Now we need to separate skeleton into 6 paths. Use region labels based on colored masks.
# Path 6: top main rail = teal + gray in upper half (y < 250)
# Path 3: lower connector = gray in middle band (150 < y < 280)
# Path 2: right spur = blue (x > 1200)
# Path 4: left spur = purple (x < 600)
# Path 1: tiny connector at right junction
# Path 5: tiny connector/cleanout at left junction

# Label skeleton pixels by path based on nearest colored region
path_assignment = np.zeros((h, w), dtype=int)
path_assignment[teal_mask | (gray_mask & (np.arange(h)[:, None] < 220))] = 6
path_assignment[gray_mask & (np.arange(h)[:, None] >= 180) & (np.arange(h)[:, None] < 270)] = 3
path_assignment[blue_mask] = 2
path_assignment[purple_mask] = 4

# For skeleton pixels near path 2 and 4 tops, also assign path 1 and 5
# Heuristic: skeleton pixels in small regions between path 6/3 and spurs
# We'll use connected component labeling on skeleton and classify each component.

# Connected components on skeleton
skel_labels, num = sk_label(skel, return_num=True, connectivity=2)
print(f'Skeleton components: {num}')

# For each component, find the dominant path assignment (mode of overlapping path_assignment pixels)
from scipy.stats import mode
new_wps = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

for comp_id in range(1, num + 1):
    comp_mask = (skel_labels == comp_id)
    comp_y, comp_x = np.where(comp_mask)
    if len(comp_y) < 10:
        continue
    # mode of path_assignment in this component
    vals = path_assignment[comp_mask]
    unique, counts = np.unique(vals[vals > 0], return_counts=True)
    if len(unique) == 0:
        continue
    dominant = unique[counts.argmax()]
    # Sort component pixels by approximate arc-length using nearest-neighbor
    pts = list(zip(comp_x.tolist(), comp_y.tolist()))
    # Simple ordering: start from one end, greedily follow nearest neighbor
    ordered = [pts[0]]
    remaining = set(pts[1:])
    while remaining:
        last = ordered[-1]
        nearest = min(remaining, key=lambda p: (p[0]-last[0])**2 + (p[1]-last[1])**2)
        ordered.append(nearest)
        remaining.remove(nearest)
    # Downsample to ~50 points max
    if len(ordered) > 60:
        step = len(ordered) // 50
        ordered = ordered[::step]
    new_wps[dominant].extend(ordered)

# Sort paths and save
for pid in new_wps:
    print(f'Path {pid}: {len(new_wps[pid])} points')

# Draw result
out = img.copy()
draw = ImageDraw.Draw(out)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
for pid in sorted(new_wps):
    pts = new_wps[pid]
    if len(pts) > 1:
        draw.line(pts, fill=colors[pid-1], width=2)
    for x, y in pts[::max(1, len(pts)//20)]:
        r = 5
        draw.ellipse([x-r, y-r, x+r, y+r], fill=colors[pid-1])
out.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\auto_waypoints.png')
print('Saved auto_waypoints.png')

# Save to JSON for inspection
with open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\auto_waypoints.json', 'w') as f:
    json.dump({str(k): [[float(x), float(y)] for x, y in v] for k, v in new_wps.items()}, f, indent=2)
