# Allen-Bradley PanelView 300 Micro (2711-M3A18L1)
# Program Transfer Procedure

**Date:** 2026-05-03  
**Source:** Old Unit → New Replacement Unit  
**Difficulty:** Medium  
**Time Required:** 30-60 minutes

---

## ⚠️ CRITICAL INFORMATION

The **2711-M3A18L1** is a **PanelView 300 Micro** — this is a "Micro" series, NOT a "Standard" series.

**Key Limitation:** PanelView Micro units have **limited or no upload capability** depending on firmware version. You may NOT be able to extract the program from the old failed unit.

**Your options:**
1. **If you have the original .pba source file** — Use that to download to the new unit
2. **If the old unit still powers on** — Attempt upload (may or may not work)
3. **If no source file exists and unit is dead** — Program must be recreated from scratch

---

## REQUIRED SOFTWARE & HARDWARE

### Software
| Item | Version | Purpose |
|------|---------|---------|
| **PanelBuilder32** | v3.83.01 (Build 7) or v3.6.1+ | HMI Development Software |
| **RSLinx Classic** | v3.51.01 or EARLIER | Communication Driver |

⚠️ **WARNING:** RSLinx v4.0.0+ dropped PanelView Micro/Standard support. Must use v3.51.01 or earlier.

### Hardware
| Item | Part Number | Purpose |
|------|-------------|---------|
| **Serial Cable** | 1747-CP3 or equivalent | RS-232 connection to PC |
| **Null Modem Adapter** | May be required | Depends on cable type |
| **24V DC Power Supply** | For testing | Both units need power |

---

## OPTION 1: UPLOAD FROM OLD UNIT (If Functional)

### Step 1: Check Old Unit Status
- Does the old unit power on?
- Does the display show anything?
- Can you access the system menu?

If **NO** — Skip to Option 2 or 3

### Step 2: Connect Old Unit
1. Power off old PanelView
2. Connect RS-232 serial cable to:
   - PanelView: Serial port (typically 9-pin D-sub)
   - PC: Serial port or USB-to-serial adapter
3. Power on PanelView

### Step 3: Configure RSLinx
1. Open **RSLinx Classic v3.51.01**
2. Go to **Communications → Configure Drivers**
3. Add driver: **RS-232 DF1**
   - Port: Your COM port (COM1, COM2, etc.)
   - Baud Rate: **19200** (default for PanelView Micro)
   - Data Bits: 8
   - Parity: None
   - Stop Bits: 1
4. Click **Auto-Configure** (should detect PanelView)
5. PanelView should appear in RSWho tree

### Step 4: Upload Program
1. Open **PanelBuilder32**
2. Select **Online → Upload**
3. Browse to your PanelView in the dialog
4. Click **Upload**
5. Save the file as: `Backup_OldUnit_YYYYMMDD.pba`

### Step 5: Verify Upload
1. Open the uploaded `.pba` file in PanelBuilder32
2. Check if screens/tags are visible
3. If editable — Success!
4. If error "hardware mismatch" — The file cannot be edited

---

## OPTION 2: DOWNLOAD USING EXISTING SOURCE FILE

### If You Have the Original .pba File

### Step 1: Verify File
1. Locate original `.pba` file (should be on old laptop, network drive, etc.)
2. Open in PanelBuilder32
3. Check application settings match your PLC program

### Step 2: Prepare New Unit
1. Power off new PanelView 300 Micro
2. Connect serial cable
3. Configure RSLinx RS-232 DF1 driver (same as above)
4. Verify communication in RSWho

### Step 3: Download Program
1. In PanelBuilder32, open your `.pba` file
2. Select **Online → Download**
3. Or use: **File → Send Application to Terminal**
4. Select target PanelView
5. Click **Download**

### Step 4: Verify Operation
1. PanelView will reboot automatically
2. Check display shows your application
3. Verify communication with PLC (green COMM light)
4. Test buttons/screens

---

## OPTION 3: NO SOURCE FILE & UPLOAD FAILED

### Recreate Program From Scratch

### Step 1: Document What You Know
- Take photos of old unit screens (if display works)
- List all buttons and their functions
- Document tag addresses from PLC program
- Note screen navigation flow

### Step 2: Create New Application
1. Open PanelBuilder32
2. **File → New**
3. Select **PanelView 300 Micro** as target
4. Select communication: **DH-485** or **RS-232 DF1**

### Step 3: Recreate Screens
1. Build each screen based on photos/notes
2. Add tags matching your PLC addresses
3. Set up screen navigation
4. Configure alarms (if used)

### Step 4: Test & Download
1. Save as new `.pba` file
2. Download to new unit
3. Test with running PLC

---

## PANELVIEW 300 MICRO SPECIFIC NOTES

### Communication Settings (Default)
| Setting | Value |
|---------|-------|
| Protocol | DH-485 or DF1 |
| Baud Rate | 19200 |
| Node Address | 1 (or match PLC) |
| Parity | None |
| Stop Bits | 1 |

### Firmware Check
To check firmware on old unit:
1. Press **System** button (or access system menu)
2. Navigate to **About** or **System Info**
3. Look for firmware version

**Firmware v2.4+** — Upload may work  
**Firmware < v2.4** — Upload likely to fail

### Common Issues

**"Cannot Communicate" Error**
- Check cable wiring (null modem may be needed)
- Verify RSLinx driver version (must be v3.51.01 or earlier)
- Check baud rate matches
- Ensure PanelView is powered and booted

**"Invalid Hardware" Error**
- Uploaded file is from different PanelView model
- Cannot be edited — must use Option 2 or 3

**"Program Too Large" Error**
- PanelView Micro has limited memory
- Reduce number of screens/tags
- Optimize graphics

---

## QUICK REFERENCE: CABLE WIRING

### 9-Pin D-Sub to 9-Pin D-Sub (Null Modem)

| PC (DB9) | | PanelView (DB9) |
|----------|---|-----------------|
| Pin 2 (RX) | ← | Pin 3 (TX) |
| Pin 3 (TX) | → | Pin 2 (RX) |
| Pin 5 (GND) | ↔ | Pin 5 (GND) |
| Pin 7 (RTS) | → | Pin 8 (CTS) |
| Pin 8 (CTS) | ← | Pin 7 (RTS) |

Use Allen-Bradley 1747-CP3 cable (correctly wired)

---

## BACKUP PROCEDURE (For Future)

Always maintain current backups:

1. **Regular Upload:** Monthly upload from running unit
2. **Source Control:** Keep `.pba` files in version control
3. **Documentation:** Print screen shots of each display
4. **Tag List:** Export and archive tag database

---

## TROUBLESHOOTING

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| Cannot communicate | Wrong RSLinx version | Use v3.51.01 or earlier |
| Upload fails | PanelView Micro limitation | Check firmware; may not support upload |
| File won't open | Corrupted or incompatible | Try older version of PanelBuilder32 |
| Download fails | Wrong panel type selected | Verify 2711-M3A18L1 selected in project |
| Screen blank after download | Wrong display settings | Check resolution/color settings |

---

## WHERE TO GET PANELBUILDER32

- Allen-Bradley Distributors (Rockwell Automation)
- Current price: ~$650 USD
- Part number: **2711-ND3**

**Alternative:** Some industrial electronics resellers may have used copies.

---

## RELATED DOCUMENTATION

- **PanelView 300 Micro User Manual:** 2711-UM001
- **PanelBuilder32 Getting Results Guide:** 2711-GR003
- **PanelBuilder32 Quick Start:** 2711-QS003

---

*Prepared for Thad's side job - PanelView 300 Micro replacement*  
*🖖 Spock*
