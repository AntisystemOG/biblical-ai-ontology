"""
Quick Leonardo API Test - Generate ONE image
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

print("Leonardo.ai API Test")
print("="*50)
print(f"API Key: {API_KEY[:20]}...")
print()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Simple test prompt
prompt = "A minimalist icon of a hand making the Vulcan salute, navy blue and gold colors, clean vector illustration"

print(f"Prompt: {prompt}")
print()

# Create generation request
payload = {
    "prompt": prompt,
    "width": 512,
    "height": 512,
    "num_images": 1
}

print("Submitting generation request...")
response = requests.post(
    f"{BASE_URL}/generations",
    headers=headers,
    json=payload
)

print(f"Response status: {response.status_code}")

if response.status_code != 200:
    print(f"ERROR: {response.text}")
    exit(1)

generation_data = response.json()
print(f"Response: {json.dumps(generation_data, indent=2)}")

# Get generation ID
if 'sdGenerationJob' in generation_data:
    generation_id = generation_data['sdGenerationJob'].get('generationId')
else:
    generation_id = generation_data.get('sdGenerationId')

if not generation_id:
    print("ERROR: No generation ID returned")
    exit(1)

print(f"\nGeneration ID: {generation_id}")
print("Waiting for completion...")

# Poll for completion
start_time = time.time()
timeout = 180  # 3 minutes

while time.time() - start_time < timeout:
    response = requests.get(
        f"{BASE_URL}/generations/{generation_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error checking status: {response.status_code}")
        break
    
    status_data = response.json()
    status = status_data.get("status")
    
    print(f"Status: {status}")
    
    if status == "COMPLETE":
        print("\nGeneration complete!")
        images = status_data.get("generated_images", [])
        if images:
            url = images[0].get("url")
            print(f"Image URL: {url}")
            
            # Download
            print("\nDownloading...")
            img_response = requests.get(url)
            save_path = Path(__file__).parent.parent / "spock_profile_test.png"
            with open(save_path, 'wb') as f:
                f.write(img_response.content)
            
            print(f"Saved to: {save_path}")
            print("\nSUCCESS! Check the image!")
        break
    elif status == "FAILED":
        print("Generation FAILED")
        print(status_data)
        break
    
    time.sleep(5)
else:
    print("Timeout!")
