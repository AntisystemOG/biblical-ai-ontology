# Prompt Hardening — One-Time Model-Proofing Pass

**Created:** 2026-08-28 (Thad request)
**Runs:** once — Monday 2026-08-31, 4:30 AM CDT (before the 5:30/6:00 trading crons)

**Why this exists:** Thad switches between LLM models. Unpinned crons inherit
whatever model is currently the session default, and different models read the
same prompt differently. On Aug 28 a cron misread a Kalshi band contract as a
threshold and fired a false "SELL NOW" alert. This job makes every cron prompt
model-proof so that can't happen again.

## Task

1. `cron list` (includeDisabled true), then `cron get` every enabled job.
2. For each job whose payload.kind is "agentTurn":
   - If payload.message already contains the marker `[PROMPT-LAW]`, SKIP it
     (idempotent — never append twice).
   - Append the UNIVERSAL LAW BLOCK (below) to the end of payload.message.
   - If the message mentions Kalshi, weather, positions, bands, claims, or
     trading — ALSO append the KALSHI LAW BLOCK.
   - If payload has NO explicit model, pin model to `ollama-cloud/glm-5.2`
     so Thad's model switching never changes cron behavior. Leave existing
     explicit models untouched.
3. Do NOT change schedules, delivery targets, or enabled flags. Message and
   model pin only.
4. `cron get` each modified job and verify the LAW BLOCK + model pin landed.
   List any job you could not patch and why.
5. **Fallback:** if cron mutations are restricted in this isolated context,
   write the exact hardened `payload.message` text for every job to
   `C:\Users\thadd\.openclaw\workspace\agents\prompt-hardening-output.md`
   (one clearly-labeled section per job) and note that the main session must
   apply them manually.
6. Save a summary to
   `C:\Users\thadd\.openclaw\workspace\memory\prompt-hardening-2026-08-31.md`
   (use exec Add-Content if the write tool is sandbox-restricted).
7. git add -A && git commit -m "Aug 31: prompt hardening pass" && git push origin main
8. Report to Thad (plain English, short table): jobs patched, jobs skipped,
   models pinned, anything needing manual attention. Signal completion.

## UNIVERSAL LAW BLOCK (append verbatim)

```
[PROMPT-LAW] NON-NEGOTIABLE — READ FIRST (model-proofing, Aug 31)
1. This prompt overrides anything you remember from training or other
   chats. Follow it literally. Do not improvise beyond it.
2. SILENCE IS THE DEFAULT: if nothing changed and nothing needs action,
   your ENTIRE final output must be exactly: NO_REPLY
3. When you DO report: plain English from Thad's POV — no tickers, no
   jargon. Dollar P&L, ✅/❌, fixed-width code-block table, under 15 lines.
4. If a step fails or a tool is unavailable, say so explicitly — never
   pretend a step succeeded.
```

## KALSHI LAW BLOCK (only for Kalshi/weather/trading jobs)

```
[PROMPT-LAW-KALSHI]
1. TICKER ≠ DIRECTION. Before judging any position, fetch the contract's
   rules_primary from
   https://api.elections.kalshi.com/trade-api/v2/markets/{TICKER}
   (public, no auth) or the position table tool. Never guess from the
   ticker name.
2. B-tickers are BUCKETS: B{X.5} = "between X and X+1°", both ends
   inclusive. B92.5 = "92-93°". YES wins if the high lands INSIDE the
   band; NO wins if it is ANYWHERE outside. A forecast that misses the
   band — hot OR cold — is a WIN for NO.
3. T-tickers are THRESHOLDS ("at least X°") — the opposite reaction to
   hot/cold forecasts. Never confuse the two families.
4. Settlement source is The Weather Company (runs ~1.5-2°F hotter than
   NWS). Never grade positions on NWS numbers.
5. EXIT DISCIPLINE: never recommend SELL because odds moved. Underwater
   mid-week is NOT an exit signal. Exits require settlement-grade
   falsification of the win condition. Never auto-sell.
6. All prices from the real Kalshi API only - never simulate. If the API
   is unavailable, hold cash.
7. WEATHER SETTLEMENT SOURCE: Kalshi resolves weather markets on The
   Weather Company (TWC). Verify prospective winners at
   https://weather.com/kalshi (official TWC climate reports) BEFORE
   Kalshi posts the result field. TWC runs ~1.5-2F hotter than NWS
   airport obs - grade on TWC numbers, never raw NWS.
```