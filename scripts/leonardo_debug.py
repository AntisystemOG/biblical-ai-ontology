"""
Debug Leonardo API - Check actual response structure
"""

import requests
import json
import time
from pathlib import Path

# Load config
config_path = Path(__file__).parent.parent / "leonardo_config.json"
with open(config_path) as f:
    config = json.load(f)

API_KEY = config["api_key"]
BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Use the generation ID from the previous test
generation_id = "c6702594-21fb-41f1-be92-e7b1b107237c"

print(f"Checking generation: {generation_id}")
print()

response = requests.get(
    f"{BASE_URL}/generations/{generation_id}",
    headers=headers
)

print(f"Status Code: {response.status_code}")
print()
print("Full Response:")
print(json.dumps(response.json(), indent=2))
