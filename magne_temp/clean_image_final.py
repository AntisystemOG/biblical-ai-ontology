"""Create final clean track image: white balance + remove red axis labels + mild grid removal."""
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation

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

# Load original
img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img).astype(float)

# Step 1: white balance
brightness = arr.max(axis=2)
threshold = np.percentile(brightness, 80)
bright_mask = brightness > threshold
mean_bg = arr[bright_mask].mean(axis=0)
scale = 255.0 / mean_bg
arr = arr * scale
arr = np.clip(arr, 0, 255)

# Step 2: remove red axis labels and any strongly red pixels
hue, sat, val = rgb_to_hsv(arr)
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
red_mask = ((hue < 25) | (hue > 335)) & (sat > 30) & (r > g + 25) & (r > b + 25) & (val > 80)
# Exclude green/blue/purple rails
red_mask &= ~((g > 180) | (b > 180) | ((r > 150) & (b > 120) & (g < 120)))
# Also mask top and left border strips to remove axis text
red_mask[:70, :] = True
red_mask[:, :60] = True

red_mask = binary_dilation(red_mask, iterations=1)
print('Masked pixels:', red_mask.sum())

# Inpaint with local median
from scipy.ndimage import median_filter
out = arr.copy()
for c in range(3):
    ch = out[:,:,c].copy()
    valid = ~red_mask
    fill_val = np.median(ch[valid])
    ch[~valid] = fill_val
    for _ in range(3):
        smoothed = median_filter(ch, size=5)
        ch[~valid] = smoothed[~valid]
    out[:,:,c] = ch

out = np.clip(out, 0, 255).astype(np.uint8)
Image.fromarray(out).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_clean_final.png')
print('Saved track_clean_final.png')
