"""
Spock Profile Picture Generator
Creates 4 variations for Telegram profile pic
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_base_image(size=512):
    """Create base canvas"""
    img = Image.new('RGB', (size, size), 'white')
    return img

def draw_vulcan_hand(draw, size, style=1):
    """Draw Vulcan salute hand in different styles"""
    center = size // 2
    
    if style == 1:
        # Minimalist outline
        color = '#1a3a5c'  # Deep blue
        width = 8
        # Simple hand silhouette
        points = [
            (center-40, size-100),
            (center-40, center-20),
            (center-60, center-80),
            (center-50, center-100),
            (center-30, center-60),
            (center-20, center-80),
            (center, center-40),
            (center+20, center-80),
            (center+30, center-60),
            (center+50, center-100),
            (center+60, center-80),
            (center+40, center-20),
            (center+40, size-100),
        ]
        draw.line(points, fill=color, width=width)
        
    elif style == 2:
        # Solid filled hand
        color = '#2d5a87'  # Medium blue
        # Palm
        draw.ellipse([center-50, center-20, center+50, size-80], fill=color)
        # Fingers
        draw.rectangle([center-45, center-80, center-25, center-20], fill=color)
        draw.rectangle([center-15, center-100, center+5, center-20], fill=color)
        draw.rectangle([center+15, center-100, center+35, center-20], fill=color)
        draw.rectangle([center+25, center-80, center+45, center-20], fill=color)
        
    elif style == 3:
        # Gradient hand with glow
        # Outer glow
        for i in range(20, 0, -2):
            glow_color = f'rgba(255, 215, 0, {i*5})'
            draw.ellipse([center-60-i, center-110-i, center+60+i, size-70+i], 
                        fill=glow_color)
        # Hand
        draw.ellipse([center-50, center-20, center+50, size-80], fill='#1e3a5f')
        draw.rectangle([center-45, center-80, center-25, center-20], fill='#1e3a5f')
        draw.rectangle([center-15, center-100, center+5, center-20], fill='#1e3a5f')
        draw.rectangle([center+15, center-100, center+35, center-20], fill='#1e3a5f')
        draw.rectangle([center+25, center-80, center+45, center-20], fill='#1e3a5f')
        
    elif style == 4:
        # Stylized icon with Bible/truth element
        # Background circle
        draw.ellipse([20, 20, size-20, size-20], fill='#1a2332')
        # Hand
        draw.ellipse([center-40, center-10, center+40, size-70], fill='#3d5a80')
        draw.rectangle([center-35, center-70, center-15, center-10], fill='#3d5a80')
        draw.rectangle([center-5, center-90, center+15, center-10], fill='#3d5a80')
        draw.rectangle([center+25, center-70, center+45, center-10], fill='#3d5a80')
        # Open book at bottom (truth/word)
        draw.polygon([center-60, size-120, center-30, size-90, center+30, size-90, center+60, size-120], 
                    fill='#ee6c4d')

def add_background(draw, size, style=1):
    """Add background based on style"""
    if style == 1:
        # Simple gradient
        for y in range(size):
            r = int(26 + (30-26) * y/size)
            g = int(58 + (90-58) * y/size)
            b = int(92 + (140-92) * y/size)
            draw.line([(0, y), (size, y)], fill=(r,g,b))
    elif style == 2:
        # Solid with subtle pattern
        draw.rectangle([0, 0, size, size], fill='#0f2744')
        # Subtle stars
        import random
        random.seed(42)
        for _ in range(50):
            x = random.randint(0, size)
            y = random.randint(0, size)
            draw.point((x, y), fill='#ffffff')
    elif style == 3:
        # Warm gradient
        for y in range(size):
            ratio = y/size
            r = int(26 + 200 * ratio)
            g = int(58 + 150 * ratio)
            b = int(92 + 100 * ratio)
            draw.line([(0, y), (size, y)], fill=(r,g,b))
    elif style == 4:
        # Deep space with stars
        draw.rectangle([0, 0, size, size], fill='#0a0e1a')
        import random
        random.seed(123)
        for _ in range(100):
            x = random.randint(0, size)
            y = random.randint(0, size)
            brightness = random.randint(150, 255)
            draw.point((x, y), fill=(brightness, brightness, brightness))

def generate_all():
    """Generate all 4 variations"""
    size = 512
    
    for i in range(1, 5):
        img = create_base_image(size)
        draw = ImageDraw.Draw(img)
        
        # Add background
        add_background(draw, size, i)
        
        # Add hand
        draw_vulcan_hand(draw, size, i)
        
        # Save
        filename = f'spock_profile_v{i}.png'
        img.save(filename)
        print(f'Generated: {filename}')
    
    print('\nAll 4 profile pictures generated!')
    print('Files: spock_profile_v1.png through spock_profile_v4.png')

if __name__ == '__main__':
    generate_all()
