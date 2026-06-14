"""Simulate realistic DEG timeline recordings with alarm scenarios for playback testing.

Run this script to generate .json recordings in dist/ that can be loaded
by the Degater PLC Tool's Playback Review window.

Copy into project root and run:
    python generate_sim_recordings.py
"""
from __future__ import annotations
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ─── All known tags (206 tags from the catalog) ───
ALL_TAGS = [
    "Complete_Runner_Drop","D1_Low_Ext_Cyl_1_Ext","D1_Low_Ext_Cyl_1_Ret",
    "D1_Low_Ext_Cyl_2_Ext","D1_Low_Ext_Cyl_2_Ret","D1_Low_Grip_Cyl1_Open",
    "D1_Low_Grip_Cyl2_Open","D1_Low_Grip_Open_Sol","D1_Low_Justify_Cyl1_Ext",
    "D1_Low_Justify_Cyl2_Ext","D1_Low_Justify_Cyl3_Ext","D1_Low_Justify_Cyl_4_Ext",
    "D1_Low_Justify_Ext_Sol","D1_Low_Justify_Ret_Sol","D1_Low_Nip_Close_Sol",
    "D1_Low_Nip_Open_Sol","D1_Up_Ext_Cyl_1_Ext","D1_Up_Ext_Cyl_1_Ret",
    "D1_Up_Ext_Cyl_2_Ext","D1_Up_Ext_Cyl_2_Ret","D1_Up_Grip_Close_Sol",
    "D1_Up_Grip_Cyl1_Open","D1_Up_Grip_Cyl2_Open","D1_Up_Grip_Open_Sol",
    "D1_Up_Justify_Cyl1_Ext","D1_Up_Justify_Cyl2_Ext","D1_Up_Justify_Cyl3_Ext",
    "D1_Up_Justify_Cyl4_Ext","D1_Up_Justify_Ext_Sol","D1_Up_Justify_Ret_Sol",
    "D1_Up_Nip_Close_Sol","D1_Up_Nip_Open_Sol","D1__Low_Grip_Close_Sol",
    "D1_Lower_Ext_Sol","D1_Lower_Ret_Sol","D1_Upper_Ext_Sol","D1_Upper_Ret_Sol",
    "D2_Low_Ext_Cyl_1_Ext","D2_Low_Ext_Cyl_1_Ret","D2_Low_Ext_Cyl_2_Ext",
    "D2_Low_Ext_Cyl_2_Ret","D2_Low_Grip_Close_Sol","D2_Low_Grip_Cyl1_Open",
    "D2_Low_Grip_Cyl2_Open","D2_Low_Grip_Open_Sol","D2_Low_Justify_Cyl1_Ext",
    "D2_Low_Justify_Cyl2_Ext","D2_Low_Justify_Cyl3_Ext","D2_Low_Justify_Cyl4_Ext",
    "D2_Low_Justify_Ext_Sol","D2_Low_Justify_Ret_Sol","D2_Low_Nip_Close_Sol",
    "D2_Low_Nip_Open_Sol","D2_Up_Ext_Cyl_1_Ext","D2_Up_Ext_Cyl_1_Ret",
    "D2_Up_Ext_Cyl_2_Ext","D2_Up_Ext_Cyl_2_Ret","D2_Up_Grip_Close_Sol",
    "D2_Up_Grip_Cyl1_Open","D2_Up_Grip_Cyl2_Open","D2_Up_Grip_Open_Sol",
    "D2_Up_Justify_Cyl1_Ext","D2_Up_Justify_Cyl2_Ext","D2_Up_Justify_Cyl3_Ext",
    "D2_Up_Justify_Cyl4_Ext","D2_Up_Justify_Ext_Sol","D2_Up_Justify_Ret_Sol",
    "D2_Up_Nip_Close_Sol","D2_Up_Nip_Open_Sol","D2_Lower_Ext_Sol",
    "D2_Lower_Ret_Sol","D2_Upper_Ext_Sol","D2_Upper_Ret_Sol",
    "D3_Low_Ext_Cyl_1_Ext","D3_Low_Ext_Cyl_1_Ret","D3_Low_Ext_Cyl_2_Ext",
    "D3_Low_Ext_Cyl_2_Ret","D3_Low_Grip_Close_Sol","D3_Low_Grip_Cyl1_Open",
    "D3_Low_Grip_Cyl2_Open","D3_Low_Grip_Open_Sol","D3_Low_Justify_Cyl1_Ext",
    "D3_Low_Justify_Cyl2_Ext","D3_Low_Justify_Cyl3_Ext","D3_Low_Justify_Cyl4_Ext",
    "D3_Low_Justify_Ext_Sol","D3_Low_Justify_Ret_Sol","D3_Low_Nip_Close_Sol",
    "D3_Low_Nip_Open_Sol","D3_Up_Ext_Cyl_1_Ext","D3_Up_Ext_Cyl_1_Ret",
    "D3_Up_Ext_Cyl_2_Ext","D3_Up_Ext_Cyl_2_Ret","D3_Up_Grip_Close_Sol",
    "D3_Up_Grip_Cyl1_Open","D3_Up_Grip_Cyl2_Open","D3_Up_Grip_Open_Sol",
    "D3_Up_Justify_Cyl1_Ext","D3_Up_Justify_Cyl2_Ext","D3_Up_Justify_Cyl3_Ext",
    "D3_Up_Justify_Cyl4_Ext","D3_Up_Justify_Ext_Sol","D3_Up_Justify_Ret_Sol",
    "D3_Up_Nip_Close_Sol","D3_Up_Nip_Open_Sol","D3_Lower_Ext_Sol",
    "D3_Lower_Ret_Sol","D3_Upper_Ext_Sol","D3_Upper_Ret_Sol",
    "DEG_Home_And_Ready","DEG1_Auto","DEG1_Done","DEG1_Home","DEG1_Lead",
    "DEG1_Lead_Shot_Count","DEG1_Lead_Shots_Complete","DEG1_Repeat_Cycle",
    "DEG1_Selection_ON","DEG1_Shot_Count","DEG1_Shots_Complete","DEG2_Auto",
    "DEG2_Done","DEG2_Home","DEG2_Lead","DEG2_Lead_Shot_Count",
    "DEG2_Lead_Shots_Complete","DEG2_Repeat_Cycle","DEG2_Selection_ON",
    "DEG2_Shot_Count","DEG2_Shots_Complete","DEG3_Auto","DEG3_Done",
    "DEG3_Home","DEG3_Lead","DEG3_Lead_Shot_Count","DEG3_Lead_Shots_Complete",
    "DEG3_Repeat_Cycle","DEG3_Selection_ON","DEG3_Shot_Count","DEG3_Shots_Complete",
    "Lower_Completed_Cuts","Lower_Ready_For_Parts","Tilt_DEG_Pos_Deflector",
    "Upper_Completed_Cuts","Upper_Ready_For_Parts",
    "_IO_EM_DO_00","_IO_EM_DO_01","_IO_EM_DO_02","_IO_EM_DO_03",
    "_IO_EM_DO_04","_IO_EM_DO_05","_IO_EM_DO_06",
    "_IO_X1_DI_01","_IO_X1_DI_02","_IO_X1_DI_03","_IO_X1_DI_04",
    "_IO_X1_DI_05","_IO_X1_DI_06","_IO_X1_DI_07","_IO_X1_DI_08",
    "_IO_X1_DI_09","_IO_X1_DI_10","_IO_X1_DI_11","_IO_X1_DI_12",
    "_IO_X1_DI_13","_IO_X1_DI_14","_IO_X1_DI_15","_IO_X1_DI_16",
    "_IO_X2_DI_01","_IO_X2_DI_02","_IO_X2_DI_03","_IO_X2_DI_04",
    "_IO_X2_DI_05","_IO_X2_DI_06","_IO_X2_DI_07","_IO_X2_DI_08",
    "_IO_X2_DI_09","_IO_X2_DI_10","_IO_X2_DI_11","_IO_X2_DI_12",
    "_IO_X2_DI_13","_IO_X2_DI_14","_IO_X2_DI_15","_IO_X2_DI_16",
    "_IO_X3_DO_00","_IO_X3_DO_01","_IO_X3_DO_02","_IO_X3_DO_03",
    "_IO_X3_DO_04","_IO_X3_DO_05","_IO_X3_DO_06","_IO_X3_DO_07",
    "_IO_X5_DO_00","_IO_X5_DO_01","_IO_X5_DO_02","_IO_X5_DO_03",
    "_IO_X5_DO_08","_IO_X5_DO_09","_IO_X5_DO_10","_IO_X5_DO_11",
    "_IO_X5_DO_12","_IO_X5_DO_13"
]


class DegaterSimulator:
    """Simulates one DEG1/2/3 degating cycle with configurable faults."""

    def __init__(self, fault: str | None = None, degater: int = 1, seed: int = 0) -> None:
        self.degater = degater
        self.prefix = f"D{degater}"
        self.seed = seed
        self.fault = fault
        self.rng = random.Random(seed + degater * 100)

        self.step = 0
        self.step_start_snap = 0
        self.snaps_in_step = 0
        self._define_steps()

    def _tag(self, suffix: str) -> str:
        return f"{self.prefix}_{suffix}"

    def _define_steps(self) -> None:
        self.steps = [
            # (name, duration_snapshots, action callable)
            ("Home / Idle",            35, self._step_home),
            ("Extend Lower",           35, self._step_extend_lower),
            ("Grip Lower",             35, self._step_grip_lower),
            ("Cut / Hold",             40, self._step_cut_hold),
            ("Retract Lower",          35, self._step_retract_lower),
            ("Extend Upper",           35, self._step_extend_upper),
            ("Grip Upper",             35, self._step_grip_upper),
            ("Cut Upper / Hold",       40, self._step_cut_upper_hold),
            ("Retract Upper",          35, self._step_retract_upper),
            ("Home Complete",          35, self._step_home),
        ]

    def _snapshot_tag_values(self, snap_idx: int) -> dict[str, bool]:
        vals: dict[str, bool] = {t: False for t in ALL_TAGS}

        _, _, action = self.steps[self.step]
        action(vals)
        self.snaps_in_step += 1
        self._inject_fault(vals)
        return vals

    # ─── Normal step actions ───
    def _step_home(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Low_Ext_Cyl_1_Ret")] = True
        vals[self._tag("Low_Ext_Cyl_2_Ret")] = True
        vals[self._tag("Up_Ext_Cyl_1_Ret")] = True
        vals[self._tag("Up_Ext_Cyl_2_Ret")] = True
        vals[self._tag("Low_Grip_Cyl1_Open")] = True
        vals[self._tag("Low_Grip_Cyl2_Open")] = True
        vals[self._tag("Up_Grip_Cyl1_Open")] = True
        vals[self._tag("Up_Grip_Cyl2_Open")] = True

    def _step_extend_lower(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Lower_Ext_Sol")] = True
        if self.snaps_in_step > 5:
            vals[self._tag("Low_Ext_Cyl_1_Ext")] = True
            vals[self._tag("Low_Ext_Cyl_2_Ext")] = True
        vals[self._tag("Low_Ext_Cyl_1_Ret")] = self.snaps_in_step <= 2
        vals[self._tag("Low_Ext_Cyl_2_Ret")] = self.snaps_in_step <= 2

    def _step_grip_lower(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Lower_Ext_Sol")] = True
        vals[self._tag("Low_Ext_Cyl_1_Ext")] = True
        vals[self._tag("Low_Ext_Cyl_2_Ext")] = True
        vals[self._tag("Low_Grip_Open_Sol")] = True
        if self.snaps_in_step > 3:
            vals[self._tag("Low_Grip_Cyl1_Open")] = True
            vals[self._tag("Low_Grip_Cyl2_Open")] = True

    def _step_cut_hold(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Lower_Ext_Sol")] = True
        vals[self._tag("Low_Ext_Cyl_1_Ext")] = True
        vals[self._tag("Low_Ext_Cyl_2_Ext")] = True
        vals[self._tag("Low_Grip_Open_Sol")] = True
        vals[self._tag("Low_Grip_Cyl1_Open")] = True
        vals[self._tag("Low_Grip_Cyl2_Open")] = True
        vals[self._tag("Low_Nip_Close_Sol")] = True

    def _step_retract_lower(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Lower_Ret_Sol")] = True
        if self.snaps_in_step > 5:
            vals[self._tag("Low_Ext_Cyl_1_Ret")] = True
            vals[self._tag("Low_Ext_Cyl_2_Ret")] = True
        vals[self._tag("Low_Ext_Cyl_1_Ext")] = self.snaps_in_step <= 2
        vals[self._tag("Low_Ext_Cyl_2_Ext")] = self.snaps_in_step <= 2
        vals[self._tag("Low_Grip_Close_Sol")] = True

    def _step_extend_upper(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Upper_Ext_Sol")] = True
        if self.snaps_in_step > 5:
            vals[self._tag("Up_Ext_Cyl_1_Ext")] = True
            vals[self._tag("Up_Ext_Cyl_2_Ext")] = True
        vals[self._tag("Up_Ext_Cyl_1_Ret")] = self.snaps_in_step <= 2
        vals[self._tag("Up_Ext_Cyl_2_Ret")] = self.snaps_in_step <= 2

    def _step_grip_upper(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Upper_Ext_Sol")] = True
        vals[self._tag("Up_Ext_Cyl_1_Ext")] = True
        vals[self._tag("Up_Ext_Cyl_2_Ext")] = True
        vals[self._tag("Up_Grip_Open_Sol")] = True
        if self.snaps_in_step > 3:
            vals[self._tag("Up_Grip_Cyl1_Open")] = True
            vals[self._tag("Up_Grip_Cyl2_Open")] = True

    def _step_cut_upper_hold(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Upper_Ext_Sol")] = True
        vals[self._tag("Up_Ext_Cyl_1_Ext")] = True
        vals[self._tag("Up_Ext_Cyl_2_Ext")] = True
        vals[self._tag("Up_Grip_Open_Sol")] = True
        vals[self._tag("Up_Grip_Cyl1_Open")] = True
        vals[self._tag("Up_Grip_Cyl2_Open")] = True
        vals[self._tag("Up_Nip_Close_Sol")] = True

    def _step_retract_upper(self, vals: dict[str, bool]) -> None:
        vals[self._tag("Upper_Ret_Sol")] = True
        if self.snaps_in_step > 5:
            vals[self._tag("Up_Ext_Cyl_1_Ret")] = True
            vals[self._tag("Up_Ext_Cyl_2_Ret")] = True
        vals[self._tag("Up_Ext_Cyl_1_Ext")] = self.snaps_in_step <= 2
        vals[self._tag("Up_Ext_Cyl_2_Ext")] = self.snaps_in_step <= 2

    # ─── Fault injection ───
    def _inject_fault(self, vals: dict[str, bool]) -> None:
        if self.fault is None:
            return

        step_name, _, _ = self.steps[self.step]

        if self.fault == "stuck_sensor_lower_ext":
            if step_name == "Extend Lower" and self.snaps_in_step > 12:
                vals[self._tag("Low_Ext_Cyl_1_Ext")] = False
            else:
                vals[self._tag("Low_Ext_Cyl_1_Ext")] = self.snaps_in_step > 5

        elif self.fault == "slow_cylinder_ret":
            if step_name == "Retract Lower":
                if self.snaps_in_step > 25:
                    vals[self._tag("Low_Ext_Cyl_1_Ret")] = True
                    vals[self._tag("Low_Ext_Cyl_2_Ret")] = True
                elif self.snaps_in_step > 2:
                    vals[self._tag("Low_Ext_Cyl_1_Ret")] = False
                    vals[self._tag("Low_Ext_Cyl_2_Ret")] = False

        elif self.fault == "sensor_unplugged":
            if step_name == "Home / Idle":
                vals[self._tag("Low_Ext_Cyl_1_Ext")] = False
                vals[self._tag("Low_Ext_Cyl_1_Ret")] = False
                vals[self._tag("Low_Ext_Cyl_2_Ext")] = False
                vals[self._tag("Low_Ext_Cyl_2_Ret")] = False

        elif self.fault == "grip_failed":
            if step_name == "Grip Lower":
                vals[self._tag("Low_Grip_Cyl1_Open")] = self.snaps_in_step > 20
                vals[self._tag("Low_Grip_Cyl2_Open")] = self.snaps_in_step > 20

        elif self.fault == "opposing_solenoid_both_on":
            if step_name == "Extend Lower":
                vals[self._tag("Lower_Ret_Sol")] = True

    def make_alarm_events(self, snap_idx: int, vals: dict[str, bool]) -> list[dict]:
        """Generate alarm events for the CURRENT step (step already advanced)."""
        events: list[dict] = []
        if self.fault is None:
            return events

        step_name, _, _ = self.steps[self.step]

        if self.fault == "stuck_sensor_lower_ext":
            if step_name == "Extend Lower" and 12 <= snap_idx - self.step_start_snap < 30:
                events.append({
                    "severity": "FAULT",
                    "source": "DEG1_Lower_Extend",
                    "message": (
                        f"D1_Lower_Ext_Sol=ON but sensor D1_Low_Ext_Cyl_1_Ext "
                        f"stuck FALSE (snap {snap_idx})"
                    ),
                    "fault_key": f"DEG1_D1_Lower_Ext_Sol_stuck_{snap_idx}"
                })

        elif self.fault == "slow_cylinder_ret":
            if step_name == "Retract Lower" and 12 <= snap_idx - self.step_start_snap < 28:
                events.append({
                    "severity": "FAULT",
                    "source": "DEG1_Lower_Retract",
                    "message": (
                        f"D1_Lower_Ret_Sol=ON but retract sensors still FALSE "
                        f"after 1.2 s (snap {snap_idx})"
                    ),
                    "fault_key": f"DEG1_D1_Lower_Ret_Sol_slow_{snap_idx}"
                })

        elif self.fault == "grip_failed":
            if step_name == "Grip Lower" and 12 <= snap_idx - self.step_start_snap < 25:
                events.append({
                    "severity": "FAULT",
                    "source": "DEG1_Lower_Grip",
                    "message": (
                        f"D1_Low_Grip_Open_Sol=ON but grip sensors FALSE "
                        f"after 1.2 s (snap {snap_idx})"
                    ),
                    "fault_key": f"DEG1_D1_Grip_slow_{snap_idx}"
                })

        elif self.fault == "sensor_unplugged":
            rel = snap_idx - self.step_start_snap
            if step_name == "Home / Idle" and 10 <= rel < 30:
                events.append({
                    "severity": "ERROR",
                    "source": "DEG1_Sensor_Sanity",
                    "message": (
                        f"DEG1 Lower sensors impossible state: both Ext "
                        f"AND Ret FALSE simultaneously (snap {snap_idx})"
                    ),
                    "fault_key": f"DEG1_sensor_sanity_{snap_idx}"
                })

        elif self.fault == "opposing_solenoid_both_on":
            if step_name == "Extend Lower" and 8 <= snap_idx - self.step_start_snap < 20:
                events.append({
                    "severity": "FAULT",
                    "source": "DEG1_Lower_Cylinder",
                    "message": (
                        f"Both D1_Lower_Ext_Sol and D1_Lower_Ret_Sol ON "
                        f"simultaneously (snap {snap_idx})"
                    ),
                    "fault_key": f"DEG1_both_solenoids_{snap_idx}"
                })

        return events


# ─── Generate a full recording ───
def generate_recording(
    scenario_name: str,
    fault: str | None,
    duration_sec: int = 60,
    polling_ms: int = 100,
    seed: int = 42,
    degaters: list[int] = [1],
) -> dict[str, Any]:
    num_snaps = (duration_sec * 1000) // polling_ms
    start = datetime.now(timezone.utc)
    snapshots: list[dict] = []
    fault_snapshots: list[int] = []

    simulators = {
        d: DegaterSimulator(fault if d == 1 else None, degater=d, seed=seed + d * 7)
        for d in degaters
    }

    for i in range(num_snaps):
        merged: dict[str, bool] = {t: False for t in ALL_TAGS}
        all_events: list[dict] = []
        has_fault = False

        for deg, sim in simulators.items():
            # Advance step BEFORE generating snapshot
            if sim.snaps_in_step >= sim.steps[sim.step][1]:
                sim.step = (sim.step + 1) % len(sim.steps)
                sim.snaps_in_step = 0
                sim.step_start_snap = i

            vals = sim._snapshot_tag_values(i)
            events = sim.make_alarm_events(i, vals)
            all_events.extend(events)
            if events:
                has_fault = True
            merged.update(vals)

        snap = {
            "timestamp": (start + timedelta(milliseconds=i * polling_ms)).isoformat(),
            "values": merged,
            "fault_detected": has_fault,
            "fault_details": [e["message"] for e in all_events],
            "alarm_events": all_events,
        }
        snapshots.append(snap)
        if has_fault:
            fault_snapshots.append(i)

    end = start + timedelta(milliseconds=(num_snaps - 1) * polling_ms)

    return {
        "project_name": f"SIM_{scenario_name}",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "snapshots": snapshots,
        "fault_snapshots": fault_snapshots,
        "controller_info": {
            "vendor": "Simulated",
            "product_name": "Degater BST33/35 Simulator",
            "product_type": "Simulator",
            "revision": {"major": 26, "minor": 6},
            "serial": f"SIM-{scenario_name}-001",
        },
        "io_config": "Simulated 206-tag I/O",
        "io_tags_mapped": 206,
    }


# ─── Scenario definitions ───
SCENARIOS = {
    "01_Normal_Cycle": {"fault": None, "duration_sec": 45, "seed": 42},
    "02_Stuck_Sensor_Lower_Ext": {"fault": "stuck_sensor_lower_ext", "duration_sec": 60, "seed": 10},
    "03_Slow_Cylinder_Retract": {"fault": "slow_cylinder_ret", "duration_sec": 60, "seed": 20},
    "04_Grip_Failure": {"fault": "grip_failed", "duration_sec": 60, "seed": 30},
    "05_Sensor_Unplugged": {"fault": "sensor_unplugged", "duration_sec": 50, "seed": 40},
    "06_Opposing_Solenoids_Both_On": {"fault": "opposing_solenoid_both_on", "duration_sec": 40, "seed": 50},
    "07_Mixed_Deg1_Faulty_Deg2_Normal": {"fault": "stuck_sensor_lower_ext", "duration_sec": 60, "seed": 60, "degaters": [1, 2]},
    "08_Multiple_Rapid_Alarms": {"fault": "slow_cylinder_ret", "duration_sec": 45, "seed": 70, "degaters": [1]},
}


def main() -> None:
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)

    for name, opts in SCENARIOS.items():
        print(f"Generating {name}...")
        rec = generate_recording(
            scenario_name=name,
            fault=opts["fault"],
            duration_sec=opts["duration_sec"],
            seed=opts["seed"],
            degaters=opts.get("degaters", [1]),
        )
        path = out_dir / f"sim_{name.lower()}.json"
        with open(path, "w") as f:
            json.dump(rec, f, indent=2)
        print(
            f"  -> {path}  "
            f"({len(rec['snapshots'])} snapshots, "
            f"{len(rec['fault_snapshots'])} alarm snapshots)"
        )

    print("\nAll done. Load these files in the Playback Review window to test.")


if __name__ == "__main__":
    main()
