# Drawing Downward-Pointing Arrows on QSlider Groove

Used in the Playback Review timeline to mark alarm positions with a red ▼ arrow
that visually points to the exact snapshot where the fault occurred.

## Code Pattern (PySide6)

```python
# Imports needed
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon

# Inside paintEvent:
painter = QPainter(self)
painter.setRenderHint(QPainter.Antialiasing)

opt = QStyleOptionSlider()
self._slider.initStyleOption(opt)
groove = self._slider.style().subControlRect(
    QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self._slider
)
groove.moveTopLeft(self._slider.mapTo(self, groove.topLeft()))

for idx in alarm_indices:
    ratio = idx / self._slider.maximum()
    x = int(groove.left() + ratio * groove.width())

    arrow_size = 7
    triangle = QPolygon([
        QPoint(x, groove.top() - arrow_size - 2),   # tip
        QPoint(x - arrow_size, groove.top() - 2),    # bottom left
        QPoint(x + arrow_size, groove.top() - 2),    # bottom right
    ])
    painter.setBrush(QColor("#dc2626"))
    painter.setPen(Qt.NoPen)
    painter.drawPolygon(triangle)

    # Thin reference line inside groove
    painter.setPen(QPen(QColor("#ef4444"), 1))
    painter.drawLine(x, groove.top() + 2, x, groove.bottom() - 2)

painter.end()
```

## Why This Pattern

| Alternative | Problem |
|---|---|
| Override `QSlider.paintEvent` | Brittle — QSlider has complex internal rendering |
| `paintEvent` on parent widget | Must map slider geometry to parent coordinate space |
| Use `QStyle.SC_SliderGroove` rect | Correct groove position regardless of stylesheet |
| Simple `drawRect` | Red rectangles looked like bugs, arrows clearly indicate position |

## Click-to-Seek on Arrows

Store `_alarm_indices` list. In `mousePressEvent`, map click X to nearest marker
and snap slider to that snapshot:

```python
def mousePressEvent(self, event) -> None:
    if self._alarm_indices:
        # ... map groove rect ...
        click_x = event.pos().x()
        for idx in self._alarm_indices:
            ratio = idx / max_val
            marker_x = int(groove.left() + ratio * groove.width())
            if abs(click_x - marker_x) <= 8:
                self._show_snapshot(idx)
                return
    super().mousePressEvent(event)
```
