"""Crop empty background corners."""
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png')
# Top left corner
img.crop((0, 0, 200, 200)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\bg_topleft.png')
# Bottom right corner
img.crop((1400, 500, 1584, 672)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\bg_bottomright.png')
# Middle top between rails maybe
img.crop((600, 120, 800, 180)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\bg_middletop.png')
print('Saved crops')
