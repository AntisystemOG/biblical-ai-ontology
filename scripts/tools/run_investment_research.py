#!/usr/bin/env python3
"""
Investment Research - Simplified version
Queries Ollama Mistral for $5k, 1-year investment analysis
"""

import requests
import json
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
OUTPUT_FILE = Path("memory/investment_report_2026-02-24.txt")

def query_ollama(prompt):
    """Query local Ollama Mistral"""
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
            return f"Ollama error: {response.status_code}"
    except Exception as e:
        return f"Connection failed: {str(e)}"

def research():
    """Run investment research"""
    
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    
    print("[Investment Research] Starting...")
    
    prompt = """
    Analyze investment options for $5,000 with a 1-year timeline. Goal: risk-mitigated returns.
    
    Consider:
    1. 1-year Treasury bills/notes
    2. CDs (Certificates of Deposit) - 1 year
    3. High-yield savings accounts
    4. Short-term bond funds (BSV, VGSH, etc.)
    5. Low-volatility dividend ETFs (SCHD, VYM, etc.)
    
    For each option, provide:
    - Expected annual return
    - Risk level
    - Liquidity
    - Tax implications
    - Suitability for 1-year horizon
    
    Then rank them 1-5, safest to best risk-adjusted return.
    Finally, recommend the single best option for someone who values risk mitigation.
    
    Be specific and actionable. This is for real decision-making.
    """
    
    print("[1/1] Querying Ollama Mistral...")
    result = query_ollama(prompt)
    
    report = f"Investment Research Report\n"
    report += f"Generated: {datetime.now().isoformat()}\n"
    report += f"Timeline: 1 year\n"
    report += f"Amount: $5,000\n"
    report += f"Risk Tolerance: Mitigated\n"
    report += f"\n{'='*60}\n\n"
    report += result
    report += f"\n\n{'='*60}\n"
    report += f"Report ready for delivery.\n"
    
    # Save with explicit encoding
    with open(OUTPUT_FILE, 'w', encoding='utf-8', errors='replace') as f:
        f.write(report)
    
    print(f"[OK] Report saved: {OUTPUT_FILE}")
    print("[OK] Ready for 3:30 PM delivery")

if __name__ == "__main__":
    research()
