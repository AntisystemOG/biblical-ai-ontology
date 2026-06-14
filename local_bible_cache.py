"""
Bible Cache System
Stores Bible passages, analysis, and notes locally to avoid re-reading same passages.
Saves token costs on Bible study.
Usage: Call during Bible reading workflow
"""

import json
import os
from datetime import datetime
from pathlib import Path

CACHE_FILE = Path(__file__).parent / "data" / "bible_cache.json"

def ensure_cache():
    """Ensure cache file exists"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CACHE_FILE.exists():
        CACHE_FILE.write_text("{}")

def get_passage(reference: str) -> dict:
    """
    Retrieve a cached Bible passage.
    
    Args:
        reference: Bible reference (e.g., "Genesis 1:1-5")
        
    Returns:
        Cached passage data or None if not found
    """
    ensure_cache()
    cache = json.loads(CACHE_FILE.read_text())
    return cache.get(reference.lower().strip())

def store_passage(reference: str, text: str, analysis: str = "", notes: str = ""):
    """
    Store a Bible passage with analysis and notes.
    
    Args:
        reference: Bible reference (e.g., "Genesis 1:1-5")
        text: Full passage text
        analysis: Optional analysis/interpretation
        notes: Optional personal notes
    """
    ensure_cache()
    cache = json.loads(CACHE_FILE.read_text())
    
    cache[reference.lower().strip()] = {
        "text": text,
        "analysis": analysis,
        "notes": notes,
        "cached_at": datetime.now().isoformat(),
        "access_count": 0
    }
    
    CACHE_FILE.write_text(json.dumps(cache, indent=2))

def update_analysis(reference: str, analysis: str):
    """Update analysis for an existing passage"""
    ensure_cache()
    cache = json.loads(CACHE_FILE.read_text())
    key = reference.lower().strip()
    
    if key in cache:
        cache[key]["analysis"] = analysis
        cache[key]["updated_at"] = datetime.now().isoformat()
        CACHE_FILE.write_text(json.dumps(cache, indent=2))

def add_notes(reference: str, notes: str):
    """Add notes to an existing passage"""
    ensure_cache()
    cache = json.loads(CACHE_FILE.read_text())
    key = reference.lower().strip()
    
    if key in cache:
        cache[key]["notes"] = notes
        cache[key]["updated_at"] = datetime.now().isoformat()
        CACHE_FILE.write_text(json.dumps(cache, indent=2))

def list_cached() -> list:
    """List all cached references"""
    ensure_cache()
    cache = json.loads(CACHE_FILE.read_text())
    return list(cache.keys())

def clear_cache():
    """Clear entire cache - use with caution"""
    ensure_cache()
    CACHE_FILE.write_text("{}")

if __name__ == "__main__":
    # Test
    store_passage("Genesis 1:1", "In the beginning God created the heavens and the earth.",
                  "Opening statement of creation narrative", "Foundation of Christian worldview")
    print(get_passage("genesis 1:1"))
