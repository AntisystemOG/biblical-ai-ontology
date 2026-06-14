# PySide6 View Menu Patterns

## Theme Toggle (Radio Items Directly in View Menu)

**Pattern:** Present Light/Dark theme choices as radio-group items directly in the View menu, not nested in a submenu. Users expect to see them at a glance.

```python
from PySide6.QtGui import QAction, QActionGroup

view_menu = menubar.addMenu("View")

self._theme_group = QActionGroup(self)
self._theme_group.setExclusive(True)

light_action = view_menu.addAction("Light Theme")
light_action.setCheckable(True)
light_action.setChecked(True)
light_action.setActionGroup(self._theme_group)
light_action.triggered.connect(lambda: self._set_theme("light"))

dark_action = view_menu.addAction("Dark Theme")
dark_action.setCheckable(True)
dark_action.setActionGroup(self._theme_group)
dark_action.triggered.connect(lambda: self._set_theme("dark"))
```

## Always on Top

**Pattern:** Toggle `Qt.WindowStaysOnTopHint` on the main window.

```python
from PySide6.QtCore import Qt

def _toggle_always_on_top(self, checked: bool) -> None:
    flags = self.windowFlags()
    if checked:
        self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
    else:
        self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
    self.show()  # Required after changing window flags
```

**Note:** The `Qt` constant is already imported via `from PySide6.QtCore import Qt` in most PySide6 projects. No need for a local `import Qt` inside the method.

## Full Screen Toggle

```python
def _toggle_fullscreen(self) -> None:
    if self.isFullScreen():
        self.showNormal()
    else:
        self.showFullScreen()
```

## Status Bar Toggle

```python
def _toggle_statusbar(self, checked: bool) -> None:
    self._status_bar.setVisible(checked)
```

## Zoom Controls (Application Font Scaling)

```python
def _zoom_in(self) -> None:
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        f = app.font()
        f.setPointSize(f.pointSize() + 1)
        app.setFont(f)

def _zoom_out(self) -> None:
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        f = app.font()
        new_size = max(8, f.pointSize() - 1)
        f.setPointSize(new_size)
        app.setFont(f)

def _zoom_reset(self) -> None:
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        f = app.font()
        f.setPointSize(13)
        app.setFont(f)
```

## Theme Switching with Stylesheet

```python
def _set_theme(self, mode: str) -> None:
    from PySide6.QtWidgets import QApplication
    from plc_tools.gui.theme import STYLESHEET, DARK_STYLESHEET

    app = QApplication.instance()
    if app is None:
        return
    if mode == "dark":
        app.setStyleSheet(DARK_STYLESHEET)
        self._status_bar.showMessage("Dark theme enabled", 2000)
    else:
        app.setStyleSheet(STYLESHEET)
        self._status_bar.showMessage("Light theme enabled", 2000)
```

## Avoid Destructive "Clear All" in View Menu

**Anti-pattern:** A "Clear All" View menu item that wipes data across all tabs. Users click View menu expecting display options, not destructive data operations.

**What to do instead:** Keep per-tab clear buttons on the tabs themselves. The View menu should only contain display/presentation options (theme, zoom, full screen, status bar, always on top).

## When to REMOVE Items from View Menu

Not every standard View menu item belongs in every application. Remove items that are irrelevant to the app's purpose or that create maintenance burden without user value.

### Theme Toggle — Remove if the app has a single intended appearance

**When to remove:** The application has one canonical visual style (e.g., a light-themed industrial diagnostics tool). A theme toggle adds complexity (two stylesheets to maintain, testing both modes) with no user benefit.

**What to do instead:** Keep only the intended stylesheet. Remove the `QActionGroup` and all theme-switching code. Don't leave dead code in the menu.

### Zoom In / Out / Reset — Remove if font scaling breaks the layout

**When to remove:** The application uses fixed-size widgets, pixel-perfect industrial layouts, or table-based UIs where font scaling causes clipping, misalignment, or unreadable text. Qt's global font scaling affects *all* widgets, not just text — this often breaks carefully tuned layouts.

**What to do instead:** Remove zoom actions entirely. If accessibility is a concern, handle it at the OS level or with per-widget font adjustments that the layout engine can accommodate.

### Status Bar Toggle — Remove if the status bar is always required

**When to remove:** The status bar carries critical connection state, alarm counts, or live data that the user must always see. Hiding it creates a safety hazard (user thinks they're connected when the bar is hidden).

**What to do instead:** Keep the status bar permanently visible. Remove the toggle action and any `setVisible(False)` paths.

### Minimal View Menu Example (industrial diagnostics app)

```python
def _build_menu(self) -> None:
    menubar = self.menuBar()

    # ── View menu (minimal) ──────────────────────────────────────────────
    view_menu = menubar.addMenu("View")

    fullscr_action = view_menu.addAction("Full Screen")
    fullscr_action.setShortcut("F11")
    fullscr_action.triggered.connect(self._toggle_fullscreen)

    view_menu.addSeparator()

    aot_action = view_menu.addAction("Always on Top")
    aot_action.setCheckable(True)
    aot_action.triggered.connect(self._toggle_always_on_top)
```

**Rule:** The View menu should only contain items that genuinely add value for *this* application's users. When in doubt, leave it out — users won't miss what they never had.

## About Dialog Best Practices

Keep the About dialog factual, minimal, and legally safe.

```python
def _show_about(self) -> None:
    QMessageBox.about(
        self,
        "About MyApp",
        "<h2>MyApp</h2>"
        "<p><b>Version 1.05</b></p>"
        "<p>Custom software made by [Author] for [Company]</p>"
        "<p>With the Assistance of AI — 5/29/2026</p>"
        "<hr>"
        "<p style='font-size:11px; color:#666;'>"
        "Built with PySide6 · pycomm3</p>"
    )
```

**Do include:** App name, version, author/company attribution, date, and third-party library credits.
**Don't include:** Unverifiable claims, excessive legal text, or dynamic data that changes between builds (causes build non-determinism).
