"""Analyze frequency content to detect grid pattern."""
import numpy as np
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('L')
arr = np.array(img)

# FFT
f = np.fft.fft2(arr)
fshift = np.fft.fftshift(f)
magnitude = 20 * np.log(np.abs(fshift) + 1)

# Save magnitude as image
mag_norm = (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min()) * 255
Image.fromarray(mag_norm.astype(np.uint8)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\fft_magnitude.png')
print('Saved fft_magnitude.png')

# Find peaks in frequency domain
h, w = magnitude.shape
# Exclude center (DC component)
center_y, center_x = h // 2, w // 2
# Look at horizontal and vertical lines through center
horiz = magnitude[center_y, :]
vert = magnitude[:, center_x]

# Find local maxima
from scipy.signal import find_peaks
h_peaks, _ = find_peaks(horiz, height=np.percentile(horiz, 99), distance=10)
v_peaks, _ = find_peaks(vert, height=np.percentile(vert, 99), distance=10)
print('Horizontal freq peaks:', h_peaks)
print('Vertical freq peaks:', v_peaks)
print('Peak magnitudes h:', horiz[h_peaks])
print('Peak magnitudes v:', vert[v_peaks])
