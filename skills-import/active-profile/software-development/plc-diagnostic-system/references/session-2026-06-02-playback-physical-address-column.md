# Session 2026-06-02: Physical Address Column in Playback Tables

## Problem

The playback review window I/O tables showed Status, Tag Name, and Description — but operators need the **physical wiring address** (e.g. `_IO_X1_DI_01`) to trace signals back to the PLC terminal block.

## Fix

Add a 4th column **"Physical Address"** to all Input and Output tables in the playback review window. Also add a 5th column to the Robot Interface tab.

## Implementation

### Import

```python
from plc_tools.catalog.physical_mapping import PHYSICAL_ADDRESS_MAP
```

### Helper

```python
def _get_physical_address(tag: str) -> str:
    if tag in PHYSICAL_ADDRESS_MAP:
        return PHYSICAL_ADDRESS_MAP[tag]
    clean = tag.lstrip("_")
    if clean in PHYSICAL_ADDRESS_MAP:
        return PHYSICAL_ADDRESS_MAP[clean]
    return "—"
```

### Table creation (4 columns)

```python
table = QTableWidget(0, 4)
table.setHorizontalHeaderLabels(["Status", "Tag Name", "Description", "Physical Address"])
table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
```

### Rendering

```python
phys = _get_physical_address(tag)
phys_item = QTableWidgetItem(phys)
phys_item.setFont(QFont("Consolas", 9))
phys_item.setForeground(QColor("#6b7280"))
if is_alarm:
    phys_item.setBackground(QColor("#fef3c7"))
table.setItem(i, 3, phys_item)
```

## Styling

- **Font:** Consolas 9pt (monospace)
- **Color:** `#6b7280` (medium gray)
- **Alarm highlight:** Yellow (`#fef3c7`) background

## Files changed
- `gui/playback_review_window.py`

## Build
- Version: 2.23.12 / 2.23.13
