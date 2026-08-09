"""Save the overview image sent in chat to the project."""
from pathlib import Path

# The image is attached in the message context. Read it from the standard attachment path.
# In OpenClaw, attached images are accessible via the message metadata; we'll try common paths.
import os

candidates = [
    Path(os.environ.get('TEMP', r'C:\Users\thadd\AppData\Local\Temp')) / 'overview_image.png',
]

# Actually, the image tool may have saved it already. Let's search for recently created image files.
from datetime import datetime, timedelta
search_dirs = [
    Path(r'C:\Users\thadd\AppData\Local\Temp'),
    Path(r'C:\Users\thadd\.openclaw\workspace'),
]

found = None
for d in search_dirs:
    if not d.exists():
        continue
    for f in d.glob('*.png'):
        if f.stat().st_mtime > datetime.now().timestamp() - 3600:
            if found is None or f.stat().st_mtime > found.stat().st_mtime:
                found = f

print('Candidates found:', found)
