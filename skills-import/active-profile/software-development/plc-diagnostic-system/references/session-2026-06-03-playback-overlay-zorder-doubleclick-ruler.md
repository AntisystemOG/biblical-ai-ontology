# Session: Playback Overlay Z-Order, Double-Click Alarm Seek, Timeline Ruler

Date: 2026-06-03 | Versions: v2.23.10 – v2.23.16

## 1. Problem: QSlider paintEvent Drawings Are Invisible

**Initial approach:** Override `QSlider.paintEvent()` to draw red alarm arrows on the timeline groove. Result: arrows were **completely invisible**.

**Root cause:** `QSlider` repaints its groove on top of any custom drawings inside `paintEvent()`. The slider's internal groove renderer runs AFTER the parent's custom drawing, covering it completely.

**Failed attempts:**
- Custom `paintEvent()` override → invisible
- Subclassing `QSlider` and calling `super().paintEvent(painter)` after custom drawing → still overwritten by internal slider renderer
- Drawing in parent window's `paintEvent()` → same z-order problem

## 2. Solution: AlarmOverlay as Transparent Sibling Widget

Create a **separate `QWidget`** that sits at the **same parent** as the slider, paints **after** it in the paint stack, and has:

```python
class AlarmOverlay(QWidget):
    """Transparent sibling widget that paints red alarm arrows above the QSlider."""

    def __init__(self, parent: QWidget, slider: QSlider, ...):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self._slider = slider
        self.resize_to_slider()
        self.show()
        self.raise_()  # Paint AFTER slider in paint order

    def resize_to_slider(self):
        geo = self._slider.geometry()
        self.setGeometry(geo.x(), geo.y(), geo.width(), geo.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw red triangles at alarm positions
        for snap_idx, snap in self._alarms:
            x = self._snap_to_x(snap_idx)
            self._draw_triangle(painter, x, y_top, 8)
            # Draw 2px red vertical line through groove
            painter.setPen(QPen(QColor("#e11d48"), 2))
            painter.drawLine(x, y_top + 8, x, y_bottom)
```

**Critical flags:**
- `WA_TransparentForMouseEvents` — lets mouse events pass through to the slider underneath
- `setAutoFillBackground(False)` — prevents default background from covering everything
- `raise_()` — ensures this widget paints AFTER the slider in the paint cycle
- `WA_TransparentBackground` — **do NOT use this**. It causes flickering and paint artifacts on some Qt styles. Use `setAutoFillBackground(False)` instead.

**Resizing alignment:**
```python
# In parent resizeEvent()
def resizeEvent(self, event):
    super().resizeEvent(event)
    self._alarm_overlay.resize_to_slider()
    self._ruler.resize_to_slider()
```

Both overlay and ruler call `resize_to_slider()` to track the slider's geometry on every window resize.

## 3. TimelineRuler: 30-Minute Tick/Label Overlay

Same overlay pattern as `AlarmOverlay`:

```python
class TimelineRuler(QWidget):
    """Paints time tick marks and H:MM labels above the slider groove."""

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Consolas", 9))

        total_seconds = self._recording.duration_seconds
        ticks_every = 1800  # 30 minutes

        for t in range(0, int(total_seconds) + 1, ticks_every):
            x = int(self._slider_pos_from_time(t))
            # Tick mark
            painter.setPen(QPen(QColor("#9ca3af"), 1))
            painter.drawLine(x, y_top, x, y_top + 6)
            # Label
            label = self._format_time(t)
            fm = QFontMetrics(painter.font())
            tw = fm.horizontalAdvance(label)
            # Clamp to bounds so first/last labels don't clip
            label_x = max(0, min(x - tw // 2, self.width() - tw))
            painter.drawText(label_x, y_top - 4, label)
```

**Label clamping:** Labels are centered on ticks but clamped to widget bounds so the first label (0:00) starts at x=0 and the last label doesn't overflow the right edge.

**Time formatting:** `H:MM` (e.g., `0:00`, `0:30`, `1:00`, `1:30`). Duration can be anything from 45 seconds to 12 hours.

## 4. Double-Click Alarm Seek: Jump ~10 Seconds Before Fault

### 4.1 Single-click (existing) vs Double-click (new)

| Gesture | Action |
|---|---|
| **Single click** on arrow | Seeks to the **exact alarm snapshot** and pauses |
| **Double click** on arrow | Seeks to **~10 seconds BEFORE** the alarm and pauses |

### 4.2 Click-to-alarm-index mapping

```python
def _snap_idx_near_x(self, click_x: int) -> int | None:
    """Return nearest alarm snapshot index if within 12px tolerance."""
    best_idx = None
    best_dist = float("inf")
    for snap_idx in self._alarm_snapshot_indices:
        x = self._snap_to_x(snap_idx)
        dist = abs(click_x - x)
        if dist < best_dist and dist <= 12:
            best_dist = dist
            best_idx = snap_idx
    return best_idx
```

12px horizontal tolerance — generous enough for touch, precise enough to avoid accidental hits.

### 4.3 Polling interval estimation from adjacent snapshots

```python
def _jump_to_pre_alarm(self, alarm_idx: int) -> None:
    snaps = self._recording.snapshots
    # Estimate polling interval from timestamp delta
    if alarm_idx > 0:
        delta_ms = (snaps[alarm_idx].timestamp - snaps[alarm_idx - 1].timestamp).total_seconds() * 1000
    elif alarm_idx < len(snaps) - 1:
        delta_ms = (snaps[alarm_idx + 1].timestamp - snaps[alarm_idx].timestamp).total_seconds() * 1000
    else:
        delta_ms = 100.0  # default fallback (Thad's preferred rate)

    polling_ms = max(delta_ms, 50.0)  # clamp minimum 50ms
    snaps_10s = max(1, int(10000 / polling_ms))
    target_idx = max(0, alarm_idx - snaps_10s)

    self._slider.setValue(target_idx)
    self._pause_playback()
```

**Why estimate from timestamps rather than hardcode?**
- Recordings may have been captured at 100 ms, 250 ms, or 500 ms depending on user settings
- Simulated recordings use 100 ms (600 snapshots × 100 ms = 60 s = 1 minute per "step")
- Real recordings may have variable intervals due to PLC load

**Math:** `snaps_10s = max(1, int(10000 / polling_ms))`
- `10000` = 10 seconds in milliseconds
- `max(1, ...)` ensures at least 1 snapshot back (never seek to the alarm itself)
- `max(0, alarm_idx - snaps_10s)` prevents negative index

## 5. Physical Address Column in Playback Review Tables

All I/O tables in `PlaybackReviewWindow` have 4 columns:
1. **Status** — LED circle widget (green/red)
2. **Tag** — logical tag name
3. **Description** — human-readable description from `io_catalog`
4. **Physical Address** — e.g., `DI 01`, `DO 07`, `DI 185` from `physical_mapping.py`

Robot Interface tab has 5 columns (added Robot Signal name):
1. Robot Signal
2. Status
3. Tag
4. Description
5. Physical Address

```python
def _get_physical_address(self, tag: str) -> str:
    """Lookup physical I/O address from PHYSICAL_ADDRESS_MAP."""
    clean = tag.lstrip("_")
    addr = PHYSICAL_ADDRESS_MAP.get(clean, "—")
    return addr if addr else "—"
```

**Single source of truth:** Both live `I/O Status` tab and `PlaybackReviewWindow` use the same `_get_physical_address()` helper that reads from `physical_mapping.PHYSICAL_ADDRESS_MAP`.

## 6. Build History for This Session

| Version | Change |
|---|---|
| v2.23.10 | Remove mode-toggle architecture completely |
| v2.23.11–12 | Stale reference cleanup, quality gate |
| v2.23.13 | Physical Address column added to Robot Interface tab |
| v2.23.14 | `AlarmOverlay` replaces invisible `paintEvent()` arrows |
| v2.23.15 | Overlay geometry fix (`show()` + remove `WA_TransparentBackground`) |
| v2.23.16 | `TimelineRuler` + double-click pre-alarm seek |

## 7. Files Modified

- `src/plc_tools/gui/playback_review_window.py` — `PlaybackReviewWindow`, `AlarmOverlay`, `TimelineRuler`, double-click logic
- `src/plc_tools/gui/tabs/playback_record.py` — review button, no mode toggle
- `src/plc_tools/recording/timeline_recorder.py` — `Snapshot.alarm_events`
- `src/plc_tools/gui/main_window.py` — passes alarm events to recorder
- `src/plc_tools/catalog/io_catalog.py` — 7 STATUS → OUTPUT reclassification
