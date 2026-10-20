"""Exercise only a project-owned PostgreSQL cluster; never connect to the user's server."""
from pathlib import Path
import argparse, json, os, re, shutil, socket, subprocess, sys, time
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
parser=argparse.ArgumentParser()
parser.add_argument('--finish-verification',action='store_true',help='Export metadata and verify lifecycle using the previously tested project-owned database')
options=parser.parse_args()
STAGE = Path(__file__).resolve().parents[1]
PROJECT = STAGE.parent
OUT = STAGE / 'verification'
OUT.mkdir(exist_ok=True)
DATA = PROJECT / '.tools' / 'pg-stage2-data'
MARKER = DATA / 'stage2-owned.txt'
PG_BIN = Path(shutil.which('psql') or r'C:\Program Files\PostgreSQL\17\bin\psql.exe').parent
DB = 'beauty_stage2_test'
env = dict(os.environ, PGCLIENTENCODING='UTF8', PGCONNECT_TIMEOUT='5')
env.pop('PGPASSWORD', None)
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

def run(cmd, data=None, timeout=60, check=True):
    args=[str(x) for x in cmd]
    if Path(args[0]).stem=='pg_ctl' and 'start' in args:
        # On Windows the detached server can inherit pipe handles. A log file
        # avoids waiting for EOF from a server that is intentionally still running.
        with (OUT/'pg_ctl-start.log').open('w',encoding='utf-8') as log:
            result=subprocess.run(args,input=data,text=True,stdout=log,stderr=subprocess.STDOUT,
                                  env=env,timeout=timeout,creationflags=HIDDEN)
        p=subprocess.CompletedProcess(args,result.returncode,(OUT/'pg_ctl-start.log').read_text(encoding='utf-8',errors='replace'),'')
    else:
        p = subprocess.run(args, input=data, text=True, encoding='utf-8', errors='replace',
                           capture_output=True, env=env, timeout=timeout, creationflags=HIDDEN)
    if check and p.returncode:
        raise RuntimeError(f'Command failed ({p.returncode}): {p.stdout[-1500:]}\n{p.stderr[-5000:]}')
    return p

if DATA.exists():
    if not MARKER.exists() or MARKER.read_text(encoding='utf-8') != str(PROJECT):
        raise RuntimeError('Refusing to use an unmarked cluster directory')
else:
    run([PG_BIN/'initdb.exe','-D',DATA,'--encoding=UTF8','--locale=C','--auth=trust','--username=stage2_admin'],timeout=45)
    MARKER.write_text(str(PROJECT),encoding='utf-8')

status = run([PG_BIN/'pg_ctl.exe','-D',DATA,'status'],check=False)
if status.returncode == 0:
    run([PG_BIN/'pg_ctl.exe','-D',DATA,'stop','-m','fast','-w'],timeout=30)
with socket.socket() as probe:
    probe.bind(('127.0.0.1',0))
    port = probe.getsockname()[1]
psql = [PG_BIN/'psql.exe','-X','-h','127.0.0.1','-p',str(port),'-U','stage2_admin','-v','ON_ERROR_STOP=1','-q','-A','-t']
(OUT/'local_test_connection.json').write_text(json.dumps({'host':'127.0.0.1','port':port,'user':'stage2_admin','database':DB,'pgdata':str(DATA),'server_stopped_after_tests':True},indent=2),encoding='utf-8')

def sql(code, database=DB, check=True):
    return run(psql+['-d',database], '\\set VERBOSITY verbose\n'+code,check=check)

def script(name,database=DB,variables=()):
    args=psql+['-d',database]
    for k,v in variables: args += ['-v',f'{k}={v}']
    return run(args+['-f',STAGE/'sql'/name])

started=False
results=[]
completed=False
if options.finish_verification:
    results=json.loads((OUT/'test_results.json').read_text(encoding='utf-8'))['checks']
    if not all(x['passed'] for x in results): raise RuntimeError('Cannot resume after a failed business check')
def record(name,ok,detail=''):
    results.append({'name':name,'passed':ok,'detail':detail})
    print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    if not ok: raise AssertionError(name+': '+detail)

try:
    run([PG_BIN/'pg_ctl.exe','-D',DATA,'-l',OUT/'postgres-test.log','-o',f'-h 127.0.0.1 -p {port} -c max_connections=20 -c timezone=Europe/Moscow','-w','-t','30','start'],timeout=40)
    started=True
    if not options.finish_verification:
        script('99_drop_database.sql','postgres',[('db_name',DB)])
        script('00_create_database.sql','postgres',[('db_name',DB)])
        script('install.sql',variables=[('with_demo_data','true')])
        record('create database and install schema with demo history',True)
        seed_counts=json.loads(sql("SELECT json_object_agg(table_name,n) FROM (SELECT table_name,(xpath('/row/c/text()',query_to_xml(format('SELECT count(*) AS c FROM beauty.%I',table_name),false,true,'')))[1]::text::bigint n FROM information_schema.tables WHERE table_schema='beauty' AND table_type='BASE TABLE') t;").stdout)
        (OUT/'seed_counts.json').write_text(json.dumps(seed_counts,ensure_ascii=False,indent=2),encoding='utf-8')
        sql("DO $$ BEGIN IF NOT EXISTS(SELECT FROM pg_roles WHERE rolname='beauty_test_backend') THEN CREATE ROLE beauty_test_backend NOLOGIN; END IF; IF NOT EXISTS(SELECT FROM pg_roles WHERE rolname='beauty_test_public') THEN CREATE ROLE beauty_test_public NOLOGIN; END IF; END $$;")
        script('06_grant_backend.sql',variables=[('backend_role','beauty_test_backend')])
    
        from cases import CASES
        for name,statement,expected,*options in CASES:
            isolation=options[0] if options else 'READ COMMITTED'
            p=sql(f"BEGIN ISOLATION LEVEL {isolation}; SET LOCAL TIME ZONE 'Europe/Moscow'; SET LOCAL statement_timeout='15s';\n{statement}\nROLLBACK;",check=False)
            codes=re.findall(r'ERROR:\s+([0-9A-Z]{5}):',p.stderr)
            ok=p.returncode==0 if expected is None else (p.returncode!=0 and expected in codes)
            record(name,ok,('expected '+str(expected)+', codes '+str(codes)+'; '+p.stderr[-1500:]) if not ok else ('rejected '+expected if expected else 'validated'))
    
        # Two real server sessions. Wait for session A to hold the named advisory lock,
        # then issue B while A's transaction remains open.
        races=[
          ('concurrent duplicate booking',"SELECT beauty.book_appointment(10001,3,3,(beauty.local_now()::date+1)+time '10:00',1125,35);", "SELECT beauty.book_appointment(10002,3,3,(beauty.local_now()::date+1)+time '10:00',1125,35);",'23P01'),
          ('booking versus schedule shortening',"SELECT beauty.book_appointment(10001,4,1,(beauty.local_now()::date+1)+time '10:00',725,45);", "UPDATE beauty.work_interval SET start_time='11:00' WHERE master_id=4 AND work_date=beauty.local_now()::date+1 AND start_time='09:00';",'23514'),
          ('concurrent duplicate review',"SELECT beauty.add_review(10002,40001,'MASTER',5::smallint,'race');", "SELECT beauty.add_review(10002,40001,'MASTER',4::smallint,'race');",'23505'),
          ('concurrent invitation consumption',"SELECT beauty.accept_invitation('demo-invitation-to-reissue','concurrent-password-2026');", "SELECT beauty.accept_invitation('demo-invitation-to-reissue','concurrent-password-2026');",'22023'),
        ]
        for name,a,b,expected in races:
            child=subprocess.Popen([str(x) for x in psql+['-d',DB]],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',env=env,creationflags=HIDDEN)
            child.stdin.write('\\set VERBOSITY verbose\nBEGIN; SET LOCAL TIME ZONE \'Europe/Moscow\'; '+a+' SELECT pg_sleep(2); COMMIT;\n')
            child.stdin.close(); child.stdin=None
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                q=sql("SELECT count(*) FROM pg_locks WHERE locktype='advisory' AND classid=407960 AND objid=409297 AND granted;").stdout.strip()
                if q=='1': break
                if child.poll() is not None: break
                time.sleep(.05)
            before=time.monotonic()
            second=sql('BEGIN; SET LOCAL lock_timeout=\'6s\'; '+b+' COMMIT;',check=False)
            elapsed=time.monotonic()-before
            first_out,first_err=child.communicate(timeout=10)
            codes=re.findall(r'ERROR:\s+([0-9A-Z]{5}):',second.stderr)
            record(name,child.returncode==0 and expected in codes and elapsed>1.0,
                   f'A={child.returncode}, B={codes}, waited={elapsed:.3f}s; '+first_err[-400:]+second.stderr[-400:])
    
        plans={}
        queries={
          'client_history':"SELECT appointment_id,start_at,status FROM beauty.appointment WHERE client_user_id=10001 ORDER BY start_at DESC LIMIT 20",
          'master_day':"SELECT appointment_id,start_at FROM beauty.appointment WHERE master_id=17 AND start_at>=beauty.local_now()::date-21 AND start_at<beauty.local_now()::date-20 ORDER BY start_at",
          'working_date':"SELECT start_time,end_time FROM beauty.work_interval WHERE master_id=17 AND work_date=beauty.local_now()::date+1 ORDER BY start_time",
          'busy_overlap':"SELECT appointment_id FROM beauty.appointment WHERE master_id=1 AND status='CONFIRMED' AND slot && tsrange(beauty.local_now()::date+1+time '09:15',beauty.local_now()::date+1+time '09:30','[)')",
          'service_and_price':"SELECT salon_id,price FROM beauty.salon_service WHERE is_active AND service_type_id=1 AND price BETWEEN 700 AND 750",
        }
        for name,query in queries.items():
            plans[name]={'query':query,'explain':json.loads(sql('EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) '+query+';').stdout)}
        (OUT/'explain_plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2),encoding='utf-8')
        record('EXPLAIN ANALYZE captured for five use-case queries',True)
    metadata_query=(STAGE/'tests'/'metadata.sql').read_text(encoding='utf-8')
    metadata=json.loads(sql(metadata_query).stdout)
    (OUT/'schema_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    record('live schema metadata exported',True)

    empty='beauty_stage2_empty'
    script('99_drop_database.sql','postgres',[('db_name',empty)])
    script('00_create_database.sql','postgres',[('db_name',empty)])
    script('install.sql',empty)
    record('production install without fixtures',sql("SELECT count(*) FROM information_schema.tables WHERE table_schema='beauty' AND table_type='BASE TABLE';",empty).stdout.strip()=='14')
    script('99_drop_database.sql','postgres',[('db_name',empty)])
    record('drop database script removes the isolated empty database',sql("SELECT count(*) FROM pg_database WHERE datname='beauty_stage2_empty';",'postgres').stdout.strip()=='0')
    completed=True
finally:
    if started: run([PG_BIN/'pg_ctl.exe','-D',DATA,'stop','-m','fast','-w'],timeout=30)
    (OUT/'test_results.json').write_text(json.dumps({'utc_finished':datetime.now(timezone.utc).isoformat(),'server_version':run([PG_BIN/'psql.exe','--version']).stdout.strip(),
      'passed':sum(x['passed'] for x in results),'total':len(results),'all_passed':completed and bool(results) and all(x['passed'] for x in results),'checks':results},ensure_ascii=False,indent=2),encoding='utf-8')
print(f"All {len(results)} checks passed. Isolated server stopped.")
