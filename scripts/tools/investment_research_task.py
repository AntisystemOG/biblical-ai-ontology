#!/usr/bin/env python3
"""
Investment Research Task - Run on idle PC
Analyzes $5k investment options for 1-year timeline with mitigated risk
Uses local Ollama Mistral for analysis
"""

import requests
import json
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
OUTPUT_FILE = Path("research_output/investment_report_2026-02-24.md")

def query_ollama(prompt):
    """Query local Ollama Mistral model"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
            },
            timeout=300
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

def research_investment_options():
    """Main research function"""
    
    print("[Investment Research] Starting analysis...")
    print(f"[{datetime.now().isoformat()}] Using local Ollama Mistral")
    
    # Create output directory
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    
    report = "# Investment Research Report - $5k, 1-Year Timeline\n\n"
    report += f"**Generated:** {datetime.now().isoformat()}\n"
    report += f"**Timeline:** 1 year\n"
    report += f"**Investment Amount:** $5,000\n"
    report += f"**Risk Tolerance:** Mitigated/Conservative\n\n"
    
    # Research Section 1: Treasury Options
    print("[1/5] Researching Treasury bills & notes...")
    prompt1 = """
    Analyze 1-year US Treasury bills and Treasury notes as an investment option for someone investing $5,000 
    for exactly 1 year. Include:
    - Current rates (as of Feb 2026)
    - Expected return
    - Risk level (very low)
    - Liquidity
    - Tax implications
    - Pros and cons
    - How to purchase
    Be specific and practical. Keep response under 500 words.
    """
    treasury_analysis = query_ollama(prompt1)
    report += f"## Option 1: Treasury Bills & Notes\n\n{treasury_analysis}\n\n"
    
    # Research Section 2: CDs & HYSA
    print("[2/5] Researching CDs and high-yield savings...")
    prompt2 = """
    Analyze 1-year Certificates of Deposit (CDs) and high-yield savings accounts for a $5,000 investment 
    over 1 year. Include:
    - Current rates available (Feb 2026 estimates)
    - Expected return
    - FDIC insurance protection
    - Liquidity and penalties
    - Best institutions for these products
    - Pros and cons
    - Tax treatment
    Keep practical and specific. Under 400 words.
    """
    cd_analysis = query_ollama(prompt2)
    report += f"## Option 2: CDs & High-Yield Savings\n\n{cd_analysis}\n\n"
    
    # Research Section 3: Bond Funds
    print("[3/5] Researching short-term bond funds...")
    prompt3 = """
    Analyze short-term bond ETFs and mutual funds for a 1-year investment horizon with $5,000. Include:
    - Examples: BND, BSV, VGSH, SCHZ (or similar)
    - Expected yield/return
    - Interest rate risk (how rates affect value)
    - Liquidity
    - Expense ratios
    - Tax efficiency
    - Pros/cons vs Treasury and CDs
    - Risk level assessment
    Under 400 words, be practical.
    """
    bond_analysis = query_ollama(prompt3)
    report += f"## Option 3: Short-Term Bond Funds\n\n{bond_analysis}\n\n"
    
    # Research Section 4: Dividend ETFs
    print("[4/5] Researching low-volatility dividend ETFs...")
    prompt4 = """
    Analyze low-volatility dividend-focused ETFs for someone investing $5,000 over 1 year. 
    Consider:
    - Examples: VYM, DGRO, SCHD (or similar)
    - Expected dividend yield
    - Capital appreciation potential
    - Volatility/risk (historical)
    - Liquidity
    - Tax treatment (qualified dividends)
    - Best for 1-year horizon?
    - Pros/cons
    Be specific. Under 400 words.
    """
    dividend_analysis = query_ollama(prompt4)
    report += f"## Option 4: Low-Volatility Dividend ETFs\n\n{dividend_analysis}\n\n"
    
    # Research Section 5: Risk Mitigation & Ranking
    print("[5/5] Compiling recommendation & risk mitigation...")
    prompt5 = """
    You are a financial advisor analyzing investment options for someone with $5,000 and a 1-year horizon 
    who wants risk mitigated. Based on Treasury bills, CDs, bond funds, and dividend ETFs:
    
    1. Rank these 5 options from SAFEST to HIGHEST RETURN (with acceptable 1-year risk)
    2. For each, explain the risk mitigation at play
    3. What's the optimal allocation if splitting $5k across multiple options?
    4. What are the key risks to watch for each?
    5. What's the SINGLE BEST choice for maximum return with minimal risk?
    
    Give specific recommendations. Under 500 words, make it actionable.
    """
    recommendation = query_ollama(prompt5)
    report += f"## Recommendations & Rankings\n\n{recommendation}\n\n"
    
    # Final summary
    report += f"## Summary\n\n"
    report += f"**Analysis Date:** {datetime.now().isoformat()}\n"
    report += f"**Model Used:** Ollama Mistral (local)\n"
    report += f"**Status:** Ready for review\n\n"
    report += f"*Report prepared by Spock for Thad*\n"
    
    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        f.write(report)
    
    print(f"[✓] Research complete. Report saved to {OUTPUT_FILE}")
    print(f"[✓] Ready for delivery at 3:30 PM")
    
    return report

if __name__ == "__main__":
    research_investment_options()
