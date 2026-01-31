
import re
import random
import os

index_path = '/Users/labc12/Documents/uriisace-main/index.html'

with open(index_path, 'r') as f:
    content = f.read()

# Extract the Carousel container
# It starts with <div class="apo-striped-photos apo-full-height owl-carousel" ...>
# and ends with </div> <!-- End of Full Page Carousel-->
# But finding the exact closing div is tricky with regex.
# However, we can use the markers I saw in the file content.

start_marker = 'class="apo-striped-photos apo-full-height owl-carousel"'
end_marker = '<!-- End of Full Page Carousel-->'

start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find carousel start")
    exit(1)

# Find the opening bracket end
start_tag_end = content.find('>', start_idx) + 1

end_idx = content.find(end_marker)
if end_idx == -1:
    print("Could not find carousel end")
    exit(1)

# The content to replace is everything between start_tag_end and end_idx
# BUT we must be careful not to include the closing </div> of the container.
# The container closing </div> is likely just before the end_marker.
# Let's look at the content just before end_idx.
# It usually looks like `    </div>\n    <!-- End of Full Page Carousel-->`
# So we shuffle the ARTICLES.

carousel_inner_html = content[start_tag_end:end_idx]

# We need to extract <article> blocks.
# We can regex for <article ... </article> with DOTALL.
# Warning: Nested tags are fine, article shouldn't contain another article.

articles = re.findall(r'<article.*?</article>', carousel_inner_html, re.DOTALL)

print(f"Found {len(articles)} existing articles.")

# Define NEW articles strings not yet in the file (if any).
# The user asked for "s3.png" and "DSC00926.jpg" and "IMG_7260.png".
# I only found IMG_7260.png.
# I will create an article for IMG_7260.png.

new_img_filename = "IMG_7260.png"
# Check if it's already there?
if new_img_filename not in carousel_inner_html:
    new_article = f"""
      <article data-bg-img-src="images/{new_img_filename}" class="apo-striped-photo">
        <div class="apo-striped-photo-description">
          <div class="apo-aligner-outer">
            <div class="apo-aligner-inner">
              <ul class="apo-striped-photo-categories">
                <li><a href="#">Gastronomy</a></li>
              </ul>
              <h2 class="apo-striped-photo-title"><a href="#">Culinary Art</a></h2>
              <div class="apo-striped-photo-meta"><small>2025</small></div>
            </div>
          </div>
        </div>
      </article>"""
    articles.append(new_article)
    print(f"Added {new_img_filename}")

# Note: The user said "agurega estas imagenes ... y las primeras que estaban te acuerdad que ya tenia, tambien reacomodalas"
# My extracted `articles` list ALREADY contains the ones currently in the file 
# (which includes the 2 new ones I just added: Impostor and Diario, AND the old ones).
# So simply shuffling `articles` satisfies the requirement "reacomodalas para que todo este como revuelto".

random.shuffle(articles)

# Reconstruct HTML
new_inner_html = "\n".join(articles)

# Indentation cleanup (optional but nice)
new_inner_html = new_inner_html.replace('\n', '\n      ') 

# Construct final content
# We need to preserve the wrapper </div> at the end.
# The `carousel_inner_html` included the closing `</div>`?
# Let's check `carousel_inner_html` content.
# If I extracted from `>` to `<!-- End...`, it includes the indentation and closing </div>.
# My regex `findall` extracted ONLY the articles.
# So I stripped the text between articles and the outer divs.
# I need to put back the closing `</div>` of the owl-carousel.

final_html = content[:start_tag_end] + "\n" + new_inner_html + "\n    </div>\n    " + content[end_idx:]

with open(index_path, 'w') as f:
    f.write(final_html)

print("Carousel shuffled and updated.")
