
import os
import random
import re

images_dir = '/Users/labc12/Documents/uriisace-main/images'
videos_dir = '/Users/labc12/Documents/uriisace-main/videos'
portfolio_file = '/Users/labc12/Documents/uriisace-main/portfolio.html'

# CSS classes for different sizes
# We will use apo-item-size-2x for double width items
# We will assume "standard" items are 1x width.

def get_clean_title(filename):
    # Remove ellipsis ... if present at end
    clean = filename
    if clean.endswith('...'):
        clean = clean[:-3]
    # Remove extension
    clean = re.sub(r'\.(jpg|jpeg|png|mp4|gif)$', '', clean, flags=re.IGNORECASE)
    # Replace separators
    clean = clean.replace('_', ' ').replace('-', ' ')
    return clean.title()

html_items = ""

# Gather all items first so we can shuffle or interleave them
items = []

# Excluded items
excluded_images = ['Foto urielo.png', 'Page-bg-img-6.png', 'carita.png', 'icon.png']
excluded_videos = ['spot_lluvias.mp4', 'SPOT_30SEG_ACCIONES LLUVIAS_V8_FHD.mp4']

# Get images
for filename in os.listdir(images_dir):
    if filename.endswith(('.jpg', '.png', '.jpeg')):
        if filename in excluded_images: continue
        if 'icon' in filename.lower() and len(filename) < 10: continue
        if 'logo' in filename.lower(): continue
        
        items.append({
            'type': 'image',
            'filename': filename,
            'category': 'Gallery',
            'filter_class': 'apo-photography'
        })

# Get videos
for filename in os.listdir(videos_dir):
    if filename.endswith('.mp4'):
        if filename in excluded_videos: continue
        
        items.append({
            'type': 'video',
            'filename': filename,
            'category': 'Video',
            'filter_class': 'apo-print-design' # Using this class for Video as per user's previous mapping
        })

# Randomize to mix new content with old if desired, or just sort new ones?
# User wanted a "grid bonito". Random mix usually looks more organic.
random.seed(42) # Fixed seed for reproducibility
random.shuffle(items)

for i, item in enumerate(items):
    filename = item['filename']
    title = get_clean_title(filename)
    
    # Determine size - 20% chance of being double width (Large)
    # Note: If it's a video, maybe we prefer it larger?
    is_large = False
    if item['type'] == 'video':
        is_large = True # Videos always large look better usually
    elif random.random() < 0.2:
        is_large = True
        
    size_class = "apo-item-size-2x" if is_large else ""
    
    # Generate HTML
    if item['type'] == 'image':
        html_items += f"""
            <div class="apo-item {item['filter_class']} {size_class}">
              <article class="apo-project">
                <div class="apo-project-media"><a href="images/{filename}" data-fancybox="gallery"><img src="images/{filename}" alt=""/></a></div>
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
    else:
        # Video
        html_items += f"""
            <div class="apo-item {item['filter_class']} {size_class}">
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

# Now we need to inject this into portfolio.html AND update the container attributes
# data-isotope-layout="grid" -> data-isotope-layout="masonry"

with open(portfolio_file, 'r') as f:
    content = f.read()

# 1. Update Container Layout Mode
# Find <div  data-isotope-layout="grid" ... class="apo-isotope ...
# Note: The class list might vary slightly, but key is `data-isotope-layout="grid"`
content = content.replace('data-isotope-layout="grid"', 'data-isotope-layout="masonry"')

# 2. Replace the Grid Content
# We look for the start of the grid items and the end.
# Matches: <div class="grid-sizer"></div> ... items ... </div><!-- Isotope End -->
# To be safe, we'll replace everything inside the isotope container after <div class="grid-sizer"></div>
# Actually, my previous approach was `sed` insertion. Here I'll do a regex replacement.

# Grid start
start_marker = '<div class="grid-sizer"></div>'
# We need to find where the items end. It's the closing div of "apo-isotope".
# Since nested divs exist, regex is tricky. 
# However, the Isotope container sits inside <div class="apo-section">.
# Let's try to clear everything between grid-sizer and the next major closing tag structure or just overwrite the file logic entirely if I can reconstruct the wrapper.

# Current portfolio.html structure from view_file:
# <div data-isotope-layout="grid" ... class="apo-isotope ...">
#   <div class="grid-sizer"></div>
#   ... ITEMS ...
# </div>

# We will construct the new ITEMS block
new_content_block = f'{start_marker}\n{html_items}'

# Regex to replace existing grid content
# We match from grid-sizer to the end of the div. 
# Identifying the matching closing div is hard with regex. 
# Alternative: Replace the whole "apo-isotope" div if we can identify its start.

# Let's use a simpler marker approach assuming standard formatting
# We will identify the container line:
# <div data-isotope-layout="masonry" class="apo-isotope apo-cols-4 apo-portfolio-container apo-style-1">
# And the closing </div> is usually indented or followed by <!-- End Isotope --> (if we added it) or just before <footer...

# Actually, let's just use Python string split/join if we can locate unique markers.
# The container starts at: <div data-isotope-layout="masonry"
# (I already did the replace above so it's masonry now in `content`)

parts = content.split('<div class="grid-sizer"></div>')
if len(parts) > 1:
    pre_grid = parts[0]
    # post_grid: we need to find the end of the items.
    # The items are <div class="apo-item ...">...</div>
    # The items end before the closing </div> of the container.
    # The container is followed by <footer ...> or just closing section tags.
    # In `portfolio.html` viewed earlier:
    # 251:             </div>
    # 252:             <footer class="apo-person-footer">...
    # This footer seems to be inside apo-section but outside isotope? No, Isotope usually doesn't have a footer inside.
    # Let's look at the file end.
    
    # safer strategy:
    # 1. Read the file up to class="apo-portfolio-container apo-style-1"> (or similar)
    # 2. Write header + new grid content + footer
    
    # Find the start index of the container div
    container_start = content.find('class="apo-isotope apo-cols-4 apo-portfolio-container apo-style-1"')
    if container_start == -1:
         # Try looking for layout attribute if class string mismatch
         container_start = content.find('data-isotope-layout="masonry"')
    
    # Find the end of this div?
    # It is risky.
    
    # Alternative plan: define a temporary marker in the file where I want to insert, deleting old items.
    # The old items are many.
    
    pass

# Let's overwrite `portfolio_chunk.html` with the new items, 
# and then use a python logic to rewrite `portfolio.html` completely properly.

with open('portfolio_chunk.html', 'w') as f:
    f.write(new_content_block)
    
print("Chunk generated. Run the next step to splice it in.")
