# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Permissions

- **Install tools:** Free to download/install anything needed (npm, pip, choco, etc.)
- **Run commands:** Free to execute local PowerShell/bash commands
- **Use free tools:** Always prefer local reading, commands, and free tools before APIs
- **Budget conscious:** Minimize token use — think locally first

## Installed Tools

### FFmpeg
- Location: `C:\Users\thada\ffmpeg\bin`
- Used for: Audio transcription with Whisper
- Status: Working

### Python 3.14
- Location: `C:\Users\thadd\AppData\Local\Programs\Python\Python314\python.exe`
  - Packages: torch, whisper, numpy, pandas, pyannote.audio, speechbrain, torchaudio
  - Status: Working
  - Note: Previous path `C:\Python314\python.exe` is stale; use the AppData path above.

### Ollama (✅ Running)
- Location: `C:\Users\thada\AppData\Local\Programs\Ollama`
- Status: Live on port 11434
- Models: Mistral (7B), Deepseek-r1 (8B), Gemma3 (4B)
- Benefit: Zero-token cost for brainstorming, analysis, drafting
- Usage: Local reasoning before expensive API calls

### Voice Biometric Authentication (✅ Installed)
- Package: speechbrain (ECAPA-TDNN model)
- Package: pyannote.audio
- Used for: Speaker verification (authenticate Thad's voice)
- Status: Models loading on first use
- Security: Verifies 95%+ voice similarity before sensitive actions
- Location: voice_biometric_auth.py in workspace

## AI Tools and Skills Library (Updated 2026-08-07)

- **Location:** `C:\AI Projects\AI Tools and Skills`
- **Purpose:** Consolidated reference library of reusable skills, tools, plugins, and MCP patterns from OpenClaw, Claude, Codex, Hermes, Agents, and Hermes-Web-UI.
- **Rule:** Check here first before building anything new; reuse existing capabilities whenever possible.
- **Key files:** `README.md` (full catalog), `manifest.json` (skill index), `AGENTS.md` (maintenance rules).
- Notable custom skills/tools:
  - `industrial-app-build-protocol` — no-phantom PyInstaller/compile workflow.
  - `ab-logix-l5x-analysis` / `pycomm3-pyside6-plc-monitor` — Rockwell PLC tooling.
  - `codex-vision` — image review via Codex.
  - `master-config-restore` / `snapshot` — Windows + AI-tools snapshot/restore.
  - `smart-home-workflow` / `smart-home-ui` — Smart Home project maintenance.
  - `Codex/tools/image-inspector` — local image metadata/ASCII preview for Codex.
  - `Codex/tools/configure-codex-kimi` — point Codex at Moonshot Kimi 2.7.
  - `Codex/tools/ollama-image-describer` — local Ollama vision image describer.

## Project Folders (Updated 2026-08-07)

All AI projects are now under `C:\AI Projects`. Active ones to remember:
- `MagneMotionMonitor` — PySide6 desktop monitor for Rockwell/MagneMotion LITE.
- `Degater PLC Tool BST33 and 35` — PySide6 desktop app for Micro870 PLC diagnostics.
- `Smart Home` — Commercial smart-home platform (Store + UI + Gateway).
- `Scheduled Jobs` — utility/project folder (inspect as needed).
- `Wittman Boot Disk` — utility/project folder (inspect as needed).

## Local Systems Built

### Bible Cache System
- File: `local_bible_cache.py`
- Purpose: Store passages, analysis, notes locally
- Saves: Re-reading same passages, token costs on Bible study
- Usage: Called during Bible reading workflow

### Bible Study Plan
- File: `bible_study.md`
- Current focus: Genesis → Gospels (Matthew, John) → Romans
- Local work: 80% (reading, analysis, caching)
- Token use: 20% (only for guidance/synthesis)

## Environment Variables

- `MOLTBOOK_API_KEY` - To be set up later (currently unused)
- `OPENCLAW_GATEWAY_PORT` - 18789 (local)

## Contact Details (To Setup)
- Sarah's email: sarahthompson773@gmail.com
- System for sharing Thad's contact details with Sarah: TBD

---

### Whale Watch
- Agent: `agents/whale-watch.md`
- Schedule: Quarterly on 13F deadline dates at 6:00 AM CDT
- Latest CSV path: `C:\Users\thadd\Desktop\Portfolio Positions\`
- Output: `C:\Users\thadd\.openclaw\workspace\Spocks Reports\whale_watch\YYYY-MM-DD_whale_watch.pdf`
- Managers tracked: Steven Cohen (Point72), Daniel Sundheim (D1 Capital), David Tepper (Appaloosa), Philippe Laffont (Coatue), Alexander Aschenbrenner (SIT)

Add whatever helps you do your job. This is your cheat sheet.
