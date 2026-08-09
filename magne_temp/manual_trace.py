"""Manually trace the rail top edge for each PLC path on full_track_grid.png.
Edit the control points below and rerun to refine."""
import json
import numpy as np
from PIL import Image, ImageDraw


def catmull_rom_chain(points, samples_per_span=20):
    """Interpolate a closed or open Catmull-Rom spline through points."""
    if len(points) < 2:
        return list(points)
    n = len(points)
    out = []
    for i in range(n - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else p2
        for k in range(samples_per_span):
            t = k / samples_per_span
            out.append(_catmull_rom(p0, p1, p2, p3, t))
    out.append(points[-1])
    return out


def _catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    x = 0.5 * (2*p1[0] + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
    y = 0.5 * (2*p1[1] + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
    return (x, y)


def resample(pts, spacing=6.0):
    if len(pts) < 2:
        return list(pts)
    out = [pts[0]]
    remain = 0.0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        seg = (dx*dx+dy*dy)**0.5
        if seg == 0:
            continue
        ux, uy = dx/seg, dy/seg
        d = remain
        while d < seg:
            out.append((a[0]+ux*d, a[1]+uy*d))
            d += spacing
        remain = d - seg
    if (out[-1][0]-pts[-1][0])**2 + (out[-1][1]-pts[-1][1])**2 > 1:
        out.append(pts[-1])
    return out


# ── Control points for each PLC path (top edge of rail) ─────────────────────
# PATH_ORDER = 6 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6
# Coordinates are pixel (x, y) on full_track_grid.png (1584x672)

path6_ctrl = [
    (40, 75), (150, 75), (350, 75), (550, 75), (750, 77),
    (950, 80), (1150, 85), (1320, 92), (1430, 105), (1500, 125),
    (1545, 150), (1560, 165), (1560, 180),
]

path1_ctrl = [
    (1560, 180), (1550, 190), (1545, 195), (1540, 200),
]

path2_ctrl = [
    (1540, 200), (1538, 250), (1535, 350), (1532, 450), (1530, 540),
    (1505, 600), (1460, 622), (1410, 625), (1375, 610), (1365, 560),
    (1362, 460), (1361, 350), (1360, 250), (1360, 200),
]

path3_ctrl = [
    (1360, 200), (1200, 202), (1000, 203), (800, 203), (600, 202),
    (500, 200),
]

path4_ctrl = [
    (500, 200), (502, 250), (505, 350), (508, 450), (510, 540),
    (535, 600), (580, 622), (630, 625), (665, 610), (675, 560),
    (678, 460), (679, 350), (680, 250), (680, 200),
]

path5_ctrl = [
    (680, 200), (500, 195), (300, 190), (150, 185), (40, 180),
]

# Interpolate and resample
plc_paths = {
    6: resample(catmull_rom_chain(path6_ctrl), 6.0),
    1: resample(path1_ctrl, 4.0),
    2: resample(catmull_rom_chain(path2_ctrl), 6.0),
    3: resample(path3_ctrl, 6.0),
    4: resample(catmull_rom_chain(path4_ctrl), 6.0),
    5: resample(path5_ctrl, 4.0),
}

# Ensure shared junctions match exactly
plc_paths[6][-1] = plc_paths[1][0]
plc_paths[1][-1] = plc_paths[2][0]
plc_paths[2][-1] = plc_paths[3][0]
plc_paths[3][-1] = plc_paths[4][0]
plc_paths[4][-1] = plc_paths[5][0]
plc_paths[5][-1] = plc_paths[6][0]

# Draw preview
img = Image.open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\full_track_grid.png').convert('RGB')
draw = ImageDraw.Draw(img)
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
for pid, pts in plc_paths.items():
    color = colors[pid-1]
    draw.line(pts, fill=color, width=2)
    for x, y in pts[::max(1, len(pts)//15)]:
        draw.ellipse([x-4, y-4, x+4, y+4], fill=color)

# Draw control points
for pid, ctrl in [(6,path6_ctrl),(1,path1_ctrl),(2,path2_ctrl),(3,path3_ctrl),(4,path4_ctrl),(5,path5_ctrl)]:
    for x, y in ctrl:
        draw.ellipse([x-3, y-3, x+3, y+3], fill=(255,255,255), outline=(0,0,0), width=1)

img.save(r'C:\Users\thadd\.openclaw\workspace\magne_temp\manual_trace_preview.png')
print('Saved manual_trace_preview.png')
print('PLC path point counts:', {k: len(v) for k, v in plc_paths.items()})

# Save as JSON for possible use
with open(r'C:\Users\thadd\.openclaw\workspace\magne_temp\manual_trace.json', 'w') as f:
    json.dump({str(k): [[round(x,1), round(y,1)] for x, y in v] for k, v in plc_paths.items()}, f, indent=2)
