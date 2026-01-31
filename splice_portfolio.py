
import os

portfolio_path = '/Users/labc12/Documents/uriisace-main/portfolio.html'
chunk_path = '/Users/labc12/Documents/uriisace-main/portfolio_chunk_unique.html'

with open(portfolio_path, 'r') as f:
    full_html = f.read()

with open(chunk_path, 'r') as f:
    new_grid_content = f.read()

# 1. Change Layout Mode
full_html = full_html.replace('data-isotope-layout="grid"', 'data-isotope-layout="masonry"')

# 2. Replace Content
# We locate the Layout container start
container_start_str = 'class="apo-isotope apo-cols-4 apo-portfolio-container apo-style-1">'
start_idx = full_html.find(container_start_str)

if start_idx != -1:
    # Offset to get inside the div
    content_start_idx = start_idx + len(container_start_str)
    
    # Locate the End of the container. 
    # We know the container is inside <div class="apo-section">
    # And usually contains <div class="grid-sizer"></div> as first child.
    
    # We will assume the container ends at the matching </div>?
    # No, that's hard to parse.
    # But we know the NEXT section starts with <footer class="apo-footer apo-style-2"> OR <div class="fp-section"> or closing </div></div> wrappers.
    # Looking at the file, the portfolio container seems to be the main thing in the section.
    
    # Let's find the closing tag for the isotope container.
    # It identifies by being the div before the closing of apo-section?
    # Let's try to find the start of the next known block or closing tags.
    # In previous views, we saw:
    # </div> <!-- End item -->
    # ...
    # </div> <!-- End Isotope -->
    # </div> <!-- End Section -->
    
    # Let's simple look for the "grid-sizer" which marks the start of content
    grid_sizer_idx = full_html.find('<div class="grid-sizer"></div>')
    if grid_sizer_idx != -1:
        # Everything before grid_sizer is kep
        pre_content = full_html[:grid_sizer_idx]
        
        # Now we need to find where to resume. 
        # We want to cut until the END of the Isotope container.
        # This is tricky without a parser.
        
        # HACK: The users file has specific indentation. 
        # The closing div for isotope likely aligns with the opening. 
        # But simpler: look for the closing of the `apo-section` which contains it?
        # <div class="apo-section">
        #    <!-- Isotope-->
        #    <div data-isotope ...>
        
        # Let's search for the substring that closes the section to be safe, 
        # or we just assume everything until `<!-- Footer-->` or `<!-- End Page Content-->` 
        # starts is part of the grid we want to replace?
        # Wait, `portfolio.html` has a footer? Yes.
        
        # Use a sentinel string that definitely appears AFTER the grid.
        # "<!-- End Page Content-->" appears at line 268 in aboutme, likely similar here.
        # Or look for `<script` tags if it's at the end.
        
        # Better: Find the `</div>` that closes the `apo-isotope` div.
        # Since I generated the PREVIOUS content, I know it ends with `</article>\n            </div>` repeated many times.
        # And finally a `</div>` for the container.
        
        # Let's act conservatively. I will find the FIRST `</div>` that is followed by `<!-- End Page Content-->` or `<!-- Footer-->` or `<script`?
        # No, that's too far.
        
        # Let's assume the Isotope container is followed by `</div>` (closing apo-section) and then `</div>` (closing page).
        
        # Let's try to match the indentation if valid HTML.
        # Or... I can read the file line by line, find the start line, count braces?
        
        lines = full_html.split('\n')
        start_line_idx = -1
        for i, line in enumerate(lines):
            if 'class="apo-isotope apo-cols-4' in line:
                start_line_idx = i
                break
        
        if start_line_idx != -1:
            # We found the start. Now find the matching end.
            # Assuming standard indentation, the closing </div> should match the indentation of the opening tag.
            # The opening tag has `        <div` (8 spaces).
            # The closing tag should have 8 spaces `        </div>`.
            
            # This is heuristics but likely works for this project.
            end_line_idx = -1
            indentation = "        " # 8 spaces
            
            open_divs = 0
            found_start = False
            
            final_lines = []
            
            # Keep header lines
            final_lines.extend(lines[:start_line_idx+1])
            
            # Insert NEW content
            final_lines.append(new_grid_content)
            
            # Skip old content lines until we find the closing div
            # We'll just look for the line that has ONLY `        </div>`?
            # Or use a distinct marker if we have one. We don't.
            
            # Let's scan forward from start to find closing div
            # Actually, `count` method is safer.
            
            # Simpler approach:
            # The Isotope container is the last big thing before footer/scripts.
            # Let's find `<script src="https://code.jquery.com` ...
            # The grid ends before that, inside the page wrappers.
            
            # Let's try `closing_marker = '<!-- End Page Content-->'`
            end_marker_idx = full_html.find('<!-- End Page Content-->')
            
            if end_marker_idx != -1:
                 # working backward from end marker, we expect:
                 # </div> (apo-page)
                 # </div> (apo-full-page/container) (maybe?)
                 # </div> (apo-section)
                 # </div> (apo-isotope) <--- THIS IS WHAT WE WANT
                 
                 # It is risky to guess the number of divs.
                 pass

# FALLBACK: Just rewrite the known structure. 
# I know the header part stops at line ~192: `<div class="grid-sizer"></div>`
# I will keep everything before that.
# I will assume the footer/scripts constant part starts at... where?
# I'll rely on the previous `replace` I did. I removed items but... ?
# Actually I haven't removed items yet.

# Let's Use `sed` to delete lines 193 to the end of the file, 
# then append the chunk, then append the footer from a reference file or known string? 
# No, I need to preserve the footer.

# Precise extraction:
# 1. Read file. 
# 2. Find `<div class="grid-sizer"></div>`
# 3. Find `<!-- End Page Content-->`
# 4. The content to replace is between (2) and a few closing divs before (3).
#    The footer is BEFORE `<!-- End Page Content-->` ? 
#    Let's check `aboutme.html` reference:
#    268:     <!-- End Page Content-->
#    269:     <!-- Footer-->
#    270:     <!-- End Footer-->
#    
#    Wait, `portfolio.html` might not have a visible footer but `apo-section` closes.
#    
#    Let's use Python to find the CLOSING div of the isotope container by counting.
    lines = full_html.splitlines()
    new_lines = []
    in_grid = False
    
    # We want to keep the container div opening line!
    
    div_balance = 0
    grid_opened = False
    
    for line in lines:
        if 'class="apo-isotope apo-cols-4' in line and not grid_opened:
            in_grid = True
            grid_opened = True
            new_lines.append(line)
            # We immediately insert our new content here
            new_lines.append(new_grid_content)
            
            # Now we must SKIP lines until the grid closes.
            # We start counting divs from HERE.
            # But `new_grid_content` is a string, not lines we iterate over.
            # We need to skip the *original* lines that were inside.
            
            # Initial state of count: we just saw <div class="apo-isotope ...
            # So balance = 1.
            # We process this line to increment balance.
            div_balance += line.count('<div') - line.count('</div')
            continue
            
        if in_grid:
            # We are inside the grid in the SOURCE file.
            # We track balance to find when it closes.
            div_balance += line.count('<div') - line.count('</div')
            
            if div_balance <= 0:
                # Grid has closed.
                # This current line is the closing line (or contains it).
                # Since we already added the new content (which includes items and self-contained divs),
                # we just need to confirm we are done skipping.
                
                # Note: `new_grid_content` currently contains `<div class="grid-sizer"></div>` ... items ...
                # It does NOT contain the closing `</div>` of the isotope container.
                # So we must append valid closing tag?
                
                # Wait, `div_balance` went to 0. That means we just processed the closing `</div>`.
                # We should append this line (it is the closing tag) and continue normal copying.
                new_lines.append(line)
                in_grid = False
        else:
            new_lines.append(line)

    final_output = '\n'.join(new_lines)
    
    with open(portfolio_path, 'w') as f:
        f.write(final_output)

