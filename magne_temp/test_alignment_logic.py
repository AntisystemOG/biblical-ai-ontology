"""Test the alignment tool geometry logic without launching GUI."""
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor\Track Alignment program')
from main import load_waypoints, _build_anchors_from_paths, _generate_plc_paths, PATH_ORDER
from pathlib import Path

wps = load_waypoints(Path(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\track_photo.py'))
print('Loaded paths:', sorted(wps.keys()))
print('Counts:', {k: len(v) for k, v in wps.items()})

anchors, junctions = _build_anchors_from_paths(wps, epsilon=4.0)
print(f'Anchors: {len(anchors)}, junctions: {junctions}')

plc = _generate_plc_paths(anchors, junctions, spacing=6.0, smooth=False)
print('Generated counts:', {k: len(v) for k, v in plc.items()})

# Make sure paths connect
for i, pid in enumerate(PATH_ORDER):
    nxt = PATH_ORDER[(i+1) % len(PATH_ORDER)]
    end = plc[pid][-1]
    start = plc[nxt][0]
    dist = ((end[0]-start[0])**2 + (end[1]-start[1])**2)**0.5
    print(f'Path {pid} end to {nxt} start distance: {dist:.2f}px')

print('Logic OK')
