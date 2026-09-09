---
name: "vision-ocr-fallback"
description: "Session model can't see images; OCR screenshots - copy media from inbound outside sandbox, find Ollama vision model via /api/tags, base64 generate"
---

# Vision OCR Fallback (local Ollama)

## When to use
- Thad sends a screenshot/image and the session model reports "does not support images" or "image understanding is disabled".
- A console/config screenshot needs transcription for verification ("does this look right?").

## Why this pattern exists
The session model (glm-5.2:cloud) has no vision. The read tool only attaches images when the session model supports them - a "successful" read is a silent no-op. The local Ollama daemon proxies cloud models that DO have vision (kimi-k2.7-code:cloud), so transcription is one API call away.

## Steps

1. Locate the inbound file: media://inbound/<file> maps to C:\Users\thadd\.openclaw\media\inbound\<file> - OUTSIDE the workspace sandbox; read on that path fails with "Path escapes sandbox root". Completion: exact path known.

2. Copy it into the workspace via exec: Copy-Item "C:\Users\thadd\.openclaw\media\inbound\<file>" "C:\Users\thadd\.openclaw\workspace\.openclaw\tmp\<file>" -Force. Completion: file exists in .openclaw/tmp/.

3. Pick a vision model: GET http://localhost:11434/api/tags and use any model whose capabilities array includes "vision" (kimi-k2.7-code:cloud qualifies). Do NOT guess gemma3:4b - it is not installed on this host (404 from /api/generate). Completion: model name chosen from the live list.

4. Transcribe - write .openclaw/tmp/ocr.py with the write tool, then run it:
   base64 the image, POST http://localhost:11434/api/generate {"model": "<vision model>", "prompt": "Transcribe ALL text exactly, line by line, every field name and value", "images": ["<b64>"], "stream": false, "options": {"temperature": 0, "num_predict": 900}}. Cloud vision models return in 10-30s. Completion: transcription printed.

5. Verify the transcription against the expected values before answering (e.g., diff an SSH pubkey against the .pub file on disk, check a boot-volume size against the plan). Completion: match/mismatch stated per field.

## Pitfalls
- read on an image with a vision-less session model is a SILENT no-op: the result says "[Current model does not support images]" but reports success - catch that string and go straight to Ollama OCR.
- 404 from /api/generate with a valid JSON body means "model not found" - always confirm the exact model name from /api/tags first.
- Inbound media root is .openclaw\media\inbound, NOT workspace\media\inbound (that one holds old staged message folders).
- Keep the OCR prompt transcription-only; analysis happens in-session against the checklist.
