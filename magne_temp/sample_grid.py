"""Sample pixel colors at grid and non-grid locations."""
import numpy as np
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)

# Sample at various locations
samples = [
    (50, 50, 'top-left corner'),
    (200, 200, 'background near top-left'),
    (400, 400, 'background center-left'),
    (800, 600, 'background lower-middle'),
    (1200, 300, 'background center-right'),
    (1500, 600, 'background lower-right'),
    (700, 95, 'top rail path6'),
    (500, 200, 'lower rail path3'),
    (1520, 450, 'right spur path2'),
    (400, 450, 'left spur path4'),
]
for x, y, desc in samples:
    c = arr[y, x]
    print(f'{desc:25s} ({x:4d},{y:4d}) RGB=({c[0]:3d},{c[1]:3d},{c[2]:3d})')
