#!/usr/bin/env python3
"""
Setup Ollama with a local model for Bible analysis and thinking.
"""

import requests
import json
import time
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama():
    """Check if Ollama is running."""
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            print("[OK] Ollama is running")
            return True
    except Exception as e:
        print(f"[FAIL] Ollama not running: {e}")
        return False

def pull_model(model_name):
    """Pull a model from Ollama registry."""
    print(f"\nPulling {model_name}... (this may take a few minutes)")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/pull",
            json={"name": model_name},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                status = data.get("status", "")
                if data.get("digest"):
                    print(f"  {status} {data['digest'][:20]}...")
                else:
                    print(f"  {status}")
        
        print(f"[OK] {model_name} pulled successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to pull {model_name}: {e}")
        return False

def test_model(model_name):
    """Test the model with a simple prompt."""
    print(f"\nTesting {model_name}...")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": "What is the significance of Genesis 1:26-27?",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Model works!")
            print(f"Response (first 200 chars):\n{result['response'][:200]}...\n")
            return True
        else:
            print(f"[FAIL] Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        return False

def list_models():
    """List available models."""
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        data = r.json()
        models = data.get("models", [])
        
        if models:
            print("\nAvailable models:")
            for model in models:
                print(f"  - {model['name']}")
        else:
            print("\nNo models installed yet")
        
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

if __name__ == "__main__":
    print("=== Ollama Setup ===\n")
    
    if not check_ollama():
        print("\nStart Ollama manually and try again.")
        exit(1)
    
    models = list_models()
    
    if not models:
        # Pull Mistral (good balance of speed and capability)
        pull_model("mistral")
        test_model("mistral")
    else:
        # Test existing model
        test_model(models[0]["name"])
    
    print("\n=== Setup Complete ===")
    print("Ollama is ready for local Bible analysis!")
