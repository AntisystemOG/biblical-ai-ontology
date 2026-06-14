# AlarmMarkerSlider

## Purpose

A `QSlider` subclass that paints **red alarm ticks** on the groove at specific indices. Used in the Playback Review Window timeline to mark snapshots where alarms/faults occurred.

## When to Use

- Any timeline/scrubber UI where events (alarms, faults, transitions) need visual markers
- Playback review of recorded PLC data where the user needs to jump to alarm moments

## Implementation

```python
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QSlider, QWidget

class AlarmMarkerSlider(QSlider):
    alarm_marker_clicked = Signal(int)   # emits snapshot index when user clicks a tick

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(Qt.Horizontal, parent)
        self._alarm_indices: set[int] = set()

    def set_alarm_indices(self, indices: list[int]) -> None:
        self._alarm_indices = set(indices)
        self.update()   # trigger repaint

    def paintEvent(self, event) -> None:
        super().paintEvent(event)   # draw normal slider first
        if not self._alarm_indices or self.maximum() == 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        groove_rect = self.rect()
        y_center = groove_rect.height() // 2
        tick_height = 10
        pen = QPen(QColor("#dc2626"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QColor("#dc2626"))
        for idx in self._alarm_indices:
            if 0 <= idx <= self.maximum():
                ratio = idx / self.maximum()
                x = int(groove_rect.left() + ratio * groove_rect.width())
                painter.drawRect(x - 1, y_center - tick_height // 2, 3, tick_height)
        painter.end()

    def mousePressEvent(self, event) -> None:
        # Check if click is near an alarm marker (±8 pixels)
        if self._alarm_indices and self.maximum() > 0:
            click_x = event.pos().x()
            groove_rect = self.rect()
            for idx in self._alarm_indices:
                ratio = idx / self.maximum()
                marker_x = int(groove_rect.left() + ratio * groove_rect.width())
                if abs(click_x - marker_x) <= 8:
                    self.alarm_marker_clicked.emit(idx)
                    return   # consume click — don't seek
        super().mousePressEvent(event)
```

## Key Details

- **Calls `super().paintEvent()` first** — normal slider groove/handle are drawn first, then alarm ticks are overlaid
- **Red color `#dc2626`** — Tailwind red-600, visible on light and dark backgrounds
- **Small rectangles** — 3px wide, 10px tall, centered on groove — unobtrusive but visible
- **Click detection ±8px** — generous hit area for small ticks
- **`alarm_marker_clicked` Signal(int)** — emits the snapshot index; handler should jump to that snapshot and auto-pause
- **Auto-pause on click** — the review window handler calls `self._pause()` after jumping, so user can inspect

## Styling

The slider's normal stylesheet (groove, handle, sub-page) is unchanged. Alarm ticks are drawn in `paintEvent` after the base rendering. No stylesheet modifications needed.

## Anti-Patterns

| Anti-Pattern | Why Bad | Correct |
|---|---|---|
| Draw ticks before `super().paintEvent()` | Ticks get covered by groove/handle | Call `super()` first, then overlay |
| No click hit area | User can't interact with small ticks | ±8px hit tolerance |
| Emit `seek_requested` instead of `alarm_marker_clicked` | Confuses normal slider seeks with alarm jumps | Separate signal for alarm clicks |
| Paint ticks at every pixel | Clutters, wastes CPU | Only at `alarm_indices` |

## Testing

1. Set `slider.setMaximum(100)` and `slider.set_alarm_indices([10, 25, 50, 75])`
2. Verify red ticks visible at ~10%, 25%, 50%, 75% of groove
3. Click near a tick — `alarm_marker_clicked` emits correct index
4. Click far from any tick — normal slider seek behavior
5. Resize window — ticks reposition correctly (paintEvent recalculates)

---
*Session: 2026-06-02. Used in PlaybackReviewWindow for Degater PLC Tool.*
