import urllib.request
import json

prompt = """Analyze these stock positions as of March 12, 2026.

Account total: $141,537.74
Positions:
- BE (Bloom Energy): 16.09%
- Cash (Money Market): 15.54%
- XOM (Exxon Mobil): 10.81%
- VST (Vistra Corp): 10.79%
- VDE (Vanguard Energy ETF): 10.79%
- XOP (SPDR Oil & Gas ETF): 8.66%
- CORZ (Core Scientific): 8.31%
- CVX (Chevron): 7.32%
- SHEL (Shell PLC): 7.17%
- INTC (Intel): 7.08%
- COP (ConocoPhillips): 5.17%
- VBND (Bond ETF): 3.53%
- RIOT (Riot Platforms): 2.53%
- APLD (Applied Digital): 0.85%
- SGOL (Gold Trust): 0.85%

Daily gain was +$2,376.84 (1.71%). Note pending activity of -$18,000.

Provide: Summary of daily changes, key risks (sector concentration, energy volatility), and insights. Keep under 300 words. Plain text only, no markdown formatting."""

data = json.dumps({
    "model": "mistral",
    "prompt": prompt,
    "stream": False
}).encode()

req = urllib.request.Request(
    "http://localhost:11434/api/generate",
    data=data,
    headers={"Content-Type": "application/json"}
)

r = urllib.request.urlopen(req, timeout=90)
result = json.loads(r.read().decode())
print(result.get("response", "No response"))
