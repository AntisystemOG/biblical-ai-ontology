"""
Leonardo.ai Image Generation Integration
Generates images using Leonardo.ai API
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

def generate_image(prompt, width=512, height=512, num_images=1, name="image"):
    """
    Generate image(s) using Leonardo.ai API
    """
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Create generation request
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_images": num_images
    }
    
    print(f"Generating: {name}")
    print(f"Prompt: {prompt[:80]}...")
    
    # Submit generation request
    response = requests.post(
        f"{BASE_URL}/generations",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        print(f"Error submitting: {response.status_code}")
        print(response.text)
        return None
    
    generation_data = response.json()
    
    # Get generation ID
    if 'sdGenerationJob' in generation_data:
        generation_id = generation_data['sdGenerationJob'].get('generationId')
    else:
        generation_id = generation_data.get('sdGenerationId')
    
    if not generation_id:
        print("No generation ID returned")
        return None
    
    print(f"Generation ID: {generation_id}")
    print("Waiting for completion...")
    
    # Poll for completion
    return wait_for_generation(generation_id, headers, name)

def wait_for_generation(generation_id, headers, name, timeout=180):
    """Wait for generation to complete"""
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(
            f"{BASE_URL}/generations/{generation_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Error checking status: {response.status_code}")
            return None
        
        status_data = response.json()
        
        # Handle nested response structure
        if 'generations_by_pk' in status_data:
            status = status_data['generations_by_pk'].get('status')
        else:
            status = status_data.get('status')
        
        print(f"  Status: {status}")
        
        if status == "COMPLETE":
            print(f"  {name} complete!")
            # Extract image URLs
            if 'generations_by_pk' in status_data:
                images = status_data['generations_by_pk'].get('generated_images', [])
            else:
                images = status_data.get('generated_images', [])
            
            urls = [img.get('url') for img in images if img.get('url')]
            return urls
        elif status == "FAILED":
            print(f"  {name} FAILED")
            print(status_data)
            return None
        
        time.sleep(5)
    
    print("Timeout waiting for generation")
    return None

def download_image(url, save_path):
    """Download image from URL to local file"""
    
    print(f"Downloading: {save_path.name}")
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Saved: {save_path}")
        return True
    else:
        print(f"Download failed: {response.status_code}")
        return False

def generate_profile_pics():
    """Generate 4 Spock profile picture variations"""
    
    # Base prompt
    base_prompt = """A minimalist icon of a hand making the Vulcan salute, 
    navy blue and gold colors, clean vector illustration, professional profile picture, 
    welcoming and trustworthy, works at small sizes, no text"""
    
    # Variations
    variations = [
        {
            "name": "spock_profile_v1_clean",
            "prompt": base_prompt + ", simple clean design, minimal shading, solid colors"
        },
        {
            "name": "spock_profile_v2_starry",
            "prompt": base_prompt + ", space background with stars, cosmic, navy purple gradient"
        },
        {
            "name": "spock_profile_v3_glow",
            "prompt": base_prompt + ", warm golden glow, amber highlights, hopeful, enlightening"
        },
        {
            "name": "spock_profile_v4_modern",
            "prompt": base_prompt + ", ultra modern flat design, bold shapes, tech startup style"
        }
    ]
    
    output_dir = Path(__file__).parent.parent
    print(f"Output directory: {output_dir}")
    print()
    
    results = []
    
    for i, var in enumerate(variations, 1):
        print(f"\n{'='*50}")
        print(f"Variation {i}/4: {var['name']}")
        print(f"{'='*50}")
        
        # Generate
        urls = generate_image(
            prompt=var["prompt"],
            width=512,
            height=512,
            num_images=1,
            name=var['name']
        )
        
        if urls:
            # Download
            save_path = output_dir / f"{var['name']}.png"
            if download_image(urls[0], save_path):
                results.append(str(save_path))
        else:
            print(f"Failed to generate {var['name']}")
        
        # Rate limit - wait between generations
        if i < len(variations):
            print("Waiting 10 seconds...")
            time.sleep(10)
    
    print(f"\n{'='*50}")
    print("Generation complete!")
    print(f"{'='*50}")
    print(f"\nGenerated {len(results)} images:")
    for path in results:
        print(f"  - {path}")
    
    return results

if __name__ == "__main__":
    print("Leonardo.ai Profile Picture Generator")
    print("="*50)
    
    # Generate profile pics
    generate_profile_pics()
