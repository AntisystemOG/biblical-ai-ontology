"""Segment rail sections using HSV on the clean 3D render."""
import numpy as np
from PIL import Image, ImageDraw

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

# Mask out grid labels and text: very bright and low saturation
bg_mask = (val > 210) & (sat < 30)
non_bg = ~bg_mask

# Teal/green: hue 150-200, sat > 20, val > 60
teal_mask = ((hue > 140) & (hue < 210)) & (sat > 25) & (val > 60) & non_bg
# Purple: hue 260-320
purple_mask = ((hue > 250) & (hue < 330)) & (sat > 30) & (val > 60) & non_bg
# Blue: hue 190-250 (overlap with teal? use higher sat and val range)
blue_mask = ((hue > 200) & (hue < 260)) & (sat > 40) & (val > 80) & non_bg
# Silver/gray: low saturation, medium value, not colored
gray_mask = (sat < 50) & (val > 70) & (val < 190) & non_bg & ~teal_mask & ~purple_mask & ~blue_mask

# Remove small noise
from scipy.ndimage import binary_opening, binary_closing
def clean(mask, size=3):
    return binary_closing(binary_opening(mask, iterations=1), iterations=size)

teal_mask = clean(teal_mask)
purple_mask = clean(purple_mask)
blue_mask = clean(blue_mask)
gray_mask = clean(gray_mask)

print(f'Teal: {teal_mask.sum()}, Purple: {purple_mask.sum()}, Blue: {blue_mask.sum()}, Gray: {gray_mask.sum()}')

# Combine all rail
rail_mask = teal_mask | purple_mask | blue_mask | gray_mask

overlay = arr.copy()
overlay[teal_mask] = [255, 255, 0]
overlay[purple_mask] = [255, 0, 255]
overlay[blue_mask] = [0, 255, 255]
overlay[gray_mask] = [255, 128, 0]
Image.fromarray(overlay).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\rail_hsv_mask.png')
Image.fromarray((rail_mask*255).astype(np.uint8)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\rail_combined_mask.png')
print('Saved masks')
