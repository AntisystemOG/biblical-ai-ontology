# Manual Mode Photo Popup Pattern

Session: 2026-05-29 — Degater PLC Tool

## Problem

When the PLC is in Auto mode, output forcing controls should be unavailable. Simply graying out ON/OFF buttons is unclear — users don't know *why* they can't force outputs or *how* to enable forcing.

## Solution

Instead of disabled controls, **swap the widget entirely**:
- **Auto mode:** Show a single **⚠ Manual** button per output row
- **Manual mode:** Show the full **ON / OFF / Release** control group

Clicking **⚠ Manual** opens a non-modal dialog with a photograph of the physical MAN-AUTO switch on the line and instructions for how to switch to manual mode.

## Why This Works Better

| Approach | Problem |
|----------|---------|
| Grayed-out ON/OFF buttons | User doesn't know *why* or *how to fix* |
| Banner text only | Easy to miss, doesn't help first-time users |
| **⚠ Manual button + photo dialog** | Tells user exactly what to do and shows them the physical switch |

## Code Pattern

```python
class ManualControlWidget(QWidget):
    def _build_ui(self) -> None:
        # ... create Manual button + ON/OFF/Release controls ...
        self.set_manual_mode(False)  # default to auto

    def set_manual_mode(self, enabled: bool) -> None:
        """Swap visibility between Manual button (auto) and controls (manual)."""
        self._manual_btn.setVisible(not enabled)
        self._on_btn.setVisible(enabled)
        self._off_btn.setVisible(enabled)
        self._release_btn.setVisible(enabled)

    def _on_manual_clicked(self) -> None:
        if self._dialog is None:
            self._dialog = ManualModeDialog(self)
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()
```

## Dialog Implementation

See the main SKILL.md for the full `ManualModeDialog` code including `QPixmap` image loading with PyInstaller `_MEIPASS` support.

## PyInstaller Asset Bundling

```python
datas=[
    ('src/plc_tools/gui/assets', 'plc_tools/gui/assets'),
],
```

The image file (e.g., `Manual.jpg`) is placed in `src/plc_tools/gui/assets/` and extracted at runtime to `sys._MEIPASS/plc_tools/gui/assets/Manual.jpg`.

**Critical: verify the `_MEIPASS` path matches the spec's `datas` mapping.** If the spec maps `('src/plc_tools/gui/assets', 'plc_tools/gui/assets')`, the runtime path must include the `plc_tools/gui` prefix — not just `gui/assets`. See `elite-coder-toolkit` skill, `references/pyinstaller-windows-from-wsl.md` for the full pitfall.

## User-Requested Display Text

The tag `DEG_MAN_AUTO` should be displayed to users as **"Degator is in Auto"** — not the raw tag name. All user-facing strings (tag browser, I/O tables, dialogs, banners) use this display name while the code continues to use `DEG_MAN_AUTO` for PLC communication.
