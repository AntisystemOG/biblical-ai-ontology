# Session 2026-06-02: Robot Interface Tab in Playback Review

## Problem

The standalone `PlaybackReviewWindow` had tabs for DEG 1, DEG 2, DEG 3, and System Controls — but the **Robot Interface** tab (DI 185–191, showing PLC → Robot digital outputs) was missing. This meant no `Upper_Ready_For_Parts`, `Lower_Completed_Cuts`, `DEG_Home_And_Ready`, `Complete_Runner_Drop`, etc. in playback review.

## Fix

Add a 5th tab to `PlaybackReviewWindow` that mirrors the live `robot_interface.py` tab exactly.

### `_build_robot_tab()` implementation

```python
def _build_robot_tab(self) -> tuple[QWidget, QTableWidget, list]:
    """Build the Robot Interface tab (DI 185–191) for playback review."""
    from plc_tools.gui.tabs.robot_interface import ROBOT_DI_MAP

    page = QWidget()
    vlay = QVBoxLayout(page)

    title = QLabel("KM Robot Digital Inputs  (PLC Outputs → Robot DI 185–191)")
    title.setStyleSheet(
        "QLabel { font-size: 14px; font-weight: bold; color: #4338ca; }"
    )
    vlay.addWidget(title)

    # Playback mode banner
    banner = QLabel("▶ PLAYBACK MODE — Reviewing recorded data")
    banner.setStyleSheet(...)
    vlay.addWidget(banner)

    # Table: 5 columns (DI #, Status, Robot Label, PLC Tag, Physical Address)
    table = QTableWidget(len(ROBOT_DI_MAP), 5)
    table.setHorizontalHeaderLabels(
        ["DI #", "Status", "Robot Label", "PLC Tag", "Physical Address"]
    )
    # ... (resize modes, stylesheets) ...

    leds: list = []
    for row, entry in enumerate(ROBOT_DI_MAP):
        di = entry["di"]
        plc_tag = entry["plc_tag"]
        robot_label = entry["robot_label"]

        # DI number (column 0)
        # Status placeholder (column 1) — grey ball, updated per snapshot
        # Robot label (column 2)
        # PLC tag (column 3)
        # Physical Address (column 4) — from PHYSICAL_ADDRESS_MAP
        phys = _get_physical_address(plc_tag)
        phys_item = QTableWidgetItem(phys)
        phys_item.setFont(QFont("Consolas", 9))
        phys_item.setForeground(QColor("#6b7280"))
        table.setItem(row, 4, phys_item)

        leds.append((row, plc_tag))

    vlay.addWidget(table, stretch=1)

    # DI 191 troubleshooting hint
    hint = QLabel("💡  If the robot reports ...")
    vlay.addWidget(hint)

    return page, table, leds
```

### `_update_robot_tab()` per-snapshot update

```python
def _update_robot_tab(self, values: dict) -> None:
    """Refresh the Robot Interface tab from current snapshot values."""
    for row, plc_tag in self._robot_leds:
        val = values.get(plc_tag, False)
        status = "🟢 ON" if val else "⚪ OFF"
        color = "#059669" if val else "#9ca3af"
        item = self._robot_table.item(row, 1)
        if item is None:
            item = QTableWidgetItem(status)
            item.setTextAlignment(Qt.AlignCenter)
            self._robot_table.setItem(row, 1, item)
        item.setText(status)
        item.setForeground(QColor(color))
```

### Updated `_show_snapshot()` wiring

```python
# In _show_snapshot():
# Update Robot Interface tab
self._update_robot_tab(snap.values)
```

## Key Design Decisions

1. **Import `ROBOT_DI_MAP` from live tab module** — never duplicate the DI mapping. The live tab is the single source of truth.
2. **Physical Address column** — same `_get_physical_address()` function as I/O tables, using `PHYSICAL_ADDRESS_MAP` from `physical_mapping.py`.
3. **Status as text (🟢/⚪) not StatusLed widget** — simpler in a QTableWidget cell, easier to update per-snapshot without widget recreation.
4. **5 columns vs 4 in live tab** — added Physical Address for consistency with all other playback tables.

## Physical Address mappings for EM DO tags

| PLC Tag | Physical Address |
|---|---|
| `Upper_Ready_For_Parts` | `_IO_EM_DO_00` |
| `Lower_Ready_For_Parts` | `_IO_EM_DO_01` |
| `Upper_Completed_Cuts` | `_IO_EM_DO_02` |
| `Lower_Completed_Cuts` | `_IO_EM_DO_03` |
| `Tilt_DEG_Pos_Deflector` | `_IO_EM_DO_04` |
| `Complete_Runner_Drop` | `_IO_EM_DO_05` |
| `DEG_Home_And_Ready` | `_IO_EM_DO_06` |

## Files changed
- `gui/playback_review_window.py` — `_build_robot_tab()`, `_update_robot_tab()`, tab registration

## Build
- Version: 2.23.11
- Size: 46 MB
