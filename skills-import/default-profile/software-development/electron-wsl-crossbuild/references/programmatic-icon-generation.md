# Programmatic Icon/Asset Generation Without External Tools

## When You Need This
- Building an Electron app and need `.ico`/`.png` icons
- No ImageMagick (`convert`/`magick`) available on the build machine
- No Python Pillow installed
- Want to avoid adding heavy dependencies just for one icon

## Technique: Raw PNG Encoding in Python Stdlib

Use Python's `struct` + `zlib` to write a valid PNG from scratch. No third-party libraries needed.

```python
import struct, zlib, io

def png_chunk(chunk_type, data):
    chunk = struct.pack('>I', len(data)) + chunk_type + data
    crc = zlib.crc32(chunk_type + data) & 0xffffffff
    return chunk + struct.pack('>I', crc)

def create_png(width, height, raw_rgba_bytes):
    buf = io.BytesIO()
    buf.write(b'\x89PNG\r\n\x1a\n')
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    buf.write(png_chunk(b'IHDR', ihdr))
    raw_rows = b''
    row_len = width * 4
    for y in range(height):
        raw_rows += b'\x00' + raw_rgba_bytes[y*row_len:(y+1)*row_len]
    compressed = zlib.compress(raw_rows)
    buf.write(png_chunk(b'IDAT', compressed))
    buf.write(png_chunk(b'IEND', b''))
    return buf.getvalue()
```

## Technique: Minimal ICO from PNG

Windows `.ico` files can embed a raw PNG for 256x256 sizes (modern Windows supports this). No BMP conversion needed.

```python
def create_ico(png_bytes):
    # Header: reserved(2), type(2), count(2)
    header = struct.pack('<HHH', 0, 1, 1)
    # Entry: width(1), height(1), colors(1), reserved(1), planes(2), bitcount(2), size(4), offset(4)
    entry = struct.pack('<BBBBHHII', 0, 0, 0, 0, 1, 32, len(png_bytes), 6 + 16)
    return header + entry + png_bytes
```

## Full Working Example (Teal Circle on Dark Background)

```python
import struct, zlib, io, os

WIDTH, HEIGHT = 256, 256
BG = (15, 15, 16)      # #0f0f10
FG = (78, 201, 176)    # #4ec9b0 (teal)
cx, cy, radius = WIDTH//2, HEIGHT//2, 90

pixels = []
for y in range(HEIGHT):
    for x in range(WIDTH):
        dx, dy = x - cx, y - cy
        dist = (dx*dx + dy*dy) ** 0.5
        if dist <= radius:
            pixels.extend([*FG, 255])
        elif dist <= radius + 1:
            alpha = int(255 * (radius + 1 - dist))
            pixels.extend([*FG, alpha])
        else:
            pixels.extend([*BG, 255])

raw = bytes(pixels)

# PNG helper functions from above...
# ... create_png() and create_ico() ...

png = create_png(WIDTH, HEIGHT, raw)
with open('resources/icon.png', 'wb') as f:
    f.write(png)

ico = create_ico(png)
with open('resources/icon.ico', 'wb') as f:
    f.write(ico)
```

## Why This Matters
- WSL builds often lack GUI/image tools
- CI/CD containers usually don't have ImageMagick
- Keeps the build self-contained and reproducible
- Electron Builder accepts `.ico` directly; no conversion step needed

## Notes
- For 256x256, ICO stores width/height as `0` in the directory entry (per spec, 0 means 256)
- Transparency works correctly on Windows 10/11
- For smaller sizes (e.g., 16x16 taskbar), generate separate PNGs and embed multiple ICONDIRENTRY records
