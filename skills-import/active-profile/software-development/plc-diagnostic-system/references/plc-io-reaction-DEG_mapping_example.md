# DEG1/2/3 I/O Mapping Reference — BST33 / BST35

Complete input/output mapping for the Degater PLC Tool I/O Alarm Watcher.

## Dual-Solenoid Cylinders (Extend ↔ Retract pairs)

Every Extend entry has a matching Retract entry. Only one solenoid is ON at a
time. When the active solenoid turns OFF, the opposing-solenoid guard checks if
the paired solenoid is ON before verifying destination sensors.

### DEG1

| Function | Output (Solenoid) | on_inputs (solenoid ON) | off_inputs (solenoid OFF) |
|---|---|---|---|
| **Lower Extend** | `_IO_X3_DO_01` (DEG1_Lower_Ext_Sol) | D1_Low_Ext_Cyl_1_Ext, D1_Low_Ext_Cyl_2_Ext | D1_Low_Ext_Cyl_1_Ret, D1_Low_Ext_Cyl_2_Ret |
| **Lower Retract** | `_IO_X3_DO_00` (DEG1_Lower_Ret_Sol) | D1_Low_Ext_Cyl_1_Ret, D1_Low_Ext_Cyl_2_Ret | D1_Low_Ext_Cyl_1_Ext, D1_Low_Ext_Cyl_2_Ext |
| **Upper Extend** | `_IO_X3_DO_03` (DEG1_Upper_Ext_Sol) | D1_Up_Ext_Cyl_1_Ext, D1_Up_Ext_Cyl_2_Ext | D1_Up_Ext_Cyl_1_Ret, D1_Up_Ext_Cyl_2_Ret |
| **Upper Retract** | `_IO_X3_DO_02` (DEG1_Upper_Ret_Sol) | D1_Up_Ext_Cyl_1_Ret, D1_Up_Ext_Cyl_2_Ret | D1_Up_Ext_Cyl_1_Ext, D1_Up_Ext_Cyl_2_Ext |

### DEG2

| Function | Output (Solenoid) | on_inputs (solenoid ON) | off_inputs (solenoid OFF) |
|---|---|---|---|
| **Lower Extend** | `_IO_X5_DO_01` (DEG2_Lower_Ext_Sol) | D2_Low_Ext_Cyl_1_Ext, D2_Low_Ext_Cyl_2_Ext | D2_Low_Ext_Cyl_1_Ret, D2_Low_Ext_Cyl_2_Ret |
| **Lower Retract** | `_IO_X5_DO_00` (DEG2_Lower_Ret_Sol) | D2_Low_Ext_Cyl_1_Ret, D2_Low_Ext_Cyl_2_Ret | D2_Low_Ext_Cyl_1_Ext, D2_Low_Ext_Cyl_2_Ext |
| **Upper Extend** | `_IO_X5_DO_03` (DEG2_Upper_Ext_Sol) | D2_Up_Ext_Cyl_1_Ext, D2_Up_Ext_Cyl_2_Ext | D2_Up_Ext_Cyl_1_Ret, D2_Up_Ext_Cyl_2_Ret |
| **Upper Retract** | `_IO_X5_DO_02` (DEG2_Upper_Ret_Sol) | D2_Up_Ext_Cyl_1_Ret, D2_Up_Ext_Cyl_2_Ret | D2_Up_Ext_Cyl_1_Ext, D2_Up_Ext_Cyl_2_Ext |

### DEG3

| Function | Output (Solenoid) | on_inputs (solenoid ON) | off_inputs (solenoid OFF) |
|---|---|---|---|
| **Lower Extend** | `_IO_X5_DO_09` (DEG3_Lower_Ext_Sol) | D3_Low_Ext_Cyl_1_Ext, D3_Low_Ext_Cyl_2_Ext | D3_Low_Ext_Cyl_1_Ret, D3_Low_Ext_Cyl_2_Ret |
| **Lower Retract** | `_IO_X5_DO_08` (DEG3_Lower_Ret_Sol) | D3_Low_Ext_Cyl_1_Ret, D3_Low_Ext_Cyl_2_Ret | D3_Low_Ext_Cyl_1_Ext, D3_Low_Ext_Cyl_2_Ext |
| **Upper Extend** | `_IO_X5_DO_11` (DEG3_Upper_Ext_Sol) | D3_Up_Ext_Cyl_1_Ext, D3_Up_Ext_Cyl_2_Ext | D3_Up_Ext_Cyl_1_Ret, D3_Up_Ext_Cyl_2_Ret |
| **Upper Retract** | `_IO_X5_DO_10` (DEG3_Upper_Ret_Sol) | D3_Up_Ext_Cyl_1_Ret, D3_Up_Ext_Cyl_2_Ret | D3_Up_Ext_Cyl_1_Ext, D3_Up_Ext_Cyl_2_Ext |

## Single-Solenoid Functions (Justify, Grip, Nip, Status)

These have only `on_inputs` OR `off_inputs`, not both. They do not need the
opposing-solenoid guard because there is no paired function.

### DEG1 Justify

| Function | Output | on_inputs | off_inputs |
|---|---|---|---|
| Low Justify Extend | D1_Low_Justify_Ext_Sol | D1_Low_Justify_Cyl1_Ext, Cyl2_Ext, Cyl3_Ext, Cyl_4_Ext | — |
| Low Justify Retract | D1_Low_Justify_Ret_Sol | — | Same 4 extend sensors |
| Up Justify Extend | D1_Up_Justify_Ext_Sol | D1_Up_Justify_Cyl1_Ext, Cyl2_Ext, Cyl3_Ext, Cyl4_Ext | — |
| Up Justify Retract | D1_Up_Justify_Ret_Sol | — | Same 4 extend sensors |

### DEG2/DEG3 Justify — same pattern with D2_/D3_ prefixes

### DEG1 Grip

| Function | Output | on_inputs | off_inputs |
|---|---|---|---|
| Low Grip Open | D1_Low_Grip_Open_Sol | D1_Low_Grip_Cyl1_Open, Cyl2_Open | — |
| Low Grip Close | D1__Low_Grip_Close_Sol | — | Same 2 open sensors |
| Up Grip Open | D1_Up_Grip_Open_Sol | D1_Up_Grip_Cyl1_Open, Cyl2_Open | — |
| Up Grip Close | D1_Up_Grip_Close_Sol | — | Same 2 open sensors |

### DEG2/DEG3 Grip — same pattern with D2_/D3_ prefixes

### Nip (no sensors mapped)

All nip solenoids have empty `on_inputs` and `off_inputs`. They produce no I/O
reaction alarms.

## System Status Bits (no outputs to check)

| Function | Output | on_inputs | off_inputs |
|---|---|---|---|
| Upper Ready For Parts | Upper_Ready_For_Parts | — | — |
| Lower Ready For Parts | Lower_Ready_For_Parts | — | — |
| Upper Completed Cuts | Upper_Completed_Cuts | — | — |
| Lower Completed Cuts | Lower_Completed_Cuts | — | — |
| Tilt DEG Pos Deflector | Tilt_DEG_Pos_Deflector | — | — |
| Complete Runner Drop | Complete_Runner_Drop | — | — |
| DEG Home And Ready | DEG_Home_And_Ready | — | — |
