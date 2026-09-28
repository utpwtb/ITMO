"""Local PDF QA helper (optional dependency: PyMuPDF and Pillow)."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
if (ROOT / '.deps').exists():
    sys.path.insert(0, str(ROOT / '.deps'))
import pymupdf as fitz
from PIL import Image, ImageDraw

out = ROOT / 'tmp/qa'
out.mkdir(parents=True, exist_ok=True)
doc = fitz.open(ROOT / 'report/main.pdf')
images = []
for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=fitz.Matrix(1.35, 1.35))
    path = out / f'page-{i+1:02}.png'
    pix.save(path)
    im = Image.open(path).convert('RGB')
    im.thumbnail((500, 710))
    images.append(im)
    outside = [w[:5] for w in page.get_text('words') if
               w[0] < 20 or w[1] < 20 or w[2] > page.rect.width-20 or w[3] > page.rect.height-20]
    print(f'Page {i+1}: {len(page.get_text())} chars; {len(outside)} items near/outside margins')
for start in range(0, len(images), 4):
    contact = Image.new('RGB', (1040, 1490), '#e7e7e7')
    draw = ImageDraw.Draw(contact)
    for k, im in enumerate(images[start:start+4]):
        x, y = 10+(k%2)*520, 30+(k//2)*740
        contact.paste(im, (x, y))
        draw.text((x, y-20), f'Page {start+k+1}', fill='black')
    contact.save(out / f'contact-{start//4+1}.png')
print(f'Total pages: {len(doc)}')
