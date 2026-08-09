"""Remove red grid overlay from full_track_grid.png using better detection + inpainting."""
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, median_filter

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
arr = np.array(img).astype(float)
h, w, _ = arr.shape

hue, sat, val = rgb_to_hsv(arr)
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

# Detect red grid: reddish hue, any saturation, and R > G,B to some degree
# Faint grid: low saturation, so use a lower saturation threshold
red_mask = ((hue < 35) | (hue > 325)) & (sat > 10) & (val > 50) & (r > g) & (r > b)

# Expand mask slightly to catch anti-aliased edges
from scipy.ndimage import binary_dilation
red_mask = binary_dilation(red_mask, iterations=2)
print('Red grid pixels after dilation:', red_mask.sum())

# Inpaint: replace masked pixels with median of non-masked pixels in a local window
out = arr.copy()
for c in range(3):
    ch = out[:,:,c].copy()
    # For masked pixels, compute local median of non-masked values
    # Use a sliding window approach: build a 2D array where masked pixels are filled
    # with the median of valid neighbors within radius.
    valid = ~red_mask
    # Distance transform to find nearest valid pixel
    dist, nearest = distance_transform_edt(~valid, return_distances=True, return_indices=True)
    # Use median filter on the channel with masked pixels replaced by a placeholder,
    # then only take the filtered value for masked pixels.
    # Simpler: use scipy's generic_filter with a custom function, but that's slow.
    # Instead, fill masked pixels with global median, then apply median filter, iterate.
    fill_val = np.median(ch[valid])
    ch[~valid] = fill_val
    for _ in range(5):
        ch = median_filter(ch, size=7)
        ch[~valid] = median_filter(ch, size=7)[~valid]
    out[:,:,c] = ch

out = np.clip(out, 0, 255).astype(np.uint8)
Image.fromarray(out).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_no_grid_v2.png')
print('Saved track_no_grid_v2.png')
