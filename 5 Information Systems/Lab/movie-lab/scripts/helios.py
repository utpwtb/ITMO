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
env['JAVA_HOME'] = os.environ.get('JAVA_HOME', '/usr/local/openjdk21')
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
if mode not in ('test', 'init', 'migrate', 'start', 'stop', 'status', 'init-test', 'start-test', 'migrate-test', 'admin', 'recover'):
    sys.exit('Usage: python3.11 scripts/helios.py test|init[-test]|migrate[-test]|start[-test]|stop|status|admin|recover')

test_target = mode.endswith('-test') or os.environ.get('MOVIE_TARGET') == 'test'
prefix = 'lab2_4101_test_' if test_target else 'lab2_4101_'

def mapped(sql):
    sql = re.sub(r'\b(movie|person|coordinates|location|app_state|app_user|import_operation)\b', lambda m: prefix+m[0], sql)
    return re.sub(r'\b(movie_[a-z_]+_idx|person_location_idx|import_operation_user_idx)\b', lambda m: prefix+m[0], sql)

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
           MOVIE_PERSISTENCE_UNIT='movies-helios-test' if test_target else 'movies-helios')

if mode == 'test':
    env.update(MOVIE_TEST_DB_URL='jdbc:postgresql://pg:5432/studs', MOVIE_TEST_SCHEMA='s407960')
    run(['mvn', '-B', '-ntp', '-s', 'scripts/maven-settings.xml',
         '-DargLine=-Xmx384m -XX:MaxMetaspaceSize=256m -XX:ActiveProcessorCount=2', 'clean', 'verify'])
elif mode in ('init', 'migrate', 'init-test', 'migrate-test'):
    paths = [ROOT / 'database/schema.sql'] if mode.startswith('init') else sorted((ROOT / 'database/migrations').glob('*.sql'))
    ddl = '\n'.join(path.read_text(encoding='utf-8') for path in paths)
    ddl = mapped(ddl)
    # Init refuses existing tables; migrations preserve rows and validate constraints.
    run(['psql', '-X', '-h', 'pg', '-d', 'studs', '-U', 's407960', '-w', '-v', 'ON_ERROR_STOP=1'],
        input='BEGIN;\nSET search_path TO s407960;\n' + ddl + '\nCOMMIT;\n', text=True)
elif mode == 'admin':
    username = os.environ.get('MOVIE_ADMIN_USER', '')
    if not re.fullmatch(r'[\w.-]{3,64}',username): sys.exit('Set MOVIE_ADMIN_USER to an already registered account')
    run(['psql','-X','-h','pg','-d','studs','-U','s407960','-w','-v','ON_ERROR_STOP=1'],
        input="BEGIN;\n" + mapped("UPDATE app_user SET role='ADMIN' WHERE username='")+username+"' RETURNING id,username,role;\nCOMMIT;\n", text=True)
elif mode == 'recover':
    if own_pid(): sys.exit('Stop this deployment and verify no other Lab 2 instance before recovery')
    # The single-instance deployment must be stopped; FOR UPDATE also waits for outstanding domain writes.
    run(['psql','-X','-h','pg','-d','studs','-U','s407960','-w','-v','ON_ERROR_STOP=1'],
        input=mapped("BEGIN; SELECT id FROM app_state WHERE id=1 FOR UPDATE; UPDATE import_operation SET status='FAILED',finished_at=now(),error_code='INTERRUPTED',error_message='Операция прервана; предыдущая транзакция завершена' WHERE status='RUNNING' RETURNING id; COMMIT;"), text=True)
elif mode in ('start', 'start-test'):
    if own_pid():
        sys.exit('This deployment is already running')
    running = subprocess.run(['ps','-ww','-U','s407960','-o','command='],text=True,capture_output=True,check=True).stdout
    if any(str(RUNTIME / 'payara-micro-6.2025.1.jar') in line and '/bin/java' in line for line in running.splitlines()):
        sys.exit('A process for this deployment still exists; wait for stop before restarting')
    # Single-instance deployment: previous Java process is gone. The row lock waits out any remaining DB transaction.
    run(['psql','-X','-h','pg','-d','studs','-U','s407960','-w','-v','ON_ERROR_STOP=1'],
        input=mapped("BEGIN; SELECT id FROM app_state WHERE id=1 FOR UPDATE; UPDATE import_operation SET status='FAILED',finished_at=now(),error_code='INTERRUPTED',error_message='Предыдущий экземпляр завершился до фиксации операции' WHERE status='RUNNING' RETURNING id; COMMIT;"),text=True)
    preboot = RUNTIME / 'preboot.txt'
    preboot.write_text('set configs.config.server-config.network-config.network-listeners.network-listener.http-listener.address=127.0.0.1\n', encoding='utf-8')
    args = [env['JAVA_HOME'] + '/bin/java', '-Xms64m', '-Xmx384m', '-XX:MaxMetaspaceSize=256m',
            '-XX:ActiveProcessorCount=2', '-jar', str(RUNTIME / 'payara-micro-6.2025.1.jar'),
            '--rootdir', str(RUNTIME / 'payara'), '--port', os.environ.get('MOVIE_HTTP_PORT','40797'), '--nocluster', '--disablephonehome',
            '--prebootcommandfile', str(preboot), '--deploy', str(ROOT / 'target/movie-lab.war')]
    with (RUNTIME / 'payara.log').open('ab') as log:
        child = subprocess.Popen(args, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    pidfile.write_text(str(child.pid), encoding='ascii')
    print(f'Started PID {child.pid}; log: {RUNTIME / "payara.log"}')
