"""Measure the rail cross-section in track_photo.png at several X positions."""
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\track_photo.png').convert('RGB')
arr = np.array(img)
h, w, _ = arr.shape
print(f'Image: {w}x{h}')

# Sample vertical brightness profiles at several X positions for the top rail
x_positions = [100, 300, 500, 700, 900, 1100, 1300, 1500]
profiles = {}
for x in x_positions:
    # take a vertical strip +/- 5 px around x
    strip = arr[:, max(0, x-5):min(w, x+6), :]
    profile = strip.mean(axis=(1, 2))
    profiles[x] = profile
    # find peaks (bright regions)
    from scipy.signal import find_peaks
    peaks, props = find_peaks(profile, height=80, distance=15)
    print(f'X={x}: peaks at Y={peaks}, heights={props["peak_heights"].round(0) if len(peaks) else []}')

# Plot
fig, axes = plt.subplots(len(x_positions), 1, figsize=(8, 12))
for ax, x in zip(axes, x_positions):
    ax.plot(profiles[x])
    ax.set_title(f'X={x}')
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 255)
plt.tight_layout()
plt.savefig(r'C:\Users\thadd\.openclaw\workspace\magne_temp\rail_profiles.png')
print('Saved rail_profiles.png')
