import atexit
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request


ROOT = Path('/home/studs/s407960/is-lab2-4101')
if len(sys.argv) not in (2, 3) or sys.argv[2:] not in ([], ['--single']):
    raise SystemExit('Usage: run-isolation-c02.py isolation-c02-YYYYMMDD-HHMMSS [--single]')
LABEL = sys.argv[1]
if not re.fullmatch(r'isolation-c02-[0-9]{8}-[0-9]{6}', LABEL):
    raise SystemExit('Invalid run label')
WORK = Path(tempfile.mkdtemp(prefix='s407960-' + LABEL + '-'))
atexit.register(shutil.rmtree, WORK)
OUT = ROOT / 'verification/Lab2' / LABEL
RUNTIME = WORK / '.runtime'
JAR = 'payara-micro-6.2025.1.jar'
WAR = 'target/movie-lab.war'
PORT = '40801'
TABLE = 's407960.lab2_4101_test_'
PSQL = ['psql', '-X', '-h', 'pg', '-U', 's407960', '-d', 'studs',
        '-w', '-v', 'ON_ERROR_STOP=1', '-At']
TABLES = ('movie', 'coordinates', 'person', 'location', 'import_operation', 'app_user')
PY = 'python3.11'
GROUPS = (
    ('default-read-committed', 'READ COMMITTED', 3),
    ('default-serializable', 'SERIALIZABLE', 3),
    ('single-serializable', 'SERIALIZABLE', 1),
    ('single-read-committed', 'READ COMMITTED', 1),
)
if sys.argv[2:]:
    isolation = os.environ.get('MOVIE_ISOLATION')
    attempts = int(os.environ.get('MOVIE_TX_ATTEMPTS', '3'))
    GROUPS = [g for g in GROUPS if g[1:] == (isolation, attempts)]
    if not GROUPS:
        raise SystemExit('Set MOVIE_ISOLATION to SERIALIZABLE or READ COMMITTED and MOVIE_TX_ATTEMPTS to 1 or 3')


def run(args, **kwargs):
    return subprocess.run(args, cwd=WORK, text=True, check=True, **kwargs)


def sql(query):
    return run(PSQL, input=query, capture_output=True).stdout.strip()


def fingerprint():
    fields = []
    for table in TABLES:
        fields.extend([f"'{table}'", f"(SELECT json_build_array(count(*), md5(coalesce("
                       f"string_agg(row_to_json(t)::text, E'\\n' ORDER BY id), ''))) FROM {TABLE}{table} t)"])
    return json.loads(sql('SELECT json_build_object(' + ','.join(fields) + ');'))


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def stop():
    run([PY, 'scripts/helios.py', 'stop'])
    for _ in range(45):
        status = run([PY, 'scripts/helios.py', 'status'], capture_output=True).stdout
        if 'Not running' in status:
            return
        time.sleep(1)
    raise RuntimeError('Test instance did not stop')


def ready():
    for _ in range(90):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/movie-lab/api/auth', timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(1)
    raise RuntimeError('Test instance did not deploy')


def cleanup(fixture):
    actions = [round_data['actions'][0]['body'] for round_data in fixture['rounds']]
    marker = fixture['marker']
    names = [a['name'] for a in actions]
    if not re.fullmatch(r'lab2-[a-z0-9-]+-C02-[0-9a-f]{6}', marker) or any(
        name != f'{marker}-r{index}-same' for index, name in enumerate(names)
    ):
        raise RuntimeError('Refusing cleanup of unrecognized fixture')
    director = int(actions[0]['director'])
    coordinates = int(actions[0]['coordinates'])
    name_list = ','.join(f"'{name}'" for name in names)
    return sql(f"""BEGIN;
SELECT id FROM {TABLE}app_state WHERE id=1 FOR UPDATE;
DELETE FROM {TABLE}movie WHERE director_id={director} AND coordinates_id={coordinates}
  AND name IN ({name_list});
DELETE FROM {TABLE}person WHERE id={director} AND passportid='{marker}'
  AND NOT EXISTS (SELECT 1 FROM {TABLE}movie WHERE {director} IN (director_id, screenwriter_id, operator_id));
DELETE FROM {TABLE}coordinates WHERE id={coordinates}
  AND NOT EXISTS (SELECT 1 FROM {TABLE}movie WHERE coordinates_id={coordinates});
COMMIT;""")


def compare(name, isolation, attempts, baseline, provenance):
    print(f'=== {name} ===', flush=True)
    if fingerprint() != baseline:
        raise RuntimeError('Test rows changed before comparison')
    env = os.environ.copy()
    env.update(MOVIE_HTTP_PORT=PORT, MOVIE_TARGET='test', MOVIE_ISOLATION=isolation, JMETER_ROUNDS='20')
    env.pop('MOVIE_API', None)
    env.pop('MOVIE_TX_ATTEMPTS', None)
    env.pop('JMETER_KEEP_GOING', None)
    if attempts == 1:
        env['MOVIE_TX_ATTEMPTS'] = '1'
    destination = OUT / name
    logfile = RUNTIME / 'payara.log'
    run([PY, 'scripts/helios.py', 'start-test'], env=env)
    try:
        ready()
        pid = int((RUNTIME / 'payara.pid').read_text())
        proc = run(['ps', 'eww', '-p', str(pid), '-o', 'command='], capture_output=True).stdout
        for setting in ('MOVIE_PERSISTENCE_UNIT=movies-helios-test', f'MOVIE_ISOLATION={isolation}'):
            if setting not in proc:
                raise RuntimeError('Test process setting differs')
        if ('MOVIE_TX_ATTEMPTS=1' in proc.split()) != (attempts == 1):
            raise RuntimeError('Test process attempts setting differs')
        offset = logfile.stat().st_size
        completed = subprocess.run([PY, 'scripts/lab2-jmeter.py', str(destination), 'C02'], cwd=WORK, env=env)
        if not (destination / 'C02/assertions.json').exists():
            raise RuntimeError(f'C02 did not reach assertions, exit {completed.returncode}')
        save(destination / 'configuration.json', dict(
            provenance, isolation=isolation, attempts=attempts, attemptsSource='override' if attempts == 1 else 'backend default',
            pid=pid, endpoint=f'127.0.0.1:{PORT}', persistenceUnit='movies-helios-test', rounds=20, threads=10,
        ))
        with logfile.open('rb') as stream:
            stream.seek(offset)
            log = stream.read()
        (destination / 'server.log').write_bytes(log)
        signals = [line for line in log.decode('utf-8', errors='replace').splitlines()
                   if any(s in line for s in ('40001', 'Rolled-back serialization failure', 'could not serialize'))]
        (destination / 'serialization.log').write_text('\n'.join(signals) + ('\n' if signals else ''), encoding='utf-8')
        raw = (destination / 'C02/responses.jsonl').read_text().splitlines()
        assertions = json.loads((destination / 'C02/assertions.json').read_text())
        stats = dict(
            group=name, isolation=isolation, attempts=attempts, runnerExit=completed.returncode,
            statusCounts=collections.Counter(str(json.loads(line)['status']) for line in raw),
            retryLogEntries=log.count(b'Rolled-back serialization failure; retry='),
            concurrentUpdateLogMentions=log.count(b'could not serialize access due to concurrent update'),
            passed=assertions['passed'],
            duplicates=assertions['duplicates'], moviesAdded=assertions['domainDelta']['movies'],
        )
    finally:
        stop()
    fixture_path = destination / 'C02/fixture.json'
    stats['cleanup'] = cleanup(json.loads(fixture_path.read_text())).splitlines()
    stats['baselineRestored'] = fingerprint() == baseline
    save(destination / 'run-statistics.json', stats)
    if not stats['baselineRestored']:
        raise RuntimeError('Test row fingerprint after cleanup differs from baseline')
    return stats


os.umask(0o077)
RUNTIME.mkdir(parents=True)
OUT.mkdir(parents=True)
(WORK / 'target').mkdir()
for directory in ('scripts', 'jmeter'):
    shutil.copytree(ROOT / directory, WORK / directory)
(WORK / 'tools').symlink_to(ROOT / 'tools', target_is_directory=True)
(WORK / WAR).symlink_to(ROOT / WAR)
(RUNTIME / JAR).symlink_to(ROOT / '.runtime' / JAR)
(RUNTIME / 'lab2-users.json').symlink_to(ROOT / '.runtime/lab2-users.json')
config = RUNTIME / 'payara/config'
config.mkdir(parents=True)
original = (ROOT / '.runtime/payara/config/domain.xml').read_text()
if original.count('start-port="40798"') != 1:
    raise RuntimeError('Unexpected Hazelcast configuration')
(config / 'domain.xml').write_text(original.replace('start-port="40798"', 'start-port="40802"'))
runner = WORK / 'scripts/lab2-jmeter.py'
script = runner.read_text()
if script.count('40797') != 2:
    raise RuntimeError('Unexpected endpoint references in runner')
runner.write_text(script.replace('40797', PORT))
jmx = WORK / 'jmeter/lab2-concurrency.jmx'
jmx_source = jmx.read_text()
error_policy = 'name="ThreadGroup.on_sample_error">'
if jmx_source.count(error_policy + 'stoptest<') != 1:
    raise RuntimeError('Unexpected original JMX error policy')
jmx.write_text(jmx_source.replace(error_policy + 'stoptest<', error_policy + 'continue<'))
shutil.copy2(jmx, OUT / 'lab2-concurrency.jmx')
baseline = fingerprint()
provenance = dict(
    host=os.uname().nodename, warSha256=sha(WORK / WAR),
    jmxSha256=sha(jmx), runnerSha256=sha(runner), jmxOnSampleError='continue',
    baselineRowFingerprint=baseline, lock='AppState PESSIMISTIC_WRITE',
)
save(OUT / 'configuration.json', provenance)
summary = []
for name, isolation, attempts in GROUPS:
    summary.append(compare(name, isolation, attempts, baseline, provenance))
    save(OUT / 'summary.json', summary)
print(json.dumps(summary, indent=2), flush=True)
