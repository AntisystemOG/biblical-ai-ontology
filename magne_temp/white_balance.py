"""White-balance the track image to remove the pinkish/red color cast."""
import numpy as np
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img).astype(float)

# Simple white balance using the bright background pixels as reference.
# Find pixels that are bright (above 80th percentile brightness)
brightness = arr.max(axis=2)
threshold = np.percentile(brightness, 80)
bright_mask = brightness > threshold

# Compute mean color of bright background
mean_bg = arr[bright_mask].mean(axis=0)
print('Bright background mean:', mean_bg)

# Scale each channel so that this mean becomes white (255,255,255)
scale = 255.0 / mean_bg
print('Channel scales:', scale)

# Apply scale, but don't oversaturate dark pixels
balanced = arr * scale
balanced = np.clip(balanced, 0, 255).astype(np.uint8)

Image.fromarray(balanced).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_white_balanced.png')
print('Saved track_white_balanced.png')
