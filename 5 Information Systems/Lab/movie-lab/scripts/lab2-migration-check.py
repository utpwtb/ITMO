"""Copy Lab 1 data into narrowly named test tables and migrate twice; never alters Lab 1."""
from pathlib import Path
import json
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
prefix='lab2_4101_test_upgrade_'
tables=['coordinates','location','person','movie','app_state','app_user']
def mapped(sql):
    sql=re.sub(r'\b(movie|person|coordinates|location|app_state|app_user|import_operation)\b',lambda m:prefix+m[0],sql)
    return re.sub(r'\b(movie_[a-z_]+_idx|person_location_idx|import_operation_user_idx)\b',lambda m:prefix+m[0],sql)
def query(sql):
    result=subprocess.run(['psql','-X','-h','pg','-d','studs','-U','s407960','-w','-v','ON_ERROR_STOP=1','-At'],input=sql,text=True,capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr)
    return result.stdout.strip()
def summary():
    return {table:query('SELECT count(*) FROM '+prefix+table+';') for table in tables}
def fingerprints():
    return {table:query("SELECT md5(coalesce(string_agg(md5(row_to_json(row_record.*)::text),'' ORDER BY id),'')) FROM (SELECT "+
       ('id,username,password_hash,salt,iterations' if table=='app_user' else '*')+' FROM '+prefix+table+') row_record;') for table in tables}
old=ROOT/'baseline/database/schema.sql'
if not old.exists():sys.exit('Keep the original baseline/database/schema.sql for migration validation')
created=False
try:
    query('BEGIN;\n'+mapped(old.read_text())+'\nCOMMIT;');created=True
    for table in tables:
        query('BEGIN; DELETE FROM '+prefix+table+'; INSERT INTO '+prefix+table+' OVERRIDING SYSTEM VALUE SELECT * FROM lab1_4101_'+table+'; COMMIT;')
    before=summary();hash_before=fingerprints()
    ddl='\n'.join(mapped(p.read_text()) for p in sorted((ROOT/'database/migrations').glob('*.sql')))
    query('BEGIN;'+ddl+'COMMIT;');query('BEGIN;'+ddl+'COMMIT;')
    after=summary();hash_after=fingerprints()
    roles=query("SELECT count(*) FROM "+prefix+"app_user WHERE role <> 'USER';")
    result={'source':'read-only lab1_4101_ copy','target':prefix,'before':before,'after':after,
      'fingerprintsBefore':hash_before,'fingerprintsAfter':hash_after,'migrationsApplied':2,
      'allExistingUsersDefaultUSER':roles=='0','passed':before==after and hash_before==hash_after and roles=='0'}
    Path(sys.argv[1]).write_text(json.dumps(result,indent=2));print(json.dumps(result))
    if not result['passed']:sys.exit(1)
finally:
    if created:query('DROP TABLE IF EXISTS '+','.join(prefix+t for t in ['import_operation','movie','person','coordinates','location','app_state','app_user'])+';')
