from pathlib import Path
import json, sys
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
s=Path(__file__).resolve().parents[1]
out=s/'tmp'/'qa'; out.mkdir(parents=True,exist_ok=True)
p=s/'output/pdf/stage2_report.pdf'
d=pdfium.PdfDocument(str(p))
thumbs=[]
for i,page in enumerate(d):
    im=page.render(scale=1.5).to_pil().convert('RGB'); im.save(out/f'page-{i+1:02d}.png')
    im.thumbnail((400,575)); tile=Image.new('RGB',(420,610),'#eeeeee'); tile.paste(im,((420-im.width)//2,25))
    ImageDraw.Draw(tile).text((10,5),f'Page {i+1}',fill='black'); thumbs.append(tile)
for start in range(0,len(thumbs),8):
    sheet=Image.new('RGB',(1680,1220),'white')
    for i,im in enumerate(thumbs[start:start+8]): sheet.paste(im,((i%4)*420,(i//4)*610))
    sheet.save(out/f'contact-{start//8+1}.png')
reader=PdfReader(str(p))
log=(s/'output/pdf/stage2_report.log').read_text(encoding='utf-8',errors='replace')
warnings=[x for x in log.splitlines() if any(y in x for y in ('Overfull','Underfull','Missing character'))]
result={'pages':len(reader.pages),'layout_warnings':warnings,'last_page_has_conclusion':'Заключение' in (reader.pages[-1].extract_text() or ''),'qa_directory':str(out)}
(s/'verification/pdf_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
