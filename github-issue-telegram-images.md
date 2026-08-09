## Bug: Telegram inbound images download but are not passed to the model as vision input

### Summary
When sending an image to the OpenClaw bot via Telegram direct message, the image file is successfully downloaded to `~/.openclaw/media/inbound/`, but the agent receives only a `<media:image>` placeholder and cannot analyze the actual image. The same workflow works correctly through the webchat / Control UI.

This appears to be the currently active form of several related Telegram media-handling regressions.

### Environment
- OpenClaw version: 2026.6.6 (8c802aa)
- OS: Windows 10.0.19045 (x64)
- Node: v24.15.0
- Channel: Telegram (direct message, @SpockOGbot)
- Primary model: ollama/kimi-k2.7-code:cloud
- Config: `tools.media.image.enabled` was previously unset/null; now explicitly `false`

### Reproduction
1. Configure Telegram channel with a bot token and `enabled: true`.
2. Send a JPEG/PNG image to the bot via Telegram DM.
3. Observe the agent-visible message contains only `<media:image>` placeholder text.
4. Check `~/.openclaw/media/inbound/` — a real image file exists matching the message timestamp.
5. Ask the agent to describe the image — it responds as if no image was provided.

### Observed logs
```
2026-06-16T16:24:57.686-05:00 info gateway/channels/telegram/inbound
Inbound message telegram:6358625036 -> @SpockOGbot (direct, image/jpeg, 17 chars)
```
The "17 chars" body is the placeholder text, not the image content.

### Related upstream issues
This looks like a continuation / current form of:
- #79162 — Telegram inbound images only appear as `<media:image>` placeholder
- #62292 — Telegram inbound images use describer-only path; never attached as native vision blocks
- #69808 — Telegram image attachments stored but not passed to LLM as vision input
- #53949 — Telegram images silently not downloaded (not my symptom — file exists)
- #44833 — Telegram group photo-only messages do not trigger image understanding

### Expected behavior
Telegram inbound images should be delivered to the agent/model as native vision content blocks, or at minimum as a readable local media attachment that the model can access, consistent with webchat/Control UI behavior.

### Actual behavior
Image is saved to disk but only placeholder text reaches the model/agent transcript.
