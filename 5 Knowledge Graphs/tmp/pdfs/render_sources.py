from pathlib import Path
from PIL import Image, ImageDraw
import subprocess, shutil, sys

root = Path(__file__).resolve().parents[2]
folder = root / 'tmp' / 'pdfs'
name, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
path = next((root / 'Lecture').glob(name))
dest = folder / path.stem
dest.mkdir(exist_ok=True)
subprocess.run([shutil.which('pdftoppm'), '-f',str(start),'-l',str(end),'-scale-to','1100','-png',str(path),str(dest/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
files = sorted(dest.glob('page-*.png'))
for idx in range(0,len(files),4):
    subset = files[idx:idx+4]
    sheet = Image.new('RGB',(2200,1320),'#dddddd')
    draw = ImageDraw.Draw(sheet)
    for j,f in enumerate(subset):
        im = Image.open(f).convert('RGB')
        im.thumbnail((1090,620))
        x,y=(j%2)*1100,(j//2)*660
        sheet.paste(im,(x,y+30))
        draw.text((x+10,y+5),path.stem+' / PDF '+str(int(f.stem.split('-')[-1])),fill='black')
    sheet.save(dest/f'sheet-{idx//4+1:02}.png')
print(path.name, 'rendered',len(files),'pages;', (len(files)+3)//4,'sheets')
