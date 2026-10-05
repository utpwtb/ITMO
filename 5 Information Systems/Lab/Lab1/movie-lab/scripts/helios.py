#!/usr/bin/env python3
"""Helios build/test/init/start helper. Credentials stay in the process environment."""
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.runtime'
RUNTIME.mkdir(mode=0o700, exist_ok=True)
os.umask(0o077)
env = os.environ.copy()
env.pop('_JAVA_OPTIONS', None)
env['JAVA_HOME'] = '/usr/local/openjdk21'
env['PATH'] = env['JAVA_HOME'] + '/bin:' + env['PATH']
env['MAVEN_OPTS'] = '-Xmx384m -XX:MaxMetaspaceSize=256m'


def pg_password():
    """Read PostgreSQL's first matching pgpass entry, including escaped : and \\."""
    pgpass = Path.home() / '.pgpass'
    if pgpass.stat().st_mode & 0o077:
        raise RuntimeError('~/.pgpass must have mode 0600')
    for line in pgpass.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        fields, field, escaped = [], '', False
        for c in line:
            if escaped:
                field += c
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == ':' and len(fields) < 4:
                fields.append(field)
                field = ''
            else:
                field += c
        fields.append(field)
        if len(fields) == 5 and all(a in ('*', b) for a, b in zip(fields[:4], ['pg', '5432', 'studs', 's407960'])):
            return fields[4]
    raise RuntimeError('No matching pgpass entry for pg:5432:studs:s407960')


def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, env=env, check=True, **kwargs)


mode = sys.argv[1] if len(sys.argv) == 2 else ''
if mode not in ('test', 'init', 'migrate', 'start', 'stop', 'status'):
    sys.exit('Usage: python3.11 scripts/helios.py test|init|migrate|start|stop|status')

pidfile = RUNTIME / 'payara.pid'


def own_pid():
    if not pidfile.exists():
        return None
    pid = int(pidfile.read_text())
    if pid <= 1:
        return None
    result = subprocess.run(['ps', '-ww', '-p', str(pid), '-o', 'command='], text=True, capture_output=True)
    # Refuse stale/reused PIDs that do not identify this deployment's Java process.
    if result.returncode == 0 and str(RUNTIME / 'payara-micro-6.2025.1.jar') in result.stdout:
        return pid
    return None


if mode in ('status', 'stop'):
    pid = own_pid()
    if mode == 'stop' and pid:
        os.kill(pid, signal.SIGTERM)
        print(f'Stop requested for PID {pid}')
    else:
        print(f'Running PID {pid}' if pid else 'Not running')
    sys.exit(0)

env.update(MOVIE_DB_USER='s407960', MOVIE_DB_PASSWORD=pg_password(),
           MOVIE_DB_URL='jdbc:postgresql://pg:5432/studs?currentSchema=s407960',
           MOVIE_PERSISTENCE_UNIT='movies-helios')

if mode == 'test':
    env.update(MOVIE_TEST_DB_URL='jdbc:postgresql://pg:5432/studs', MOVIE_TEST_SCHEMA='s407960')
    run(['mvn', '-B', '-ntp', '-s', 'scripts/maven-settings.xml',
         '-DargLine=-Xmx384m -XX:MaxMetaspaceSize=256m -XX:ActiveProcessorCount=2', 'clean', 'verify'])
elif mode in ('init', 'migrate'):
    ddl_path = 'database/schema.sql' if mode == 'init' else 'database/migrations/001_accounts.sql'
    ddl = (ROOT / ddl_path).read_text(encoding='utf-8')
    ddl = re.sub(r'\b(movie|person|coordinates|location|app_state|app_user)\b', r'lab1_4101_\1', ddl)
    ddl = re.sub(r'\b(movie_[a-z]+_idx|person_location_idx)\b', r'lab1_4101_\1', ddl)
    # Init refuses existing tables; migration only adds the account table.
    run(['psql', '-X', '-h', 'pg', '-d', 'studs', '-U', 's407960', '-w', '-v', 'ON_ERROR_STOP=1'],
        input='BEGIN;\nSET search_path TO s407960;\n' + ddl + '\nCOMMIT;\n', text=True)
elif mode == 'start':
    if own_pid():
        sys.exit('This deployment is already running')
    preboot = RUNTIME / 'preboot.txt'
    preboot.write_text('set configs.config.server-config.network-config.network-listeners.network-listener.http-listener.address=127.0.0.1\n', encoding='utf-8')
    args = [env['JAVA_HOME'] + '/bin/java', '-Xms64m', '-Xmx384m', '-XX:MaxMetaspaceSize=256m',
            '-XX:ActiveProcessorCount=2', '-jar', str(RUNTIME / 'payara-micro-6.2025.1.jar'),
            '--rootdir', str(RUNTIME / 'payara'), '--port', '40796', '--nocluster', '--disablephonehome',
            '--prebootcommandfile', str(preboot), '--deploy', str(ROOT / 'target/movie-lab.war')]
    with (RUNTIME / 'payara.log').open('ab') as log:
        child = subprocess.Popen(args, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    pidfile.write_text(str(child.pid), encoding='ascii')
    print(f'Started PID {child.pid}; log: {RUNTIME / "payara.log"}')
