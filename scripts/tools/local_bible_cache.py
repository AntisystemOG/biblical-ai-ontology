#!/usr/bin/env python3
"""
Local Bible Analysis Cache
Stores parsed Bible passages, summaries, and insights to avoid re-reading.
"""

import json
import os
from pathlib import Path
from datetime import datetime

class BibleCache:
    def __init__(self, cache_dir="~/.openclaw/cache/bible"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.load_index()
    
    def load_index(self):
        """Load or initialize the cache index."""
        if self.index_file.exists():
            with open(self.index_file) as f:
                self.index = json.load(f)
        else:
            self.index = {
                "books": {},
                "passages": {},
                "notes": {},
                "lastUpdated": datetime.now().isoformat()
            }
    
    def save_index(self):
        """Save cache index to disk."""
        self.index["lastUpdated"] = datetime.now().isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def cache_passage(self, book, chapter, verse_start, verse_end, text):
        """Store a Bible passage."""
        key = f"{book}_{chapter}:{verse_start}-{verse_end}"
        cache_file = self.cache_dir / f"{key}.txt"
        
        with open(cache_file, 'w') as f:
            f.write(text)
        
        self.index["passages"][key] = {
            "book": book,
            "chapter": chapter,
            "verses": f"{verse_start}-{verse_end}",
            "file": str(cache_file),
            "cached_at": datetime.now().isoformat()
        }
        self.save_index()
    
    def cache_analysis(self, name, analysis_text):
        """Store analysis/notes about a passage or concept."""
        key = name.lower().replace(" ", "_")
        note_file = self.cache_dir / f"analysis_{key}.md"
        
        with open(note_file, 'w') as f:
            f.write(f"# {name}\n\n")
            f.write(analysis_text)
        
        self.index["notes"][key] = {
            "name": name,
            "file": str(note_file),
            "cached_at": datetime.now().isoformat()
        }
        self.save_index()
    
    def get_passage(self, key):
        """Retrieve a cached passage."""
        if key in self.index["passages"]:
            file_path = self.index["passages"][key]["file"]
            with open(file_path) as f:
                return f.read()
        return None
    
    def get_analysis(self, key):
        """Retrieve cached analysis."""
        key = key.lower().replace(" ", "_")
        if key in self.index["notes"]:
            file_path = self.index["notes"][key]["file"]
            with open(file_path) as f:
                return f.read()
        return None
    
    def list_cached(self):
        """List all cached passages and analyses."""
        files = list(self.cache_dir.glob("*.txt")) + list(self.cache_dir.glob("*.md"))
        return {
            "passages": len(self.index["passages"]),
            "analyses": len(self.index["notes"]),
            "total_cache_size": sum(os.path.getsize(f) for f in files if f.is_file())
        }

if __name__ == "__main__":
    # Test
    cache = BibleCache()
    print("Bible Cache initialized")
    print(f"Cache location: {cache.cache_dir}")
    print(f"Status: {cache.list_cached()}")
