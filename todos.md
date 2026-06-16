# Spock To-Do List

## Active Issues

### [2026-06-15] Telegram image mismatch bug
- **Problem:** A keypad photo sent at 19:05 rendered as an orange tabby cat image from an earlier 03:10 message.
- **Evidence:**
  - Both messages referenced the same Telegram `file_id`: `AgACAgEAAxkBAAIMg2owkmo3l2UNRmhgfyQhfxakMmEhAAKWDGsbcESIRY-CHzC07xIPAQADAgADeQADPAQ`
  - Downloaded file size: 141,048 bytes
  - Local path: `C:\Users\thadd\.openclaw\media\inbound\f926c867-6c91-429a-a6a0-4d414d76431e.jpg`
- **Possible causes:**
  1. OpenClaw media cache keyed on `file_id` and not invalidating when Telegram reuses or rotates IDs.
  2. Inbound media downloader writing new downloads to a stale cached path.
  3. Session/attachment mapping linking the wrong stored file to the incoming message.
- **Status:** Confirmed bug (not a security fix). Pending gateway restart to flush cache; if recurrence persists, file OpenClaw bug report.
