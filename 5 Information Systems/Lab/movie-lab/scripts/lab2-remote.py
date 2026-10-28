"""Local Windows SSH transport. DPAPI credential stays in process memory.

Usage: python scripts/lab2-remote.py exec COMMAND
       python scripts/lab2-remote.py put LOCAL REMOTE
       python scripts/lab2-remote.py get REMOTE LOCAL
       python scripts/lab2-remote.py tunnel [LOCAL_PORT] [REMOTE_PORT]
"""
import json
import os
from pathlib import Path
import socketserver
import select
import subprocess
import sys
import paramiko

def connect():
    command = "$c=Import-Clixml -LiteralPath 'C:\\Users\\CHL\\AppData\\Local\\MovieLab\\credentials\\helios-s407960-lab2.clixml'; @{user=$c.UserName;password=($c.GetNetworkCredential().Password)}|ConvertTo-Json -Compress"
    result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', command], capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace'))
    credential = json.loads(result.stdout.decode('utf-8-sig'))
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home()/'.ssh/known_hosts'))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect('helios.cs.ifmo.ru', port=2222, username=credential['user'], password=credential['password'], look_for_keys=False, allow_agent=False, timeout=25)
    client.get_transport().set_keepalive(30)
    credential.clear()
    return client

def main():
    client = connect()
    try:
        mode = sys.argv[1]
        if mode == 'exec':
            _, stdout, stderr = client.exec_command(sys.argv[2], get_pty=False)
            channel = stdout.channel
            while True:
                ready, _, _ = select.select([channel], [], [], 1)
                if ready:
                    if channel.recv_ready():
                        sys.stdout.buffer.write(channel.recv(65536)); sys.stdout.buffer.flush()
                    if channel.recv_stderr_ready():
                        sys.stderr.buffer.write(channel.recv_stderr(65536)); sys.stderr.buffer.flush()
                if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready(): break
            return channel.recv_exit_status()
        if mode in ('put', 'get'):
            with client.open_sftp() as sftp:
                getattr(sftp, mode)(sys.argv[2], sys.argv[3])
            return 0
        if mode == 'tunnel':
            local = int(sys.argv[2]) if len(sys.argv)>2 else 18083
            remote = int(sys.argv[3]) if len(sys.argv)>3 else 40797
            class Handler(socketserver.BaseRequestHandler):
                def handle(self):
                    chan = client.get_transport().open_channel('direct-tcpip', ('127.0.0.1',remote), self.request.getpeername())
                    try:
                        while True:
                            readable, _, _ = select.select([self.request,chan],[],[])
                            for source in readable:
                                data=source.recv(65536)
                                if not data: return
                                (chan if source is self.request else self.request).sendall(data)
                    finally: chan.close()
            class Server(socketserver.ThreadingTCPServer):
                allow_reuse_address=True
                daemon_threads=True
            with Server(('127.0.0.1',local),Handler) as server:
                print(f'Helios tunnel 127.0.0.1:{local} -> 127.0.0.1:{remote}',flush=True)
                server.serve_forever()
        raise ValueError('Unknown mode')
    finally: client.close()

if __name__ == '__main__':
    sys.exit(main())
