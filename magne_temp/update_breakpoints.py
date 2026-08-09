"""Update REAL_TO_PIXEL_BREAKPOINTS and the accuracy paragraph in track_photo.py."""
from pathlib import Path

path = Path(r'C:\AI Projects\MagneMotionMonitor\mm_monitor\track_photo.py')
text = path.read_text(encoding='utf-8')

# Replace the old breakpoints block
old = '''# Fix: a piecewise-linear correction, anchored at the two leg/curve transition
# points on both sides — (real_fraction, pixel_fraction) pairs measured directly
# from these paths' own waypoint lists and track_geometry's real segment
# lengths. Between anchors, a real fraction is linearly remapped to the pixel
# fraction it should ACTUALLY correspond to, before the normal arc-length
# lookup runs. Paths without an entry here (1, 3, 5, 6) use real_frac ==
# pixel_frac directly — their curves are a small enough share of the total
# length that this mismatch isn't meaningfully visible.
# Anchors: (0, 0) and the two leg/curve transitions come from track_geometry's
# real segment lengths + the measured pixel arc-length of those transitions in
# the waypoints above. The EXTRA middle anchor (~0.71 real) is a "Load lift":
# the HMI Load 2 meter (3.405 m) maps mathematically to only ~37% up the return
# leg, but on the real machine the load station sits ~2/3 up the leg (field-
# confirmed by the operator with a pointer). Rather than distrust the HMI meter
# everywhere, this single anchor pulls the Load region up to match reality; the
# leg/curve anchors keep the U-turn correct and Cooling (top) unaffected. If the
# operator flags a station as still off, nudge the matching anchor's pixel value.
REAL_TO_PIXEL_BREAKPOINTS: dict[int, list[tuple[float, float]]] = {
    2: [(0.0, 0.0), (0.465, 0.424), (0.546, 0.576), (0.704, 0.860), (1.0, 1.0)],
    4: [(0.0, 0.0), (0.459, 0.424), (0.541, 0.577), (0.712, 0.860), (1.0, 1.0)],
}'''

new = '''# NOTE: Breakpoints reset to identity for the full_track_grid.png render. The
# dense edge-following waypoints already capture the U-turn geometry, but if cart
# pacing through the mold loops looks wrong compared to the real machine,
# recalibrate from track_geometry's real segment lengths vs. the pixel arc-length
# of the leg/curve transitions in the waypoints below.
REAL_TO_PIXEL_BREAKPOINTS: dict[int, list[tuple[float, float]]] = {
    2: [(0.0, 0.0), (1.0, 1.0)],
    4: [(0.0, 0.0), (1.0, 1.0)],
}'''

if old not in text:
    # try with CRLF
    text_crlf = text.replace('\n', '\r\n')
    if old in text_crlf:
        text_crlf = text_crlf.replace(old, new)
        path.write_text(text_crlf.replace('\n', '\r\n'), encoding='utf-8')
        print('Updated with CRLF')
    else:
        print('Old breakpoints block not found')
else:
    text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')
    print('Updated with LF')
