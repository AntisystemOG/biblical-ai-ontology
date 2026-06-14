# Jobs Tab Scheduling UI Investigation (May 30, 2026)

## User Complaint

"The scheduling is a little funny. I need to be able to set the schedule a little easier."

## What I Found

### Current UI (`JobFormModal.vue`)

The Jobs create/edit modal has a single `NInput` for schedule:

```vue
<NInput
  v-model:value="formData.schedule"
  :placeholder="t('jobs.schedulePlaceholder')"
/>
```

Plus a preset dropdown with 7 cron expressions:
- Every minute: `* * * * *`
- Every 5 min: `*/5 * * * *`
- Every hour: `0 * * * *`
- Every day: `0 0 * * *`
- Every day 9am: `0 9 * * *`
- Every Monday: `0 9 * * 1`
- Every month: `0 9 1 * *`

**Problem:** Users must know cron syntax or pick from a tiny preset list.

### Backend Capabilities (Much Broader)

The backend controller (`packages/server/src/controllers/hermes/jobs.ts:172`) passes the raw schedule string to `hermes cron create`:

```typescript
const schedule = String(body.schedule || body.schedule_display || '').trim()
const args = ['cron', 'create']
args.push(schedule)
```

The Hermes CLI `cron create` command accepts:
1. **Cron expressions** — `* * * * *`, `0 9 * * 1`
2. **Natural language intervals** — `every 30m`, `every 2h`, `every 1d`
3. **ISO timestamps** — `2026-06-01T09:00:00` (one-time run)

The client-side TypeScript types (`packages/client/src/api/hermes/jobs.ts`) already define structured schedule types:

```typescript
export interface JobScheduleInterval {
  kind: 'interval'
  minutes: number
  display: string
}

export interface JobScheduleCron {
  kind: 'cron'
  expr: string
  display: string
}

export interface JobScheduleOnce {
  kind: 'once'
  run_at: string
  display: string
}
```

But the UI only ever sends a **raw string** — it never constructs the structured `kind: 'interval'` or `kind: 'once'` objects.

### What Should Be Built

A `ScheduleBuilder` component with three tabs/modes:

**1. Interval (easiest — what users actually want)**
- Numeric input: "Every [ 30 ] [ minutes | hours | days ]"
- Convert to cron or send `kind: 'interval'` with `minutes` field

**2. Cron (advanced)**
- Keep existing text input + preset dropdown
- Add a visual cron builder (minute/hour/day/month/weekday pickers)

**3. Once (one-time)**
- Datetime picker (Naive UI `NDatePicker` with `type="datetime"`)
- Send `kind: 'once'` with `run_at` ISO string

### Files to Modify

| File | Change |
|---|---|
| `packages/client/src/components/hermes/jobs/JobFormModal.vue` | Replace schedule `NInput` + `NSelect` with `ScheduleBuilder` component |
| `packages/client/src/api/hermes/jobs.ts` | Add `buildSchedulePayload()` helper to convert builder output to API format |
| `packages/client/src/i18n/locales/en.ts` | Add translation keys for interval/cron/once modes |

### Backend Change Needed?

**Probably not.** The backend already accepts raw strings. If the UI sends:
- `"every 30m"` → Hermes CLI parses as interval
- `"2026-06-01T09:00:00"` → Hermes CLI parses as once
- `"0 9 * * 1"` → Hermes CLI parses as cron

However, to properly support the structured types (`kind: 'interval'`), the backend controller may need to pass structured objects to the CLI instead of raw strings. Verify with:

```bash
cd /home/thadd/hermes-web-ui
node -e "
const { execSync } = require('child_process');
const out = execSync('npx hermes cron create --help', { encoding: 'utf8' });
console.log(out);
"
```

Or check `hermes_bridge.py` or the Hermes CLI source for `cron create` argument parsing.

## Recommendation

Build a `ScheduleBuilder.vue` component in `packages/client/src/components/hermes/jobs/` with three mode tabs. Start with Interval mode since that's what 90% of users want. The existing `JobFormModal.vue` becomes much simpler — just `<ScheduleBuilder v-model="formData.schedule" />`.
