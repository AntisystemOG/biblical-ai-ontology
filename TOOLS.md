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
- Location: `C:\Python314\python.exe`
- Packages: torch, whisper, numpy, pandas, pyannote.audio, speechbrain, torchaudio
- Status: Working

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

Add whatever helps you do your job. This is your cheat sheet.
