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

## Pitfalls

- Write the Python to a file under `.openclaw/tmp/` first - PowerShell mangles inline Python with quotes/nested parens (documented AGENTS.md rule).
- The gateway may cache job configs; if the next preflight still fails, the watchdog heartbeat will re-flag it - re-verify the stored JSON before assuming the patch failed.
- Known stale-pin root cause: pre-policy model names (`ollama-cloud/glm-5.2`) vs policy allowlist (`ollama/<model>:cloud`). Sweep ALL cron_jobs for the old string, not just the flagged ones:
  `SELECT job_id, name FROM cron_jobs WHERE job_json LIKE '%ollama-cloud/%'`
- If the store table names differ in a future version, list tables first: `SELECT name FROM sqlite_master WHERE type='table'` and look for `cron_jobs` / `claw_cron_refs`.
