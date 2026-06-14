# Session: Remove In-App Playback, Crash Fix, Strip Bottom Playback Widgets

Date: 2026-06-03 | Versions: v2.23.16 → v2.23.17

## Problem: App Crashes During Playback

**Symptom:** The entire app crashes intermittently when using the timeline playback feature.

**Root cause:** `_on_playback_update()` in `main_window.py` pushed snapshot data (`bool_values`) to live tabs (`_tab_io`, `_tab_all_tags`) via the `playback_update` signal while the background PLC poll was ALSO pushing live data. Two competing data streams → race conditions inside `setUpdatesEnabled(True/False)` blocks → eventual crash.

**Additional crash factors:**
- `_playback_stability_filter` counters were shared between playback and live data, causing state corruption
- `setUpdatesEnabled(False)` + long-running CIP reads on the main thread created deadlock windows
- `PlaybackStrip` (bottom widget) had its own timer fighting with the tab's `_play_timer`

## Solution: Playback Never Touches Live Tabs

**Architecture change:** The standalone `PlaybackReviewWindow` already existed and handled all playback visualization. The fix was to **delete the in-app playback path entirely** so playback data never reaches live tabs.

### What was deleted

**`playback_record.py` — stripped from 771 lines to ~270 lines**
- ❌ Timeline slider (QSlider)
- ❌ Transport buttons (⏮ ◀◀ ◀ ▶ ▶▶ ⏭)
- ❌ Speed selector buttons (x1 x2 x4 x8 x16)
- ❌ I/O Values table (left pane of splitter)
- ❌ Fault Snapshots table (right pane of splitter)
- ❌ `playback_update` Signal (the crash source)
- ❌ `_play_timer`, `_advance`, `_toggle_play`, `_set_speed`, `_go_prev`, `_go_next`
- ✅ Kept: `▶ Start Recording`, `■ Stop Recording`, `📂 Load Recording`, `▶ Playback Recording`

**`main_window.py` — removed 100+ lines of playback fight code**
- ❌ `PlaybackStrip` import + `_pb_strip` widget → bottom timeline bar removed from all pages
- ❌ `_on_playback_update()` — the crash source (removed entirely)
- ❌ `_on_strip_play_pause()`, `_on_strip_seek()`, `_on_strip_sync()`
- ❌ `_playback_last_values`, `_playback_stability_counter`, `_playback_stability_threshold` attributes
- ❌ All `playback_update` signal wiring (`.connect()` calls)
- ❌ All `_pb_strip.arm()` / `.set_playing()` / `.set_idle()` / `.update_status()` calls

### Visual result

- **Playback & Record tab** is now just two button rows + info text. Clean and simple.
- **No bottom strip** on any page — the footer is gone.
- **Playback only happens in the standalone `PlaybackReviewWindow`**, completely isolated from live data.

## Files Modified

| File | Lines Changed | What |
|---|---|---|
| `src/plc_tools/gui/tabs/playback_record.py` | ~771 → ~270 | Strip to recording controls + review launcher |
| `src/plc_tools/gui/main_window.py` | -100+ lines | Remove `_on_playback_update()`, `_pb_strip`, playback wiring |
| `src/plc_tools/gui/widgets/playback_strip.py` | unchanged | Module still exists but no longer imported by `main_window.py` |

## Quality Gate

Before build: `py_compile` changed files, AST parse all 40 `.py` files, stale reference hunt (`grep -rn _pb_strip\|_playback_last_values\|_playback_stability`). Zero stale references found.

## Build

`dist/Degater PLCTool BST33 and 35.exe` v2.23.17, 46 MB (unchanged size because removed code was negligible in bundle).
