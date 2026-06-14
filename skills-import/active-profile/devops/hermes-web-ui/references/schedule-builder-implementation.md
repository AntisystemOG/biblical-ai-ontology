# Jobs ScheduleBuilder Implementation (May 31, 2026)

## What Was Built

Replaced the raw cron text input + 7-preset dropdown in `JobFormModal.vue` with an inline **Schedule Builder** featuring 5 mode tabs.

## Modes

| Mode | Controls | Example Output |
|---|---|---|
| **Interval** | Number + Minutes/Hours/Days | `*/30 * * * *` |
| **Daily** | Time picker | `0 9 * * *` |
| **Weekly** | Day-of-week + Time picker | `0 9 * * 1` |
| **Monthly** | Date (1-31) + Time picker | `0 9 15 * *` |
| **Custom Cron** | Raw text input | `0 9 * * 1` |

## Key Implementation Details

### 1. State Structure

```typescript
type ScheduleMode = 'interval' | 'daily' | 'weekly' | 'monthly' | 'cron'

const scheduleMode = ref<ScheduleMode>('interval')
const intervalValue = ref<number>(30)
const intervalUnit = ref<'min' | 'hour' | 'day'>('min')
const dailyTime = ref<number | null>(null)        // ms from midnight
const weeklyDay = ref<number>(1)                    // 0=Sun ... 6=Sat
const weeklyTime = ref<number | null>(null)
const monthlyDate = ref<number>(1)
const monthlyTime = ref<number | null>(null)
```

### 2. Time Helpers

`NTimePicker` uses `number` values (ms since midnight). Converters:

```typescript
function timeStrToMs(timeStr: string): number | null {
  if (!timeStr) return null
  const [h, m] = timeStr.split(':').map(Number)
  return ((h * 60 + m) * 60 * 1000)
}

function msToTimeStr(ms: number | null): string {
  if (ms == null) return ''
  const totalMin = Math.floor(ms / 60000)
  return `${String(Math.floor(totalMin / 60)).padStart(2, '0')}:${String(totalMin % 60).padStart(2, '0')}`
}
```

### 3. Cron Generation

```typescript
function buildCronFromState(): string {
  switch (scheduleMode.value) {
    case 'interval': {
      const n = Math.max(1, Math.round(intervalValue.value || 1))
      if (intervalUnit.value === 'min') return `*/${n} * * * *`
      if (intervalUnit.value === 'hour') return `0 */${n} * * *`
      return `0 0 */${n} * *`
    }
    case 'daily': {
      const t = msToTimeStr(dailyTime.value)
      if (!t) return '0 0 * * *'
      const [h, m] = t.split(':')
      return `${m} ${h} * * *`
    }
    // ... weekly, monthly similar
    case 'cron':
    default:
      return formData.value.schedule
  }
}
```

### 4. Reverse Parsing (Edit Mode)

When editing an existing job, the raw cron string is parsed back into builder state:

```typescript
function parseExistingSchedule(scheduleStr: string) {
  const s = scheduleStr.trim()
  // interval: */N * * * *, 0 */N * * *, 0 0 */N * *
  // daily: M H * * *
  // weekly: M H * * D
  // monthly: M H DD * *
  // fallback: cron mode
}
```

Regex patterns used:
- Interval minutes: `/^\*\/(\d+) \* \* \* \*$/`
- Interval hours: `/^0 \*\/(\d+) \* \* \*$/`
- Interval days: `/^0 0 \*\/(\d+) \* \*$/`
- Daily: `/^(\d{1,2})\s+(\d{1,2})\s+\*\s+\*\s+\*$/`
- Weekly: `/^(\d{1,2})\s+(\d{1,2})\s+\*\s+\*\s+(\d)$/`
- Monthly: `/^(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+\*\s+\*$/`

### 5. Real-Time Preview

Every builder row displays a `cron-preview` badge showing the generated expression:

```vue
<span class="cron-preview">{{ formData.schedule }}</span>
```

Styled as monospace, muted color, inside a bordered pill.

### 6. Naive UI Components Used

- `NRadioGroup` / `NRadio` — mode selection
- `NInputNumber` — interval value
- `NSelect` — interval unit, day-of-week, day-of-month
- `NTimePicker` — time selection (format="HH:mm", actions=['clear'])

## Files Changed

| File | Change |
|---|---|
| `packages/client/src/components/hermes/jobs/JobFormModal.vue` | Complete rewrite of schedule section |
| `packages/client/src/i18n/locales/en.ts` | Added `modeInterval`, `modeDaily`, `modeWeekly`, `modeMonthly`, `modeCron` |

## What Was NOT Changed

- Backend controller — still passes raw string to `hermes cron create`
- `packages/client/src/api/hermes/jobs.ts` — no new helpers needed; inline functions in modal
- No separate `ScheduleBuilder.vue` component — everything inline to avoid extra file

## Default Behavior

New jobs default to **Interval / 30 minutes** (`*/30 * * * *`).

## i18n Keys Added

```typescript
jobs: {
  modeInterval: 'Interval',
  modeDaily: 'Daily',
  modeWeekly: 'Weekly',
  modeMonthly: 'Monthly',
  modeCron: 'Custom Cron',
}
```

## Pitfall: NTimePicker Value Format

`NTimePicker` v-model is a **number** (ms since midnight), NOT a string. The `format="HH:mm"` prop only affects display. Use the converter functions above — do NOT pass string values directly.

## Build Verification

```bash
cd /home/thadd/hermes-web-ui
npx tsc --noEmit  # TypeScript passes clean
# Full build: npm run build (takes ~4-5 min)
```
