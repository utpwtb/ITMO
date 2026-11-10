from pathlib import Path
from urllib.parse import unquote
import re, csv, json, platform, subprocess, shutil
import pypdf, PIL

root=Path(__file__).resolve().parents[2]
notes=root/'Notes'
files=list(notes.rglob('*.md'))
lookup={p.relative_to(notes).with_suffix('').as_posix():p for p in files}
manifest=json.loads((notes/'_meta/材料清单.json').read_text(encoding='utf-8'))
counts={x['file']:x['pages'] for x in manifest}
errors=[]
links=0
wikis=0
source_refs=0
def prose(text):
    text=re.sub(r'(?ms)^(`{3,}).*?^\1\s*$','',text)
    return re.sub(r'`[^`\n]*`','',text)
for file in files:
    # The verbatim taskbook contains illustrative, intentionally unreal targets.
    if file.name=='执行任务书.md': continue
    content=file.read_text(encoding='utf-8')
    clean=prose(content)
    assert len(re.findall(r'^# ',content,re.M))==1,file
    if sum(1 for l in content.splitlines() if l.startswith('```'))%2:
        errors.append(f'{file.name}: unbalanced code fence')
    for target in re.findall(r'\[\[([^\]]+)\]\]',clean):
        target=target.split('|')[0]
        path,sep,heading=target.partition('#')
        dest=lookup.get(path)
        if not dest:
            matches=[p for key,p in lookup.items() if key.rsplit('/',1)[-1]==path]
            dest=matches[0] if len(matches)==1 else None
        if not dest: errors.append(f'{file.name}: missing wiki {target}');continue
        if sep:
            headers=re.findall(r'^#{1,6}\s+(.+?)\s*$',dest.read_text(encoding='utf-8'),re.M)
            if heading not in headers: errors.append(f'{file.name}: missing heading {target}')
        wikis+=1
    for url in re.findall(r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)',clean):
        url=url.strip().strip('<>')
        if re.match(r'^[a-z]+:',url):continue
        path,_,fragment=unquote(url).partition('#')
        dest=(file.parent/path).resolve()
        if not dest.exists(): errors.append(f'{file.name}: missing local {url}')
        if dest.suffix.lower()=='.pdf' and fragment.startswith('page='):
            page=int(fragment.removeprefix('page='))
            if not 1<=page<=counts.get(dest.name,0):errors.append(f'{file.name}: page out of bounds {url}')
            source_refs+=1
        links+=1

with (notes/'_meta/材料逐页定位.tsv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
for name,n in counts.items():
    seq=[int(r['PDF页序']) for r in rows if r['来源PDF']==name]
    if seq!=list(range(1,n+1)):errors.append(f'{name}: page sequence')
assert sum(counts.values())==880 and len(rows)==880
assert (notes/'_meta/执行任务书.md').read_bytes()==Path('C:/Users/CHL/.codex/visualizations/2026/11/03/01a1a39f-20b7-73f3-8407-b878ba92ecdd/知识图谱_Obsidian笔记执行计划.md').read_bytes()
result={'date':'2026-11-04','python':platform.python_version(),'pypdf':pypdf.__version__,'Pillow':PIL.__version__,
    'pdftoppm':subprocess.run([shutil.which('pdftoppm'),'-v'],capture_output=True,text=True).stderr.splitlines()[0],
    'source_files':len(manifest),'source_pages':len(rows),'markdown_files_checked':len(files)-1,
    'wiki_links_checked':wikis,'local_links_checked':links,'pdf_page_references_checked':source_refs,
    'taskbook_copy':'byte-identical','obsidian_render':'not performed; no running Obsidian process found',
    'errors':errors,'status':'PASS' if not errors else 'FAIL'}
(notes/'_meta/环境与核查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
