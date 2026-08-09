"""Test that station positions are computed correctly for alignment tool."""
import sys
sys.path.insert(0, r'C:\AI Projects\MagneMotionMonitor\Track Alignment program')
from main import load_csv_points, _station_pixel_positions
from pathlib import Path

rows = load_csv_points(Path(r'C:\AI Projects\MagneMotionMonitor\Track Alignment program\track_points.csv'))
print(f'Loaded {len(rows)} CSV rows')

stations = _station_pixel_positions(rows, Path(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\track_photo.py'))
print(f'Mapped {len(stations)} stations to pixels')
for s in stations[:10]:
    print(f"  {s['station']}: path {s['path_id']} @ {s['pos_m']:.3f}m -> ({s['x']:.1f}, {s['y']:.1f})")
