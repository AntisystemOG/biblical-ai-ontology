# UI Kit Image → PySide6 QSS Translation

## Context
User provided a reference image from a gradient-colored UI kit collection (`6349091.jpg`) and asked to redesign buttons in a PySide6 PLC diagnostic app to match it. First attempt produced flat colors that looked nothing like the reference. Second attempt succeeded after detailed vision analysis.

## First Attempt Failure
- Flat solid colors (`#4a1d8a`, `#6b2c91`) — looked like generic dark buttons
- Single generic `#deep_purple` style — no role differentiation
- No gradients, no shadows, no pill shapes
- User response: *"The buttons look nothing like they should please try again"*

## Root Cause
Vision analysis was not performed before writing QSS. The image was assumed to be "purple buttons" and approximated with flat colors. UI kits use **radial gradients**, **elevation shadows**, and **precise geometry** that cannot be guessed.

## Second Attempt — Exact Translation Workflow

### Step 1: Vision Analyze the Reference Image
Use `vision_analyze` with a detailed question requesting:
- Exact border radii (pill = large, icon square = medium, small pill = small)
- Gradient types (linear vs radial) and color stops
- Shadow elevations (blur radius, offset, color)
- Font weight and size
- Active vs rest state color differences

**Result from this session:**
- Large pills: `border-radius: 24px`
- Icon buttons: `44×44px`, `border-radius: 16px`
- Speed pills: `border-radius: 12px`
- Radial gradient on active buttons (`cx:0.3, cy:0.3, radius:1`)
- Light surfaces: `#f0f0f7`, `#f8f9fc`, `#ffffff`
- Deep purple palette: `#6d28d9`, `#7c3aed`, `#5b21b6`, `#a78bfa`, `#c4b5fd`

### Step 2: Create Role-Specific QSS Classes
Never one generic style. Map UI kit roles to object-name selectors:

| UI Kit Role | QSS Selector | Geometry |
|---|---|---|
| Large pill rest | `#deep_purple` | `border-radius: 24px`, `min-height: 40px` |
| Large pill active | `#deep_purple_active` | Same + `qradialgradient` fill |
| Icon square rest | `#deep_purple_icon` | `width: 44px; height: 44px; border-radius: 16px` |
| Icon square active | `#deep_purple_icon_active` | Same + solid purple fill |
| Outlined secondary | `#deep_purple_outline` | White bg + purple border |
| Small pill rest | `#deep_purple_speed` | `border-radius: 12px`, `min-height: 28px` |
| Small pill active | `#deep_purple_speed_active` | Same + gradient fill |

### Step 3: Apply Light Surfaces in BOTH Themes
User explicitly constrained: **"only use light background buttons"** — even dark theme must use light button surfaces.

```qss
/* Dark theme section — buttons stay light */
#deep_purple {
    background-color: #f0f0f7;
    color: #1f2937;
    border: 2px solid #6d28d9;
    ...
}
```

### Step 4: Drop Shadows via QGraphicsDropShadowEffect
For elevation, apply programmatically (QSS `box-shadow` is not supported in Qt):
```python
effect = QGraphicsDropShadowEffect(parent=btn)
effect.setBlurRadius(14)
effect.setColor(QColor("#6d28d9"))
effect.setOffset(0, 4)
btn.setGraphicsEffect(effect)
```

### Step 5: Switch objectName at Runtime
Apply the `runtime-objectname-stylesheet-switching` pattern. Always guard with idempotency:
```python
def _set_playing(self, playing: bool) -> None:
    if getattr(self, "_playing", None) == playing:
        return
    self._playing = playing
    self._play_btn.setObjectName(
        "deep_purple_icon_active" if playing else "deep_purple_icon"
    )
    self._play_btn.style().unpolish(self._play_btn)
    self._play_btn.style().polish(self._play_btn)
    self._play_btn.update()
```

## Files Changed in This Session
- `src/plc_tools/gui/theme.py` — Complete rewrite of `#deep_purple` section (both light and dark)
- `src/plc_tools/gui/tabs/playback_record.py` — Button object-name assignments
- `src/plc_tools/gui/widgets/playback_strip.py` — Strip transport buttons

## Checklist for Future UI Kit Translations
- [ ] Run `vision_analyze` on the reference image before writing any QSS
- [ ] Extract exact border radii, gradient types, and color hex values
- [ ] Create role-specific object-name selectors (never one generic style)
- [ ] Apply light surfaces if user requests light buttons
- [ ] Use `QGraphicsDropShadowEffect` for elevation (QSS box-shadow unsupported)
- [ ] Guard every `setObjectName()` with an idempotency check
- [ ] Batch multiple button updates with `setUpdatesEnabled(False/True)`
