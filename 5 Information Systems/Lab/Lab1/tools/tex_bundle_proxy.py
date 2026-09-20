"""Local TeX bundle cache; all outbound requests target the public Tectonic bundle."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.request, time, subprocess, gzip
root=Path(__file__).resolve().parent
cache=root/'tex-ranges';cache.mkdir(exist_ok=True)
remote='https://data1b.fullyjustified.net/tlextras-2022.0r0.tar'
class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self):
  self.send_response(200);self.send_header('Accept-Ranges','bytes');self.end_headers()
 def do_GET(self):
  if self.path.endswith('.index.gz'):
   data=(root/'tex-index.gz').read_bytes();self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  byte_range=self.headers.get('Range')
  if not byte_range:
   self.send_response(200);self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length','0');self.end_headers();return
  start,end=map(int,byte_range.removeprefix('bytes=').split('-'))
  file=cache/f'{start}-{end}'
  try:
   if file.exists():data=file.read_bytes()
   else:
    request=urllib.request.Request(remote,headers={'Range':byte_range,'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(request,timeout=25) as response:
     if response.status!=206:raise RuntimeError('Expected HTTP 206')
     data=response.read()
    if len(data)!=end-start+1:raise RuntimeError('Range length mismatch')
    file.write_bytes(data)
    print(f'cached {start}-{end}: {len(data)} bytes',flush=True)
   self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/*');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  except Exception as e:
   print(str(e),flush=True);self.send_error(502,str(e))
 def log_message(self,*args):pass
print('TeX cache proxy on 127.0.0.1:18768',flush=True)
ThreadingHTTPServer(('127.0.0.1',18768),Handler).serve_forever()
