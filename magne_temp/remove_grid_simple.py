"""Remove red grid by covering top/left border strips with background color."""
import numpy as np
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img).copy()
h, w, _ = arr.shape

# Fill top strip (grid X labels) and left strip (grid Y labels) with background color
# Use average color of a safe background region
bg_sample = arr[80:120, 80:120]  # area inside the grid, should be background
bg_color = tuple(np.median(bg_sample, axis=(0,1)).astype(int))
print('Background color:', bg_color)

arr[:60, :] = bg_color       # top strip
arr[:, :50] = bg_color       # left strip

out = Image.fromarray(arr)
out.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_no_grid_simple.png')
print('Saved track_no_grid_simple.png')
