# Playback Data Stability Filter

## Problem
Timeline playback showed output booleans flickering ON→OFF→ON within single snapshots. The original root cause analysis identified two sources:
1. `_PollWorker` forcing `False` when a tag read errors
2. PLC scan-cycle noise where outputs briefly read as OFF between writes

## Historic Fix (Two-Layer Defense) — Now Superseded

The original plan added:
- **Layer 1** — Last-known-value caching in the poll worker (retain last good read instead of forcing `False` on error)
- **Layer 2** — 2-snapshot stability threshold in playback that suppressed booleans until they held for 2 consecutive frames

**Why Layer 2 was removed:** In practice, the stability filter **blocked legitimate ON values from reaching the UI** during playback. Outputs would appear to turn on briefly then immediately go off because the second frame hadn't arrived yet. The filter was curing the symptom by hiding the problem, which made operators think outputs weren't working during review.

## Correct Fix: Remove Playback-Side Filtering

Remove all stability filters from `_on_playback_update()`. Let booleans pass through unfiltered:

```python
# REMOVED — suppresses legitimate ON values
if self._is_output_boolean(tag):
    last = self._playback_last_values.get(tag)
    ...

# NEW — pass through directly
snapshot = frame["values"]
self._update_io_display(snapshot)
```

**Principle:** The playback tab should be a **truthful replay** of the recording data. If glitches exist, fix them at the source (poll worker caching), not in playback.

### What to Keep: Poll Worker Last-Known-Value

```python
class _PollWorker(QObject):
    """Caches last known good values to prevent false OFFs entering recordings."""

    def __init__(self):
        super().__init__()
        self._last_known_values: dict[str, Any] = {}

    def _read_tag(self, tag_name: str) -> Any:
        try:
            value = self._driver.read_tag(tag_name)
            self._last_known_values[tag_name] = value
            return value
        except Exception:
            return self._last_known_values.get(tag_name, False)
```

This is still correct because a read error does NOT mean the output is OFF.

### Companion Fix: Live/Playback Mode Toggle

Playback flicker wasn't the only problem. Live polls **overwrite** the playback display if the timer keeps running. See `references/playback-live-mode-toggle.md` for the `_data_mode` single-source-of-truth architecture that prevents this.

## Verification

1. Record a timeline with a long-held ON output (e.g., 5 seconds)
2. Inspect JSON recording — verify no spurious OFF frames (poll worker caching does its job)
3. Play back at 1× speed — output LED should hold steady green for the full duration
4. No flickering ON→OFF→ON within the held period
5. Mode toggle button clearly shows 🔵 PLAYBACK while loaded
