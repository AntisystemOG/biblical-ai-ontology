---
name: "gateway-cron-direct-patch"
description: "Cron preflight failures, stale model pins, automations tool unavailable - patch cron payloads directly in the gateway state store"
---

Patch Cron Job Payloads Directly in the Gateway State Store

Use when a cron job fails preflight (e.g., stale model pin like `ollama-cloud/glm-5.2` after a provider policy rename) and the automations tool is NOT in the current session's toolset (common in fallback-model sessions).

## Procedure

1. **Locate the store**: `C:\Users\thadd\.openclaw\state\openclaw.sqlite` (WAL mode; the gateway may be running - concurrent writes are safe).
2. **Read the job**: Python `sqlite3`, table `cron_jobs`, columns `job_id`, `name`, `job_json` (the full payload JSON lives in `job_json`):
   ```python
   rows = conn.execute("SELECT job_id, name, job_json FROM cron_jobs WHERE job_id IN (...ids...)").fetchall()
   ```
3. **Patch only the target field**: `json.loads(job_json)` -> modify the one field (e.g., `j["payload"]["model"] = "ollama/glm-5.2:cloud"`) -> `UPDATE cron_jobs SET job_json=? WHERE job_id=?`. Never touch other fields; a Python dict round-trip preserves key order.
4. **Verify by re-read**: SELECT again and print the patched field before reporting.
5. **Notify the source**: the request usually arrives via inter-session message from the watchdog cron (`agent:main:cron:<uuid>:trigger`). Reply through `sessions_send` to that session key with one line per job confirming the new value.
6. **Log**: append the fix (job, old -> new value, root cause) to `memory/YYYY-MM-DD.md` and push.

## The Skip Epidemic (a second preflight failure mode - not a pin problem)

When MANY cron jobs show `lastRunStatus: skipped` and the diagnostic says "local provider preflight failed at http://127.0.0.1:11434", the Ollama local-server probe timed out (2500ms deadline) - usually CPU starvation, not a dead server:

1. Probe: GET http://127.0.0.1:11434/api/tags with a 10s timeout and measure ms. Ollama binary: `C:\Users\thadd\AppData\Local\Programs\Ollama\ollama.exe`. Port 11434 LISTENING is not enough - it must respond inside the 2500ms deadline; a probe over ~1s under load predicts preflight failures.
2. Find the hog: read cron_jobs state_json lastDurationMs across jobs - a single runaway run (e.g., a heartbeat at 4.36h, erroring only when it finally dies) starves the 2-core box and every other cron skips while it holds the slot. The skips self-heal when the hog ends; verify Ollama answers <2500ms before re-running anything.
3. Disabling superseded zombie jobs via the store: the `cron_jobs` table has BOTH an `enabled` column AND `job_json.enabled` - disabling requires patching BOTH (`UPDATE ... SET enabled=0, job_json=?` with `j["enabled"]=False`), then verify by re-read. Zombies that re-enable themselves steal scheduler slots and cause the skip cascade.

## Pitfalls

- Write the Python to a file under `.openclaw/tmp/` first - PowerShell mangles inline Python with quotes/nested parens (documented AGENTS.md rule).
- The gateway may cache job configs; if the next preflight still fails, the watchdog heartbeat will re-flag it - re-verify the stored JSON before assuming the patch failed.
- Known stale-pin root cause: pre-policy model names (`ollama-cloud/glm-5.2`) vs policy allowlist (`ollama/<model>:cloud`). Sweep ALL cron_jobs for the old string, not just the flagged ones:
  `SELECT job_id, name FROM cron_jobs WHERE job_json LIKE '%ollama-cloud/%'`
- If the store table names differ in a future version, list tables first: `SELECT name FROM sqlite_master WHERE type='table'` and look for `cron_jobs` / `claw_cron_refs`.

## Schedule Edits — the CLI path (openclaw cron get/edit)

When the automations tool is absent from the session's function set (fallback-model sessions) and the job needs a SCHEDULE change (expr/tz), use the OpenClaw CLI's first-class cron commands instead of sqlite surgery — 3 short commands, no file write, no concurrent-write concerns:

1. Verify the mandate first: the requesting cron's agent file / REGISTRY should name the exact target expr (e.g. whale-watch's quarterly `0 6 18 2,5,8,11 *`).
2. `openclaw cron get <jobId>` — inspect the current schedule/payload before touching anything.
3. `openclaw cron edit <jobId> --cron "<expr>" --tz "<IANA>"` — patch schedule fields only. Check `openclaw cron edit --help` for the flag names first (`--cron` takes 5/6-field exprs, `--tz` IANA, `--at` one-shots) — don't guess flags.
4. Verify: `openclaw cron get <jobId>` again and confirm the new expr/tz printed.
5. Update the doc trail: the agent file's pending-fix note -> APPLIED (with the date and the CLI path), the REGISTRY entry, memory append, push.

Pitfalls:
- The requesting cron's run is usually already archived (subagents.archiveAfterMinutes) — the durable docs (agent file + REGISTRY + memory) are the reply; skip sessions_send back to the dead run.
- This CLI path is verified for schedule/delivery/enabled fields. Payload-field changes (model pins, message bodies) were historically done via the store surgery above — run `openclaw cron edit --help` first if a payload field needs patching and fall back to the store if no flag exists.
