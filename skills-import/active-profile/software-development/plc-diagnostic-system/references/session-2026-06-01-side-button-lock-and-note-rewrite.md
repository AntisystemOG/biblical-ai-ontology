# Session 2026-06-01: Side Button Lock + Note Rewording (Final)

## Scope

Three user requests completed in this session:
1. **Disable side output-control buttons completely in Auto mode** — no picture popup, no button state change on click, but buttons still show real PLC color state
2. **Buttons must follow PLC state at all times** — green/red colors update even in Auto mode so operators can see what's happening
3. **Update on-screen note/banner text** to reference the hardware manual switch

---

## What Changed

### 1. `io_status.py` — Side button behavior finalized (setEnabled approach + PLC sync)

**Goal:** When `DEG MAN-AUTO` = TRUE (Auto mode), the ON / OFF / Release buttons must be **truly disabled** (`setEnabled(False)`) AND still display the actual PLC output state via color.

**Final implementation:**
- `_update_button_states(self, enabled)` — called on every poll cycle
  - `self._on_btn.setEnabled(enabled)`
  - `self._off_btn.setEnabled(enabled)`
  - `self._release_btn.setEnabled(enabled and self._forced)`
- `update_from_plc()` — **NO early return** for `not self._manual_enabled`
  - Syncs button `setChecked()` state **regardless** of Auto/Manual mode (unless `self._forced`)
  - This is the critical fix: operators see real PLC state even when they can't click
- Click handlers (`_on_on_clicked`, `_on_off_clicked`, `_on_release_clicked`):
  - When `not self._manual_enabled`: show `ManualModeDialog` and `return` — no state change, no force action
- **`:checked:disabled` stylesheet rules added** so disabled buttons retain their ON/OFF color:
  ```css
  ManualControlButton:checked:disabled#ON  {
      background-color: #10b981; color: white; border-color: #059669;
  }
  ManualControlButton:checked:disabled#OFF {
      background-color: #ef4444; color: white; border-color: #dc2626;
  }
  ```

**Why `setEnabled(False)` + unconditional `update_from_plc()`?**
- `setEnabled(False)` prevents any accidental click/keyboard interaction — cleaner than intercept-and-revert
- Unconditional `update_from_plc()` ensures buttons show real PLC state in real time, even in Auto mode
- The `:checked:disabled` stylesheet rules make the visual state visible despite being disabled

**Tooltip text (final):**
- Disabled buttons: `"These buttons will not work unless manual switch is on."`

### 2. `io_status.py` — Note and banner rewording (final)

**Before:**
- `Output note`: `⚠  Output controls require Manual mode — hover over buttons to see status`
- `Auto banner`: `🟡 AUTO — Hover over buttons to see details`

**After:**
- `Output note`: `⚠  These buttons will not work unless manual switch is on.`
- `Auto banner`: `🟡 AUTO — Manual controls locked while in Auto mode`

---

## Critical Bug: `patch` tool silently failed

All `patch` calls on `io_status.py` silently failed because the file had been previously read with `offset`/`limit` pagination. The `patch` tool reported no error, but the file on disk remained at the original 66,496 bytes with original content.

**Verification:** `stat` showed unchanged modification time and file size.

**Recovery:** Direct file modification via `terminal` + Python/sed script successfully wrote changes to disk.

**Lesson:** When a file was previously read with pagination, ALWAYS re-read the full file (no offset/limit) before patching, and verify file size/timestamp after patching.

### Build outcome

```
Build complete: dist/Degater PLCTool BST33 and 35.exe
```

---

## Verification Checklist for Button-State Changes

- [ ] `_update_button_states()` uses `setEnabled(enabled)` not `setEnabled(True)`
- [ ] `update_from_plc()` does NOT return early when `not self._manual_enabled`
- [ ] `:checked:disabled` stylesheet rules exist for ON and OFF buttons
- [ ] Release button stays enabled in Auto when `self._forced == True`
- [ ] Buttons show tooltip `"These buttons will not work unless manual switch is on."` when disabled
- [ ] Auto-mode banner: `"🟡 AUTO — Manual controls locked while in Auto mode"`
- [ ] Run `python3 -m py_compile src/plc_tools/gui/tabs/io_status.py` after edits
- [ ] Verify file size/timestamp changed after `patch` — if unchanged, use direct file edit
