"""Detect red guide line using HSV color space in pure numpy."""
import numpy as np
from PIL import Image

def rgb_to_hsv(rgb):
    """Vectorized RGB to HSV. rgb: (H,W,3) uint8. Returns h,s,v in 0-180,0-255,0-255."""
    rgb = rgb.astype(float)
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    diff = mx - mn
    v = mx
    s = np.where(mx > 0, diff / mx * 255, 0)
    # hue
    h = np.zeros_like(mx)
    mask = diff > 0
    # r is max
    mr = mask & (mx == r)
    h[mr] = ((g[mr] - b[mr]) / diff[mr] * 60) % 360
    # g is max
    mg = mask & (mx == g)
    h[mg] = ((b[mg] - r[mg]) / diff[mg] * 60 + 120) % 360
    # b is max
    mb = mask & (mx == b)
    h[mb] = ((r[mb] - g[mb]) / diff[mb] * 60 + 240) % 360
    return h, s, v

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
arr = np.array(img)
h, s, v = rgb_to_hsv(arr)

# Red: hue near 0 or 360, high saturation, moderate+ value
red_mask = ((h < 20) | (h > 340)) & (s > 80) & (v > 80)
# Also require R dominant
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
red_mask &= (r > g + 20) & (r > b + 20)

print('Red HSV pixels:', red_mask.sum())
Image.fromarray((red_mask * 255).astype(np.uint8)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_hsv_np_mask.png')

# Highlight
overlay = arr.copy()
overlay[red_mask] = [255, 255, 0]
Image.fromarray(overlay).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\red_hsv_np_overlay.png')
print('Saved overlays')
