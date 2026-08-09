"""Remove red grid labels/lines from full_track_grid.png."""
import numpy as np
from PIL import Image
from scipy.ndimage import median_filter

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
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

# Detect red grid: red-ish, not too dark, not the rail colors
# Red has hue near 0 or 360, moderate saturation and value
red_mask = ((hue < 25) | (hue > 335)) & (sat > 50) & (val > 80) & (val < 240)
# Exclude rail colors: if green/blue channel is high, it's not pure red text
# The text is pure-ish red; rails are green/blue/purple/gray
# Keep only pixels where R is clearly dominant
red_mask &= (r > g + 30) & (r > b + 30)

print('Red grid pixels detected:', red_mask.sum())

# Inpaint: for each red pixel, use median of a local neighborhood after removing red pixels
# Simple approach: fill with background color. The background is light gray/white.
# Use a median filter on the image with red pixels masked out.

# Create a filled background image by replacing red pixels with NaN and using median
filled = arr.copy().astype(float)
filled[red_mask] = np.nan

# For each channel, fill NaNs with median of nearby non-NaN pixels
from scipy.ndimage import generic_filter

def nan_median(window):
    vals = window[~np.isnan(window)]
    return np.median(vals) if len(vals) > 0 else 255.0

for c in range(3):
    ch = filled[:,:,c]
    # Find NaN pixels
    nan_mask = np.isnan(ch)
    if not nan_mask.any():
        continue
    # Use median filter with a footprint; but generic_filter with NaN handling is slow on large images.
    # Faster: just replace NaNs with local median of valid neighbors using convolution.
    # For simplicity, iterate a few times with a small median filter on filled values.
    # First fill NaNs with a coarse global median
    global_median = np.nanmedian(ch)
    ch[nan_mask] = global_median
    # Then apply median filter a few times to smooth
    for _ in range(3):
        ch = median_filter(ch, size=5)
        ch[nan_mask] = median_filter(ch, size=5)[nan_mask]
    filled[:,:,c] = ch

out = np.clip(filled, 0, 255).astype(np.uint8)
Image.fromarray(out).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_no_grid.png')
print('Saved track_no_grid.png')
