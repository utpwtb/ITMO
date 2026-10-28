"""Restart actual production process and verify persistence/recovery with an explicit SQL fixture."""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
from lab2_api import ROOT
out=ROOT/'verification/Lab2/production'
def run(args,**kwargs):return subprocess.run(args,cwd=ROOT,check=True,**kwargs)
fixture="INSERT INTO lab2_4101_import_operation(user_id,status,started_at,filename) SELECT id,'RUNNING',now()-interval '5 minutes','restart-recovery-probe.json' FROM lab2_4101_app_user WHERE username='lab2_user_a' RETURNING id;"
run(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-v','ON_ERROR_STOP=1','-c',fixture])
run(['python3.11','scripts/lab2-deployment-check.py','snapshot',str(out/'before-restart.json')])
run(['python3.11','scripts/helios.py','stop'])
for _ in range(45):
    status=subprocess.run(['python3.11','scripts/helios.py','status'],cwd=ROOT,capture_output=True,text=True,check=True)
    if 'Not running' in status.stdout:break
    time.sleep(1)
else:raise RuntimeError('Previous production process still exists')
offset=(ROOT/'.runtime/payara.log').stat().st_size
env=os.environ.copy();env.update(MOVIE_ISOLATION='READ COMMITTED',MOVIE_TARGET='production')
run(['python3.11','scripts/helios.py','start'],env=env)
for _ in range(60):
    try:
        with urllib.request.urlopen('http://127.0.0.1:40797/movie-lab/api/auth',timeout=2) as response:
            if response.status==200:break
    except Exception:pass
    time.sleep(1)
else:raise RuntimeError('Restarted application not ready')
run(['python3.11','scripts/lab2-deployment-check.py','after-restart',str(out/'before-restart.json')])
run(['python3.11','scripts/lab2-audit.py',str(out/'database-audit.json')])
deployment=json.loads((out/'deployment.json').read_text());deployment['previousPid']=deployment['pid']
deployment['pid']=int((ROOT/'.runtime/payara.pid').read_text());deployment['restartVerified']=True
(out/'deployment.json').write_text(json.dumps(deployment,indent=2))
with (ROOT/'.runtime/payara.log').open('rb') as stream:stream.seek(offset);(out/'restart.log').write_bytes(stream.read())
print(json.dumps({'passed':True,'pid':deployment['pid'],'restartVerified':True}),flush=True)
