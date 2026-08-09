"""Remove red grid lines from white-balanced track image."""
import numpy as np
from PIL import Image
from scipy.ndimage import median_filter, binary_dilation

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

# Start from white-balanced image
img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_white_balanced.png').convert('RGB')
arr = np.array(img).astype(float)

hue, sat, val = rgb_to_hsv(arr)
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

# Detect red grid: red hue, not too saturated, R clearly dominant
# Grid lines are likely (R high, G/B lower) but not as pure as the axis text
red_mask = ((hue < 30) | (hue > 330)) & (sat > 15) & (sat < 180) & (r > g + 15) & (r > b + 15) & (val > 80)

# Remove rail colors: don't classify green/purple/blue as red
# If G or B is very high, it's probably a rail, not grid
red_mask &= ~((g > 150) | (b > 150))

# Dilate slightly
red_mask = binary_dilation(red_mask, iterations=1)
print('Red grid pixels:', red_mask.sum())

# Inpaint carefully: only for masked pixels, use median of a small window
# but pre-fill with a neutral color to avoid edge effects
out = arr.copy()
for c in range(3):
    ch = out[:,:,c].copy()
    valid = ~red_mask
    fill_val = np.median(ch[valid])
    ch[~valid] = fill_val
    # Apply small median filter and restore only masked pixels
    smoothed = median_filter(ch, size=5)
    ch[~valid] = smoothed[~valid]
    out[:,:,c] = ch

out = np.clip(out, 0, 255).astype(np.uint8)
Image.fromarray(out).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_clean_v3.png')
print('Saved track_clean_v3.png')
