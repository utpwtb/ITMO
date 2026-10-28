"""Verify the downloaded server archive and every original evidence file before review."""
import hashlib
import json
from pathlib import Path,PurePosixPath
import tarfile
ROOT=Path(__file__).resolve().parent
archive=ROOT/'lab2-server-evidence.tar.gz'
expected='7d5a228d1ab60cfbc68e3d62e42d5f56a4e12fe8974b3c88f66e16e31cd8b3d4'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
dest=(ROOT/'server').resolve();dest.mkdir(exist_ok=True)
with tarfile.open(archive) as tar:
    for member in tar:
        parts=PurePosixPath(member.name).parts
        if not parts or parts[0]!='Lab2' or '..' in parts:raise ValueError('Unexpected archive path')
        if len(parts)==1:continue
        member.name='/'.join(parts[1:])
        if not (member.isfile() or member.isdir()) or not (dest/member.name).resolve().is_relative_to(dest):raise ValueError('Unsafe archive entry')
        tar.extract(member,path=dest,filter='data')
manifest=json.loads((dest/'evidence-manifest.json').read_text())
errors=[]
for name,value in manifest.items():
    path=(dest/name).resolve()
    if not path.is_relative_to(dest) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=value:errors.append(name)
assert not errors,errors
war=dest/'final/movie-lab.war'
expected_war=json.loads((dest/'production/deployment.json').read_text())['warSha256']
assert hashlib.sha256(war.read_bytes()).hexdigest()==expected_war
(ROOT/'download-integrity.json').write_text(json.dumps({'archiveSha256':expected,'filesVerified':len(manifest),'allMatched':True,'warSha256':expected_war,'warMatched':True},indent=2))
print('Verified',len(manifest),'evidence files and exact production WAR')
