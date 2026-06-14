# Proactive Playback Mode Switch

When the user clicks Play in the playback tab, the mode must switch to **playback immediately**, before the first timer tick arrives. Waiting for the first `_refresh()` call creates a race condition where live PLC data can leak in.

## Problem

The original flow:
1. User clicks ▶ Play → `_play()` starts `_play_timer`
2. First timer tick arrives → `_refresh()` runs
3. `_refresh()` sets `_mode = "playback"` and emits `playback_update`
4. Only then does `MainWindow._on_playback_update()` switch modes
5. Between step 1 and step 3, live polls may still arrive and overwrite the UI

This creates **visible flicker** — user sees live data briefly before playback takes over.

## Fix: Set Mode Before Starting Timer

In `playback_record.py`:

```python
def _play(self) -> None:
    if not self._recording:
        return
    self._is_playing = True
    self._btn_play.setText("⏸")
    self._btn_play.setToolTip("Pause")
    # ── Switch the entire app into playback mode first ─────────────
    if self._mode != "playback":
        self._mode = "playback"
        self._update_mode_button()
        self.mode_changed.emit("playback")
    # ───────────────────────────────────────────────────────────────
    self._update_play_interval()
    self._play_timer.start()
```

Sequence after fix:
1. `_play()` sets `_mode = "playback"`
2. Emits `mode_changed("playback")` immediately
3. `MainWindow._set_data_mode()` stops live poll timer
4. `_update_play_interval()` configures playback timer
5. `_play_timer.start()` — no live data leak possible

The UI switches to "▶ PLAYBACK" **instantly** — user sees zero live data before playback.

## Related Fix: Ensure Only Playback Data Drives I/O Display

Even with `_data_mode == "playback"`, old live data may still be cached in the tab's display cells. `_on_playback_update()` must call a **display reset method** that zeroes cached values:

```python
def _on_playback_update(self, io_values: dict[str, Any], ...):
    if self._data_mode != "playback":
        return
    self._active_io_table._reset_cached_values()   # prevent stale-live contamination
    self._render_io_state(io_values.copy())
```

## Anti-Patterns

| Anti-Pattern | Why Bad | What To Do |
|---|---|---|
| Reactive mode switch (after timer tick) | Live data leaks during window | Proactive emit before `timer.start()` |
| Playback tab drives mode alone | Other tabs miss the signal | Central `_set_data_mode()` in MainWindow |
| No poll discard guard | Queued live poll overwrites first frame | `_on_poll_done` early return |
| Old cached values in I/O cells | Stale live data visible alongside recording | `_reset_cached_values()` before render |
