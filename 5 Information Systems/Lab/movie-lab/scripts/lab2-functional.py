"""Run real HTTP acceptance checks against the Helios candidate (test tables only)."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from lab2_api import Client,ROOT,credentials,import_movie

base=os.environ.get('MOVIE_API','http://127.0.0.1:40797/movie-lab/api')
mode=sys.argv[1]
if mode=='accounts':
    path=ROOT/'.runtime/lab2-users.json'
    if not path.exists():
        users=[{'username':'lab2_'+role,'password':secrets.token_urlsafe(24)} for role in ('user_a','user_b','admin_a','admin_b')]
        path.write_text(json.dumps(users));path.chmod(0o600)
    users=credentials()
    for user in users:
        client=Client(base)
        status,data=client.call('auth/register','POST',user)
        if status not in (201,409):raise RuntimeError('Account setup failed '+str(status))
        if 'admin' in user['username']:
            env=os.environ.copy();env.update(MOVIE_ADMIN_USER=user['username'],MOVIE_TARGET=os.environ.get('MOVIE_TARGET','test'))
            subprocess.run(['python3.11','scripts/helios.py','admin'],cwd=ROOT,env=env,check=True)
    print('Two ordinary users and two admins prepared; credentials excluded from evidence')
else:
    users=credentials(); clients=[Client(base,**u) for u in users]; a,b,admin,admin_b=clients
    run=secrets.token_hex(5); results=[]
    def check(name,condition,details=None):
        results.append({'case':name,'passed':bool(condition),'details':details})
        if not condition:raise AssertionError(name+': '+str(details))
    out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    try:
        check('H05 unauthenticated',Client(base).call('imports')[0]==401)
        check('H05 missing csrf',a.call('imports','POST',file=('x.json',b'{}'),csrf=False)[0]==403)
        check('H03 role escalation',Client(base).call('auth/register','POST',{'username':'escalation_'+run,'password':secrets.token_urlsafe(16),'role':'ADMIN'})[0]==400)
        before=a.call('imports')[1]['total']
        check('F10 missing file',a.call('imports','POST',data={})[0]==415)
        check('F10 wrong part media',a.call('imports','POST',file=('x.json',b'{}'),media='text/plain')[0]==415)
        check('F10 empty file',a.call('imports','POST',file=('x.json',b''))[0]==400)
        check('F10 oversize',a.call('imports','POST',file=('x.json',b' '*5242881))[0]==413)
        check('F10 entry rejections have no history',a.call('imports')[1]['total']==before)
        doc={'formatVersion':1,'movies':[import_movie(run+' one',run),import_movie(run+' two',run)]}
        status,data=a.upload(doc,'http-valid.json');check('F01 valid HTTP multipart',status==201 and data['addedCount']==2,data)
        operation=data['operationId'];check('H03 other user detail',b.call('imports/'+operation)[0]==404)
        check('H02 administrator detail',admin.call('imports/'+operation)[0]==200)
        check('H03 ignored userId parameter',b.call('imports?userId='+data['userId'])[1]['total']==b.call('imports')[1]['total'])
        status,failed=b.upload(doc,'duplicate.json');check('U06 duplicate upload',status==409 and failed['code']=='DUPLICATE_MOVIE',failed)
        check('H01 failed count null',b.call('imports/'+failed['operationId'])[1]['addedCount'] is None)
        status,syntax=a.call('imports','POST',file=('invalid.json',b'{invalid'))
        check('F10 accepted invalid JSON history',status==400 and a.call('imports/'+syntax['operationId'])[1]['status']=='FAILED',syntax)
        check('H02 admin total',admin.call('imports')[1]['total']>=a.call('imports')[1]['total']+b.call('imports')[1]['total'])
        check('H05 independent sessions',a.call('auth')[1]['user']!=b.call('auth')[1]['user'])
    finally:
        (out/'http-functional.json').write_text(json.dumps({'base':base,'results':results,'passed':all(x['passed'] for x in results)},indent=2))
    print(json.dumps({'checks':len(results),'passed':all(x['passed'] for x in results)}))
