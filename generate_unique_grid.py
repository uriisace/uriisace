
import os
import hashlib

images_dir = '/Users/labc12/Documents/uriisace-main/images'
videos_dir = '/Users/labc12/Documents/uriisace-main/videos'
portfolio_file = '/Users/labc12/Documents/uriisace-main/portfolio.html'

# Excludes
excluded_images = ['Foto urielo.png', 'Page-bg-img-6.png', 'carita.png', 'icon.png']
# Add generated prefixes from previous steps if we want to ignore them
# But better to just check file hash or duplicate sizes.

# We will build a map of file_size -> [list of filenames]
# Then for each list with >1 file, we compare hashes.
# If hash matches, we only pick ONE to display.
# Preference: Prefer the one with 'car_' prefix if exists? Or the one WITHOUT 'car_' prefix?
# User said "cambiaste nmbres y aparecen dobles". Maybe keep the cleaner name?
# Let's prefer shorter names or specific ones.

def get_file_hash(filepath):
    """Calculates MD5 hash of file"""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def clean_title(filename):
    clean = filename
    if clean.endswith('...'): clean = clean[:-3]
    clean = os.path.splitext(clean)[0]
    clean = clean.replace('_', ' ').replace('-', ' ')
    return clean.title()

# 1. Identify Unique Images
unique_images = [] # List of filenames to include
seen_hashes = set()

# Get all candidates
candidates = []
for f in os.listdir(images_dir):
    if f.endswith(('.jpg', '.png', '.jpeg')) and f not in excluded_images:
        path = os.path.join(images_dir, f)
        if os.path.getsize(path) < 10000: continue # Skip tiny icons
        candidates.append(f)

# Sort candidates to ensure deterministic order (maybe prefer shorter names?)
# If we have 'car_1.jpg' and '49283...jpg', let's prefer 'car_1.jpg' as it is cleaner?
# Or maybe prefer the original if 'car_1' is already in the slider? 
# The user wants "Grid mas profesional". 
# Duplicates came from me copying '492...' to 'car_4'.
# So 'car_4.png' and '492...png' are identical.
# I should show only ONE. 
# Let's prefer the one that is NOT 'car_X' if we want to avoid showing the "slider asset" name?
# But 'car_X' is shorter. 
# Let's just pick the first one we see, but sort by name length so we pick the "cleaner" (shorter) one?
# 'car_1.jpg' (9 chars) vs '4920484628343664028.jpg' (20+ chars).
# Shorter is better for title generation too.

candidates.sort(key=len)

for f in candidates:
    path = os.path.join(images_dir, f)
    file_hash = get_file_hash(path)
    
    if file_hash in seen_hashes:
        continue # Skip duplicate
    
    seen_hashes.add(file_hash)
    unique_images.append(f)

# 2. Identify Unique Videos
unique_videos = []
seen_video_hashes = set()
excluded_videos = ['spot_lluvias.mp4']

video_candidates = []
for f in os.listdir(videos_dir):
    if f.endswith('.mp4') and f not in excluded_videos:
        video_candidates.append(f)

video_candidates.sort(key=len)

for f in video_candidates:
    path = os.path.join(videos_dir, f)
    # Hashing large videos is slow. Let's trust size + first 1000 bytes?
    # Or just filename if no duplicates expected.
    # User only mentioned duplicate photos.
    # But I copied video513... to video_nuevo.mp4. So yes, duplicates exist.
    
    stat = os.stat(path)
    size = stat.st_size
    
    # Read partial hash
    with open(path, 'rb') as vf:
        chunk = vf.read(4096)
    
    v_hash = f"{size}_{hashlib.md5(chunk).hexdigest()}"
    
    if v_hash in seen_video_hashes:
        continue
        
    seen_video_hashes.add(v_hash)
    unique_videos.append(f)

# 3. Generate HTML
import random
random.seed(42)

items = []
for img in unique_images:
    items.append({'type': 'image', 'filename': img, 'category': 'Gallery', 'class': 'apo-photography'})
for vid in unique_videos:
    items.append({'type': 'video', 'filename': vid, 'category': 'Video', 'class': 'apo-print-design'})


# 4. Add Specific External Web/Game Items
external_items = [
    {
        'filename': 'game_impostor_tarot.png',
        'title': 'Impostor Tarot',
        'category': 'Game Dev',
        'url': 'https://impostortarot.netlify.app/'
    },
    {
        'filename': 'game_unchingo_dijieron.png',
        'title': 'Un Chingo Dijieron',
        'category': 'Game Dev',
        'url': 'https://unchingodijieron.netlify.app/'
    },
    {
        'filename': 'web_hotel_miranchito.png',
        'title': 'Hotel Mi Ranchito',
        'category': 'Web Dev',
        'url': 'http://hotelmiranchito.com/'
    },
    {
        'filename': 'web_diario_mujer_cafe.png',
        'title': 'Diario Mujer y Cafe',
        'category': 'Web Dev',
        'url': 'https://www.diariomujerycafemovie.com/'
    }
]

# Ensure these images are in unique_images list (they should be detected if files exist)
# We need to find them in `items` list if they were added as generic images, 
# REMOVE them from generic items, and ADD them as special items.

# Filter out generic entries for these files
items = [i for i in items if i['filename'] not in [x['filename'] for x in external_items]]

# Add special items
for ext in external_items:
    items.append({
        'type': 'external', 
        'filename': ext['filename'], 
        'title': ext['title'],
        'category': ext['category'],
        'url': ext['url'],
        'class': 'apo-web-design' # Use web design class for filter
    })

random.shuffle(items)

html_output = '<div class="grid-sizer"></div>'

for item in items:
    filename = item['filename']
    
    # 20% large items
    size_class = ""
    if item['type'] == 'video' or random.random() < 0.2:
        size_class = "apo-item-size-2x"
        
    if item['type'] == 'image':
        title = clean_title(filename)
        # Create a caption for the lightbox
        # Ideally this would come from metadata, but we'll generate a professional looking default.
        caption = f"Project: {title} | 2024"
        
        html_output += f"""
            <div class="apo-item {item['class']} {size_class}">
              <article class="apo-project">
                <div class="apo-project-media">
                    <a href="images/{filename}" data-fancybox="gallery" data-caption="{caption}">
                        <img src="images/{filename}" alt=""/>
                    </a>
                </div>
                <div class="apo-project-content-wrap">
                  <div class="apo-aligner-outer">
                    <div class="apo-aligner-inner">
                      <header class="apo-project-header">
                        <h2 class="apo-project-title"><a href="#">{title}</a></h2>
                        <ul class="apo-project-categories">
                          <li><a href="#">{item['category']}</a></li>
                        </ul>
                      </header>
                    </div>
                  </div>
                </div>
              </article>
            </div>"""
    elif item['type'] == 'video':
        title = clean_title(filename)
        html_output += f"""
            <div class="apo-item {item['class']} {size_class}">
              <article class="apo-project">
                <div class="apo-project-media">
                     <video width="100%" controls preload="metadata">
                        <source src="videos/{filename}" type="video/mp4">
                    </video>
                </div>
                <div class="apo-project-content-wrap">
                  <div class="apo-aligner-outer">
                    <div class="apo-aligner-inner">
                      <header class="apo-project-header">
                        <h2 class="apo-project-title"><a href="#">{title}</a></h2>
                        <ul class="apo-project-categories">
                          <li><a href="#">{item['category']}</a></li>
                        </ul>
                      </header>
                    </div>
                  </div>
                </div>
              </article>
            </div>"""
    elif item['type'] == 'external':
        html_output += f"""
            <div class="apo-item {item['class']} {size_class}">
              <article class="apo-project">
                <div class="apo-project-media"><a href="{item['url']}" target="_blank"><img src="images/{filename}" alt=""/></a></div>
                <div class="apo-project-content-wrap">
                  <div class="apo-aligner-outer">
                    <div class="apo-aligner-inner">
                      <header class="apo-project-header">
                        <h2 class="apo-project-title"><a href="{item['url']}" target="_blank">{item['title']}</a></h2>
                        <ul class="apo-project-categories">
                          <li><a href="#">{item['category']}</a></li>
                        </ul>
                      </header>
                    </div>
                  </div>
                </div>
              </article>
            </div>"""

with open('/Users/labc12/Documents/uriisace-main/portfolio_chunk_unique.html', 'w') as f:
    f.write(html_output)

print("Unique chunk generated.")
