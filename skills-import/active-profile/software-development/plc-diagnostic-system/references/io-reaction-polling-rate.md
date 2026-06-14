# Polling Rate Considerations for I/O Reaction Validation

## Problem Statement

Pneumatic cylinder reed switches take **100-500ms** to settle after the solenoid changes state. If the PLC poll interval is **1 second**, the sample often captures the sensor in its **old state**, producing:
- False "swap" perception (sensor shows previous cycle's position)
- Continuous check false alarms (sensor hasn't settled within the grace window)
- Misleading timelines that look like Extend/Retract are reversed

## Root Cause

The sampling theorem applies to digital I/O just like analog signals. To reliably detect a transition, you need **2-4 samples during the settle period**.

| Sensor Type | Settle Time | Minimum Poll Rate | Recommended |
|---|---|---|---|
| Reed switch (pneumatic) | 100-500ms | 250ms (4 samples/sec) | **100-250ms** |
| Hall effect (pneumatic) | 50-200ms | 100ms (10 samples/sec) | **50-100ms** |
| Proximity (hydraulic) | 200-800ms | 250ms | **250ms** |
| Limit switch (mechanical) | 300-1000ms | 500ms | **250-500ms** |

## Micro870 Throughput Limits

The Allen-Bradley Micro870 (2080-LC70) over Ethernet/IP with pycomm3:
- Batch read of 127 tags: **~15-30ms round-trip** on local LAN
- With **only two devices** on the network (PC + PLC), 100ms is safe with no congestion risk
- Conservative minimum poll interval: **50ms** (20 Hz)
- **User-preferred default: 100ms** for pneumatic cylinder applications on lightly loaded networks

Going below 50ms risks:
- Network congestion on shared industrial switches
- pycomm3 socket buffer overflow
- PLC CIP connection saturation (Micro870 has limited CIP sessions)

## End-of-Scan Cycle Insight

**Important domain correction:** The user's PLC (Micro870) executes ladder logic scans continuously, and **I/O state changes are committed at the end of each scan cycle**. By the time pycomm3's CIP read returns values, the PLC has already allowed one full scan for internal settling. This means:
- The poll rate captures the **post-scan settled state**, not mid-scan transitional state
- Grace periods must still account for **mechanical settling time** (cylinders move ~200-800ms *after* the solenoid bit changes in the PLC scan)
- False alarms come from **mechanical settling**, not scan-cycle jitter
- Therefore, `timeout_sec` should be set to the **machine's worst-case pneumatic settle time** (2-5 seconds), while `poll_interval` is set to **capture sensor transitions** (100-250ms)

## Implementation in PySide6

```python
# diagnostics.py — Alarm Settings panel
self._poll_rate_combo = QComboBox()
self._poll_rate_combo.addItem("100 ms", 100)
self._poll_rate_combo.addItem("250 ms", 250)
self._poll_rate_combo.addItem("500 ms", 500)
self._poll_rate_combo.addItem("1000 ms", 1000)
self._poll_rate_combo.setCurrentIndex(0)  # default 100 ms when network is light

# Signal emitted on Accept
poll_rate_changed = Signal(int)  # milliseconds

# main_window.py
self._poll_timer.setInterval(ms)
```

## User-Specific Constraint

**Software-side fixes only.** The user explicitly does NOT want to edit PLC ladder logic. All solutions must work within the PC application:
- Polling rate adjustment
- UI timeout tuning
- Sensor filtering algorithms
- Grace period tuning

Never propose ladder logic changes as a fix.

## Inline Stylesheet for Accept Buttons

Theme class names (`#uiverse_green`, `#uiverse_btn`) fail to render on dynamically created `QPushButton` widgets. Always use `setStyleSheet()` with hard-coded hex values:

```python
btn.setStyleSheet(
    "QPushButton {"
    "  background-color: #22c55e;"
    "  color: #ffffff;"
    "  font-weight: 700;"
    "  font-size: 13px;"
    "  border: 2px solid #16a34a;"
    "  border-radius: 6px;"
    "}"
    "QPushButton:hover { background-color: #16a34a; }"
    "QPushButton:pressed { background-color: #15803d; }"
)
```