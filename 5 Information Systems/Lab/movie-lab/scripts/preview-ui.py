"""Loopback-only frontend preview using the existing SSH-tunnel backend."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import mimetypes

ROOT = Path(__file__).resolve().parents[1] / 'src/main/webapp'


class Handler(BaseHTTPRequestHandler):
    def handle_request(self):
        if self.path.startswith('/movie-lab/api/'):
            data = self.rfile.read(int(self.headers.get('Content-Length', 0))) or None
            headers = {k: v for k, v in self.headers.items() if k.lower() not in ('host', 'connection', 'accept-encoding')}
            try:
                response = urlopen(Request('http://127.0.0.1:18082' + self.path,
                                          data=data, headers=headers, method=self.command), timeout=30)
            except HTTPError as error:
                response = error
            with response:
                body = response.read()
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ('transfer-encoding', 'content-length', 'connection', 'content-encoding'):
                        self.send_header(key, value)
        else:
            name = self.path.split('?', 1)[0].removeprefix('/movie-lab/') or 'index.html'
            if name not in ('index.html', 'app.js', 'style.css', 'ui-text.js', 'validation.js'):
                self.send_error(404)
                return
            body = (ROOT / name).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', (mimetypes.guess_type(name)[0] or 'text/plain') + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = do_PUT = do_DELETE = handle_request

    def log_message(self, *_):
        pass


if __name__ == '__main__':
    print('Preview: http://127.0.0.1:18085/movie-lab/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 18085), Handler).serve_forever()
