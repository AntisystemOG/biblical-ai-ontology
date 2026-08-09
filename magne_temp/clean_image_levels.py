"""Remove subtle grid by applying levels: background becomes pure white."""
import numpy as np
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_white_balanced.png').convert('RGB')
arr = np.array(img).astype(float)

# Brightness
brightness = arr.max(axis=2)

# Find a threshold that separates background from rails
# Rails are darker than background. Use Otsu or percentile.
# Background is roughly above 200, rails below.
# We'll compress the background range to white.

# Method: for each pixel, if it's bright (background-like), push it to white.
# Use a smooth transition.

# Compute threshold from histogram
hist, bins = np.histogram(brightness, bins=256, range=(0, 256))
# Otsu threshold
def otsu(hist):
    total = hist.sum()
    sum_total = np.sum(hist * np.arange(256))
    sum_bg = 0
    weight_bg = 0
    max_var = 0
    threshold = 0
    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break
        sum_bg += t * hist[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        var = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if var > max_var:
            max_var = var
            threshold = t
    return threshold

thr = otsu(hist)
print('Otsu threshold:', thr)

# Apply levels: brighten everything above threshold toward white, keep below
# Use a smooth S-curve or just raise shadows
out = arr.copy()
# Increase contrast: map [0, thr] to [0, 255] and clamp above-threshold to 255
out = np.clip((out / thr) * 255, 0, 255)

# Alternative: just make bright pixels white
mask = brightness > thr * 0.7
for c in range(3):
    out[:,:,c][mask] = 255

out = np.clip(out, 0, 255).astype(np.uint8)
Image.fromarray(out).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_levels.png')
print('Saved track_levels.png')
