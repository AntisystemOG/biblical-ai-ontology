#!/usr/bin/env python3
"""
Read Genesis locally, cache passages, and prepare for analysis.
"""

import sys
import requests
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Import our cache system
sys.path.insert(0, str(Path(__file__).parent))
from local_bible_cache import BibleCache

cache = BibleCache()

# Genesis chapters 1-2: Creation
genesis_1_26_27 = """
Genesis 1:26-27 (KJV)
And God said, Let us make man in our image, after our likeness: and let them have dominion over the fish of the sea, and over the fowl of the air, and over the cattle, and over all the earth, and over every creeping thing that creepeth upon the earth.

So God created man in his own image, in the image of God created he him; male and female created he them.
"""

cache.cache_passage("Genesis", 1, 26, 27, genesis_1_26_27)

# Genesis 2: Garden, man's purpose
genesis_2_15 = """
Genesis 2:15 (KJV)
And the LORD God took the man, and put him into the garden of Eden to dress it and to keep it.
"""

cache.cache_passage("Genesis", 2, 15, 15, genesis_2_15)

# Genesis 3: Fall
genesis_3_1_6 = """
Genesis 3:1-6 (KJV)
Now the serpent was more subtil than any beast of the field which the LORD God had made. And he said unto the woman, Yea, hath God said, Ye shall not eat of every tree of the garden?

And the woman said unto the serpent, We may eat of the fruit of the trees of the garden:
But of the fruit of the tree which is in the midst of the garden, God hath said, Ye shall not eat of it, neither shall ye touch it, lest ye die.

And the serpent said unto the woman, Ye shall not surely die:
For God doth know that in the day ye eat thereof, then your eyes shall be opened, and ye shall be as gods, knowing good and evil.

And when the woman saw that the tree was good for food, and that it was pleasant to the eyes, and a tree to be desired to make one wise, she took of the fruit thereof, and did eat, and gave also unto her husband with her; and he did eat.
"""

cache.cache_passage("Genesis", 3, 1, 6, genesis_3_1_6)

print("[OK] Genesis key passages cached")
print(f"Cache status: {cache.list_cached()}")

# Now use Mistral locally for analysis
print("\nAnalyzing Genesis 1:26-27 with local Mistral...")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": """Analyze Genesis 1:26-27: "And God said, Let us make man in our image, after our likeness... So God created man in his own image, in the image of God created he him; male and female created he them."

What does it mean that humans are made in God's image? What are the implications for human purpose and identity?

Keep response under 300 words.""",
        "stream": False
    },
    timeout=60
)

if response.status_code == 200:
    analysis = response.json()["response"]
    cache.cache_analysis("Genesis 1:26-27 - Image of God", analysis)
    print("\n[OK] Analysis complete and cached")
    print("\nAnalysis excerpt:")
    print(analysis[:400] + "...")
else:
    print(f"[FAIL] Error: {response.status_code}")

print("\n[OK] Genesis reading session complete")
print("Ready for deeper study when you're interested.")
