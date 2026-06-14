# Historical Snapshot Comparison Pattern

Compare current state against prior snapshots to show change metrics (dollar, percent) over selectable time horizons. Used in single-file dashboards that persist user data to `localStorage`.

## When to use

- Dashboards that track portfolios, budgets, inventories, or any quantitative state over time.
- Users upload or save periodic snapshots (CSV imports, manual saves, auto-captures).
- You want to show "+5.2% this month" without a backend or time-series database.

## Data model

```javascript
// Snapshot stored in localStorage
{
  exportDate: 'MM/DD/YYYY',      // Human-readable date
  addedAt: Date.now(),            // Milliseconds for precise sorting
  total: 123456.78,
  positions: [
    { symbol, accountName, currentValue, costBasis, quantity, isCash }
  ]
}
```

Keep a capped array (e.g., 30 snapshots) in `localStorage` under a namespaced key (`pp_history`).

## Time horizon mapping

```javascript
const now = Date.now();
const periodMs = {
  '1D':  86400000,
  '1W':  604800000,
  '1M':  2592000000,
  '3M':  7776000000,
  '1Y':  31536000000,
  'YTD': now - new Date(new Date().getFullYear(), 0, 1).getTime(),
  'ALL': Infinity
};
```

`YTD` is dynamic because the span changes every day; compute it at render time.

## Baseline lookup

```javascript
function findBaseline(accountName, history, filter) {
  const cutoff = filter === 'ALL' ? 0 : now - periodMs[filter];
  // Reverse to get most recent snapshot at or before cutoff
  const baseline = [...history].reverse().find(h =>
    parseExportDate(h.exportDate).getTime() <= cutoff
  );
  if (!baseline) return null;

  // Sum currentValue for positions belonging to this account
  return baseline.positions
    .filter(p => p.accountName === accountName)
    .reduce((sum, p) => sum + (p.currentValue || 0), 0);
}
```

**Graceful degradation:** If no snapshot exists for the selected period, return `null` and hide the change row rather than showing `NaN` or `undefined`.

## Change calculation

```javascript
const current = getCurrentAccountValue(accountName);
const baseline = findBaseline(accountName, S.history, S.historyFilter);

if (baseline !== null && baseline > 0) {
  const changeDollar = current - baseline;
  const changePct  = (changeDollar / baseline) * 100;
  const signClass  = changeDollar >= 0 ? 'positive' : 'negative';
  const arrow      = changeDollar >= 0 ? '▲' : '▼';
  // render: ▲ +$247.12 (+5.21%) 1M
}
```

## UI wiring

Use **event delegation** on the filter container so re-rendering the cards does not re-attach listeners:

```javascript
document.getElementById('timeFilter').addEventListener('click', e => {
  if (e.target.classList.contains('time-btn')) {
    S.historyFilter = e.target.dataset.period;   // '1M', 'YTD', etc.
    renderSummary();                              // re-renders account cards
  }
});
```

Store the active filter in your global state object (`S.historyFilter`) so `renderSummary()` can read it without touching the DOM.

## Pitfalls

1. **Account name drift** — If a user renames an account in their broker export, `accountName` won't match older snapshots. Consider normalizing names (strip whitespace, lowercase) or letting the user alias accounts in the dashboard.

2. **Sparse snapshots** — If the user uploads CSVs irregularly, the "1M" baseline might actually be 47 days old. Document this in the UI (e.g., show the actual baseline date on hover).

3. **Cash vs. invested** — Decide whether cash positions (`isCash: true`) should be included in the change calculation. Usually yes for total account value, but you may want a toggle for "invested only."

4. **Zero baseline** — A brand-new account with no prior snapshot yields `baseline === null`. Hide the change row; do not render `+∞%`.
