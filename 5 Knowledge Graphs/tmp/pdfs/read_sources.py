from pathlib import Path
from pypdf import PdfReader
import json

root = Path(__file__).resolve().parents[2]
out = root / 'tmp' / 'pdfs'
pages = {}
for path in sorted((root / 'Lecture').glob('*.pdf')):
    reader = PdfReader(path)
    texts = [p.extract_text(extraction_mode='layout') for p in reader.pages]
    pages[path.name] = texts
    (out / (path.stem + '.txt')).write_text('\n\n'.join(f'=== PDF PAGE {i} ===\n{t}' for i,t in enumerate(texts,1)), encoding='utf-8')
    print(path.name, len(texts), 'pages;', sum(len(t) for t in texts), 'chars')
(out / 'pages.json').write_text(json.dumps(pages,ensure_ascii=False), encoding='utf-8')
(out / 'page-headings.txt').write_text('\n'.join(f'{name}\n' + '\n'.join(f'{i:03d}: '+ ' | '.join([s.strip() for s in t.splitlines() if s.strip()][:3])[:230] for i,t in enumerate(texts,1)) for name,texts in pages.items()),encoding='utf-8')
