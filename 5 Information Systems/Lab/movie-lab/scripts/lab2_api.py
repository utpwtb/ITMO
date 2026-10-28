"""HTTP client shared by Helios fixture generation and verification; never logs credentials."""
import http.cookiejar
import json
from pathlib import Path
import secrets
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]

class Client:
    def __init__(self, base, username=None, password=None):
        self.base=base.rstrip('/')
        self.csrf=''
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        if username:
            status,data=self.call('auth','POST',{'username':username,'password':password})
            if status!=200: raise RuntimeError('HTTP login failed: '+str(status))
            self.csrf=data['csrf']

    def call(self,path,method='GET',data=None,file=None,csrf=True,media='application/json'):
        headers={}
        if csrf:headers['X-CSRF-Token']=self.csrf
        if file is not None:
            boundary='movie-lab-'+secrets.token_hex(12)
            filename,content=file
            payload=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {media}\r\n\r\n').encode()+content+f'\r\n--{boundary}--\r\n'.encode()
            headers['Content-Type']='multipart/form-data; boundary='+boundary
        else:
            payload=None if data is None else json.dumps(data,ensure_ascii=False).encode()
            if payload is not None:headers['Content-Type']='application/json'
        req=urllib.request.Request(self.base+'/'+path,data=payload,headers=headers,method=method)
        try:
            response=self.opener.open(req,timeout=40)
        except urllib.error.HTTPError as error:response=error
        raw=response.read()
        try:result=json.loads(raw)
        except ValueError:result={'error':'Non-JSON response','preview':raw[:200].decode(errors='replace')}
        return response.status,result

    def create(self,kind,data):
        status,result=self.call(kind,'POST',data)
        if status!=201:raise RuntimeError(f'Fixture {kind} failed {status}: {result}')
        return result

    def upload(self,document,filename='fixture.json'):
        return self.call('imports','POST',file=(filename,json.dumps(document,ensure_ascii=False).encode()))

def credentials():
    return json.loads((ROOT/'.runtime/lab2-users.json').read_text())

def import_movie(name,passport=None):
    return {'name':name,'coordinates':{'x':1,'y':-2},'oscarsCount':1,'budget':'9007199254740993',
            'totalBoxOffice':None,'mpaaRating':'PG','length':120,'usaBoxOffice':1,'tagline':name,'genre':'COMEDY',
            'director':None if passport is None else {'name':'Import director','birthday':'1980-01-01T00:00:00Z',
              'passportID':passport,'location':{'x':'9007199254740993','y':-1.5,'name':'Test location'}}}

def movie(name,coordinates,director=None):
    result=import_movie(name)
    result['coordinates']=coordinates
    result['director']=director
    return result
