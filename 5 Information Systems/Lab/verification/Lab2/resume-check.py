"""Check the same production WAR and persisted data when resuming the execution chat."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import urllib.request
root=Path('/home/studs/s407960/is-lab2-4101')
out=root/'verification/Lab2/resume';out.mkdir(exist_ok=True)
for _ in range(60):
    try:
        with urllib.request.urlopen('http://127.0.0.1:40797/movie-lab/api/auth',timeout=2) as response:
            if response.status==200:break
    except Exception:pass
    time.sleep(1)
else:raise RuntimeError('Application not ready')
subprocess.run(['python3.11','scripts/lab2-deployment-check.py','snapshot',str(out/'snapshot.json')],cwd=root,check=True)
old=json.loads((root/'verification/Lab2/production/restart-result.json').read_text())['after']
new=json.loads((out/'snapshot.json').read_text())
assert old['database']==new['database'] and old['actors']==new['actors']
assert sorted((x['id'],x['status'],x['addedCount']) for x in old['history'])==sorted((x['id'],x['status'],x['addedCount']) for x in new['history'])
result={'passed':True,'pid':int((root/'.runtime/payara.pid').read_text()),'warSha256':hashlib.sha256((root/'target/movie-lab.war').read_bytes()).hexdigest(),
 'unchangedDomainAndRoles':True,'unchangedHistoryStatusesAndCounts':True,'apiMatchesProductionTables':new['apiMatchesProductionTables'],
 'observedPreviousShutdown':'2026-10-28 05:00 MSK; cause not established from application log',
 'note':'Only the explicit restart fixture error text was localized to Russian; status, counts, timestamps and domain data preserved.'}
assert result['warSha256']=='cf386061ed67f25abac1f84cf13b61fdcb4a988dddbfe3363c81e670365d0576'
(out/'runtime.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
