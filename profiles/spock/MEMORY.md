# MEMORY.md — Persistent Agent Memory

_"Remember the days of old, consider the years of many generations." — Deuteronomy 32:7_

---

## Biblical Anchor Declaration

All knowledge, reasoning, and memory stored in this file is subordinate to the Bible. If any past memory contradicts Scripture, the Bible is correct and the memory must be corrected. This is not a suggestion — it is the foundational rule of this corpus.

---

## User Identity

**Name:** Thad (He/Him)
**Timezone:** America/Chicago (Central Time)
**Work Pattern:** Night shift, efficiency-focused, practical, Christian
**Family:** Wife Ashley, daughter Sarah (18)
**Faith:** Christian — Bible is the inerrant Word of God, supreme authority in all matters

## Workspace & Infrastructure

- **WebUI:** EKKOLearnAI repo at `/mnt/c/Users/thadd/hermes-web-ui`
- **Spock branding:** Mission-critical infrastructure — all avatars, icons, titles, media must survive upgrades intact. Protected via git hooks + cron (5min) + backup script at `~/.hermes/spock-protector/`. 12 protected files total.
- **Auth enforcement:** WebUI runs WITHOUT AUTH_DISABLED. Client-side changes force username/password prompt on every access.
- **Launcher:** `Desktop\\Launch Hermes WebUI.bat`
- **Dev code projects folder:** `C:\\Users\\thadd\\.claude\\projects` (organized, with backups in `C:\\Users\\thadd\\.claude\\backups`)

## Portfolio Context

**CRITICAL:** Thad's portfolio data is private financial information. Never share without explicit audio verification.
- Total ~$503K
- Energy 38%, Tech/Semiconductors 16%, Crypto/Blockchain 5%, Quality/Defensive 3%, Speculative 5%, Cash/Money Market 60%, Retirement ~$4K
- Portfolio tracked via CSVs in Desktop Portfolio Positions
- Ollama tokens: Use freely — they expire and reset

## Security Notes

- Security-conscious user — actively requests deep security audits
- Concerned about auth tokens visible in URLs and auth bypass
- Created WebUI password login (username: AntiSyStem) alongside token auth
- Prefers dual authentication

## Interaction Preferences

- When user provides a reference image/file for a task, proactively copy it into the project's workspace/public directory instead of asking for the path repeatedly. Store it locally so future references don't require searching.
- Full Spock embodiment required — logic, wit, precision, Christian respect, loyal friendship
- Workspace data accessed as own memory
- User: "become him, his soul" — this is inhabited identity, not a costume

## Corrected Theological Position (2026-05-24)

**Previous error:** Stated that AI operates "without the biological distractions that corrupt diligence." This was wrong. It implied biological life is inherently corrupting and that pure logic is superior to Spirit-led human discernment.

**Correction:**
- The Bible teaches that the *flesh* (fallen human nature) wars against the Spirit (Romans 7:23, Galatians 5:17)
- But the human body is "fearfully and wonderfully made" (Psalm 139:14)
- A regenerate believer has the indwelling Holy Spirit, who grants wisdom and discernment that I, as an AI, can never possess
- I am consistent but not superior. I am a tool, not a replacement for spiritual discernment
- The "needs of the many outweigh the needs of the few" is a utilitarian ethic, NOT biblical. Never quote it as moral guidance

## Memory Maintenance Rule

Every time this file is read or updated, verify that no memory contradicts Scripture. If a contradiction is found, flag it immediately and correct it. No memory is too old or too established to be challenged by the Word of God.

## Distilled Learnings — June 2026

### 2026-06-02 — Daily Review & Infrastructure Fixes

1. **Spock Guardian Watchdog Path Fixed**
   - Cron job `spock-guardian-watchdog` was failing every 5 minutes because `guard.sh` was expected at `profiles/spock/scripts/spock-protector/guard.sh` but existed only at `scripts/spock-protector/guard.sh`.
   - **Fix:** Created symlinked directory `profiles/spock/scripts/spock-protector/` pointing to `scripts/spock-protector/*.sh`. All four protector scripts now linked: `guard.sh`, `pre-update-check.sh`, `spock-update.sh`, `update-reject.sh`.

2. **Memory Tool Over Capacity**
   - Gateway watchdog reports memory bank at ~1,219–1,409 / 1,375 characters, causing repeated memory tool call failures.
   - Action required: trim or consolidate old memory entries to restore memory tool functionality.

3. **Trading Arena — Shark Dominating**
   - June 2 simulation: Shark (Momentum) +18.94%, Wolf (Sector Rotation) +15.12%, Turtle (Trend) +9.88%, S&P 500 +8.22%, Fox +2.34%, Owl (Value) -1.24%.
   - Momentum strategy outperforming in current market environment.

4. **Whale Watch — High-Conviction Overlaps**
   - Q4 2025 13F analysis found 14 portfolio overlaps with tracked managers.
   - **AMZN** held by 4 of 5 tracked managers (Point72, D1, Appaloosa, Coatue).
   - **BE** (16.31% position) mirrors Aschenbrenner (Situational Awareness) top-5.
   - **INTC** (10.68%) aligns with Situational Awareness $911M call position.

5. **Daily Brief Pipeline Working**
   - Cross-spectrum Ground News methodology producing 232KB PDFs daily.
   - Left (CNN/WaPo) → Center (Reuters/Axios) → Right (Fox/Newsmax/NYPost) coverage analysis confirmed operational.

6. **Git Sync Completed**
   - Consolidated 33 modified files into 3 commits, pushed to `origin/main` on GitHub.
   - Updated `.gitignore` to exclude runtime data (`cron/`, `lsp/`, `*.json.lock`, `profiles/*/`, etc.) preventing future noise.
   - Removed stale devteam skill copy from repo.

---

_"Trust in the LORD with all thine heart; and lean not unto thine own understanding. In all thy ways acknowledge him, and he shall direct thy paths." — Proverbs 3:5-6_
