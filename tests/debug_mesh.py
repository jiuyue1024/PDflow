"""Debug the mesh gradient visual."""
import os, sys
PROJECT_ROOT = r"e:\印流PDflow项目"
sys.path.insert(0, PROJECT_ROOT)
import fitz
from PIL import Image

width_pt, height_pt = 242.6, 153.0
doc = fitz.open()
page = doc.new_page(width=width_pt, height=height_pt)
from export import render_with_pymupdf
render_with_pymupdf(page, width_pt, height_pt, bg_style="blue_gradient")
doc.save(r"e:\印流PDflow项目\tests\debug_mesh.pdf")
doc.close()

doc = fitz.open(r"e:\印流PDflow项目\tests\debug_mesh.pdf")
pix = doc[0].get_pixmap(dpi=300)
pix.save(r"e:\印流PDflow项目\tests\debug_mesh.png")
doc.close()

img = Image.open(r"e:\印流PDflow项目\tests\debug_mesh.png")
w, h = img.size
print(f"Image: {w}x{h}")

# Check vertical line at multiple x positions
for x in [10, 20, 30, 50, 100]:
    prev = None
    max_d = 0
    for y in range(0, h, 5):
        px = img.getpixel((x, y))
        if prev is not None:
            d = max(abs(px[0]-prev[0]), abs(px[1]-prev[1]), abs(px[2]-prev[2]))
            max_d = max(max_d, d)
        prev = px
    print(f"  x={x}: max ΔRGB={max_d}")

# Check at a specific y row
print()
for y in [10, 50, 100, 200, 300, 400, 500, 600]:
    prev = None
    max_d = 0
    for x in range(0, w, 5):
        px = img.getpixel((x, y))
        if prev is not None:
            d = max(abs(px[0]-prev[0]), abs(px[1]-prev[1]), abs(px[2]-prev[2]))
            max_d = max(max_d, d)
        prev = px
    print(f"  y={y}: max ΔRGB={max_d}")

# Show pixels at x=20, y=0 to y=20 to see cell boundaries
print()
print("Detailed vertical sample at x=20, y=0..30:")
prev = None
for y in range(0, 30):
    px = img.getpixel((20, y))
    if prev is not None:
        d = max(abs(px[0]-prev[0]), abs(px[1]-prev[1]), abs(px[2]-prev[2]))
        if d > 0:
            print(f"  y={y}: {prev} -> {px}  Δ={d}")
    prev = px
