"""Find top edges of rails in full_track_grid.png using gradient analysis."""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, sobel

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img).astype(float)
h, w, _ = arr.shape

# Grayscale
gray = arr.mean(axis=2)
# Smooth
smooth = gaussian_filter(gray, sigma=1.5)
# Vertical gradient (positive = getting brighter downward)
grad_y = sobel(smooth, axis=0)

# Top edge of an object: strong positive gradient in y (dark above, bright below?)
# Actually rail is darker than background, so top edge is bright(above) -> dark(below)
# That means grad_y = below - above = dark - bright = negative
# We want strong negative gradient, but not part of text/grid.
# Use a threshold on the gradient magnitude.

# Background mask: very bright
bg_mask = smooth > 220

# Top edge mask: smooth is not background, and grad_y is strongly negative
# (transition from background above to rail below)
top_edge_mask = (~bg_mask) & (grad_y < -15)

# Remove grid text: top 60px and very bottom
edge_img = (top_edge_mask * 255).astype(np.uint8)
Image.fromarray(edge_img).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\top_edges_raw.png')

# Hough or simple per-column top edge
# For each column, find the topmost edge pixel that is part of a connected component
from skimage.measure import label
labeled, num = label(top_edge_mask, connectivity=2, return_num=True)
print('Components:', num)

# Visualize
overlay = arr.copy()
overlay[top_edge_mask] = [255, 0, 0]
Image.fromarray(overlay.astype(np.uint8)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\top_edges_overlay.png')
print('Saved overlays')
