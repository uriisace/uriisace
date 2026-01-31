
import os

images_dir = '/Users/labc12/Documents/uriisace-main/images'
videos_dir = '/Users/labc12/Documents/uriisace-main/videos'
portfolio_file = '/Users/labc12/Documents/uriisace-main/portfolio.html'

# Read existing portfolio to find used images
used_images = set()
with open(portfolio_file, 'r') as f:
    content = f.read()
    for filename in os.listdir(images_dir):
        if filename in content:
            used_images.add(filename)

# Also exclude carousel images we just added manually to index.html if we don't want them here?
# User said "add all the REST". Carousel images are used in index.html, but maybe acceptable in portfolio too?
# Usually "rest" means what is NOT used. But they are new. I'll include them if they are not in portfolio.html yet.

# Also exclude the "lluvias" video
excluded_videos = ['spot_lluvias.mp4', 'SPOT_30SEG_ACCIONES LLUVIAS_V8_FHD.mp4']

html_output = ""

# Get all images
for filename in os.listdir(images_dir):
    if filename.endswith(('.jpg', '.png', '.jpeg')):
        if filename in used_images:
            continue
        
        # basic exclusion of small icons or technical files
        if 'icon' in filename or 'logo' in filename.lower() and len(filename) < 10:
            continue
            
        html_output += f"""
            <div class="apo-item apo-photography">
              <article class="apo-project">
                <div class="apo-project-media"><a href="images/{filename}" data-fancybox="gallery"><img src="images/{filename}" alt=""/></a></div>
                <div class="apo-project-content-wrap">
                  <div class="apo-aligner-outer">
                    <div class="apo-aligner-inner">
                      <header class="apo-project-header">
                        <h2 class="apo-project-title"><a href="#">{filename[:15]}...</a></h2>
                        <ul class="apo-project-categories">
                          <li><a href="#">Gallery</a></li>
                        </ul>
                      </header>
                    </div>
                  </div>
                </div>
              </article>
            </div>"""

# Get all videos
for filename in os.listdir(videos_dir):
    if filename.endswith('.mp4'):
        if filename in excluded_videos: continue
        
        # Create a video item
        # We'll use a simple video tag preview
        html_output += f"""
            <div class="apo-item apo-print-design">
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
                        <h2 class="apo-project-title"><a href="#">{filename[:15]}...</a></h2>
                        <ul class="apo-project-categories">
                          <li><a href="#">Video</a></li>
                        </ul>
                      </header>
                    </div>
                  </div>
                </div>
              </article>
            </div>"""

with open('portfolio_chunk.html', 'w') as f:
    f.write(html_output)
