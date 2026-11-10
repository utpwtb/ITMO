"""HTTP F03: valid first record, invalid final length; four domain tables and revision unchanged."""
import json
import os
import secrets
from pathlib import Path
import subprocess
import sys
from lab2_api import Client,ROOT,credentials
client=Client('http://127.0.0.1:40797/movie-lab/api',**credentials()[0])
prefix='lab2_4101_test_' if os.environ.get('MOVIE_TARGET')=='test' else 'lab2_4101_'
def counts():
    sql=f"SELECT json_build_object('Movie',(SELECT count(*) FROM {prefix}movie),'Person',(SELECT count(*) FROM {prefix}person),'Coordinates',(SELECT count(*) FROM {prefix}coordinates),'Location',(SELECT count(*) FROM {prefix}location));"
    return json.loads(subprocess.run(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-Atc',sql],capture_output=True,text=True,check=True).stdout)
before=counts();revision=client.call('revision')[1]['revision']
document=json.loads((ROOT/'src/test/resources/import/invalid-last-field.json').read_bytes())
run=secrets.token_hex(6)
for movie in document['movies']:
    movie['name']+=' '+run
    for role in ('director','screenwriter','operator'):
        if movie.get(role):movie[role]['passportID']+='-'+run
status,error=client.call('imports','POST',file=('invalid-last-field.json',json.dumps(document).encode()))
after=counts();next_revision=client.call('revision')[1]['revision']
assert status==400 and error['recordNumber']==2 and error['path']=='movies[1].length'
history=client.call('imports/'+error['operationId'])[1]
assert before==after and revision==next_revision and history['status']=='FAILED' and history['addedCount'] is None
result={'passed':True,'status':status,'error':error,'before':before,'after':after,'revisionBefore':revision,'revisionAfter':next_revision,'history':history,'freshFixtureRunId':run,'firstRecordName':document['movies'][0]['name']}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2));print(json.dumps({'passed':True,'path':error['path'],'operationId':error['operationId'],'noDomainChange':before==after}))
