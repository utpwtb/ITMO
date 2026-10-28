"""Non-destructive production snapshot and restart assertion; never returns credentials/tokens."""
import json
from pathlib import Path
import subprocess
import sys
from lab2_api import Client,ROOT,credentials

def snapshot():
    users=credentials();clients=[Client('http://127.0.0.1:40797/movie-lab/api',**u) for u in users]
    actors=[]
    for client in clients:
        status,user=client.call('auth');assert status==200
        actors.append({k:user[k] for k in ('user','userId','role')})
    assert [x['role'] for x in actors]==['USER','USER','ADMIN','ADMIN']
    histories=[];page=0
    while True:
        status,result=clients[2].call('imports?page='+str(page)+'&size=100');assert status==200
        histories.extend(result['items'])
        if len(histories)>=result['total']:break
        page+=1
    query="""SELECT json_build_object(
      'movies',(SELECT json_agg(row_to_json(m) ORDER BY id) FROM lab2_4101_movie m),
      'peopleCount',(SELECT count(*) FROM lab2_4101_person),
      'coordinatesCount',(SELECT count(*) FROM lab2_4101_coordinates),
      'locationsCount',(SELECT count(*) FROM lab2_4101_location),
      'duplicateKeys',(SELECT count(*) FROM (SELECT name,director_id FROM lab2_4101_movie GROUP BY name,director_id HAVING count(*)>1) d),
      'badHistoryCounts',(SELECT count(*) FROM lab2_4101_import_operation WHERE (status='SUCCESS') IS DISTINCT FROM (added_count IS NOT NULL)))"""
    db=subprocess.run(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-Atc',query],capture_output=True,text=True,check=True)
    result={'actors':actors,'history':histories,'database':json.loads(db.stdout)}
    assert result['database']['duplicateKeys']==0 and result['database']['badHistoryCounts']==0
    api_movies=[];page=0
    while True:
        status,view=clients[2].call('movies?page='+str(page)+'&size=100');assert status==200
        api_movies.extend(view['items'])
        if len(api_movies)>=view['total']:break
        page+=1
    sql_movies=result['database']['movies'] or []
    assert sorted((str(m['id']),m['name']) for m in api_movies)==sorted((str(m['id']),m['name']) for m in sql_movies)
    for kind,count_field in [('people','peopleCount'),('coordinates','coordinatesCount'),('locations','locationsCount')]:
        status,view=clients[2].call(kind);assert status==200 and len(view)==result['database'][count_field]
    result['apiMatchesProductionTables']=True
    for client,user in zip(clients[:2],actors[:2]):
        status,owned=client.call('imports?userId=ignored&size=100');assert status==200
        assert all(row['user']==user['user'] for row in owned['items'])
    return result

mode=sys.argv[1];path=Path(sys.argv[2])
if mode=='snapshot':
    result=snapshot();path.write_text(json.dumps(result,indent=2));print('Production snapshot saved; roles/history/domain invariants pass')
elif mode=='after-restart':
    before=json.loads(path.read_text());after=snapshot()
    assert before['actors']==after['actors'] and before['database']==after['database']
    previous={x['id']:x for x in before['history']};actual={x['id']:x for x in after['history']}
    for id,old in previous.items():
        new=actual[id]
        assert new['userId']==old['userId'] and new['addedCount']==old['addedCount']
        if old['filename']=='restart-recovery-probe.json':assert old['status']=='RUNNING' and new['status']=='FAILED' and new['errorCode']=='INTERRUPTED'
        else:assert new['status']==old['status'] and new['finishedAt']==old['finishedAt']
    out=path.with_name('restart-result.json');out.write_text(json.dumps({'passed':True,'before':before,'after':after,'recoveryFixture':'Manually inserted orphan RUNNING, not an actual network-uncertain commit'},indent=2))
    print('Actual process restart passed: accounts, roles, terminal histories, movies preserved; orphan RUNNING recovered')
else:raise ValueError('snapshot|after-restart FILE')
