"""Create a source-only reproducible-content manifest and archive (never .runtime/credentials)."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
ROOT=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]);out.parent.mkdir(parents=True,exist_ok=True)
allowed={'src','database','scripts','jmeter','docs'}
paths=[p for p in ROOT.rglob('*') if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or len(p.relative_to(ROOT).parts)==1 and p.name in ('pom.xml','README.md')) and '__pycache__' not in p.parts]
manifest={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
(ROOT/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with tarfile.open(out,'w:gz') as tar:
    for p in sorted(paths)+[ROOT/'source-manifest.json']:tar.add(p,arcname=str(p.relative_to(ROOT)))
print('Source SHA256 '+hashlib.sha256(out.read_bytes()).hexdigest())
