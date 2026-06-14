---
name: pyside6-widget-flicker-fix
description: Eliminate widget flicker/blink when rapidly updating PySide6 UI elements (playback, polling, timelines)
---

# PySide6 Widget Flicker Fix

## Problem
Widgets (LEDs, buttons, labels, banners) appear to blink or glitch when updated rapidly — e.g. during timeline playback or fast PLC polling.

## Root Causes

### 1. Unconditional `setStyleSheet()` / `setChecked()` calls
Every update frame reapplies styles even when state hasn't changed, triggering full repaints.

**Fix:** Guard with state comparison:
```python
# BEFORE — flickers every frame
self._on_btn.setChecked(is_on)

# AFTER — only repaints on change
if self._on_btn.isChecked() != is_on:
    self._on_btn.setChecked(is_on)
```

### 2. Unconditional stylesheet override in mode switchers
```python
# BEFORE — thrashes stylesheet every snapshot
def set_manual_mode(self, enabled: bool):
    self._manual_enabled = enabled
    self._update_button_states()   # ← always runs

# AFTER — only when mode changes
if enabled == self._manual_enabled:
    return
self._manual_enabled = enabled
self._update_button_states()
```

### 3. Status indicators repainting every frame
```python
# BEFORE
self._led.set_green()   # calls update() every time
self._label.setText("ON")

# AFTER — early return if no change
if on == self._is_on:
    return
self._is_on = on
self._led.set_green()
```

### 4. Banner text re-set every frame
Cache the previous value and only update on change:
```python
cached = getattr(self, "_cached_man_auto", None)
if cached != is_auto:
    self._cached_man_auto = is_auto
    self._set_manual_mode_banner(not is_auto)
```

### 5. Runtime objectName-based stylesheet switching (no inline CSS)
For buttons that change color based on state (play/pause, active speed, mode toggle), use `#id` selectors in a central QSS file and switch `objectName` at runtime instead of `setStyleSheet`:

```python
# In theme.py — define both states
#deep_purple { background: #4a1d8a; ... }
#deep_purple_active { background: #6b2c91; ... }

# In widget code — switch objectName
self._play_btn.setObjectName("deep_purple_active")
self._play_btn.style().unpolish(self._play_btn)
self._play_btn.style().polish(self._play_btn)
self._play_btn.update()
```

This eliminates inline CSS duplication, reduces runtime parsing cost, and keeps theme logic centralized. Always guard with an idempotency check (`if current_name == new_name: return`) to avoid unnecessary polish cycles.

See `references/runtime-objectname-stylesheet-switching.md` for full implementation details.

## Checklist

| Widget Type | Guard Strategy |
|---|---|
| `QPushButton.setChecked()` | Compare `isChecked()` before setting |
| `QPushButton.setStyleSheet()` | Cache mode flag, skip if unchanged |
| `QLabel.setText()` | Cache last text, skip if same |
| `QLabel.setStyleSheet()` | Cache mode flag, skip if same |
| Custom paint widgets (`StatusLed`) | Cache color string, `update()` only on change |
| `setEnabled()` | Compare current state before setting |

## Batching (additional technique)
For bulk updates across many widgets, wrap in `setUpdatesEnabled`:
```python
self.parent_widget.setUpdatesEnabled(False)
try:
    # ... update hundreds of indicators ...
    for indicator in self._indicators:
        indicator.set_on(new_value)
finally:
    self.parent_widget.setUpdatesEnabled(True)
```

## Architectural Decision: Upstream Deduplication vs. Downstream Idempotency

When rapid updates arrive (e.g. playback snapshots or fast PLC polling), you have two places to prevent flicker:

| Approach | Pros | Cons |
|---|---|---|
| **Upstream deduplication** (dedupe in data source) | Fewer signals emitted | Leaks business logic into data layer; still need guards downstream for safety |
| **Downstream idempotency** (guard in every widget) | Robust; widgets safe regardless of source | More code; must add guard to every update path |

**Recommendation:** Prefer **downstream idempotency** for PLC playback/polling apps. The UI must be safe even if the data layer changes or emits duplicates. Add guards in every `set_on()`, `set_manual_mode()`, `setChecked()`, and `setText()` call.

## Checklist (expanded)

| Widget Type | Guard Strategy |
|---|---|
| Custom indicator `set_on(bool)` | Cache `_is_on`, early-return if same |
| Mode widget `set_manual_mode(bool)` | Cache `_manual_enabled`, early-return if same |
| `QPushButton.setChecked()` | Compare `isChecked()` before setting |
| `QPushButton.setStyleSheet()` | Cache mode flag, skip if unchanged |
| `QLabel.setText()` | Cache last text, skip if same |
| `QLabel.setStyleSheet()` | Cache mode flag, skip if same |
| Custom paint widgets (`StatusLed`) | Cache color string, `update()` only on change |
| `setEnabled()` | Compare current state before setting |

### 4. Emoji clipping in fixed-width nav items
Wide emoji glyphs (e.g., `🔴`) can be clipped by the right edge of a fixed-width `QListWidgetItem` or narrow `QListWidget`.

**Fix:** Widen the container or use a narrower character:
```python
# BEFORE — 180px sidebar clips the red circle emoji
self._nav_list.setFixedWidth(180)
item.setText("🔴 Alarms & Logs")   # right edge of emoji cut off

# AFTER — 200px gives enough room
self._nav_list.setFixedWidth(200)
splitter.setSizes([200, 880])       # adjust splitter to match
item.setText("🔴 Alarms & Logs")    # full emoji visible
```

If widening is not an option, substitute a narrower character:
```python
# Narrower alternative — single-color, no right-edge overflow
item.setText("● Alarms & Logs")     # bullet glyph, monochrome
```

## Visual Polish: Gradient Buttons from UI Kit References

When a user provides a UI kit image (buttons, gradients, palettes) and asks for matching QSS, flat colors are insufficient. Professional UI kit buttons use radial gradients, drop shadows, and precise geometry.

### Translation Workflow
1. **Vision-analyze the reference image** — extract exact border radii, color hex values, gradient types (linear vs radial), shadow elevations, and font weights.
2. **Map UI kit roles to QSS object-name classes** — never one generic style. Create role-specific selectors:
   - `#deep_purple` — large pill rest state (`border-radius: 24px`)
   - `#deep_purple_active` — active pill with `qradialgradient(cx:0.3, cy:0.3, radius:1, ...)`
   - `#deep_purple_icon` / `#deep_purple_icon_active` — 44×44 rounded squares (`border-radius: 16px`)
   - `#deep_purple_outline` — white surface + purple border for secondary actions
   - `#deep_purple_speed` / `#deep_purple_speed_active` — small pills (`border-radius: 12px`)
3. **Apply via objectName switching** — see `references/runtime-objectname-stylesheet-switching.md`
4. **Idempotency guard every switch** — skip polish cycles if the name hasn't changed

### Critical User Constraint: Light Surfaces Only
When the user says "only use light background buttons," apply light surfaces (`#f0f0f7`, `#f8f9fc`, `#ffffff`) **even in the dark theme section** of the stylesheet. Do not default to dark gray for dark mode buttons.

### Deep Purple Palette (from UI kit)
| Token | Hex | Usage |
|---|---|---|
| Primary | `#6d28d9` | Rest border, hover accent |
| Active | `#7c3aed` | Active fill center |
| Dark | `#5b21b6` | Active edge, pressed |
| Light | `#a78bfa` | Hover highlights |
| Pale | `#c4b5fd` | Very light accents |

### Elevation with Drop Shadow
```python
effect = QGraphicsDropShadowEffect(parent=btn)
effect.setBlurRadius(14)
effect.setColor(QColor("#6d28d9"))
effect.setOffset(0, 4)
btn.setGraphicsEffect(effect)
```

See `references/ui-kit-to-qss-translation.md` for the full two-attempt story and checklist.

## Verification
Run playback at 1× speed. All widgets should hold steady — no blinking.

## Session Example
See `references/degater-playback-blink-fix.md` for a full reproduction — three root causes in one PySide6 PLC playback app, all fixed with downstream idempotency guards.

See `references/ui-kit-to-qss-translation.md` for the full two-attempt story of translating a UI kit reference image into exact QSS — including the critical "vision analyze first" rule.

## Invisible Theme-Styled Button Fix
When a user reports a missing button that exists in code, the problem is **styling/visibility**, not absence. Theme-based QSS via `setObjectName()` is non-deterministic inside `QFormLayout` or when theme colors match the parent background. Use **inline `setStyleSheet()`** with high-contrast colors instead.

**Example from the Degater project (Alarm Settings panel, June 2026):**
- Button existed as `QPushButton("Apply")` with `objectName("uiverse_btn")` — invisible
- Renamed to "Accept", switched to `uiverse_green` — still invisible
- **Fix:** Hard-coded inline stylesheet with `#22c55e` green background + white bold text

```python
self._btn.setStyleSheet(
    "QPushButton {"
    "  background-color: #22c55e;"
    "  color: #ffffff;"
    "  font-weight: 700;"
    "  font-size: 13px;"
    "  border: 2px solid #16a34a;"
    "  border-radius: 6px;"
    "  padding: 2px 10px;"
    "}"
    "QPushButton:hover { background-color: #16a34a; }"
    "QPushButton:pressed { background-color: #15803d; }"
")
```

Full details in `references/invisible-theme-button-fix.md`.
