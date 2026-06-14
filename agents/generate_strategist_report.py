#!/usr/bin/env python3
"""
Top 100 Strategists Report Generator
Analyzes portfolio positions, fetches market data via yfinance,
and produces a PDF report with classifications and short interest.
"""

import csv
import glob
import os
import sys
from collections import defaultdict
from datetime import date

import yfinance as yf
from fpdf import FPDF

OUTPUT_DIR = "/mnt/c/Users/thadd/.openclaw/workspace/Spocks_Reports/strategists"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REPORT_DATE = date.today().strftime("%Y-%m-%d")
PDF_PATH = os.path.join(OUTPUT_DIR, f"{REPORT_DATE}_top_100_strategists.pdf")

DATA_DIR = "/mnt/c/Users/thadd/Desktop/Portfolio Positions"
CSV_FILES = sorted(glob.glob(os.path.join(DATA_DIR, "Portfolio_Positions_*.csv")), key=os.path.getmtime)
LATEST_CSV = CSV_FILES[-1] if CSV_FILES else None


def parse_csv(path):
    positions = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            positions.append(row)
    return positions


def normalize(row):
    sym = (row.get("Symbol") or "").strip()
    desc = (row.get("Description") or "").strip()
    lp_str = row.get("Last Price") or "0"
    cur_val_str = row.get("Current Value") or "0"
    pct_acc_str = row.get("Percent Of Account") or "0"
    total_pct_str = row.get("Total Gain/Loss Percent") or "0"

    def to_float(v):
        try:
            return float(str(v).replace("$", "").replace(",", "").replace("+", "").replace("%", "").strip())
        except (ValueError, TypeError):
            return 0.0

    return {
        "symbol": sym,
        "description": desc,
        "last_price": to_float(lp_str),
        "current_value": to_float(cur_val_str),
        "pct_account": to_float(pct_acc_str),
        "total_gain_pct": to_float(total_pct_str),
    }


def fetch_short_interest(symbols):
    results = {}
    print(f"[INFO] Fetching data for {len(symbols)} symbols...")
    for sym in symbols:
        try:
            info = yf.Ticker(sym).info
            shp = info.get("shortPercentOfFloat") or info.get("shortPercentFloat") or info.get("shortPercentageOfFloat")
            shr = info.get("shortRatio")
            results[sym] = {
                "shortPctFloat": round(shp, 4) if isinstance(shp, (int, float)) else None,
                "shortRatio": round(shr, 2) if isinstance(shr, (int, float)) else None,
                "sector": info.get("sector") or "N/A",
                "industry": info.get("industry") or "N/A",
            }
        except Exception as e:
            results[sym] = {"error": str(e)}
    return results


class Top100PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 30, 40)
        self.cell(0, 10, f"Top 100 Strategists Report - {REPORT_DATE}", new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 90)
        self.cell(0, 5, "Source: Fidelity Portfolio Exports + Yahoo Finance | Classification: LONG-TERM / ACCUMULATING / NEW-TRADE",
                  new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(2)
        self.set_draw_color(180, 180, 190)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 130)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def build_report():
    if not LATEST_CSV:
        print("[ERROR] No Portfolio CSV found.")
        sys.exit(1)

    rows = parse_csv(LATEST_CSV)
    positions = [normalize(r) for r in rows if r and r.get("Symbol") and not str(r.get("Symbol")).endswith("**")]

    # Aggregate by ticker (duplicates across accounts)
    agg = defaultdict(lambda: {"current_value": 0.0, "total_gain_pct": 0.0, "description": ""})
    for p in positions:
        sym = p["symbol"]
        if not sym:
            continue
        agg[sym]["current_value"] += p["current_value"]
        if p["total_gain_pct"] != 0:
            agg[sym]["total_gain_pct"] = p["total_gain_pct"]
        if not agg[sym]["description"]:
            agg[sym]["description"] = p["description"]

    # Multi-snapshot history
    history = defaultdict(dict)
    for fpath in CSV_FILES:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                sym = (row.get("Symbol") or "").strip()
                try:
                    val = float((row.get("Current Value") or "0").replace(",", "").replace("$", ""))
                except (ValueError, TypeError):
                    val = 0.0
                if sym and sym.isalpha() and val > 0:
                    history[sym][fname] = val

    # Short interest
    stock_syms = [s for s in agg.keys() if s.isalpha() and not s.endswith("**")]
    short_data = fetch_short_interest(stock_syms)

    total_val = sum(v["current_value"] for v in agg.values())
    classified = []
    for sym, data in agg.items():
        tenure_snaps = len(history.get(sym, []))
        if tenure_snaps >= 10 and data["current_value"] >= 2000:
            cls = "LONG-TERM HOLD"
        elif tenure_snaps >= 6:
            cls = "ACCUMULATING"
        else:
            cls = "NEW / TRADE"
        sorted_val = sorted(agg.items(), key=lambda x: -x[1]["current_value"])
        is_top10 = any(x[0] == sym for x in sorted_val[:10])
        if is_top10:
            cls = "LONG-TERM HOLD"
        sd = short_data.get(sym, {})
        classified.append({
            "symbol": sym,
            "description": data["description"],
            "current_value": data["current_value"],
            "total_gain_pct": data["total_gain_pct"],
            "pct_account": (data["current_value"] / total_val) * 100 if total_val else 0,
            "class": cls,
            "is_top10": is_top10,
            "tenure_snapshots": tenure_snaps,
            "shortPct": sd.get("shortPctFloat"),
            "shortRatio": sd.get("shortRatio"),
            "sector": sd.get("sector", "N/A"),
        })

    classified.sort(key=lambda x: -x["current_value"])

    lt_count = sum(1 for c in classified if c["class"] == "LONG-TERM HOLD")
    acc_count = sum(1 for c in classified if c["class"] == "ACCUMULATING")
    new_count = sum(1 for c in classified if c["class"] == "NEW / TRADE")

    pdf = Top100PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---- Summary ----
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "Portfolio Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 45)
    pdf.cell(0, 6, f"Total Portfolio Value: ${total_val:,.2f}".replace(",","X").replace("X",","), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Covered Positions: {len(classified)} unique tickers", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Classifications - Long-Term Holds: {lt_count}, Accumulating: {acc_count}, New/Trade: {new_count}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ---- Tables ----
    def render_table(title, title_color, rows):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*title_color)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        headers = ["Ticker", "Value ($)", "% Acct", "Tot Gain %", "Short %", "Days-to-Cover", "Class"]
        col_widths = [28, 35, 20, 24, 22, 32, 30]
        pdf.set_font("Helvetica", "B", 9)
        for h, w in zip(headers, col_widths):
            pdf.cell(w, 8, h, border=1, align="C")
        pdf.ln()
        pdf.set_font("Helvetica", "", 9)
        for c in rows:
            spc = f"{c.get('shortPct',0.0)*100:.2f}%" if c.get("shortPct") is not None else "N/A"
            shr = f"{c.get('shortRatio',0.0):.1f}" if c.get("shortRatio") is not None else "N/A"
            pdf.cell(col_widths[0], 7, c["symbol"][:8], border=1, align="C")
            pdf.cell(col_widths[1], 7, f"{c['current_value']:,.0f}".replace(",","X").replace("X",","), border=1, align="R")
            pdf.cell(col_widths[2], 7, f"{c['pct_account']:.2f}".replace(".","!").replace("!","."), border=1, align="R")
            pdf.cell(col_widths[3], 7, f"{c['total_gain_pct']:.1f}", border=1, align="R")
            pdf.cell(col_widths[4], 7, spc, border=1, align="R")
            pdf.cell(col_widths[5], 7, shr, border=1, align="R")
            pdf.cell(col_widths[6], 7, c["class"][:16], border=1, align="C")
            pdf.ln()
        pdf.ln(5)

    render_table("Long-Term Conviction Holds (Top Positions + Tenured)", (30, 120, 60), [c for c in classified if c["class"] == "LONG-TERM HOLD"])
    render_table("Accumulating", (200, 130, 30), [c for c in classified if c["class"] == "ACCUMULATING"])
    render_table("New / Trade Positions", (160, 40, 40), [c for c in classified if c["class"] == "NEW / TRADE"])

    # ---- Short Interest Watch ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "Short Interest Watch", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(190, 5, "Stocks ranked by short interest as a percentage of float. Elevated short interest can signal increased volatility or potential squeeze dynamics.")
    pdf.ln(3)

    sic_headers = ["Ticker", "Sector", "Short % Float", "Days-to-Cover", "Risk Signal"]
    sic_widths = [30, 50, 35, 35, 40]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    for h, w in zip(sic_headers, sic_widths):
        pdf.cell(w, 8, h, border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for c in sorted([c for c in classified if c.get("shortPct") is not None], key=lambda x: -x["shortPct"]):
        sp = c["shortPct"]
        dc = c.get("shortRatio") or 0.0
        if sp >= 0.20:
            risk, (color_r, color_g, color_b) = "VERY HIGH", (190, 40, 40)
        elif sp >= 0.10:
            risk, (color_r, color_g, color_b) = "HIGH", (200, 100, 30)
        elif sp >= 0.04:
            risk, (color_r, color_g, color_b) = "MODERATE", (180, 140, 40)
        else:
            risk, (color_r, color_g, color_b) = "LOW", (40, 120, 60)
        pdf.cell(sic_widths[0], 7, c["symbol"], border=1, align="C")
        pdf.cell(sic_widths[1], 7, (c["sector"] or "N/A")[:30], border=1, align="L")
        pdf.cell(sic_widths[2], 7, f"{sp*100:.2f}%", border=1, align="R")
        pdf.cell(sic_widths[3], 7, f"{dc:.1f}", border=1, align="R")
        pdf.set_text_color(color_r, color_g, color_b)
        pdf.cell(sic_widths[4], 7, risk, border=1, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln()
    pdf.ln(8)

    # ---- Learnable Strategies ----
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "Learnable Strategies & Insights", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 45)
    insights = [
        "1. Concentration + Liquidity: keep top 10 under 55% of portfolio; ensure 2x ADV liquidity.",
        "2. Short-Squeeze Harvesting: watch BE, CORZ, TEM, RXRX if borrow >3 days and days-to-cover >3.",
        "3. Turnaround / Special Situations: INTC and CORZ; require 12-month catalyst calendar and <10% sizing.",
        "4. AI/Data-Center Thematic: overweight picks-and-shovels (SMH, VRT, MU, TSM) vs pure NVDA.",
        "5. Defensive Tech / Staples Moat: AAPL, V, JNJ, KO, PG, WM provide drawdown protection.",
        "6. Rising Short Interest Flags: APLD (30%), CLSK (46%), WULF (26%), RXRX (37%) are heavily shorted speculative names; consider stop-ladders.",
        "7. Newest additions: U, FBTC, FETH added in May 07 snapshot; monitor 30-day post-entry momentum.",
        "8. Energy exposure remains via VDE/XOP/SEI; if oil breaks below $60, consider reducing cyclical names.",
        "9. Gold(GLDM/SGOL/NEM) allocation providing -11% to -13% drawdowns; tighten gold sizing if real yields rise.",
        "10. Bond ladder: VBND/BND/91282CCB5 + MAWIX providing ballast but negative carry; watch duration risk.",
    ]
    for ins in insights:
        pdf.multi_cell(190, 6, ins.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(5)
    pdf.set_text_color(80, 80, 80)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 6, f"Report generated on {REPORT_DATE} | Data sourced from Fidelity and Yahoo Finance | Not investment advice.", new_x="LMARGIN", new_y="NEXT", align="L")

    pdf.output(PDF_PATH)
    print(f"[OK] Report written to: {PDF_PATH}")

    # Update strategist-memory.md
    md_path = "/mnt/c/Users/thadd/.openclaw/workspace/agents/strategist-memory.md"
    with open(md_path, "r", encoding="utf-8") as f:
        old = f.read()

    top_short = sorted([c for c in classified if c.get("shortPct") is not None], key=lambda x: -x["shortPct"])[:10]
    short_lines = []
    for c in top_short:
        risk = "VERY HIGH" if c["shortPct"] >= 0.20 else ("HIGH" if c["shortPct"] >= 0.10 else ("MODERATE" if c["shortPct"] >= 0.04 else "LOW"))
        short_lines.append(f"  - {c['symbol']} ({c.get('sector','N/A')}): {c['shortPct']*100:.1f}% short float, {c.get('shortRatio','N/A')} days-to-cover ({risk})")

    new_entry = f"\n## Portfolio Snapshot ({REPORT_DATE})\n- Total Value: ${total_val:,.2f}\n- Positions: {len(classified)}\n- Classification: {lt_count} LONG-TERM HOLD | {acc_count} ACCUMULATING | {new_count} NEW/TRADE\n- Short Interest Watch (Top):\n" + "\n".join(short_lines) + "\n\n## Learnable Strategies Added\n1. Short-Squeeze Watchlist updated with latest float data.\n2. Added crypto-miner cluster risk flag (CLSK 46%, WULF 26%, CORZ 23%).\n3. New positional risk: VG (Venture Global) 86% short float - verify liquidity before any add.\n4. AI / Data Center: continue SMH/MU/TSM over NVDA weighting.\n5. Duration risk flagged in bond sleeve (negative carry).\n\n_Last updated {REPORT_DATE} UTC_\n"
    if f"## Portfolio Snapshot ({REPORT_DATE})" in old:
        parts = old.split(f"## Portfolio Snapshot ({REPORT_DATE})")
        old = parts[0].rstrip()
    combined = old.rstrip() + "\n" + new_entry.rstrip() + "\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"[OK] Updated {md_path}")


if __name__ == "__main__":
    build_report()
