"""Deploy only the five UI assets; keep Java classes and the database untouched.

Uses the existing SSH account and its normal interactive authentication. No
credential is stored. Builds and verifies a WAR before restarting the service.
"""
import base64
import json
from pathlib import Path
import subprocess
import zlib

source = Path(__file__).resolve().parents[1] / 'src/main/webapp'
files = {name: (source / name).read_text(encoding='utf-8')
         for name in ('index.html', 'app.js', 'style.css', 'ui-text.js', 'validation.js')}
payload = base64.b64encode(zlib.compress(json.dumps(files, ensure_ascii=False).encode())).decode()
remote = r'''
import base64, datetime, hashlib, json, os, shutil, subprocess, time, urllib.request, zipfile, zlib
from pathlib import Path
root = Path('/home/studs/s407960/is-lab1-4101')
os.chdir(root)
files = json.loads(zlib.decompress(base64.b64decode(PAYLOAD)))
war = root / 'target/movie-lab.war'
backup = root / '.runtime' / ('frontend-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir()
shutil.copy2(war, backup / 'movie-lab.previous.war')
new_war = backup / 'movie-lab.new.war'
with zipfile.ZipFile(war) as old, zipfile.ZipFile(new_war, 'w') as new:
    for info in old.infolist():
        if info.filename not in files and info.filename != 'i18n.js':
            new.writestr(info, old.read(info.filename))
    for name, text in files.items():
        new.writestr(name, text.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(new_war) as new:
    for name, text in files.items():
        assert new.read(name) == text.encode('utf-8'), name
    assert 'i18n.js' not in new.namelist()
print('WAR verified; backup:', backup, flush=True)
for name, text in files.items():
    path = root / 'src/main/webapp' / name
    path.write_text(text, encoding='utf-8')
(root / 'src/main/webapp/i18n.js').unlink(missing_ok=True)

def helper(mode):
    return subprocess.check_output(['python3.11', 'scripts/helios.py', mode], text=True).strip()
print(helper('stop'), flush=True)
for attempt in range(40):
    if helper('status') == 'Not running':
        break
    time.sleep(1)
else:
    raise RuntimeError('Service did not stop; existing WAR was not replaced')
os.replace(new_war, war)
print(helper('start'), flush=True)
ready = False
for attempt in range(90):
    try:
        with urllib.request.urlopen('http://127.0.0.1:40796/movie-lab/ui-text.js', timeout=2) as response:
            ready = response.status == 200 and response.read() == files['ui-text.js'].encode('utf-8')
        if ready:
            break
    except Exception:
        pass
    time.sleep(1)
if not ready:
    print(helper('stop'), flush=True)
    for attempt in range(40):
        if helper('status') == 'Not running':
            break
        time.sleep(1)
    else:
        raise RuntimeError('New service did not stop; manual rollback required: ' + str(backup))
    shutil.copy2(backup / 'movie-lab.previous.war', war)
    print(helper('start'), flush=True)
    raise RuntimeError('New deployment failed readiness check; previous WAR restored')
hashes = {}
for name, text in files.items():
    with urllib.request.urlopen('http://127.0.0.1:40796/movie-lab/' + name, timeout=10) as response:
        served = response.read()
    assert served == text.encode('utf-8'), 'Served file differs: ' + name
    hashes[name] = hashlib.sha256(served).hexdigest()
(backup / 'verification.json').write_text(json.dumps(hashes, indent=2))
print('DEPLOYED ' + json.dumps(hashes), flush=True)
'''.replace('PAYLOAD', repr(payload))
program = base64.b64encode(zlib.compress(remote.encode())).decode()
command = 'python3.11 -u -c "import base64,zlib; exec(zlib.decompress(base64.b64decode(\'' + program + '\')))"'
if len(command) > 28000:
    raise RuntimeError('SSH command exceeds the safe Windows command-line size')
raise SystemExit(subprocess.call(['ssh', '-tt', '-o', 'ServerAliveInterval=10', '-o', 'ServerAliveCountMax=3',
    '-p', '2222', 's407960@helios.cs.ifmo.ru', command]))
