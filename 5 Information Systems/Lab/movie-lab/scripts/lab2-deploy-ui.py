"""Build a UI-only revision on Helios, retain the tested backend, and record live evidence.

Run in the existing production deployment: python3.11 scripts/lab2-deploy-ui.py
Optional `poll` creates a deliberately malformed import for the first test user,
so an already-open history page can prove automatic polling without a revision change.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from lab2_api import Client, credentials

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/Lab2/ui-review'
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:40797/movie-lab/'
ASSETS = {'index.html', 'app.js', 'ui-text.js', 'style.css'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def client():
    return Client(BASE + 'api', **credentials()[0])


def snapshot():
    api = client()
    result = {}
    for path in ('revision', 'movies?size=50', 'people?size=50', 'coordinates?size=50', 'locations?size=50'):
        status, data = api.call(path)
        assert status == 200, (path, status)
        result[path] = data
    return result


def own_status():
    return subprocess.check_output(['python3.11', 'scripts/helios.py', 'status'], cwd=ROOT, text=True).strip()


def stop():
    subprocess.run(['python3.11', 'scripts/helios.py', 'stop'], cwd=ROOT, check=True)
    for _ in range(60):
        if own_status() == 'Not running':
            return
        time.sleep(1)
    raise RuntimeError('Previous deployment process did not stop')


def start():
    env = os.environ.copy()
    env['MOVIE_ISOLATION'] = 'READ COMMITTED'
    subprocess.run(['python3.11', 'scripts/helios.py', 'start'], cwd=ROOT, env=env, check=True)
    with zipfile.ZipFile(ROOT / 'target/movie-lab.war') as archive:
        expected = {name: archive.read(name) for name in ASSETS}
    for _ in range(120):
        try:
            with urllib.request.urlopen(BASE + 'api/auth', timeout=3) as response:
                # Payara can answer auth during its initial deployment and briefly
                # return 503 for static assets during its second deployment pass.
                if response.status == 200 and all(
                    urllib.request.urlopen(BASE + name, timeout=3).read() == content
                    for name, content in expected.items()
                ):
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(1)
    raise RuntimeError('Deployment did not become ready')


def deploy():
    war = ROOT / 'target/movie-lab.war'
    backup = ROOT / '.runtime/ui-review-previous.war'
    if backup.exists() or (OUT / 'deployment.json').exists():
        raise RuntimeError('Evidence/backup already exists; preserve it and select a new run directory')
    before = snapshot()
    previous_hash = digest(war.read_bytes())
    shutil.copy2(war, backup)
    stop()
    try:
        env = os.environ.copy()
        env.update(JAVA_HOME='/usr/local/openjdk21', MAVEN_OPTS='-Xmx384m -XX:ActiveProcessorCount=2')
        with (OUT / 'build.log').open('w') as log:
            subprocess.run(['mvn', '-B', '-ntp', '-s', 'scripts/maven-settings.xml', '-DskipTests', 'package'],
                           cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        with zipfile.ZipFile(backup) as old, zipfile.ZipFile(war) as new:
            assert set(old.namelist()) == set(new.namelist()), 'WAR entry set changed'
            changed = sorted(name for name in old.namelist() if old.read(name) != new.read(name))
            assert set(changed) == ASSETS, changed
            unchanged = {name: digest(new.read(name)) for name in new.namelist() if name not in ASSETS}
        start()
        assets = {}
        for name in sorted(ASSETS):
            local = (ROOT / 'src/main/webapp' / name).read_bytes()
            served = urllib.request.urlopen(BASE + name, timeout=10).read()
            assert local == served, 'Served asset mismatch: ' + name
            assets[name] = digest(served)
        after = snapshot()
        assert before == after, 'Domain state changed across deployment'
        result = {'passed': True, 'previousWarSha256': previous_hash, 'warSha256': digest(war.read_bytes()),
                  'serverMavenPackagePassed': True, 'testsRerun': False,
                  'changedWarEntries': changed, 'allOtherWarEntriesUnchanged': True,
                  'unchangedWarEntryHashes': unchanged, 'servedAssets': assets,
                  'domainSnapshotUnchanged': True, 'before': before, 'after': after,
                  'process': own_status(), 'isolation': 'READ COMMITTED',
                  'note': '140 Java tests and 1640 JMeter targets belong to previousWarSha256. This UI revision preserves every other WAR entry byte for byte.'}
        (OUT / 'deployment.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in result.items() if k not in ('unchangedWarEntryHashes', 'before', 'after')}))
    except BaseException:
        stop()
        shutil.copy2(backup, war)
        start()
        raise


def poll():
    api = client()
    before = api.call('revision')[1]['revision']
    status, data = api.call('imports', 'POST', file=('ui-auto-refresh.json', b'{invalid'))
    after = api.call('revision')[1]['revision']
    assert status == 400 and data['status'] == 'FAILED' and before == after
    result = {'passed': True, 'operationId': data['operationId'], 'httpStatus': status,
              'code': data['code'], 'revisionBefore': before, 'revisionAfter': after,
              'username': credentials()[0]['username']}
    (OUT / 'poll-trigger.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    poll() if len(sys.argv) > 1 and sys.argv[1] == 'poll' else deploy()
