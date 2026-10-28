"""Controlled server experiment: restore identical private snapshot, run same WAR and scenarios."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
from lab2_api import ROOT

label,isolation=sys.argv[1:3]
if isolation not in ('READ COMMITTED','SERIALIZABLE'):raise ValueError('Unsupported isolation')
out=ROOT/'verification/Lab2'/label;out.mkdir(parents=True,exist_ok=True)
def run(args,**kwargs):return subprocess.run(args,cwd=ROOT,check=True,**kwargs)
run(['python3.11','scripts/helios.py','stop'])
for i in range(45):
    result=subprocess.run(['python3.11','scripts/helios.py','status'],cwd=ROOT,capture_output=True,text=True,check=True)
    if 'Not running' in result.stdout:break
    time.sleep(1)
else:raise RuntimeError('Candidate did not stop')
run(['python3.11','scripts/lab2-test-state.py','restore'])
env=os.environ.copy();env.update(MOVIE_ISOLATION=isolation,JMETER_KEEP_GOING='1')
logfile=ROOT/'.runtime/payara.log';offset=logfile.stat().st_size
run(['python3.11','scripts/helios.py','start-test'],env=env)
for i in range(60):
    try:
        with urllib.request.urlopen('http://127.0.0.1:40797/movie-lab/api/auth',timeout=2) as response:
            if response.status==200:break
    except Exception:pass
    time.sleep(1)
else:raise RuntimeError('Candidate did not become ready')
config={'host':os.uname().nodename,'directory':str(ROOT),'isolation':isolation,'lock':'AppState FOR UPDATE',
 'rounds':int(env.get('JMETER_ROUNDS','20')),'attempts':3,'http':'127.0.0.1:40797',
 'warSha256':hashlib.sha256((ROOT/'target/movie-lab.war').read_bytes()).hexdigest(),
 'baselineDumpSha256':hashlib.sha256((ROOT/'.runtime/comparison-baseline.dump').read_bytes()).hexdigest()}
(out/'configuration.json').write_text(json.dumps(config,indent=2))
code=subprocess.run(['python3.11','scripts/lab2-jmeter.py',str(out)],cwd=ROOT,env=env).returncode
with logfile.open('rb') as stream:stream.seek(offset);logs=stream.read()
(out/'server.log').write_bytes(logs)
statistics={'jmeterRunnerExit':code,'serializationRetries':logs.count(b'Rolled-back serialization failure; retry='),
 'retryExhaustionHint':logs.count(b'40001'),'sameWAR':config['warSha256'],'sameBaseline':config['baselineDumpSha256']}
(out/'run-statistics.json').write_text(json.dumps(statistics,indent=2));print(json.dumps(statistics),flush=True)
sys.exit(code)
