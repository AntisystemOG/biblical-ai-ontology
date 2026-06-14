# Runtime ObjectName Stylesheet Switching

## Problem
Dynamically changing button colors at runtime with `setStyleSheet()` causes stylesheet thrashing, repaint storms, and code duplication. Every state change rewrites inline CSS.

## Solution: ObjectName-Based Classes in Central QSS

Define all visual states as `#id` selectors in a central stylesheet (`theme.py`), then switch `objectName` at runtime. This keeps styling in one place and leverages Qt's native stylesheet engine.

### 1. Define Classes in Theme

```python
# theme.py — light theme section
STYLESHEET = """
/* ... existing styles ... */

#deep_purple {
    background-color: #4a1d8a;
    color: #ffffff;
    border: 2px solid #6b2c91;
    border-radius: 8px;
    font-weight: bold;
    font-size: 11px;
    padding: 4px 12px;
}
#deep_purple:hover {
    background-color: #5a2d9a;
    border-color: #7b3ca1;
}
#deep_purple:pressed {
    background-color: #3a0d7a;
    border-color: #4a1d8a;
}
#deep_purple:disabled {
    background-color: #2a1d4a;
    color: #9ca3af;
    border-color: #3a2d5a;
}

#deep_purple_active {
    background-color: #6b2c91;
    color: #ffffff;
    border: 2px solid #8b4cb1;
    border-radius: 8px;
    font-weight: bold;
    font-size: 11px;
    padding: 4px 12px;
}
#deep_purple_active:hover {
    background-color: #7b3ca1;
    border-color: #9b5cc1;
}
#deep_purple_active:pressed {
    background-color: #5a1c81;
    border-color: #6b2c91;
}
"""

# Also define in DARK_STYLESHEET with adjusted colors
```

### 2. Apply ObjectName at Runtime

```python
from PySide6.QtWidgets import QPushButton

class TransportControls(QWidget):
    def __init__(self):
        super().__init__()
        self._play_btn = QPushButton("▶ Play")
        self._play_btn.setObjectName("deep_purple")
        # No inline stylesheet needed

    def _set_playing(self, playing: bool) -> None:
        """Switch button visual state between active and idle."""
        # BEFORE — thrashes inline stylesheet every toggle
        # self._play_btn.setStyleSheet("...long CSS...")

        # AFTER — clean objectName switch with polish cycle
        self._play_btn.setObjectName(
            "deep_purple_active" if playing else "deep_purple"
        )
        self._play_btn.style().unpolish(self._play_btn)
        self._play_btn.style().polish(self._play_btn)
        self._play_btn.update()
```

### 3. Batch Updates for Multiple Buttons

```python
def _update_speed_buttons(self, active_speed: str) -> None:
    """Update all speed toggle buttons in one polish cycle."""
    self.setUpdatesEnabled(False)
    try:
        for speed, btn in self._speed_buttons.items():
            is_active = (speed == active_speed)
            btn.setObjectName(
                "deep_purple_active" if is_active else "deep_purple"
            )
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()
    finally:
        self.setUpdatesEnabled(True)
```

### 4. Idempotency Guard (Still Required)

ObjectName switching still benefits from change-guarding:

```python
def _set_mode_active(self, active: bool) -> None:
    if getattr(self, "_mode_active", None) == active:
        return  # no change, skip expensive polish cycle
    self._mode_active = active
    self._mode_btn.setObjectName(
        "deep_purple_active" if active else "deep_purple"
    )
    self._mode_btn.style().unpolish(self._mode_btn)
    self._mode_btn.style().polish(self._mode_btn)
    self._mode_btn.update()
```

## Why This Beats Inline Stylesheets

| Concern | Inline `setStyleSheet` | ObjectName + Central QSS |
|---|---|---|
| Code duplication | High — CSS scattered in Python | Low — one theme file |
| Runtime cost | Parses CSS string every call | Qt's native ID lookup |
| Theme switching | Manual rebuild of all strings | Single stylesheet swap |
| Dark/light | Duplicate CSS with adjusted colors | Two stylesheet strings |
| Maintainability | Hard to grep, easy to drift | Centralized, versioned |

## Pitfalls

1. **Forgotten polish cycle** — Without `unpolish()` + `polish()` + `update()`, Qt may not re-evaluate the stylesheet for that widget immediately. The visual change appears delayed or missing.
2. **Wrong selector type** — Use `#id` (object name) not `.class` (Qt stylesheet classes don't work like CSS classes on arbitrary widgets). `QPushButton#deep_purple` is valid; `.deep_purple` is not.
3. **Object name collision** — `setObjectName()` replaces the entire name. If you also use object names for `findChild()`, pick a naming scheme: `"btn_deep_purple"` vs `"deep_purple_active"`.
