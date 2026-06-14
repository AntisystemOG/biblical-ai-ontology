# Post-Migration Cleanup Checklist

Run these steps immediately after `hermes claw migrate` finishes.

## 1. Remove deprecated `MESSAGING_CWD` from `.env`

OpenClaw stored `MESSAGING_CWD` in `.env`. Hermes deprecated this in favor of `config.yaml` (`terminal.cwd`). The gateway warns on every start if the old key remains:

```bash
# Check if it exists
grep 'MESSAGING_CWD' ~/.hermes/.env

# Move to config.yaml
hermes config set terminal.cwd /mnt/c/Users/thadd/.openclaw/workspace

# Remove from .env
sed -i '/^MESSAGING_CWD=/d' ~/.hermes/.env
```

## 2. Verify which secrets actually migrated

The migration summary message can be misleading. It may say *"API keys were NOT migrated"* even when some tokens (e.g. `OLLAMA_API_KEY`, `TELEGRAM_BOT_TOKEN`) did transfer.

```bash
# Check what's actually in .env now
cat ~/.hermes/.env | grep -E 'API_KEY|TOKEN'
```

If `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, or other provider keys are missing, they were likely stored as Windows environment variables rather than in OpenClaw's config files. Add them manually:

```bash
hermes config env-path   # shows ~/.hermes/.env
# Edit and add missing keys
```

## 3. Restart the gateway

New `.env` values and config changes only take effect after restart:

```bash
hermes gateway restart
```

## 4. Verify Telegram pairing

If the Telegram bot token migrated, confirm pairing:

```bash
hermes pairing list
hermes pairing approve telegram <chat_id>   # if user needs re-auth
```

## 5. Check for other deprecated warnings

Watch the gateway logs on first restart:

```bash
grep -i "deprecated\|warning" ~/.hermes/logs/gateway.log | tail -5
```

Address any remaining deprecated settings the same way: move to `config.yaml`, remove from `.env`, restart gateway.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `MESSAGING_CWD deprecated` in logs | Old `.env` key still present | `sed -i '/^MESSAGING_CWD=/d' ~/.hermes/.env` |
| API keys missing after migration | Stored as Windows env vars, not in OpenClaw config | Add manually to `~/.hermes/.env` |
| Telegram bot not responding | Token migrated but gateway needs restart | `hermes gateway restart` |
| Gateway restart still warns | Config set but `.env` not cleaned | Confirm `sed` removed the line, then restart |
