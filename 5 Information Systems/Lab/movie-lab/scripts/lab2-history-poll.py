"""Trigger only a failed import in production: history changes while movie revision stays fixed."""
import json
from pathlib import Path
import sys
from lab2_api import Client,credentials
client=Client('http://127.0.0.1:40797/movie-lab/api',**credentials()[3])
before=client.call('revision')[1]['revision']
status,result=client.call('imports','POST',file=('history-poll-failure.json',b'{invalid'))
after=client.call('revision')[1]['revision']
assert status==400 and before==after and result['status']=='FAILED'
out={'passed':True,'operationId':result['operationId'],'status':status,'code':result['code'],'revisionBefore':before,'revisionAfter':after,'actor':'lab2_admin_b'}
Path(sys.argv[1]).write_text(json.dumps(out,indent=2));print(json.dumps(out))
