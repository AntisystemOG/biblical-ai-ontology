"""
Minimal dual-solenoid guard implementation.
Drop this into IOAlarmWatcher._start_check() to prevent false alarms when a
solenoid turns OFF before the opposing solenoid has turned ON.
"""

# --- In __init__ or class-level — map opposing function pairs ---
# For a degater, "Lower Extend" ↔ "Lower Retract", "Upper Extend" ↔ "Upper Retract"

class _DualSolenoidGuardMixin:
    """Mixin providing the opposing-solenoid guard for IOAlarmWatcher."""

    def _opposing_solenoid(self, pair: dict) -> dict | None:
        """Return the opposite pair entry for dual-solenoid cylinders.

        Example: "Lower Extend" → "Lower Retract" and vice versa.
        Returns None if not a dual-solenoid entry.
        """
        deg = pair.get("degater", 0)
        func = pair.get("function", "")

        if "Extend" not in func and "Retract" not in func:
            return None  # Not dual-solenoid (grip, nip, justify, etc.)

        opp_func = (
            func.replace("Extend", "Retract")
            if "Extend" in func
            else func.replace("Retract", "Extend")
        )

        for p in self._pairs:
            if p.get("degater") == deg and p.get("function") == opp_func:
                return p
        return None

    def _start_check(self, pair, out_val, now, io_values=None):
        """When output changes, queue the appropriate input check.

        Guard: when a dual-solenoid output turns OFF, only verify off_inputs
        if the opposing solenoid is already ON.
        """
        phys_out = pair["output_physical"]
        expected = pair.get("off_inputs_physical" if not out_val else "on_inputs_physical", [])

        if not expected:
            return  # nothing to verify for this transition

        # Dual-solenoid guard for OFF transitions
        if not out_val and io_values is not None:
            opp = self._opposing_solenoid(pair)
            if opp:
                opp_val = self._resolve(
                    io_values,
                    opp["output_physical"],
                    opp.get("output_tag", "")
                )
                if opp_val is None or not opp_val:
                    # Opposing solenoid is OFF — cylinder at rest, not moving.
                    # Skip off_inputs verification entirely.
                    return

        # ... continue creating _PendingCheck with expected inputs, timeout, etc.

    # --- In _continuous_check ---
    # Only validate on_inputs (solenoid ON).
    # off_inputs describe the DESTINATION after a transition.
    # The transition check already proved the cylinder arrived.
    # Checking off_inputs continuously would false-alarm while
    # the opposing solenoid is actively commanding motion.
