"""Detect rail top edges in full_track_grid.png and generate waypoints."""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter1d

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)
h, w, _ = arr.shape
r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)

# Color masks for rail sections
# Green rail (top-left main): G dominant, R and B lower
green_mask = (g > 120) & (g > r + 30) & (g > b + 30)
# Purple rail (left spur): R and B high, G lower
purple_mask = (r > 100) & (b > 100) & (g < r - 20) & (g < b - 20)
# Blue rail (right spur): B dominant, R and G lower
blue_mask = (b > 120) & (b > r + 30) & (b > g + 30)

# Silver/gray rail: all channels similar and not too bright (not background)
gray_mask = (np.abs(r - g) < 25) & (np.abs(g - b) < 25) & (np.abs(r - b) < 25) & (r < 200) & (r > 80)

# Remove green/purple/blue from gray mask
gray_mask &= ~green_mask & ~purple_mask & ~blue_mask

print(f'Green pixels: {green_mask.sum()}')
print(f'Purple pixels: {purple_mask.sum()}')
print(f'Blue pixels: {blue_mask.sum()}')
print(f'Gray pixels: {gray_mask.sum()}')

# Save masks
overlay = arr.copy()
overlay[green_mask] = [255, 255, 0]
overlay[purple_mask] = [255, 0, 255]
overlay[blue_mask] = [0, 255, 255]
overlay[gray_mask] = [255, 128, 0]
Image.fromarray(overlay).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\rail_color_mask.png')

# For each mask, find the top edge (minimum y per x)
def top_edge(mask, x_range):
    edge = []
    for x in range(x_range[0], x_range[1]):
        ys = np.where(mask[:, x])[0]
        if len(ys) > 0:
            edge.append((x, int(ys.min())))
    return edge

# Path 6: top main rail. Combine green + gray in upper half.
path6_mask = (green_mask | gray_mask) & (np.arange(h)[:, None] < 250)
path6_edge = top_edge(path6_mask, (50, 1550))
print(f'Path 6 edge points: {len(path6_edge)}')

# Path 3: lower connector. Gray in middle band.
path3_mask = gray_mask & (np.arange(h)[:, None] > 150) & (np.arange(h)[:, None] < 280)
path3_edge = top_edge(path3_mask, (400, 1500))
print(f'Path 3 edge points: {len(path3_edge)}')

# Path 2: right spur (blue). Find left edge? No, for right spur we want the top/outer edge.
# The spur is a U-shape. We need the right edge when going down, bottom curve, then left edge when going up?
# Actually for a U on the right, the pallet travels down the LEFT leg, around the bottom, up the RIGHT leg (or vice versa).
# The "top edge" of the rail: when viewed from above, the rail has two edges. We want one consistent edge.
# For the right spur, let's take the OUTER edge (right side going down, left side going up? No, outer is the rightmost edge throughout).
# Actually, for a U-shaped rail, the two legs are parallel. The "top edge" could mean the top surface edge facing the camera.
# In the 3D render, the rail is an extrusion. We want the upper edge of the visible top surface.
# For a vertical rail, the top surface edge is the upper horizontal edge of the profile.
# Let's find the top edge of the blue mask (minimum y per x) for the upper parts, but for vertical legs the top edge is the upper side.

# For now, let's sample the top edge of blue mask across its x-range.
path2_mask = blue_mask
path2_edge = top_edge(path2_mask, (1200, 1580))
print(f'Path 2 edge points: {len(path2_edge)}')

# Path 4: left spur (purple)
path4_mask = purple_mask
path4_edge = top_edge(path4_mask, (0, 600))
print(f'Path 4 edge points: {len(path4_edge)}')

# Draw edges on original
out = img.copy()
draw = ImageDraw.Draw(out)
for pts, color in [(path6_edge, (255,0,0)), (path3_edge, (0,255,0)), (path2_edge, (0,0,255)), (path4_edge, (255,0,255))]:
    if len(pts) > 1:
        draw.line(pts, fill=color, width=2)
    for x, y in pts[::10]:
        draw.ellipse([x-3, y-3, x+3, y+3], fill=color)
out.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\rail_top_edges.png')
print('Saved rail_top_edges.png')
