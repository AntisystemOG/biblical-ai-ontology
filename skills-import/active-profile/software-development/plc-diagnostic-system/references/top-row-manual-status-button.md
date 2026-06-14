# Top-Row Manual Mode Status Button

Session: 2026-05-29 — Degater PLC Tool

## Problem

The per-row "⚠ Manual" button in the outputs table works for individual rows, but there was no persistent top-level indicator of the overall PLC mode. Users had to scroll through the I/O table to see whether manual controls were available.

## Solution

Add a **green status button** next to the Refresh button in the top bar of the I/O Status page:

```
┌──────────┐ ┌──────────┐  [Note label ... ]          [Status]
│ ↻ Refresh│ │Manual:OFF│
└──────────┘ └──────────┘
```

- **"Manual: OFF"** — light green background (`#dcfce7`), dark green text (`#166534`), green border (`#22c55e`)
- **"Manual: ON"** — solid green background (`#22c55e`), white text, darker green border (`#16a34a`)

Clicking the button opens the same Manual Mode dialog with the physical switch photo.

## Implementation

```python
class IOStatusTab(QWidget):
    def _build_ui(self) -> None:
        ...
        self._manual_btn = QPushButton("Manual: OFF")
        self._manual_btn.setFixedSize(100, 28)
        self._manual_btn.setStyleSheet("""
            QPushButton {
                background: #dcfce7; color: #166534;
                border: 2px solid #22c55e; border-radius: 6px;
                font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background: #bbf7d0; border-color: #16a34a; }
        """)
        self._manual_btn.clicked.connect(self._on_manual_status_clicked)
        ...
        top.addWidget(self._manual_btn)

    def update_io_values(self, io_values: dict[str, bool]) -> None:
        if "DEG_MAN_AUTO" in io_values:
            is_manual = not bool(io_values["DEG_MAN_AUTO"])
            self._set_manual_btn_state(is_manual)
        ...

    def _set_manual_btn_state(self, manual: bool) -> None:
        if manual:
            self._manual_btn.setText("Manual: ON")
            self._manual_btn.setStyleSheet("""
                QPushButton {
                    background: #22c55e; color: white;
                    border: 2px solid #16a34a; border-radius: 6px;
                    font-weight: bold; font-size: 11px;
                }
                QPushButton:hover { background: #16a34a; border-color: #15803d; }
            """)
        else:
            self._manual_btn.setText("Manual: OFF")
            self._manual_btn.setStyleSheet("""
                QPushButton {
                    background: #dcfce7; color: #166534;
                    border: 2px solid #22c55e; border-radius: 6px;
                    font-weight: bold; font-size: 11px;
                }
                QPushButton:hover { background: #bbf7d0; border-color: #16a34a; }
            """)

    def _on_manual_status_clicked(self) -> None:
        if self._manual_dialog is None:
            self._manual_dialog = ManualModeDialog(self)
        self._manual_dialog.show()
        self._manual_dialog.raise_()
        self._manual_dialog.activateWindow()
```

## Key Points

- The button is **always clickable** regardless of mode (opens the photo dialog)
- Visual state updates every poll cycle via `update_io_values()`
- Reuses the same `ManualModeDialog` class as the per-row controls
- Sits in the top bar next to Refresh so it's always visible
- **Sizing fix:** 100px × 28px clips the left edge of "M" in bold text. Use 112px width, 10px font, and 2px padding:
  ```python
  self._manual_btn.setFixedSize(112, 28)
  # stylesheet: font-size: 10px; padding: 2px 4px;
  ```
- **Top-bar layout:** Place buttons in a QHBoxLayout row, then the note label in a separate QHBoxLayout or QVBoxLayout row below. A single horizontal row causes the note text to overlap the button.
  ```python
  top = QVBoxLayout()
  btn_row = QHBoxLayout()
  btn_row.addWidget(self._refresh_btn)
  btn_row.addWidget(self._manual_btn)
  btn_row.addStretch()
  btn_row.addWidget(self._status_lbl)
  top.addLayout(btn_row)
  
  note_lbl = QLabel("...")
  note_lbl.setWordWrap(True)
  top.addWidget(note_lbl)
  ```
- **Mode banner cache:** `DEG_MAN_AUTO` appears in every snapshot. Cache `_cached_man_auto` to prevent banner/control flicker during playback. See `references/degater-playback-blink-fix.md` in `pyside6-widget-flicker-fix` skill.
