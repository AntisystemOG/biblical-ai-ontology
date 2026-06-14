# Home PC Gateway Setup Commands

## 1. Pull Latest from GitHub
```powershell
cd "C:\Users\thada\OneDrive\Desktop\Spocks Reports\workspace"
git pull origin main
```

## 2. Fix Telegram Config
```powershell
openclaw config set channels.telegram.botToken 8616325150:AAE97uvrdOL1hOVDcPh6WJKsFmjnqWjlr0k
openclaw config set channels.telegram.enabled true
openclaw config set channels.telegram.dmPolicy pairing
```

## 3. Verify Memory Files Synced
```powershell
# Check memory files exist
dir memory\2026-04-*.md
dir memory\2026-04-08.md
dir memory\2026-04-07-moltbook-register-fail.md
```

## 4. Verify Skills Synced
```powershell
# Check new skills installed
dir skills\yahoo-finance
dir skills\alpha-vantage-api
dir skills\code-runner
dir skills\code-review-fix
```

## 5. Start Gateway
```powershell
openclaw gateway start
```

## 6. Verify Everything Working
```powershell
openclaw gateway status
openclaw plugins list
```

---

## Quick One-Liner (Copy/Paste This)
```powershell
cd "C:\Users\thada\OneDrive\Desktop\Spocks Reports\workspace"; git pull origin main; openclaw config set channels.telegram.botToken 8616325150:AAE97uvrdOL1hOVDcPh6WJKsFmjnqWjlr0k; openclaw config set channels.telegram.enabled true; openclaw gateway start
```
