"""Generate shared race fixtures, execute JMeter ON Helios, then verify DB + exact outcomes.

Only targets lab2_4101_test_ tables; credentials stay in .runtime. No destructive cleanup.
"""
import collections
import csv
import json
import os
from pathlib import Path
import secrets
import statistics
import subprocess
import sys
import time
from lab2_api import Client,ROOT,credentials,import_movie,movie

SCENARIOS=['C01','C02','C02D','C03','C04','C05','C06','C07','C08','C09','C10','C11','C12']
base=os.environ.get('MOVIE_API','http://127.0.0.1:40797/movie-lab/api')
users=credentials()
api=Client(base,**users[2])

def database():
    query="""select json_build_object(
      'movies',(select count(*) from lab2_4101_test_movie),
      'coordinates',(select count(*) from lab2_4101_test_coordinates),
      'people',(select count(*) from lab2_4101_test_person),
      'locations',(select count(*) from lab2_4101_test_location),
      'duplicates',(select count(*) from (select name,director_id from lab2_4101_test_movie group by name,director_id having count(*)>1) d),
      'orphans',(select count(*) from lab2_4101_test_movie m left join lab2_4101_test_coordinates c on c.id=m.coordinates_id where c.id is null),
      'histories',(select json_agg(json_build_object('id',id::text,'status',status,'count',added_count,'filename',filename)) from lab2_4101_test_import_operation))"""
    result=subprocess.run(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-Atc',query],capture_output=True,text=True,check=True)
    return json.loads(result.stdout)

def prepare(scenario,threads,rounds,out):
    marker='lab2-'+out.parent.name+'-'+scenario+'-'+secrets.token_hex(3)
    fixture={'scenario':scenario,'threads':threads,'rounds':[],'marker':marker}
    coordinates=api.create('coordinates',{'x':1,'y':1})['id']
    people=[api.create('people',{'name':'Same director name','birthday':'1980-01-01T00:00Z','passportID':marker+str(i)})['id'] for i in range(2)]
    def seed(name,director=None):return api.create('movies',movie(name,coordinates,director))
    for r in range(rounds):
        prefix=marker+'-r'+str(r)+'-'
        meta={'prefix':prefix,'actions':[]}
        actions=meta['actions']
        target=seed(prefix+'old') if scenario in ('C01','C02','C02D') else None
        if scenario=='C12':
            bonus=movie(prefix+'bonus',coordinates);bonus['length']=2147483647
            meta['bonus']=api.create('movies',bonus)['id']
        for i in range(threads):
            action={'method':'POST','path':'movies','expected':[201]}
            def update(object,body):
                return {'method':'PUT','path':'movies/'+object['id'],'body':dict(body,version=object['version']), 'read':'movies/'+object['id'],'version':object['version'],'expected':[200,409]}
            def delete(object):
                return {'method':'DELETE','path':'movies/'+object['id']+'?version='+str(object['version']),'read':'movies/'+object['id'],'version':object['version'],'expected':[200,404,409]}
            def upload(names,passport=None):
                document={'formatVersion':1,'movies':[import_movie(n,passport) for n in names]}
                file=out/f'r{r}-p{i}.json';file.write_text(json.dumps(document));
                return {'method':'POST','path':'imports','file':str(file.resolve()),'expected':[201,409],'code':'DUPLICATE_MOVIE'}
            if scenario=='C01':action=update(target,{'tagline':prefix+'winner'+str(i)});action['code']='VERSION_CONFLICT'
            elif scenario=='C02':action=update(target,{'tagline':prefix+'update'}) if i==0 else delete(target);action['expected']=[200,404,409]
            elif scenario=='C02D':action=delete(target)
            elif scenario in ('C03','C04'):
                action.update(body=movie(prefix+'same',coordinates,people[0] if scenario=='C03' else None),expected=[201,409],code='DUPLICATE_MOVIE')
            elif scenario=='C05':action['body']=movie(prefix+('same' if i<2 else 'different'+str(i)),coordinates,people[i%2])
            elif scenario=='C06':
                original=seed(prefix+'original'+str(i));action=update(original,{'name':prefix+'target'});action['code']='DUPLICATE_MOVIE'
            elif scenario=='C07':action=upload([prefix+'shared1',prefix+'shared2'],prefix+'passport')
            elif scenario=='C08':
                if i==0:action.update(body=movie(prefix+'shared',coordinates),expected=[201,409],code='DUPLICATE_MOVIE')
                else:action=upload([prefix+'unique',prefix+'shared'],prefix+'import-person')
                # Same null director is essential: person reuse must not mask movie-key race.
                if i>0:
                    doc=json.loads(Path(action['file']).read_text());doc['movies'][0]['director']=None;doc['movies'][1]['director']=None;Path(action['file']).write_text(json.dumps(doc))
            elif scenario=='C09':action=upload([prefix+'unique'+str(i),prefix+'shared'],prefix+'passport')
            elif scenario=='C10':
                if i==0:action=upload([prefix+'rollback',prefix+'rollback'],prefix+'rollback-person');action['expected']=[409]
                elif i%3==1:action['body']=movie(prefix+'create'+str(i),coordinates)
                elif i%3==2:action=update(seed(prefix+'edit'+str(i)),{'tagline':prefix+'edited'+str(i)});action['expected']=[200]
                else:action=delete(seed(prefix+'delete'+str(i)));action['expected']=[200]
            elif scenario=='C11':
                if i==0:action=upload([prefix+'first',prefix+'second'],prefix+'passport');action['expected']=[201]
                else:action={'method':'GET','path':'operations/prefix?value='+prefix,'expected':[200],'atomicRead':True}
            elif scenario=='C12':
                if i%5==0:action['body']=movie(prefix+'create'+str(i),coordinates)
                elif i%5==1:action=update(seed(prefix+'edit'+str(i)),{'tagline':prefix+'edited'+str(i)});action['expected']=[200]
                elif i%5==2:action=delete(seed(prefix+'delete'+str(i)));action['expected']=[200]
                elif i%5==3:action=upload([prefix+'import'+str(i)+'a',prefix+'import'+str(i)+'b'],prefix+'person'+str(i));action['expected']=[201]
                else:action={'method':'POST','path':'operations/award?length=10000&count=1','expected':[200]}
            actions.append(action)
        if target:meta['target']=target['id'];meta['targetVersion']=target['version']
        fixture['rounds'].append(meta)
    return fixture

def verify(fixture,records,before,after,out):
    errors=[]
    def check(value,message):
        if not value:errors.append(message)
    check(len(records)==len(fixture['rounds'])*fixture['threads'],'Missing target samples')
    check(all(x['passed'] for x in records),'Unexpected HTTP outcome')
    check(after['duplicates']==0,'Duplicate movie keys in DB');check(after['orphans']==0,'Orphan references')
    imported=0; new_people=0; new_locations=0
    histories={x['id']:x for x in (after['histories'] or [])}
    for r,meta in enumerate(fixture['rounds']):
        rows=sorted([x for x in records if x['round']==r],key=lambda x:x['participant']);statuses=collections.Counter(x['status'] for x in rows)
        scenario=fixture['scenario']; count=fixture['threads']
        prefix=meta['prefix']; movies=api.call('operations/prefix?value='+prefix)[1]
        if scenario in ('C01','C06'):check(statuses=={200:1,409:count-1},f'{r}: exact update winners {statuses}')
        if scenario=='C01':
            final=api.call('movies/'+meta['target'])[1];winner=next((x for x in rows if x['status']==200),None)
            check(winner is not None and final['version']==meta['targetVersion']+1 and final['tagline']==prefix+'winner'+str(winner['participant']),f'{r}: winner value/version')
        if scenario in ('C02','C02D'):
            check(statuses[200]==1 and statuses[404]+statuses[409]==count-1,f'{r}: delete/update winners {statuses}')
            exists=api.call('movies/'+meta['target'])[0]==200
            if scenario=='C02D':check(not exists,f'{r}: double delete final state')
            else:
                success=next((x for x in rows if x['status']==200),{})
                check(exists==(success.get('method')=='PUT'),f'{r}: update/delete final state')
                check(statuses[409 if exists else 404]==count-1,f'{r}: update/delete loser status')
        if scenario in ('C03','C04','C07','C08','C09'):check(statuses=={201:1,409:count-1},f'{r}: exact create/import winners {statuses}')
        if scenario=='C05':check(statuses=={201:count},f'{r}: independent legal keys')
        if scenario=='C06':check(sum(m['name']==prefix+'target' for m in movies)==1 and len(movies)==count,f'{r}: failed edit preserved')
        if scenario in ('C07','C09'):check(len(movies)==2,f'{r}: atomic winner file')
        if scenario=='C08':
            importer_won=any(x['method']=='POST' and x['path']=='imports' and x['status']==201 for x in rows)
            check(len(movies)==(2 if importer_won else 1),f'{r}: import loser unique row rollback')
        if scenario=='C10':
            check(not any(m['name']==prefix+'rollback' for m in movies),f'{r}: rollback domain residue')
            expected_creates=sum(1 for i in range(1,count) if i%3==1)
            check(statuses=={409:1,201:expected_creates,200:count-1-expected_creates},f'{r}: independent transactions commit')
            for i in range(1,count):
                if i%3==2:check(any(m['tagline']==prefix+'edited'+str(i) for m in movies),f'{r}: independent edit retained')
                if i%3==0:check(not any(m['name']==prefix+'delete'+str(i) for m in movies),f'{r}: independent delete retained')
        if scenario=='C11':check(len(movies)==2,f'{r}: final complete import')
        if scenario=='C12':
            awards=sum(1 for x in rows if x['path'].startswith('operations/award') and x['status']==200)
            # Every round's bonus exists throughout this scenario; all successful awards affect all bonus rows.
            total_awards=sum(1 for x in records if x['path'].startswith('operations/award') and x['status']==200)
            check(api.call('movies/'+meta['bonus'])[1]['oscarsCount']==1+total_awards,f'{r}: special operation no lost awards')
        for row in rows:
            if row['path']=='imports':
                op=histories.get(row['operationId']);check(op is not None,f'{r}: missing import history')
                if not op:continue
                success=row['status']==201
                check(op['status']==('SUCCESS' if success else 'FAILED'),f'{r}: history status matches commit')
                check(op['count']==(2 if success else None),f'{r}: history count')
                if success:
                    imported+=2
                    if scenario!='C08':new_people+=1;new_locations+=1
    check(after['coordinates']-before['coordinates']==imported,'Failed import coordinates residue / successful import count')
    check(after['people']-before['people']==new_people,'Failed import person residue')
    check(after['locations']-before['locations']==new_locations,'Failed import location residue')
    values=sorted(x['elapsed'] for x in records)
    result={'scenario':fixture['scenario'],'threads':fixture['threads'],'rounds':len(fixture['rounds']),
            'completedRounds':sum(sum(x['round']==r for x in records)==fixture['threads'] for r in range(len(fixture['rounds']))),
            'requests':len(records),'commits':sum(x['status'] in (200,201) and x['method']!='GET' for x in records),
            'expectedConflicts':sum(x['status'] in (404,409) for x in records),'unexpected':sum(not x['passed'] for x in records),
            'averageMs':statistics.mean(values) if values else None,'p95Ms':values[min(len(values)-1,int(len(values)*.95))] if values else None,
            'duplicates':after['duplicates'],'failedImportResidue':0 if not any('residue' in e for e in errors) else None,
            'passed':not errors,'errors':errors}
    (out/'assertions.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    run=Path(sys.argv[1]);run.mkdir(parents=True,exist_ok=True)
    rounds=int(os.environ.get('JMETER_ROUNDS','20'))
    requested=sys.argv[2:] or SCENARIOS
    results=[]
    for scenario in requested:
        threads=2 if scenario in ('C01','C02','C02D','C06','C08','C09') else 10
        out=run/scenario;out.mkdir()
        fixture=prepare(scenario,threads,rounds,out)
        (out/'fixture.json').write_text(json.dumps(fixture,indent=2))
        before=database();(out/'database-before.json').write_text(json.dumps(before,indent=2))
        env=os.environ.copy();env.update(JAVA_HOME='/usr/local/openjdk21',HEAP='-Xms64m -Xmx256m',JVM_ARGS='-XX:ActiveProcessorCount=2 -XX:MaxMetaspaceSize=160m')
        cmd=[str(ROOT/'tools/apache-jmeter-5.6.3/bin/jmeter'),'-n','-t','jmeter/lab2-concurrency.jmx',
             '-Jhost=127.0.0.1','-Jport=40797','-JbasePath=/movie-lab/api','-Jscenario='+scenario,
             '-Jthreads='+str(threads),'-Jrounds='+str(rounds),'-JfixtureFile='+str((out/'fixture.json').resolve()),
             '-JcredentialsFile='+str(ROOT/'.runtime/lab2-users.json'),'-JresultFile='+str((out/'responses.jsonl').resolve()),
             '-l',str(out/'results.jtl'),'-j',str(out/'jmeter.log'),'-e','-o',str(out/'html')]
        (out/'command.json').write_text(json.dumps(cmd,indent=2))
        started=time.time()
        with (out/'stdout.log').open('w') as log:code=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        after=database();(out/'database-after.json').write_text(json.dumps(after,indent=2))
        raw=out/'responses.jsonl';records=[json.loads(x) for x in raw.read_text().splitlines()] if raw.exists() else []
        result=verify(fixture,records,before,after,out)
        jtl=list(csv.DictReader((out/'results.jtl').open())) if (out/'results.jtl').exists() else []
        failed=[x for x in jtl if x['success']!='true']
        result.update(jmeterExit=code,jtlFailures=len(failed),elapsedSeconds=time.time()-started)
        if code or failed or not jtl:result['passed']=False;result['errors'].append('JMeter process/JTL setup or sampler failure')
        (out/'assertions.json').write_text(json.dumps(result,indent=2));results.append(result)
        (run/'summary.json').write_text(json.dumps(results,indent=2));print(json.dumps(result),flush=True)
        if not result['passed'] and os.environ.get('JMETER_KEEP_GOING')!='1':sys.exit(1)
    if not all(result['passed'] for result in results):sys.exit(1)
