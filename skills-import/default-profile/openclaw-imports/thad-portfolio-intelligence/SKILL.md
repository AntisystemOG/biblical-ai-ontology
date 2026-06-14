---
name: thad-portfolio-intelligence
description: "Automated portfolio analysis for Thad's Schwab holdings — CSV ingestion, allocation vs Master Trend targets, deviation detection, action triggers."
triggers:
  - "check portfolio"
  - "rebalance needed"
  - "portfolio allocation"
  - "should I sell"
  - "should I buy"
  - "trading arena"
  - "master trend"
  - "allocation review"
  - "compare to target"
toolsets: ["terminal", "file", "execute_code"]
---

# Thad Portfolio Intelligence

Automated analysis pipeline for Thad's Schwab/Fidelity holdings against the **Master Trend Intelligence** targets.

---

## 1. Data Ingestion (latest CSV)

**Source:** `C:\Users\thadd\Desktop\Portfolio Positions\Portfolio_Positions_*.csv`

**Read latest CSV:**
```bash
LATEST=$(ls -t /mnt/c/Users/thadd/Desktop/Portfolio\ Positions/*.csv | head -1)
echo "Using: $LATEST"
head -20 "$LATEST"
```

**Parse with Python:**
```python3
import pandas as pd, glob, os

pattern = '/mnt/c/Users/thadd/Desktop/Portfolio Positions/*.csv'
files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
latest = files[0] if files else None

df = pd.read_csv(latest)
# Typical columns: Symbol, Description, Quantity, Price, Market Value, etc.
print(df.head())
print(f"Total positions: {len(df)}")

# Sum total portfolio value
portfolio_total = df['Market Value'].sum() if 'Market Value' in df.columns else 0
print(f"Total portfolio: ${portfolio_total:,.2f}")
```

---

## 2. Allocation by Category

**Sector Mapping (Thad's holdings):**

| Ticker | Category | Sub-Category |
|--------|----------|--------------|
| BE | Energy | Hydrogen/Electrification |
| VDE | Energy | Broad Energy ETF |
| XOP | Energy | Oil & Gas Exploration |
| SHEL | Energy | Integrated Oil (Defensive) |
| SEI | Energy | Nuclear/Small Modular |
| CEG | Energy | Nuclear Generation |
| INTC | Tech/Semiconductors | Foundry |
| MU | Tech/Semiconductors | Memory |
| NVDA | Tech/Semiconductors | AI Chips |
| SMH | Tech/Semiconductors | Semiconductor ETF |
| TSM | Tech/Semiconductors | Fabrication |
| RIOT | Crypto/Blockchain | Mining |
| CORZ | Crypto/Blockchain | Mining |
| COIN | Crypto/Blockchain | Exchange |
| HUT | Crypto/Blockchain | Mining |
| FBTC | Crypto/Blockchain | Bitcoin ETF |
| JNJ | Quality/Defensive | Healthcare |
| KO | Quality/Defensive | Consumer Staples |
| PG | Quality/Defensive | Consumer Staples |
| V | Quality/Defensive | Financial/Payments |
| WM | Quality/Defensive | Waste Management |
| RDDT | Speculative | Social Media |
| TEM | Speculative | Emerging Tech |
| RXRX | Speculative | Biotech/AI Drug |
| CBLL | Speculative | Biotech |

**Compute current allocations:**
```python3
# After loading df
energy_tickers = ['BE', 'VDE', 'XOP', 'SHEL', 'SEI', 'CEG']
tech_tickers = ['INTC', 'MU', 'NVDA', 'SMH', 'TSM']
crypto_tickers = ['RIOT', 'CORZ', 'COIN', 'HUT', 'FBTC']
quality_tickers = ['JNJ', 'KO', 'PG', 'V', 'WM']
spec_tickers = ['RDDT', 'TEM', 'RXRX', 'CBLL']

categories = {
    'Energy': energy_tickers,
    'Tech/Semiconductors': tech_tickers,
    'Crypto/Blockchain': crypto_tickers,
    'Quality/Defensive': quality_tickers,
    'Speculative': spec_tickers,
}

for cat, tickers in categories.items():
    mask = df['Symbol'].isin(tickers)
    value = df.loc[mask, 'Market Value'].sum()
    pct = (value / portfolio_total * 100) if portfolio_total else 0
    print(f"{cat:25s}: ${value:>12,.2f} ({pct:5.1f}%)")
```

---

## 3. Master Trend Intelligence Targets (May 2026)

**Current targets from MEMORY:**

| Target | Allocation | Action | Rationale |
|--------|-----------|--------|-----------|
| Energy | 38% | HOLD | Continuing leadership; BE hydrogen thesis intact |
| Tech/Semiconductors | 16% | HOLD/SELECTIVE | INTC foundry turnaround +40-80% potential; NVDA P/E compression likely |
| Crypto/Blockchain | 5% | **SELL 100%** | Miner washout predicted: RIOT -40-60%, CORZ -30-50% |
| Quality/Defensive | 3% | HOLD | Compounders outperforming (ZTS, GE, UBER) — consider rotating JNJ/PG |
| Speculative | 5% | HOLD/MANAGE | RDDT, TEM, RXRX, CBLL — high variance, thesis-dependent |
| Cash/Money Market | ~60% | **DEPLOY** | $265K idle; opportunity to add URA/URNM, VXUS/VEA 10-15% |
| International Value | 0% → **10-15%** | **BUY** | VXUS/VEA at 0% allocation — deep value opportunity |
| Uranium/Nuclear | 0% → **5-10%** | **BUY** | URA/URNM — nuclear renaissance accelerating |

**Specific ticker actions from MEMORY:**

| Ticker | Action | Target |
|--------|--------|--------|
| MU | **TRIM 50%** | Cyclical peak reached; +38% weekly move unsustainable |
| RIOT | **SELL 100%** | Predicted -40-60% downside |
| CORZ | **SELL 100%** | Predicted -30-50% downside |
| INTC | **HOLD/ADD** | Foundry turnaround thesis; +40-80% upside potential |
| VST (if held) | **HOLD/ADD** | +40-60% predicted; nuclear renaissance |
| VXUS/VEA | **BUY** | 0% → 10-15% allocation |
| URA/URNM | **BUY** | 0% → 5-10% allocation |
| LAR (lithium) | **BUY** | 0% → small; 50-100% upside by 2028 |

---

## 4. Deviation Detection

**Compare current vs target:**

```python3
targets = {
    'Energy': 38,
    'Tech/Semiconductors': 16,
    'Crypto/Blockchain': 0,      # SELL
    'Quality/Defensive': 3,
    'Speculative': 5,
    'Cash/Money Market': 60,      # Target to gradually deploy
}

print("\n=== ALLOCATION DEVIATIONS ===")
for cat, tickers in categories.items():
    mask = df['Symbol'].isin(tickers)
    value = df.loc[mask, 'Market Value'].sum()
    current_pct = value / portfolio_total * 100
    target_pct = targets.get(cat, 0)
    delta = current_pct - target_pct
    
    if abs(delta) > 3:  # 3% threshold
        direction = "OVERWEIGHT" if delta > 0 else "UNDERWEIGHT"
        print(f"  {cat}: {current_pct:.1f}% vs target {target_pct:.1f}% — {direction} by {abs(delta):.1f}pp")
        print(f"    Action needed: {'SELL' if delta > 0 else 'BUY'} ${abs(delta)/100 * portfolio_total:,.0f}")
```

---

## 5. Rebalancing Orders

**If deviation exceeds threshold → generate order rationale:**

```python3
# Example: Crypto at 5% vs target 0%
crypto_mask = df['Symbol'].isin(crypto_tickers)
crypto_value = df.loc[crypto_mask, 'Market Value'].sum()
crypto_pct = crypto_value / portfolio_total * 100

if crypto_pct > 1:  # Any crypto is over target
    print(f"\n🚨 CRYPTO ALERT: ${crypto_value:,.2f} ({crypto_pct:.1f}%) still deployed")
    print("   Target: 0% (complete exit)")
    print("   Predicted: RIOT -40-60%, CORZ -30-50%")
    print("   Suggested order: Market sell all crypto positions")
    print("   Proceeds to deploy: VXUS/VEA (10-15%) or URA/URNM (5-10%)")
```

---

## 6. Report Generation

**Minimal terminal output (Thad's preference):**

```
Portfolio Intel: May-14-2026 (latest CSV)
─────────────────────────────────────
Total:    $503,213
Cash:     $267,890 (53.2%) — deployment candidate
Deployed: $235,323 (46.8%)

Energy:       38.1% ✓ ON TARGET
Tech:         15.8% ✓ ON TARGET  
Crypto:        4.7% ⚠ OVER (+4.7pp) — EXIT RECOMMENDED
Quality:       3.1% ✓ ON TARGET
Speculative:   4.9% ✓ ON TARGET
International: 0.0% ⚠ MISSING (+10-15pp target)
Uranium:      0.0% ⚠ MISSING (+5-10pp target)

Actions:
1. SELL: All crypto (RIOT, CORZ, COIN, HUT, FBTC) — ~$23K
2. TRIM: MU 50% — cyclical peak signal
3. DEPLOY: VXUS/VEA $50-75K, URA/URNM $25-50K
4. HOLD: INTC (foundry thesis), BE (hydrogen)
```

**Full report file:**
```python3
report = f"""# Portfolio Intelligence Report — {date}
... (structured markdown)
"""
with open('/home/thadd/.hermes/webui/openclaw-migrated/reports/portfolio_intel_latest.md', 'w') as f:
    f.write(report)
```

---

## Pitfalls

| Mistake | Consequence |
|---------|-------------|
| Using stale CSV | Wrong allocation; check filename date |
| Hardcoding totals in memory | Stale; always recompute from latest CSV |
| Forgetting cash/money market | Underestimates deployable capital |
| Ignoring dividend reinvestment | May undercount compounding positions |
| Not updating tickers after splits/acquisitions | JNJ/KO may have changed |

---

## See Also

- `spock-infrastructure-health` — Gateway/cron monitoring
- `hermes-secure-github-backup` — Backup this skill's outputs
- `openclaw-imports/stock-monitor` — Real-time price monitoring
- `openclaw-imports/telegram-notify` — Alert delivery
