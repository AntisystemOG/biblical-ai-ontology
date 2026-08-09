"""Detect red guide line using HSV color space."""
import numpy as np
from PIL import Image
import cv2

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)
hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)

# Red wraps around hue 0/180. Use two ranges and combine.
lower1 = np.array([0, 100, 50])
upper1 = np.array([10, 255, 255])
lower2 = np.array([160, 100, 50])
upper2 = np.array([180, 255, 255])
mask1 = cv2.inRange(hsv, lower1, upper1)
mask2 = cv2.inRange(hsv, lower2, upper2)
mask = cv2.bitwise_or(mask1, mask2)

# Save mask
Image.fromarray(mask).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_hsv_mask.png')
print('Red HSV pixels:', mask.sum() // 255)

# Overlay on original
overlay = arr.copy()
overlay[mask > 0] = [255, 255, 0]  # yellow highlight
Image.fromarray(overlay).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_hsv_overlay.png')
print('Saved overlays')

# Try skeletonization
from skimage.morphology import skeletonize
skel = skeletonize(mask // 255).astype(np.uint8) * 255
Image.fromarray(skel).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_skeleton.png')
print('Skeleton pixels:', skel.sum() // 255)
