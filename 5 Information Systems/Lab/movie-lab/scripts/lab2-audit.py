"""Read-only PostgreSQL audit of production rules and untouched Lab1 fingerprints."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from lab2_api import ROOT
def query(sql):
    result=subprocess.run(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-Atc',sql],capture_output=True,text=True,check=True)
    return result.stdout.strip()
tables=['coordinates','location','person','movie','app_state','app_user']
fingerprints={table:query("SELECT md5(coalesce(string_agg(md5(row_to_json(row_record.*)::text),'' ORDER BY id),'')) FROM (SELECT "+
    ('id,username,password_hash,salt,iterations' if table=='app_user' else '*')+' FROM lab1_4101_'+table+') row_record;') for table in tables}
baseline=json.loads((ROOT/'verification/Lab2/candidate/migration.json').read_text())['fingerprintsBefore']
constraints=json.loads(query("SELECT coalesce(json_agg(row_to_json(r)), '[]'::json) FROM (SELECT c.conname,c.contype,pg_get_constraintdef(c.oid) AS definition FROM pg_constraint c WHERE c.conrelid IN ('lab2_4101_movie'::regclass,'lab2_4101_person'::regclass,'lab2_4101_app_user'::regclass) ORDER BY c.conname) r;"))
indexes=json.loads(query("SELECT coalesce(json_agg(row_to_json(r)), '[]'::json) FROM (SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='s407960' AND tablename IN ('lab2_4101_movie','lab2_4101_person','lab2_4101_app_user') ORDER BY indexname) r;"))
no_unique=query("SELECT count(*) FROM pg_index WHERE indrelid='lab2_4101_movie'::regclass AND indisunique AND NOT indisprimary;")=='0'
no_trigger=query("SELECT count(*) FROM pg_trigger WHERE tgrelid='lab2_4101_movie'::regclass AND NOT tgisinternal;")=='0'
result={'lab1FingerprintsBefore':baseline,'lab1FingerprintsAfter':fingerprints,'lab1Unchanged':baseline==fingerprints,
 'constraints':constraints,'indexes':indexes,'noMovieCombinationUniqueIndex':no_unique,'noMovieUserTrigger':no_trigger,
 'warSha256':hashlib.sha256((ROOT/'target/movie-lab.war').read_bytes()).hexdigest(),
 'passed':baseline==fingerprints and no_unique and no_trigger}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2));print(json.dumps({'passed':result['passed'],'lab1Unchanged':result['lab1Unchanged'],'warSha256':result['warSha256']}))
if not result['passed']:sys.exit(1)
