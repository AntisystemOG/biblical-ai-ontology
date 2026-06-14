import urllib.request
import json

prompt = """Analyze stock portfolio as of April 3, 2026. From March 12 positions:
Account $141,537. BE $22,776 (16%), Cash $21,999 (15.5%), XOM $15,294 (10.8%), VST $15,273 (10.8%), VDE $15,266 (10.8%), XOP $12,250 (8.7%), CORZ $11,764 (8.3%), CVX $10,362 (7.3%), SHEL $10,146 (7.2%), INTC $10,018 (7.1%), COP $7,322 (5.2%), VBND $5,000 (3.5%), RIOT $3,587 (2.5%), APLD $1,205 (0.85%), SGOL $1,202 (0.85%). Energy = 55%.

Current data: BE $135.63 (April 2 +2.4%), VST ~$146 (was $166), INTC ~$43 (52wk lows), CVX $199 (+0.79%). S&P 500 -1.7% to -2.1% this week.

Write 250-word max plain text report with: 1) Daily changes summary, 2) Key risks (concentration, BE/VST drawdown ~20% from highs, INTC), 3) Insights. Be direct."""

data = {
    "model": "mistral",
    "messages": [{"role": "user", "content": prompt}],
    "stream": False
}

req = urllib.request.Request(
    "http://localhost:11434/api/chat",
    data=json.dumps(data).encode(),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
    print(result["message"]["content"])
