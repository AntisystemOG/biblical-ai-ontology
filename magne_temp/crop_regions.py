"""Crop key regions to inspect red line detection."""
from PIL import Image

img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\waypoints_on_red_mask.png')
# Crop top main rail region
img.crop((0, 0, 1584, 200)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\crop_top_rail.png')
# Crop right spur region
img.crop((1200, 200, 1584, 650)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\crop_right_spur.png')
# Crop left spur region
img.crop((0, 200, 600, 650)).save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\crop_left_spur.png')
print('Crops saved')
