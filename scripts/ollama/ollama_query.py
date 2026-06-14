import requests
import json

with open('temp_stock_analysis.txt', 'r') as f:
    prompt = f.read()

payload = {
    "model": "mistral",
    "prompt": prompt,
    "stream": False
}

try:
    r = requests.post('http://localhost:11434/api/generate', json=payload, timeout=60)
    result = r.json()
    print(result.get('response', result))
except Exception as e:
    print(f"Error: {e}")
