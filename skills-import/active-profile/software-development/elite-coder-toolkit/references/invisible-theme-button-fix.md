# Invisible Theme-Styled Button Fix

## Context
User reported: "there is no accept button" on the Diagnostics tab's Alarm Settings panel. The button existed in code (`QPushButton("Apply")`) but was invisible in the UI.

## First Attempt Failure
Changed button label from "Apply" → "Accept" and switched `objectName` from `uiverse_btn` to `uiverse_green`, assuming the theme stylesheet would render it visible. The button remained invisible because the theme QSS selector either didn't match or used colors that blended into the QFormLayout background.

## Root Cause
`setObjectName()` + theme stylesheet is **non-deterministic for visibility** when:
- The widget is nested inside a `QFormLayout` with its own background
- The theme QSS uses selectors that don't match the exact widget hierarchy
- The theme color happens to be the same as the parent container
- The EXE bundles a different Qt/PySide6 version than the dev environment, changing stylesheet parsing

## Second Attempt — Inline Stylesheet
Hard-code `setStyleSheet()` directly on the widget with high-contrast colors:

```python
self._alarm_timeout_btn = QPushButton("Accept")
self._alarm_timeout_btn.setFixedWidth(80)
self._alarm_timeout_btn.setFixedHeight(28)
self._alarm_timeout_btn.setStyleSheet(
    "QPushButton {"
    "  background-color: #22c55e;"
    "  color: #ffffff;"
    "  font-weight: 700;"
    "  font-size: 13px;"
    "  border: 2px solid #16a34a;"
    "  border-radius: 6px;"
    "  padding: 2px 10px;"
    "}"
    "QPushButton:hover {"
    "  background-color: #16a34a;"
    "}"
    "QPushButton:pressed {"
    "  background-color: #15803d;"
    "}"
)
```

This bypasses the theme system entirely. The button is bright green with white bold text — visible in both light and dark themes.

## Lesson
When a user reports a missing UI element that exists in code, the issue is **styling/visibility**, not existence. Do not add another theme selector. Do not assume `objectName` + QSS will work. Hard-code `setStyleSheet()` with high-contrast inline styles immediately. Verify with a screenshot if possible.

## Checklist
- [ ] User says element is missing → check if it exists in code first
- [ ] If it exists → issue is visibility/styling, not absence
- [ ] Use `setStyleSheet()` inline, not `setObjectName()` + theme QSS
- [ ] Pick high-contrast colors (#22c55e green on white text)
- [ ] Add `:hover` and `:pressed` for tactile feedback
- [ ] Verify with screenshot from user if still invisible after fix
