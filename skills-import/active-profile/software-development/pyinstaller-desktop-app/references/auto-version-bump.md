# Auto-Version Bump for PyInstaller Desktop Apps

Pattern: **`MAJOR.WEEKLY.BUILD`** semantic versioning with automatic
increment on every build.

## Rules

| Segment | When It Bumps | Reset Behavior |
|---|---|---|
| **MAJOR** | Manual only (architectural change) | Reset WEEKLY and BUILD to 0 |
| **WEEKLY** | Auto on first build of a new ISO calendar week | Continues from prev week |
| **BUILD** | Auto on **every** PyInstaller rebuild | Never resets; increments forever |

## Implementation

### 1. version.py (single source of truth)

Place in `src/my_app/version.py`:

```python
from __future__ import annotations
from datetime import datetime

_MAJOR: int = 2
_WEEKLY: int = 22
_BUILD: int = 0

__version__: str = f"{_MAJOR}.{_WEEKLY}.{_BUILD}"


def _iso_year_week(dt: datetime) -> int:
    iso_cal = dt.isocalendar()
    return int(f"{iso_cal.year}{iso_cal.week:02d}")


def auto_bump(is_build: bool = False) -> str:
    """Bump version and return new string.

    is_build=False -> weekly bump if new week
    is_build=True  -> weekly bump + build bump (always)
    """
    global _WEEKLY, _BUILD

    today = datetime.now()
    today_yw = _iso_year_week(today)
    stored_yw = (today.year % 100) * 100 + _WEEKLY

    changed = []
    if today_yw != stored_yw:
        _WEEKLY = today_yw % 100
        changed.append(f"WEEKLY -> {_WEEKLY}")

    if is_build:
        _BUILD += 1
        changed.append(f"BUILD -> {_BUILD}")

    new_ver = f"{_MAJOR}.{_WEEKLY}.{_BUILD}"
    if changed:
        print(f"Version: {__version__} -> {new_ver}")
        for c in changed:
            print(f"  {c}")
    return new_ver
```

### 2. build_exe.py (calls auto_bump before PyInstaller)

```python
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")


def _bump_version() -> str:
    sys.path.insert(0, SRC)
    try:
        from my_app.version import auto_bump
        new_version = auto_bump(is_build=True)

        # Overwrite version.py with bumped values
        # (parse new_version and regenerate the file)
        ...

        return new_version
    finally:
        sys.path.remove(SRC)


def main() -> None:
    version = _bump_version()
    env = os.environ.copy()
    env["MY_APP_VERSION"] = version

    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "MyApp.spec", "--noconfirm"],
        check=True,
        env=env,
    )
    print(f"Build complete. Version: {version}")
```

### 3. Display version in the app

**Window title:**
```python
from my_app.version import __version__
self.setWindowTitle(f"My App  v{__version__}")
```

**About tab:**
```python
version_label = QLabel(f"Version <b>v{__version__}</b>")
```

**QApplication metadata:**
```python
app.setApplicationVersion(__version__)
```

## Why Not semver.patch?

- Semver `patch` is human-decided ("bugfix" vs "feature")
- `WEEKLY` is calendar-driven (time-based release cadence)
- `BUILD` is mechanical (every rebuild increments, no judgment calls)
- Together they guarantee every EXE has a unique, sortable identifier

## Pitfalls

- **Week boundary at midnight between Sat/Sun** — ISO week starts Monday.
  A build on Sunday night and Monday morning may get same week number
  depending on timezone. Use localtime consistently.
- **Git commits don't bump** — only the EXE build bumps. `version.py`
  is runtime-readable, so the committed source always shows the PREVIOUS
  build number. This is correct — the build process is what increments.
- **Parallel builds** — if two developers build simultaneously from same
  commit, they get same version. Add a CI build number suffix if needed.
- **Hardcoded version strings in About dialogs / Help menus** — A
  common pattern in PySide6 apps is a `QMessageBox.about()` in a Help
  menu that shows a hardcoded version. This gets stale immediately.
  Always use the dynamic import:
  ```python
  def _show_about(self) -> None:
      from my_app.version import __version__
      QMessageBox.about(
          self, "About",
          f"<p><b>Version {__version__}</b></p>"
          ...
      )
  ```
  Never hardcode `<p><b>Version 1.05</b></p>` in the dialog text.
