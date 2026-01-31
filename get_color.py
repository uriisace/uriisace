
from PIL import Image
from collections import Counter

def get_dominant_color(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        pixels = img.getdata()
        
        # Filter transparent pixels and white/black if needed, but let's just look for most common
        valid_pixels = []
        for r, g, b, a in pixels:
            if a > 0: # Not transparent
                # Ignore pure white/black if it's a logo with background, but carita might be the color
                valid_pixels.append((r, g, b))
                
        if not valid_pixels:
            return "#ffffff"
            
        most_common = Counter(valid_pixels).most_common(1)[0][0]
        return '#{:02x}{:02x}{:02x}'.format(most_common[0], most_common[1], most_common[2])
    except Exception as e:
        print(f"Error: {e}")
        return "#ff0000" # Default error red

print(get_dominant_color('images/carita.png'))
