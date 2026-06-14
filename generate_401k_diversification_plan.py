#!/usr/bin/env python3
"""
401k Diversification Plan Generator
Creates a professional PDF report with diversification recommendations.
"""

from fpdf import FPDF
from datetime import datetime
import os

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Add fonts - remove deprecated uni parameter
        self.add_font("SegoeUI", "", "C:/Windows/Fonts/segoeui.ttf")
        self.add_font("SegoeUI", "B", "C:/Windows/Fonts/segoeuib.ttf")
        self.add_font("SegoeUI", "I", "C:/Windows/Fonts/segoeuii.ttf")
        
    def header(self):
        if self.page_no() > 1:
            self.set_font("SegoeUI", "", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, "401k Diversification Plan - May 2026", 0, new_x="LMARGIN", new_y="TOP", align="C")
            self.ln(5)
            # Line under header
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font("SegoeUI", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        
    def chapter_title(self, title):
        self.set_font("SegoeUI", "B", 16)
        self.set_text_color(0, 51, 102)  # Dark blue
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(2)
        # Line under title
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        
    def chapter_subtitle(self, subtitle):
        self.set_font("SegoeUI", "B", 12)
        self.set_text_color(0, 102, 153)
        self.cell(0, 8, subtitle, new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(1)
        
    def body_text(self, text, bold=False):
        self.set_font("SegoeUI", "B" if bold else "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(2)
        
    def bullet_point(self, text, indent=0):
        self.set_x(10 + indent)
        self.set_font("SegoeUI", "", 10)
        self.set_text_color(50, 50, 50)
        # Use a fixed width for the bullet and content
        bullet = "- "
        self.cell(5, 6, bullet)
        # Calculate remaining width for text
        remaining_width = 190 - indent - 5
        self.multi_cell(remaining_width, 6, text)
        
    def warning_box(self, text):
        # Light yellow background box
        self.set_fill_color(255, 248, 220)
        self.set_draw_color(218, 165, 32)
        self.set_text_color(139, 69, 19)
        self.set_font("SegoeUI", "B", 10)
        self.cell(0, 8, " WARNING", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("SegoeUI", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(190, 6, text, border=1, fill=True)
        self.ln(5)
        
    def info_box(self, title, text):
        # Light blue background
        self.set_fill_color(230, 242, 255)
        self.set_draw_color(70, 130, 180)
        self.set_text_color(0, 51, 102)
        self.set_font("SegoeUI", "B", 10)
        self.cell(0, 8, f" {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(50, 50, 50)
        self.set_font("SegoeUI", "", 10)
        self.multi_cell(190, 6, text, border=1, fill=True)
        self.ln(5)
        
    def asset_card(self, number, ticker, name, expense, wins, loses, rationale):
        # Asset card with header
        self.set_fill_color(240, 248, 255)
        self.set_draw_color(0, 102, 204)
        self.set_text_color(0, 51, 102)
        self.set_font("SegoeUI", "B", 12)
        self.cell(0, 10, f"  {number}. {ticker} - {name}", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        # Content
        self.set_text_color(50, 50, 50)
        self.set_font("SegoeUI", "", 9)
        
        # Expense ratio
        self.set_font("SegoeUI", "B", 9)
        self.cell(35, 6, "Expense Ratio:")
        self.set_font("SegoeUI", "", 9)
        self.cell(0, 6, expense, new_x="LMARGIN", new_y="NEXT")
        
        # When it wins
        self.set_font("SegoeUI", "B", 9)
        self.cell(35, 6, "When it WINS:")
        self.set_text_color(0, 128, 0)
        self.set_font("SegoeUI", "", 9)
        self.multi_cell(155, 6, wins)
        self.set_text_color(50, 50, 50)
        
        # When it loses
        self.set_font("SegoeUI", "B", 9)
        self.cell(35, 6, "When it LOSES:")
        self.set_text_color(178, 34, 34)
        self.set_font("SegoeUI", "", 9)
        self.multi_cell(155, 6, loses)
        self.set_text_color(50, 50, 50)
        
        # Rationale
        self.set_font("SegoeUI", "B", 9)
        self.cell(0, 6, "Why for Thad:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("SegoeUI", "", 9)
        self.multi_cell(190, 5, rationale)
        self.ln(2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)


def create_diversification_plan():
    pdf = PDF()
    pdf.add_page()
    
    # ===== TITLE PAGE =====
    pdf.set_y(60)
    pdf.set_font("SegoeUI", "B", 28)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, "401k Diversification Plan", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("SegoeUI", "", 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Strategic Asset Allocation for Uncorrelated Returns", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("SegoeUI", "B", 14)
    pdf.set_text_color(0, 102, 153)
    pdf.cell(0, 10, "Prepared for: Thad Thompson", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("SegoeUI", "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "May 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("SegoeUI", "I", 10)
    pdf.cell(0, 8, "Five assets. Five market regimes. One resilient portfolio.", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # ===== EXECUTIVE SUMMARY =====
    pdf.add_page()
    pdf.chapter_title("Executive Summary")
    
    pdf.body_text(
        "This diversification plan is designed to address the concentration risks in your current portfolio "
        "while building a 401k allocation that thrives across different market regimes. The goal is not "
        "just 'more stocks' - it's uncorrelated return streams that respond differently to economic stress."
    )
    
    pdf.info_box(
        "Current Portfolio Snapshot",
        "Total Assets: ~$380,000 across BrokerageLink (~$181k), Roth IRA (~$10k), and 401k (~$188k). "
        "Current 401k is primarily in target-date funds (RFHTX) with limited diversification across market regimes."
    )
    
    pdf.chapter_subtitle("The Problem: Concentration Risk")
    pdf.body_text(
        "Your BrokerageLink account shows significant concentration in three areas:"
    )
    pdf.bullet_point("Energy sector: ~40% exposure through multiple stocks and ETFs (XOM, CVX, COP, SHEL, VDE, XOP, etc.)")
    pdf.bullet_point("Individual stock risk: BE (Bloom Energy) is a ~$18k position, down 18% from cost basis")
    pdf.bullet_point("Crypto correlation: ~10% in crypto-adjacent stocks (CORZ, RIOT, COIN, etc.)")
    pdf.ln(3)
    
    pdf.warning_box(
        "Your current 401k (LAITRAM LLC account) holds ~$188k in target-date fund RFHTX and basic index funds. "
        "While diversified by age, it lacks exposure to inflation hedges, international diversification, and alternative strategies "
        "that could protect against specific market stresses like stagflation or rising rates."
    )
    
    pdf.chapter_subtitle("The Solution: Five-Asset Framework")
    pdf.body_text(
        "We recommend restructuring your 401k allocation around five core positions, each optimized "
        "for a different economic environment. These are not 'better stocks' - they are different return streams "
        "that move independently under various market conditions."
    )
    
    # ===== CURRENT PORTFOLIO ANALYSIS =====
    pdf.add_page()
    pdf.chapter_title("Current Portfolio Analysis")
    
    pdf.chapter_subtitle("401k Holdings (LAITRAM LLC Account)")
    pdf.body_text("Current allocation as of March 2026:")
    
    # Create a simple table
    pdf.set_font("SegoeUI", "B", 9)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 8, "Fund", border=1, fill=True)
    pdf.cell(80, 8, "Description", border=1, fill=True)
    pdf.cell(30, 8, "Allocation", border=1, fill=True, align="R")
    pdf.cell(40, 8, "Risk", border=1, fill=True, align="C")
    pdf.ln()
    
    holdings = [
        ("RFHTX", "Fidelity Target 2045", "~37%", "Age-based"),
        ("MAWIX", "Bond Institutional", "~38%", "Interest rate"),
        ("FXAIX", "500 Index Fund", "~8%", "US equity"),
        ("FXNAX", "US Bond Index", "~9%", "Interest rate"),
        ("FDIVX", "International", "~4%", "Currency/EM"),
        ("PRRIX", "Real Return (TIPS)", "~4%", "Inflation"),
    ]
    
    pdf.set_font("SegoeUI", "", 9)
    for i, (fund, desc, alloc, risk) in enumerate(holdings):
        fill = i % 2 == 0
        pdf.cell(40, 7, fund, border=1, fill=fill)
        pdf.cell(80, 7, desc, border=1, fill=fill)
        pdf.cell(30, 7, alloc, border=1, fill=fill, align="R")
        pdf.cell(40, 7, risk, border=1, fill=fill, align="C")
        pdf.ln()
    
    pdf.ln(5)
    
    pdf.chapter_subtitle("Concentration Analysis")
    pdf.warning_box(
        "HIGH CONCENTRATION RISKS IDENTIFIED:\n\n"
        "1. Target-date fund (RFHTX) dominates at 37% - glides toward bonds but offers limited inflation protection\n"
        "2. Bond funds (MAWIX + FXNAX) total ~47% - highly vulnerable to rising rate environments\n"
        "3. Limited international diversification (4%) - misses growth opportunities outside US\n"
        "4. No commodity/REIT/alternative exposure - no hedge against inflation or market crashes"
    )
    
    pdf.chapter_subtitle("Correlation with Existing Holdings")
    pdf.body_text(
        "Your BrokerageLink holdings are heavily energy-weighted (~40%). The 401k's S&P 500 exposure "
        "(FXAIX) correlates highly with energy stocks during risk-off events. When oil crashes, both energy "
        "stocks AND the broad market often decline together. This plan addresses that correlation risk."
    )
    
    # ===== THE FIVE ASSETS =====
    pdf.add_page()
    pdf.chapter_title("The Five Diversification Assets")
    pdf.body_text(
        "Each asset below is selected for how it responds to a specific market regime. "
        "Together, they create a portfolio that can weather multiple economic scenarios."
    )
    pdf.ln(3)
    
    # Asset 1: VTI (Total Stock Market)
    pdf.asset_card(
        1, "VTI", "Vanguard Total Stock Market ETF",
        "0.03% (ultra-low cost)",
        "Growth environments, economic expansion, risk-on sentiment, tech earnings growth",
        "Recessions, bear markets, sector rotations away from growth stocks",
        "Your 401k already has US equity via FXAIX, but VTI offers broader diversification "
        "than just the S&P 500. It captures mid-caps and small-caps that often outperform "
        "in early recovery phases. Complements your energy-heavy BrokerageLink by adding "
        "growth sectors (healthcare, tech, consumer discretionary) that move independently."
    )
    
    # Asset 2: VXUS (Total International)
    pdf.asset_card(
        2, "VXUS", "Vanguard Total International Stock ETF",
        "0.08% (low cost)",
        "US dollar weakness, foreign economic outperformance, emerging market growth, commodity demand",
        "US dollar strength, global recession, geopolitical tensions, trade wars",
        "Currently only 4% international in your 401k. VXUS adds developed and emerging markets "
        "(Europe, Japan, China, India) that often move independently from US markets. "
        "Provides currency diversification - when USD falls, international stocks typically rise in USD terms."
    )
    
    # Asset 3: BNDW (Total World Bond)
    pdf.asset_card(
        3, "BNDW", "Vanguard Total World Bond ETF",
        "0.06% (ultra-low cost)",
        "Risk-off environments, flight to safety, economic uncertainty, deflation",
        "Rising interest rates, inflation surprises, credit spread widening",
        "Your 401k already holds bonds (MAWIX, FXNAX), but they're US-only and vulnerable to "
        "rising US rates. BNDW adds international bonds (hedged) providing diversification. "
        "However, consider keeping some allocation to short-duration bonds or TIPS for rate protection."
    )
    
    # Asset 4: VNQ (Real Estate/REITs)
    pdf.asset_card(
        4, "VNQ", "Vanguard Real Estate ETF",
        "0.12% (low cost)",
        "Inflation environments, economic growth, low interest rates, real asset appreciation",
        "Rising interest rates, recession (vacancies rise), commercial real estate stress",
        "Currently ZERO real estate exposure in your 401k. REITs provide: (1) inflation hedge "
        "(rents adjust upward), (2) income (typically 3-4% yields), (3) diversification "
        "(correlation to stocks ~0.6, not 1.0). Complements your energy stocks by adding "
        "real assets that respond to different economic drivers."
    )
    
    # Asset 5: PDBC (Commodities)
    pdf.asset_card(
        5, "PDBC", "Invesco Optimum Yield Diversified Commodity",
        "0.62% (higher cost but justified)",
        "Inflation spikes, commodity supercycles, supply shocks, dollar weakness, geopolitical risk",
        "Deflation, global slowdown, commodity oversupply, strong dollar",
        "ZERO commodity exposure currently. PDBC holds energy, metals, agriculture - "
        "the raw inputs that rise when inflation hits. Energy stocks (your current 40% "
        "exposure) are NOT the same as commodities - when oil prices spike, energy stocks "
        "often underperform the commodity due to cost pressures. PDBC provides direct "
        "inflation protection that your energy stocks cannot."
    )
    
    # ===== ALLOCATION RECOMMENDATIONS =====
    pdf.add_page()
    pdf.chapter_title("Recommended 401k Allocation")
    
    pdf.body_text(
        "Based on your age, risk tolerance, and existing holdings, here's a proposed "
        "reallocation for your LAITRAM 401k (~$188,000):"
    )
    pdf.ln(5)
    
    # Allocation table
    pdf.set_font("SegoeUI", "B", 10)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(50, 10, "Asset", border=1, fill=True)
    pdf.cell(25, 10, "Current", border=1, fill=True, align="C")
    pdf.cell(25, 10, "Target", border=1, fill=True, align="C")
    pdf.cell(30, 10, "Change", border=1, fill=True, align="C")
    pdf.cell(60, 10, "Rationale", border=1, fill=True)
    pdf.ln()
    
    allocations = [
        ("Total US Stock (VTI)", "8%", "25%", "+17%", "Core growth exposure"),
        ("Intl Stock (VXUS)", "4%", "15%", "+11%", "Geographic diversification"),
        ("REITs (VNQ)", "0%", "10%", "+10%", "Real assets, inflation hedge"),
        ("Commodities (PDBC)", "0%", "10%", "+10%", "Direct inflation protection"),
        ("World Bonds (BNDW)", "0%", "15%", "+15%", "Deflation/recession hedge"),
        ("TIPS (keep PRRIX)", "4%", "5%", "+1%", "Inflation-linked safety"),
        ("Target Date (RFHTX)", "37%", "10%", "-27%", "Reduce glide path auto-adjust"),
        ("US Bonds (MAWIX/FXNAX)", "47%", "10%", "-37%", "Cut rate-sensitive duration"),
    ]
    
    pdf.set_font("SegoeUI", "", 9)
    pdf.set_text_color(50, 50, 50)
    for i, (asset, current, target, change, rationale) in enumerate(allocations):
        fill = i % 2 == 0
        pdf.cell(50, 8, asset, border=1, fill=fill)
        pdf.cell(25, 8, current, border=1, fill=fill, align="C")
        pdf.cell(25, 8, target, border=1, fill=fill, align="C")
        
        # Color code the change
        if change.startswith("+"):
            pdf.set_text_color(0, 128, 0)
        elif change.startswith("-"):
            pdf.set_text_color(178, 34, 34)
        pdf.cell(30, 8, change, border=1, fill=fill, align="C")
        pdf.set_text_color(50, 50, 50)
        
        pdf.cell(60, 8, rationale, border=1, fill=fill)
        pdf.ln()
    
    pdf.ln(10)
    
    pdf.info_box(
        "Why This Allocation Works",
        "Growth (35%): VTI + VXUS capture equity upside during expansions\n"
        "Real Assets (20%): VNQ + PDBC provide inflation protection\n"
        "Fixed Income (30%): BNDW + TIPS + reduced US bonds for rate protection\n"
        "Flexibility (15%): Keep some RFHTX for hands-off rebalancing"
    )
    
    # ===== REBALANCING STRATEGY =====
    pdf.add_page()
    pdf.chapter_title("Rebalancing Strategy")
    
    pdf.chapter_subtitle("Phase 1: Immediate (Next 30 Days)")
    pdf.body_text("Priority actions to reduce concentration risk:")
    pdf.bullet_point("Reduce RFHTX from 37% to 20% - sell ~$32,000, redeploy to VTI/VXUS")
    pdf.bullet_point("Trim MAWIX/FXNAX combined from 47% to 25% - reduce rate sensitivity")
    pdf.bullet_point("Initiate positions in VNQ (REITs) and PDBC (commodities) at 5% each")
    pdf.ln(5)
    
    pdf.chapter_subtitle("Phase 2: 60-90 Days")
    pdf.body_text("Complete the transition to target allocation:")
    pdf.bullet_point("Further reduce RFHTX to 10% target")
    pdf.bullet_point("Build VNQ and PDBC to full 10% targets")
    pdf.bullet_point("Increase VXUS to full 15% international exposure")
    pdf.ln(5)
    
    pdf.chapter_subtitle("Rebalancing Rules")
    pdf.body_text("Set automatic rebalancing triggers:")
    pdf.bullet_point("Time-based: Review quarterly, rebalance semi-annually")
    pdf.bullet_point("Threshold-based: Rebalance when any allocation drifts +/-5% from target")
    pdf.bullet_point("Event-based: Rebalance after major market moves (>15% in single quarter)")
    pdf.ln(5)
    
    pdf.warning_box(
        "TAX CONSIDERATIONS:\n\n"
        "This reallocation is within your 401k (tax-deferred), so no immediate tax consequences. "
        "However, if you rebalance taxable accounts (BrokerageLink), be mindful of:\n"
        "- Short-term vs long-term capital gains\n"
        "- Harvest losses from positions like BE (-18%) before year-end\n"
        "- Consider donating appreciated shares to charity instead of selling"
    )
    
    # ===== CORRELATION MATRIX CONCEPT =====
    pdf.add_page()
    pdf.chapter_title("Correlation Matrix Concept")
    
    pdf.body_text(
        "Understanding how these assets behave relative to each other is critical. "
        "The matrix below shows approximate correlation coefficients (1.0 = perfect correlation, "
        "0.0 = no correlation, -1.0 = perfect inverse)."
    )
    pdf.ln(5)
    
    # Correlation table header
    pdf.set_font("SegoeUI", "B", 8)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(25, 8, "", border=1, fill=True, align="C")
    assets_short = ["VTI", "VXUS", "BNDW", "VNQ", "PDBC"]
    for asset in assets_short:
        pdf.cell(25, 8, asset, border=1, fill=True, align="C")
    pdf.ln()
    
    # Correlation data (simplified)
    correlations = [
        ("VTI", ["1.00", "0.85", "0.35", "0.60", "0.40"]),
        ("VXUS", ["0.85", "1.00", "0.30", "0.55", "0.35"]),
        ("BNDW", ["0.35", "0.30", "1.00", "0.45", "-0.10"]),
        ("VNQ", ["0.60", "0.55", "0.45", "1.00", "0.20"]),
        ("PDBC", ["0.40", "0.35", "-0.10", "0.20", "1.00"]),
    ]
    
    pdf.set_font("SegoeUI", "", 8)
    pdf.set_text_color(50, 50, 50)
    for i, (row_asset, row_vals) in enumerate(correlations):
        pdf.set_font("SegoeUI", "B", 8)
        pdf.set_fill_color(200, 220, 240)
        pdf.cell(25, 8, row_asset, border=1, fill=True, align="C")
        pdf.set_font("SegoeUI", "", 8)
        pdf.set_fill_color(255, 255, 255)
        for j, val in enumerate(row_vals):
            fill = i == j  # Diagonal
            if fill:
                pdf.set_fill_color(200, 220, 240)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.cell(25, 8, val, border=1, fill=fill, align="C")
        pdf.ln()
    
    pdf.ln(10)
    
    pdf.chapter_subtitle("Key Insights")
    pdf.body_text("What the correlations tell us:")
    pdf.bullet_point("PDBC (commodities) shows the LOWEST correlation to other assets - strongest diversifier")
    pdf.bullet_point("BNDW (bonds) is negatively correlated to commodities - classic hedge pairing")
    pdf.bullet_point("VTI and VXUS are highly correlated (0.85) - but that's fine, they're both 'growth' assets")
    pdf.bullet_point("VNQ (REITs) sits in the middle - provides partial diversification from pure equities")
    pdf.ln(5)
    
    pdf.info_box(
        "The Diversification Math",
        "A portfolio of five assets with average correlation of 0.40 has approximately:\n"
        "- 35% lower volatility than any single asset\n"
        "- Similar expected returns (long-term)\n"
        "- Better risk-adjusted returns (higher Sharpe ratio)\n\n"
        "This is the 'free lunch' of diversification - reduced risk without reduced returns."
    )
    
    # ===== MARKET REGIMES =====
    pdf.add_page()
    pdf.chapter_title("How This Portfolio Handles Market Regimes")
    
    regimes = [
        ("Growth/Risk-On", 
         "Economic expansion, low rates, strong earnings",
         "VTI leads, VXUS participates, VNQ benefits from low rates",
         "PDBC may lag (no inflation pressure), BNDW may lag (rates rising)"),
        
        ("Recession/Deflation", 
         "Economic contraction, falling rates, risk-off",
         "BNDW surges (flight to safety), PDBC may rise (dollar weakness)",
         "VTI/VXUS decline (earnings compression), VNQ hurt (vacancies rise)"),
        
        ("Inflation/Commodity Boom", 
         "Rising prices, supply constraints, rate hikes",
         "PDBC and VNQ excel (real assets), VXUS may benefit (currency hedge)",
         "BNDW hurt (rates rising), VTI mixed (some sectors benefit)"),
        
        ("Rising Rates", 
         "Fed tightening, economic slowing",
         "Short-duration bonds, PDBC may benefit",
         "VNQ hurt (REITs rate-sensitive), VTI/VXUS pressured (higher discount rates)"),
        
        ("Market Volatility/Crisis", 
         "Black swan events, liquidity crunch",
         "BNDW provides ballast, PDBC may spike (safe haven)",
         "All risk assets decline initially - but diversification reduces drawdown"),
    ]
    
    for regime, desc, winners, losers in regimes:
        pdf.set_font("SegoeUI", "B", 11)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, regime, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("SegoeUI", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, desc, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("SegoeUI", "", 9)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(20, 6, "WINS:")
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(170, 6, winners)
        pdf.set_text_color(178, 34, 34)
        pdf.cell(20, 6, "LOSES:")
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(170, 6, losers)
        pdf.ln(3)
    
    # ===== IMPLEMENTATION CHECKLIST =====
    pdf.add_page()
    pdf.chapter_title("Implementation Checklist")
    
    pdf.chapter_subtitle("Step 1: Review 401k Provider Options")
    pdf.bullet_point("Confirm VTI, VXUS, VNQ, PDBC, BNDW are available in your LAITRAM 401k")
    pdf.bullet_point("If not available as ETFs, look for equivalent mutual funds:")
    pdf.bullet_point("- VTI -> VTSAX (Vanguard Total Stock)", indent=5)
    pdf.bullet_point("- VXUS -> VTIAX (Vanguard Intl)", indent=5)
    pdf.bullet_point("- VNQ -> VGSLX (Vanguard REIT)", indent=5)
    pdf.bullet_point("- PDBC -> PCRIX (PIMCO Commodity)", indent=5)
    pdf.bullet_point("- BNDW -> VTABX (Vanguard Intl Bond)", indent=5)
    pdf.ln(5)
    
    pdf.chapter_subtitle("Step 2: Execute Trades")
    pdf.bullet_point("Log into Fidelity NetBenefits (401k portal)")
    pdf.bullet_point("Initiate exchange from RFHTX -> VTI/VXUS (Phase 1)")
    pdf.bullet_point("Reduce MAWIX/FXNAX positions gradually")
    pdf.bullet_point("Set up automatic investments to maintain target allocation")
    pdf.ln(5)
    
    pdf.chapter_subtitle("Step 3: Set Monitoring")
    pdf.bullet_point("Add tickers to your watchlist (VST, Yahoo Finance, etc.)")
    pdf.bullet_point("Set calendar reminder: Quarterly review (Jan/Apr/Jul/Oct)")
    pdf.bullet_point("Set calendar reminder: Semi-annual rebalance (Jan/Jul)")
    pdf.ln(5)
    
    pdf.chapter_subtitle("Step 4: Coordinate with BrokerageLink")
    pdf.warning_box(
        "Your BrokerageLink (~$181k) remains heavily energy-weighted. Consider:\n\n"
        "1. Gradually trimming individual energy stocks (BE, CORZ especially)\n"
        "2. Adding healthcare/defensive positions to complement 401k growth allocation\n"
        "3. Maintaining some energy via VDE (broad ETF) vs individual stocks\n"
        "4. The 401k diversification reduces need to over-diversify BrokerageLink - "
        "let each account serve its purpose"
    )
    
    # ===== FINAL NOTES =====
    pdf.add_page()
    pdf.chapter_title("Final Notes & Disclaimers")
    
    pdf.body_text(
        "This diversification plan is designed to reduce concentration risk and provide "
        "exposure to multiple market regimes. However, all investments carry risk, including "
        "loss of principal. Past performance does not guarantee future results."
    )
    pdf.ln(5)
    
    pdf.chapter_subtitle("Monitoring & Adjustment")
    pdf.body_text(
        "This is a starting point, not a set-and-forget strategy. Review annually and adjust for:\n"
        "- Changes in risk tolerance\n"
        "- Major life events (retirement approaching, etc.)\n"
        "- Significant market regime shifts (secular inflation, etc.)\n"
        "- Fund availability changes in your 401k\n"
        "- Expense ratio changes (always favor lower-cost alternatives)"
    )
    pdf.ln(5)
    
    pdf.chapter_subtitle("Questions to Ask Your Plan Administrator")
    pdf.bullet_point("Are commission-free ETF trades available?")
    pdf.bullet_point("Is automatic rebalancing available?")
    pdf.bullet_point("Can I set up automatic investment into specific funds?")
    pdf.bullet_point("What are the fees for the target-date fund vs individual funds?")
    pdf.ln(10)
    
    pdf.set_font("SegoeUI", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Report generated: May 6, 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Prepared by Spock", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Save PDF
    output_path = "C:/Users/thadd/OneDrive/Desktop/Spocks Reports/diversification/2026-05-06_401k_diversification_plan.pdf"
    pdf.output(output_path)
    print(f"PDF generated successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    create_diversification_plan()
