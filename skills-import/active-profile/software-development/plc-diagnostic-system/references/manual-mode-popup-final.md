# Manual Mode Popup Dialog — Final Implementation

Session: 2026-05-29 — Degater PLC Tool

## Final Design

A standalone `Qt.Window` dialog that shows:
- Title bar: "Manual Mode Required"
- Instruction text
- A photograph of the physical MAN-AUTO switch
- Close button

## Dialog Sizing

**Critical: `Qt.Window` consumes ~30px of the top for the title bar.** The dialog's fixed height must account for this:

| | Old (Broken) | Fixed |
|---|---|---|
| Constructor | `super().__init__(parent)` | `super().__init__(parent, Qt.Window)` |
| Fixed size | `640 × 520` | `660 × 600` |
| Title bar | none / clipped | proper chrome |
| Close button | bleeds out bottom | fully inside |

```python
class ManualModeDialog(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("Manual Mode Required")
        self.setFixedSize(660, 600)
        self._build_ui()
```

## Content Layout

```python
def _build_ui(self) -> None:
    layout = QVBoxLayout(self)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    # Title
    title = QLabel("Manual Mode Required")
    title.setStyleSheet(
        "QLabel { color: #dc2626; font-size: 16px; font-weight: bold; }"
    )
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    # Instruction
    instr = QLabel(
        "Switch to Manual on the line to enable output controls.\n"
        "Input: X2 Digital Input 30  (DEG MAN-AUTO = FALSE → Manual mode)"
    )
    instr.setStyleSheet("QLabel { color: #4b5563; font-size: 12px; }")
    instr.setAlignment(Qt.AlignCenter)
    layout.addWidget(instr)

    # Image
    self._img_lbl = QLabel()
    self._img_lbl.setAlignment(Qt.AlignCenter)
    self._img_lbl.setStyleSheet(
        "QLabel { background: #f3f4f6; border-radius: 8px; }"
    )
    layout.addWidget(self._img_lbl, stretch=1)
    self._load_image()

    # Close button
    close_btn = QPushButton("Close")
    close_btn.setStyleSheet("""
        QPushButton {
            background: #6366f1; color: white; border-radius: 6px;
            padding: 8px 24px; font-weight: bold; font-size: 12px;
        }
        QPushButton:hover { background: #4f46e5; }
    """)
    close_btn.clicked.connect(self.close)
    layout.addWidget(close_btn, alignment=Qt.AlignCenter)
```

## Image Loading

Use a candidate list that handles both development and PyInstaller bundle paths:

```python
def _load_image(self) -> None:
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "assets", "Manual.jpg"),
        os.path.join(os.path.dirname(__file__), "..", "..", "gui", "assets", "Manual.jpg"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Manual.jpg"),
    ]
    if getattr(sys, "_MEIPASS", None):
        candidates.insert(0, os.path.join(
            sys._MEIPASS, "plc_tools", "gui", "assets", "Manual.jpg"
        ))

    for path in candidates:
        if os.path.isfile(path):
            pm = QPixmap(path)
            if not pm.isNull():
                # Size to fit inside dialog margins
                scaled = pm.scaled(
                    560, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self._img_lbl.setPixmap(scaled)
                return

    self._img_lbl.setText("[Manual.jpg not found — image missing from bundle]")
```

## Trigger Points

The dialog opens from multiple places:
1. Any dimmed ON/OFF/Release button click (auto mode)
2. The green "Manual: OFF" status button in the I/O page top bar
3. The alarm flash nav item click (optional)

## Previous Iterations (for reference)

- **v1:** Swapped widget between single "⚠ Manual" button and ON/OFF/Release group — rejected by user, wanted original buttons always visible.
- **v2:** Dimmed buttons with dialog popup — accepted, but dialog had no `Qt.Window` flag causing title clipping.
- **v3 (current):** Added `Qt.Window` flag, increased height to 600px, widened to 660px, reduced image scale to 560px.
