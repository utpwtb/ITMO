"""Assemble requested source/report/raw evidence; validate every included source and result first."""
import hashlib
import json
from pathlib import Path
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
app=ROOT/'movie-lab'
source=json.loads((app/'source-manifest.json').read_text())
for name,expected in source.items():assert hashlib.sha256((app/name).read_bytes()).hexdigest()==expected,name
with tarfile.open(HERE/'source-final.tar.gz') as tar:
    for entry in tar:
        assert not any(part in ('.runtime','target','credentials','__pycache__') for part in Path(entry.name).parts),entry.name
rc=json.loads((HERE/'server/final-RC/summary.json').read_text())
assert len(rc)==13 and all(x['passed'] and x['completedRounds']==20 for x in rc)
assert sum(x['requests'] for x in rc)==1640 and sum(x['unexpected'] for x in rc)==0
stats=[ET.parse(p).getroot() for p in (HERE/'server/final/surefire-reports').glob('TEST-*.xml')]
assert sum(int(x.attrib['tests']) for x in stats)==140
assert all(int(x.attrib.get(k,'0'))==0 for x in stats for k in ('failures','errors','skipped'))
assert json.loads((HERE/'server/production/restart-result.json').read_text())['passed']
assert json.loads((HERE/'resume/runtime.json').read_text())['passed']
assert json.loads((HERE/'resume/last-row-check.json').read_text())['passed']
assert json.loads((HERE/'download-integrity.json').read_text())['allMatched']
ui=json.loads((HERE/'ui-review/deployment.json').read_text(encoding='utf-8'))
assert ui['passed'] and ui['allOtherWarEntriesUnchanged'] and ui['domainSnapshotUnchanged']
assert json.loads((HERE/'browser/final-ui-checks.json').read_text(encoding='utf-8'))['passed']
assert hashlib.sha256((HERE/'ui-review/movie-lab.war').read_bytes()).hexdigest()==ui['warSha256']
with zipfile.ZipFile(HERE/'server/final/movie-lab.war') as old, zipfile.ZipFile(HERE/'ui-review/movie-lab.war') as new:
    assert set(old.namelist())==set(new.namelist())
    assert sorted(n for n in old.namelist() if old.read(n)!=new.read(n))==ui['changedWarEntries']
pdf=ROOT/'report/Lab2/report.pdf'
reader=PdfReader(pdf)
assert len(reader.pages)==13 and 'Заключение' in reader.pages[-1].extract_text()
for name,expected in json.loads((ROOT/'report/Lab2/uml/source-hashes.json').read_text()).items():
    assert hashlib.sha256((app/name).read_bytes()).hexdigest()==expected,name

# Test secrets are checked in plain text artifacts without disclosing them.
test_passwords=[x['password'].encode() for x in json.loads((app/'.runtime/lab2-users.json').read_text())]
text_extensions={'.py','.java','.js','.groovy','.jmx','.md','.tex','.json','.jsonl','.xml','.txt','.log','.csv','.jtl','.sql','.html','.properties'}
scan=set(app/name for name in source)
scan.update(p for p in HERE.rglob('*') if p.is_file() and p.suffix.lower() in text_extensions)
leaks=[]
for path in scan:
    content=path.read_bytes()
    if any(secret in content for secret in test_passwords):leaks.append(str(path.relative_to(ROOT)))
    if path.suffix=='.xml' and b'<property name="MOVIE_DB_PASSWORD"' in content:leaks.append(str(path.relative_to(ROOT)))
assert not leaks,leaks

paths=set(app/name for name in source);paths.add(app/'source-manifest.json')
for path in (ROOT/'report/Lab2').rglob('*'):
    if path.is_file() and path.suffix.lower() in {'.tex','.pdf','.png','.svg','.dot','.json','.md','.txt','.otf'} and path.name!='main.pdf':paths.add(path)
paths.add(ROOT/'defense/Lab2/README.md')
names=['ACCEPTANCE.md','DEPLOYMENT.md','baseline.md','helios-environment.md','isolation-analysis.md','progress.md','progress-history.md',
       'source-final.tar.gz','lab2-server-evidence.tar.gz','unpack-evidence.py','download-integrity.json','source-final-verification.txt',
       'report-final-compile.log','recovery-language.sql','recovery-language.txt','resume-start.txt','resume-check.txt','last-row-check.txt']
paths.update(HERE/name for name in names)
paths.update(p for p in (HERE/'resume').rglob('*') if p.is_file())
paths.update(p for p in (HERE/'browser').glob('final-*') if p.is_file())
paths.update(p for p in (HERE/'ui-review').rglob('*') if p.is_file())
paths.add(Path(__file__).resolve())
for path in paths:
    assert path.is_file(),path
    assert path.resolve().is_relative_to(ROOT.resolve())
    assert '.runtime' not in path.relative_to(ROOT).parts
manifest={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
manifest_path=HERE/'delivery-manifest.json'
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(HERE/'lab2-delivery.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
    for path in sorted(paths):z.write(path,str(path.relative_to(ROOT)))
    z.write(manifest_path,str(manifest_path.relative_to(ROOT)))
result={'passed':True,'javaTests':140,'jmeterTargetRequests':1640,'jmeterScenarios':13,'jmeterUnexpectedFailures':0,
        'fullTestsWarSha256':ui['previousWarSha256'],'currentUiWarSha256':ui['warSha256'],'uiRevisionFullTestsRerun':False,
        'pdfPages':len(reader.pages),'sourceFiles':len(source),'textArtifactsScanned':len(scan),'testCredentialLeaks':0,
        'bundleFiles':len(paths)+1,'bundleSha256':hashlib.sha256((HERE/'lab2-delivery.zip').read_bytes()).hexdigest(),
        'reportSha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
        'sourceArchiveSha256':hashlib.sha256((HERE/'source-final.tar.gz').read_bytes()).hexdigest()}
(HERE/'delivery-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
