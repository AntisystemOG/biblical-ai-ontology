"""Patch main.py to use linear interpolation and epsilon=4 by default."""
from pathlib import Path

path = Path(r'C:\AI Projects\MagneMotionMonitor\Track Alignment program\main.py')
text = path.read_text(encoding='utf-8')

replacements = [
    # _load_all epsilon
    ('_build_anchors_from_paths(wps, epsilon=8.0)', '_build_anchors_from_paths(wps, epsilon=4.0)'),
    # TrackView render
    ('_generate_plc_paths(self._master_points, list(self._split_indices), spacing=6.0, smooth=True)',
     '_generate_plc_paths(self._master_points, list(self._split_indices), spacing=6.0, smooth=False)'),
    # _refresh_path_list
    ('_generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=True)',
     '_generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=False)'),
    # _update_info duplicated call
    ('plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=True)\n        total = sum(len(v) for v in plc.values())',
     'plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=False)\n        total = sum(len(v) for v in plc.values())'),
    # _reduce_now epsilon
    ('seg_keep = _rdp(seg, 8.0)', 'seg_keep = _rdp(seg, 4.0)'),
    # _save
    ('plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=True)', 'plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=False)'),
    # _export_json (second occurrence, after _save was changed this will match only export)
    ('plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=True)', 'plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=False)'),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
        print(f'Replaced: {old[:40]}...')
    else:
        print(f'Not found: {old[:40]}...')

path.write_text(text, encoding='utf-8')
print('Done')
