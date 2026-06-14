# Timeline Recording Subsampling

## Problem

At 100ms polling with 127 I/O tags per snapshot:
- Snapshot JSON: ~3.7 KB
- 12-hour recording: 432,000 snapshots = **~1.5 GB**

Loading a 1.5 GB JSON playback file is impractical — it consumes excessive RAM and slows timeline playback to a crawl.

## Solution: Decouple Poll Rate from Record Rate

Poll PLC at the fastest rate needed for real-time validation (100ms), but **write only 1 in N snapshots** to the timeline recording. This keeps the alarm watcher responsive while bounding disk usage.

| Poll Rate | Record Interval | Effective Record Rate | 12-Hour File Size |
|---|---|---|---|
| 100 ms | 1 | 100 ms | **1.5 GB** |
| 100 ms | **10** | **1 sec** | **~150 MB** |
| 250 ms | 4 | 1 sec | ~150 MB |
| 1000 ms | 1 | 1 sec | ~150 MB |

**Key insight:** 1-second resolution is sufficient for playback. Cylinder motion takes 200-800ms to settle; you don't need 100ms granularity in the historical recording.

## Implementation

### TimelineRecorder

```python
class TimelineRecorder:
    def __init__(self):
        self._record_interval: int = 1   # 1 = every poll, 10 = every 10th
        self._record_tick: int = 0
        # ...

    def set_record_interval(self, interval: int) -> None:
        """Save 1 in N snapshots. interval=10 → save every 10th poll."""
        self._record_interval = max(1, int(interval))
        self._record_tick = 0

    def record_snapshot(self, values: dict) -> Snapshot | None:
        if not self._is_recording:
            return None

        # 12-hour cap check first
        if self.elapsed_seconds >= MAX_DURATION_SECONDS:
            self.stop()
            return None

        # Subsample: skip snapshots that aren't on the interval
        self._record_tick += 1
        if self._record_tick < self._record_interval:
            return None   # silently skip — values still polled for UI/alarms
        self._record_tick = 0

        # ... proceed to fault detection and snapshot creation
```

### MainWindow Wiring

```python
def _start_recording(self, path: str) -> None:
    # Auto-compute interval: target ~1 second wall time between saved snapshots
    poll_ms = self._poll_timer.interval()
    interval = max(1, int(1000 / poll_ms))
    self._timeline_recorder.set_record_interval(interval)

    self._timeline_recorder.start("DEG System BST33/35")
```

| Poll Rate | Auto-Computed Interval | Behavior |
|---|---|---|
| 100 ms | 10 | Save every 1.0 second |
| 250 ms | 4 | Save every 1.0 second |
| 500 ms | 2 | Save every 1.0 second |
| 1000 ms | 1 | Save every 1.0 second |

The user never needs to adjust this — it stays consistent regardless of polling rate.

## Architecture Principle

**Poll fast, record slow.** The poll loop serves two independent consumers with different latency requirements:

| Consumer | Latency Requirement | Receives |
|---|---|---|
| Alarm watcher | <1 second (catch failures fast) | Every poll (100ms) |
| Live UI panels | <1 second (visual responsiveness) | Every poll (100ms) |
| Timeline recording | 1 second is fine (historical playback) | Every Nth poll |

Decoupling these rates is critical for long-duration recording on machines with many I/O tags.

## Pitfall: Poll Rate ≠ Record Rate

If you naively save every poll just because you poll fast, you get multi-gigabyte recordings. Always subsample when poll rate < 250ms and tag count > 50.
