"""Server-only test-table probe: verify real HTTP lock timeout and capture deployed ORM error log."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from lab2_api import Client,ROOT,credentials
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
client=Client('http://127.0.0.1:40797/movie-lab/api',**credentials()[0])
holder=subprocess.Popen(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-At','-v','ON_ERROR_STOP=1'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
holder.stdin.write("BEGIN; SELECT id FROM lab2_4101_test_app_state WHERE id=1 FOR UPDATE; SELECT pg_sleep(12) /* lab2_4101_test_app_state */; ROLLBACK;\n");holder.stdin.close()
# Check the holder has entered pg_sleep after acquiring the row lock.
for i in range(30):
    probe=subprocess.run(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-Atc',"SELECT count(*) FROM pg_stat_activity WHERE usename=current_user AND wait_event='PgSleep' AND query LIKE '%lab2_4101_test_app_state%';"],capture_output=True,text=True,check=True)
    if probe.stdout.strip()=='1':break
    time.sleep(.1)
else:raise RuntimeError('Holder did not acquire test lock')
started=time.monotonic();status,body=client.call('coordinates','POST',{'x':1,'y':1});elapsed=time.monotonic()-started
holder.wait(timeout=20)
result={'status':status,'code':body.get('code'),'elapsedSeconds':elapsed,'expected':'503 DATABASE_TEMPORARY around 10 seconds','passed':status==503 and body.get('code')=='DATABASE_TEMPORARY' and 9<=elapsed<=12}
(out/'http-lock-timeout.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if not result['passed']:sys.exit(1)
