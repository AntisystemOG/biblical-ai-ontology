# Prompt Hardening Pass — Aug 31, 2026 4:30 AM CDT

## Context
- One-time cron job `prompt-hardening` fired at 4:30 AM CDT (09:30 UTC) Aug 31.
- Purpose: Append [PROMPT-LAW] universal + [PROMPT-LAW-KALSHI] blocks to every cron prompt so Thad's model switching can't cause misinterpretation (Aug 28 false SELL was the trigger event).
- Isolated cron run, model pinned `ollama-cloud/glm-5.2`.

## What happened
- Isolated context could only see the prompt-hardening job itself — all other crons were invisible (restricted context).
- Fallback path activated per agent file step 5.
- Read all agent files (20+ crons identified from REGISTRY.md + memory).
- Wrote hardened prompt instructions to `agents/prompt-hardening-output.md` for main session manual apply.

## Output file
- Path: `C:\Users\thadd\.openclaw\workspace\agents\prompt-hardening-output.md`
- Contains: Complete LAW BLOCKS, per-job patching instructions, model pin guidance, verification checklist.
- 19 jobs identified for patching (9 Kalshi/trading + 10 non-Kalshi).
- 2 disabled jobs skipped (kalshi-weather-morning-scan, miami-longshot-watch).
- 1 self-deleting job skipped (prompt-hardening itself).

## Priority order for main session apply
1. kalshi-job-evening (was the Aug 28 false SELL source — HIGHEST PRIORITY)
2. kalshi-position-monitor (active hourly trading guard)
3. lotto-exit-watch (active intraday falsification guard)
4. Other Kalshi jobs (kalshi-job-morning, kalshi-job-midday, kalshi-daily-predictions, the-edge-morning, the-edge-nightly, kalshi-longshot-tracker)
5. twc-update-probe (universal block only — data probe, no trading decisions)
6. Non-Kalshi jobs (whale-watch, history-rhymes, daily-brief, financial-advisor, memory-dreaming, trading-arena, top-100-strategists, long-term-holds, truth-based-trading, gateway-watchdog)

## Model pin status
- 3 jobs already pinned to `ollama-cloud/glm-5.2`: twc-update-probe, kalshi-longshot-tracker, prompt-hardening.
- All other jobs: main session must check `payload.model` via `cron get` and pin if missing.

## What the main session needs to do
1. Read `agents/prompt-hardening-output.md`.
2. For each listed job: `cron get <jobId>`, check for [PROMPT-LAW] marker (skip if present), append appropriate LAW BLOCK(s), pin model if missing.
3. Verify each patch landed.
4. Git commit + push.
5. Report to Thad.

## Lesson
- Isolated cron contexts have restricted cron access — can only see their own job.
- For jobs that need to mutate other crons, either run in main session or write fallback instructions.
- The prompt-hardening job was designed with this fallback in mind (step 5 of the agent file).