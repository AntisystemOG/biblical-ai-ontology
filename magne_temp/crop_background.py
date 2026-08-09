"""Crop a background area to inspect grid pattern."""
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png')
# Crop a 200x200 background area with no rail
img.crop((250, 250, 450, 450)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\bg_crop.png')
print('Saved bg_crop.png')
