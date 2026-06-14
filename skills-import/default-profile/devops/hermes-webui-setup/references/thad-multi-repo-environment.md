# Thad's Multi-Repo WebUI Environment

## Default / Authoritative Repository

**User's explicit rule (May 21, 2026):** When Thad says "web ui" or "webui", he is **always** referring to the EKKOLearnAI Hermes WebUI repo.

| Repo | Path (WSL) | Path (Windows) | Git Remote | Stack | Status |
|------|-----------|----------------|------------|-------|--------|
| **EKKOLearnAI** (authoritative) | `/mnt/c/Users/thadd/hermes-web-ui` | `C:\Users\thadd\hermes-web-ui` | `EKKOLearnAI/hermes-web-ui` | Node.js/Vue | Active — this is "the webui" |
| `hermes-webui-new` (stale/colliding) | `~/hermes-webui-new` | N/A | — | Python | May harbor a stale `server.py` process on port 8648 — kill before starting EKKOLearnAI |
| `hermes-web-ui-ekko` | `~/hermes-web-ui-ekko` | N/A | `AntisystemOG/hermes-web-ui` | Node.js/Vue | Old fork clone with **pre-built Spock customizations** in `dist/`. Used as a source of custom assets, not as the runtime server. |

**Never** pivot to other repos even if they appear to be running. If another repo's process (e.g., `server.py` from `hermes-webui-new`) is occupying port 8648, kill it first, then start the EKKOLearnAI one.

### User's Fork Contains Customizations

Thad has a fork at `https://github.com/AntisystemOG/hermes-web-ui` with commit `f636b1b` ("feat: rebrand to Spock — icon, sidebar text, browser title"). **This fork is the source of truth for customizations** (logo, thinking avatar video, title, sidebar branding). The EKKOLearnAI upstream repo does NOT have these changes.

**Important:** The `hermes-web-ui-ekko` local repo is a clone of this fork (or built from it) and contains the **pre-built `dist/`** with customizations already baked in. This pre-built `dist/client/` can be copied to the correct repo when the local build environment is broken (see §"Build Failure Fallback: Copy Pre-built dist" in SKILL.md).

## Mandatory Pre-Flight Check Before Any Shortcut or Launch

Before creating shortcuts, restarting, or debugging:

```bash
# Check what is actually binding port 8648 RIGHT NOW
lsof -iTCP:8648 -sTCP:LISTEN
ss -tlnp | grep :8648
ps aux | grep -E "server\.py|node.*hermes-web-ui"

# Critical: also check for a systemd user service that auto-respawns the WRONG server
systemctl --user status hermes-webui.service 2>/dev/null || echo "No hermes-webui.service"
cat ~/.config/systemd/user/hermes-webui.service 2>/dev/null || echo "No service file"
```

### Root Cause: systemd user service auto-respawning wrong server

If killing a Python `server.py` process on port 8648 only for a new PID to appear seconds later, a **systemd user service** is the culprit. Thad's environment had `~/.config/systemd/user/hermes-webui.service` with:

```ini
[Unit]
Description=Hermes Web UI
After=network.target
[Service]
ExecStart=/home/thadd/.hermes/hermes-agent/venv/bin/python3 /home/thadd/hermes-webui-new/server.py
Restart=on-failure
```

**Symptom:** `kill -9 <PID>` → new PID appears in `lsof` within seconds. No `nohup` or cron — systemd is respawning it.

**Fix:**
```bash
systemctl --user stop hermes-webui.service
systemctl --user disable hermes-webui.service
# Verify it's dead and won't restart
systemctl --user status hermes-webui.service   # should show "inactive (dead)"
```

**If `hermes-webui-new/server.py` is shown:** That is the WRONG process. Kill it (`kill -9 <PID>`), clear `~/.hermes-web-ui/server.pid` if it exists, **disable the systemd service first**, then start the EKKOLearnAI server.

**If nothing is listening:** The EKKOLearnAI server needs to be started. Run `node bin/hermes-web-ui.mjs start` from `/mnt/c/Users/thadd/hermes-web-ui`.

### Distinguish Which Server Is Actually Running (Port 8648)

When multiple repos could be serving port 8648, use HTTP response content to identify which one is live:

```bash
# EKKOLearnAI server (correct) — HTML starts with <html lang="zh-CN">
curl -s http://127.0.0.1:8648/ | head -1
# → <!doctype html>
# → <html lang="zh-CN">

# Old Python Spock server (wrong) — has <title>Spock</title> and git conflict markers
curl -s http://127.0.0.1:8648/ | head -5
# → <!--
# → <<<<<<< Updated upstream
# → ...
# → <title>Spock</title>
```

The `zh-CN` lang attribute is a reliable EKKOLearnAI discriminator. Git conflict markers (`<<<<<<<`) are a dead giveaway for a broken or stale Spock server build.

## Which one is the "real" WebUI?

**The answer is always the EKKOLearnAI Node.js repo.** Do not ask. Do not verify by looking at running processes and guessing. The user already established the preference explicitly.

**When the user says "the webui":**
1. Assume he means `C:\Users\thadd\hermes-web-ui` (EKKOLearnAI repo)
2. Check if anything else is squatting on port 8648
3. If yes, kill it
4. Start the EKKOLearnAI server
5. Only then build shortcuts or troubleshoot

## Desktop Shortcuts and Their Targets

| Shortcut | File | What it launches |
|----------|------|-----------------|
| `Spock WebUI.lnk` | `.lnk` pointing to `Start Hermes WebUI.bat` | The batch file |
| `Spocks WebUI.url` | `.url` with `http://172.24.60.180:8648/` | Browser only |
| `Start Hermes WebUI.bat` | Batch file on Desktop | Either Python or Node server |

**The batch file is the single source of truth.** If it contains:
- `python3 server.py` with `SPOCK_WEBUI_*` → it's launching `hermes-webui-new` (WRONG — update it)
- `node dist/server/index.js` with `HERMES_WEB_UI_HOME` → it's launching `hermes-web-ui-ekko` (check if this is the same as EKKOLearnAI or an older clone)

**Target for the authoritative repo:**
- Working dir: `C:\Users\thadd\hermes-web-ui`
- Server inside WSL: `wsl bash -c "cd /mnt/c/Users/thadd/hermes-web-ui && node bin/hermes-web-ui.mjs start"`
- Icon: `C:\Users\thadd\hermes-web-ui\packages\client\public\favicon.ico`

## Multiple Desktop Entries: Naming and Cleanup

Thad's Desktop may accumulate multiple launchers over sessions (`.bat`, `.lnk`, `.vbs`, `.ps1`, `.url`). Before creating a new shortcut, list existing ones and remove any pointing to the wrong repo:

```bash
# In WSL, scan Desktop for WebUI-related launchers
ls /mnt/c/Users/thadd/Desktop/ | grep -i -E "hermes|webui|spock|launch"
# Example output:  Hermes WebUI.lnk  Launch Hermes WebUI.bat  Spocks WebUI.url
```

**If `Hermes WebUI.lnk` exists** — check its target (it may point to a stale VBS/PS1 or to `~/hermes-webui-new`). Rebuild if uncertain.

**If `Launch Hermes WebUI.bat` exists** — read it to verify the `node` path and repo. If it launches `server.py`, overwrite it with the correct `.bat` template.

**Recommended naming convention:**
- Primary launcher: `Launch Hermes WebUI.bat` (visible, testable) or `Hermes WebUI.lnk` (clean, hidden)
- Remove old names like `Spock WebUI.lnk`, `Start Hermes WebUI.bat` if they point to the wrong repo

## Workspace Scripts That Touch WebUI

| Script | Must Target |
|--------|-------------|
| `scripts/apply-webui-customizations.sh` | `WEBUI_DIR=/mnt/c/Users/thadd/hermes-web-ui` |
| Desktop `.lnk`/`.bat` launchers | `C:\Users\thadd\hermes-web-ui` |

## Customizations: EKKOLearnAI Repo + Fork Dist

The authoritative server runs from the **EKKOLearnAI repo** (`/mnt/c/Users/thadd/hermes-web-ui`), but the **visual customizations** (Spock branding, Star Trek badge) come from the **fork** (`AntisystemOG/hermes-web-ui`) via its pre-built `dist/`:

```bash
# 1. EKKOLearnAI repo: runs the server (latest upstream code)
cd /mnt/c/Users/thadd/hermes-web-ui
node bin/hermes-web-ui.mjs start

# 2. Fork dist: provides custom assets (when build fails)
cp -r /home/thadd/hermes-web-ui-ekko/dist/client/* \
      /mnt/c/Users/thadd/hermes-web-ui/dist/client/
```

This two-repo pattern is necessary when:
- `npm run build` fails in the EKKOLearnAI repo (missing native bindings, etc.)
- The user's fork `dist/` is already built and customized

## Common Confusion Scenarios

### "The webui isn't loading"
- Check if ANY server is running on 8648
- If nothing is running, the shortcut is broken or the server was never started
- If the WRONG server is running (`server.py` from `hermes-webui-new`), kill it and start EKKOLearnAI

### "Fix the webui shortcut"
- Read the `.lnk` target and the VBS/batch it points to
- If the target is `hermes-webui-new`, rebuild it to point to `C:\Users\thadd\hermes-web-ui`
- See `references/launcher-shortcut-pattern.md` for the correct VBS+PowerShell pattern

### "I said the wrong web ui" / "this is the wrong one"
- Stop whatever is running
- Kill any stale Python/Node processes on port 8648
- Start the EKKOLearnAI server: `cd /mnt/c/Users/thadd/hermes-web-ui && node bin/hermes-web-ui.mjs start`
- Rebuild shortcut to point to EKKOLearnAI repo
- Verify with `ss -tlnp | grep :8648` — should show node, not python

### "My customizations are gone"
**Likely cause:** The EKKOLearnAI repo's `dist/client/` has been rebuilt or overwritten with default upstream assets.

**Fix:** Copy the pre-built custom `dist/client/` from `hermes-web-ui-ekko`:
```bash
pkill -f "dist/server/index.js"
sleep 2
cp -r /home/thadd/hermes-web-ui-ekko/dist/client/* \
      /mnt/c/Users/thadd/hermes-web-ui/dist/client/
# Verify customizations
grep "title" /mnt/c/Users/thadd/hermes-web-ui/dist/client/index.html
ls -la /mnt/c/Users/thadd/hermes-web-ui/dist/client/assets/mp4/
# Restart server
cd /mnt/c/Users/thadd/hermes-web-ui
export AUTH_DISABLED=1
nohup node bin/hermes-web-ui.mjs start > ~/.hermes-web-ui/server.log 2>&1 &
```
