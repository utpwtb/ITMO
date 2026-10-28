"""Promote the exact tested WAR to already initialized production tables, then smoke-check."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
from lab2_api import ROOT
out=ROOT/'verification/Lab2/production';out.mkdir(parents=True,exist_ok=True)
def run(args,**kwargs):return subprocess.run(args,cwd=ROOT,check=True,**kwargs)
run(['python3.11','scripts/helios.py','stop'])
for _ in range(45):
    status=subprocess.run(['python3.11','scripts/helios.py','status'],cwd=ROOT,capture_output=True,text=True,check=True)
    if 'Not running' in status.stdout:break
    time.sleep(1)
else:raise RuntimeError('Old candidate is still running')
env=os.environ.copy();env.update(MOVIE_ISOLATION='READ COMMITTED',MOVIE_TARGET='production')
offset=(ROOT/'.runtime/payara.log').stat().st_size
run(['python3.11','scripts/helios.py','start'],env=env)
for _ in range(60):
    try:
        with urllib.request.urlopen('http://127.0.0.1:40797/movie-lab/api/auth',timeout=2) as response:
            if response.status==200:break
    except Exception:pass
    time.sleep(1)
else:raise RuntimeError('Production did not become ready')
run(['python3.11','scripts/lab2-functional.py','accounts'],env=env)
run(['python3.11','scripts/lab2-functional.py','run',str(out)],env=env)
run(['python3.11','scripts/lab2-deployment-check.py','snapshot',str(out/'initial-smoke.json')],env=env)
run(['python3.11','scripts/lab2-audit.py',str(out/'database-audit.json')],env=env)
expected=json.loads((ROOT/'verification/Lab2/final-RC/configuration.json').read_text())['warSha256']
actual=hashlib.sha256((ROOT/'target/movie-lab.war').read_bytes()).hexdigest();assert actual==expected
with (ROOT/'.runtime/payara.log').open('rb') as stream:stream.seek(offset);(out/'startup.log').write_bytes(stream.read())
manifest={'host':os.uname().nodename,'root':str(ROOT),'pid':int((ROOT/'.runtime/payara.pid').read_text()),
 'http':'127.0.0.1:40797','database':'pg:5432/studs','schema':'s407960','tablePrefix':'lab2_4101_',
 'persistenceUnit':'movies-helios','isolation':'READ COMMITTED','warSha256':actual,'sameAsFinalJMeterWAR':actual==expected}
(out/'deployment.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest),flush=True)
