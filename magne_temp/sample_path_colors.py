"""Sample colors along current waypoints to characterize the red/orange line."""
import numpy as np
from PIL import Image
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor')
from mm_monitor.track_photo import PATH_WAYPOINTS_PX

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)

for pid, pts in PATH_WAYPOINTS_PX.items():
    print(f'\nPath {pid}:')
    for i in [0, len(pts)//4, len(pts)//2, 3*len(pts)//4, -1]:
        x, y = int(round(pts[i][0])), int(round(pts[i][1]))
        if 0 <= x < arr.shape[1] and 0 <= y < arr.shape[0]:
            c = arr[y, x]
            print(f'  ({x:4d},{y:4d}) RGB=({c[0]:3d},{c[1]:3d},{c[2]:3d})')
