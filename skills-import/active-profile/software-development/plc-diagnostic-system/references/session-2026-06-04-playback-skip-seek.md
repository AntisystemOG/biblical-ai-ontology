# Playback Skip/Seek Buttons — Session 2026-06-04

## What was added

Skip buttons (`−1m`, `−5m`, `−15m`, `−1h`) and forward skip buttons (`+1m`, `+5m`, `+15m`, `+1h`) plus `↻ Restart` to the `PlaybackReviewWindow` transport bar.

## Implementation

### Time-based seek (not snap-based)

Computed by wall-clock time, not raw snapshot index, so irregular snapshots (e.g. from inconsistent polling) seek correctly:

```python
def _skip_backward(self, minutes: int) -> None:
    """Seek backward by N minutes. Pause if playing."""
    if self._is_playing:
        self._toggle_play()
    n = len(self._recording.snapshots)
    if n == 0: return
    current_time = (self._recording.snapshots[self._current_index].timestamp
                    - self._recording.start_time).total_seconds()
    target = max(0, current_time - minutes * 60)
    # Find closest snapshot to target
    best_idx = 0
    best_diff = abs((self._recording.snapshots[0].timestamp
                     - self._recording.start_time).total_seconds() - target)
    for i in range(1, n):
        diff = abs((self._recording.snapshots[i].timestamp
                   - self._recording.start_time).total_seconds() - target)
        if diff < best_diff:
            best_diff = diff
            best_idx = i
    self._current_index = best_idx
    self._show_snapshot(best_idx)
```

### Transport bar layout

```
[▶ Play] [◀ Prev] [Next ▶] | [−1m] [−5m] [−15m] [−1h] [+1m] [+5m] [+15m] [+1h] [↻ Restart] | Speed x1 x2 x4 x8 x16 | spacer | [✕ Close Review]
```

### Auto-pause on seek

All skip methods check `self._is_playing` and call `_toggle_play()` before computing. This prevents the timer from clobbering the newly-selected snapshot before the user sees it.

### Restart button

`_goto_start()` sets index to 0 and pauses. Identical pattern to skip with target=0.

## File

`gui/playback_review_window.py` — `_skip_backward()`, `_skip_forward()`, `_goto_start()`

## Quality gate applied

Full syntax + AST check on all 33 `.py` files before build.
