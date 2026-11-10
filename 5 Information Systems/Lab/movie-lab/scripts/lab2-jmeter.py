"""Run the three Lab 2 races on Helios and verify HTTP outcomes and PostgreSQL state."""

import collections
import csv
import json
import os
from pathlib import Path
import secrets
import statistics
import subprocess
import sys
import time

from lab2_api import Client, ROOT, credentials, import_movie, movie


SCENARIOS = {'C01': 2, 'C02': 10, 'C03': 2}
API = 'http://127.0.0.1:40797/movie-lab/api'


def require_test_instance():
    pidfile = ROOT / '.runtime/payara.pid'
    if not pidfile.is_file():
        raise SystemExit('Start the isolated Helios instance with scripts/helios.py start-test.')
    # FreeBSD ps includes the process environment. Capture it and never log it.
    process = subprocess.run(
        ['ps', 'eww', '-p', pidfile.read_text().strip(), '-o', 'command='],
        capture_output=True, text=True,
    )
    jar = ROOT / '.runtime/payara-micro-6.2025.1.jar'
    if process.returncode or str(jar) not in process.stdout or (
        'MOVIE_PERSISTENCE_UNIT=movies-helios-test' not in process.stdout.split()
    ):
        raise SystemExit('The running Helios instance must use movies-helios-test.')
    if os.environ.get('MOVIE_API', API).rstrip('/') != API:
        raise SystemExit(f'This Helios runner targets {API}.')


def database():
    query = """select json_build_object(
      'movies',(select count(*) from lab2_4101_test_movie),
      'coordinates',(select count(*) from lab2_4101_test_coordinates),
      'people',(select count(*) from lab2_4101_test_person),
      'locations',(select count(*) from lab2_4101_test_location),
      'duplicates',(select count(*) from (select name,director_id from lab2_4101_test_movie group by name,director_id having count(*)>1) d),
      'orphans',(select count(*) from lab2_4101_test_movie m left join lab2_4101_test_coordinates c on c.id=m.coordinates_id where c.id is null),
      'histories',(select json_agg(json_build_object('id',id::text,'status',status,'count',added_count,'filename',filename)) from lab2_4101_test_import_operation))"""
    result = subprocess.run(
        ['psql', '-X', '-h', 'pg', '-U', 's407960', '-d', 'studs', '-w', '-Atc', query],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def prepare(api, scenario, threads, rounds, out):
    marker = f'lab2-{out.parent.name}-{scenario}-{secrets.token_hex(3)}'
    fixture = {'scenario': scenario, 'threads': threads, 'rounds': [], 'marker': marker}
    if scenario != 'C03':
        coordinates = api.create('coordinates', {'x': 1, 'y': 1})['id']
    if scenario == 'C02':
        director = api.create('people', {
            'name': 'JMeter director', 'birthday': '1980-01-01T00:00Z', 'passportID': marker,
        })['id']
    for r in range(rounds):
        prefix = f'{marker}-r{r}-'
        meta = {'prefix': prefix, 'actions': []}
        if scenario == 'C01':
            target = api.create('movies', movie(prefix + 'old', coordinates))
            path, version = f"movies/{target['id']}", target['version']
            meta['target'], meta['targetVersion'] = target['id'], version
            meta['actions'] = [
                {'method': 'PUT', 'path': path, 'read': path, 'version': version,
                 'body': {'tagline': prefix + 'updated', 'version': version}, 'expected': [200, 404]},
                {'method': 'DELETE', 'path': f'{path}?version={version}', 'read': path,
                 'version': version, 'expected': [200, 409]},
            ]
        elif scenario == 'C02':
            action = {'method': 'POST', 'path': 'movies', 'body': movie(prefix + 'same', coordinates, director),
                      'expected': [201, 409], 'code': 'DUPLICATE_MOVIE'}
            meta['actions'] = [action] * threads
        else:
            for i in range(threads):
                names = [f'{prefix}unique{i}', prefix + 'shared']
                document = {'formatVersion': 1,
                            'movies': [import_movie(name, prefix + 'passport') for name in names]}
                file = out / f'r{r}-p{i}.json'
                file.write_text(json.dumps(document), encoding='utf-8')
                meta['actions'].append({
                    'method': 'POST', 'path': 'imports', 'file': str(file.resolve()),
                    'expected': [201, 409], 'code': 'DUPLICATE_MOVIE',
                    'errorPath': 'movies[1].director',
                })
        fixture['rounds'].append(meta)
    return fixture


def verify(api, fixture, records, before, after):
    errors = []

    def check(value, message):
        if not value:
            errors.append(message)

    scenario, threads = fixture['scenario'], fixture['threads']
    rounds = len(fixture['rounds'])
    check(len(records) == rounds * threads, 'Unexpected number of target samples')
    check(all(row['passed'] for row in records), 'Unexpected HTTP outcome')
    check(after['duplicates'] == 0, 'Duplicate movie keys in DB')
    check(after['orphans'] == 0, 'Orphan references')
    histories = {op['id']: op for op in (after['histories'] or [])}
    winners = collections.Counter()
    completed = late_conflicts = 0
    for r, meta in enumerate(fixture['rounds']):
        rows = sorted((row for row in records if row['round'] == r), key=lambda row: row['participant'])
        if [row['participant'] for row in rows] != list(range(threads)):
            check(False, f'{r}: expected one result per participant')
            continue
        completed += 1
        actions = meta['actions']
        check(all(row['method'] == action['method'] and row['path'] == action['path']
                  for row, action in zip(rows, actions)), f'{r}: request differs from fixture')
        statuses = collections.Counter(row['status'] for row in rows)
        if scenario == 'C01':
            status, final = api.call(f"movies/{meta['target']}")
            edit, delete = rows
            if edit['status'] == 200:
                winners['edit'] += 1
                check(delete['status'] == 409, f'{r}: outdated delete must conflict')
                check(status == 200 and final.get('tagline') == actions[0]['body']['tagline']
                      and final.get('version') == meta['targetVersion'] + 1, f'{r}: edited value or version differs')
            elif delete['status'] == 200:
                winners['delete'] += 1
                check(edit['status'] == 404 and status == 404, f'{r}: delete winner must leave no movie')
            else:
                check(False, f'{r}: neither edit nor delete won')
            continue

        check(statuses == {201: 1, 409: threads - 1}, f'{r}: expected exactly one winner, got {statuses}')
        status, movies = api.call('operations/prefix?value=' + meta['prefix'])
        if status != 200 or not isinstance(movies, list):
            check(False, f'{r}: could not read final movies')
            continue
        if scenario == 'C02':
            body = actions[0]['body']
            check(len(movies) == 1 and movies[0]['name'] == body['name']
                  and (movies[0]['director'] or {}).get('id') == body['director'], f'{r}: one exact movie key required')
            continue

        for row, action in zip(rows, actions):
            history = histories.get(row['operationId'])
            success = row['status'] == 201
            check(history is not None and history['filename'] == Path(action['file']).name
                  and history['status'] == ('SUCCESS' if success else 'FAILED')
                  and history['count'] == (2 if success else None), f'{r}: history differs from upload outcome')
            if success:
                winners['import'] += 1
                expected = json.loads(Path(action['file']).read_text(encoding='utf-8'))['movies']
                check(collections.Counter(m['name'] for m in movies) ==
                      collections.Counter(m['name'] for m in expected), f'{r}: winning file differs or losing movie remains')
            else:
                late_duplicate = (row['status'] == 409 and row['code'] == 'DUPLICATE_MOVIE'
                                  and row['errorPath'] == 'movies[1].director')
                check(late_duplicate, f'{r}: rejection must occur on the second movie')
                late_conflicts += int(late_duplicate)

    domain_delta = {key: after[key] - before[key] for key in ('movies', 'coordinates', 'people', 'locations')}
    if scenario == 'C01':
        expected_delta = {'movies': -winners['delete'], 'coordinates': 0, 'people': 0, 'locations': 0}
    elif scenario == 'C02':
        expected_delta = {'movies': rounds, 'coordinates': 0, 'people': 0, 'locations': 0}
    else:
        imports = winners['import']
        expected_delta = {'movies': 2 * imports, 'coordinates': 2 * imports, 'people': imports, 'locations': imports}
    check(domain_delta == expected_delta, f'Unexpected domain delta or failed import residue: {domain_delta}')
    values = sorted(row['elapsed'] for row in records)
    result = {
        'scenario': scenario, 'threads': threads, 'rounds': rounds, 'completedRounds': completed,
        'requests': len(records), 'commits': sum(row['status'] in (200, 201) for row in records),
        'expectedConflicts': sum(row['passed'] and row['status'] in (404, 409) for row in records),
        'unexpected': sum(not row['passed'] for row in records), 'duplicates': after['duplicates'],
        'averageMs': statistics.mean(values) if values else None,
        'p95Ms': values[min(len(values) - 1, int(len(values) * .95))] if values else None,
        'domainDelta': domain_delta, 'passed': not errors, 'errors': errors,
    }
    if scenario == 'C01':
        result['editWins'], result['deleteWins'] = winners['edit'], winners['delete']
    if scenario == 'C03':
        result['lateDuplicateConflicts'] = late_conflicts
        result['failedImportResidue'] = 0 if not errors else None
    return result


def main(args):
    if not args or args == ['--help']:
        print('Usage: python3.11 scripts/lab2-jmeter.py OUTPUT_DIR [C01 C02 C03]')
        return 0 if args else 2
    requested = args[1:] or list(SCENARIOS)
    if len(set(requested)) != len(requested) or any(scenario not in SCENARIOS for scenario in requested):
        raise SystemExit('Choose distinct scenarios from C01, C02, C03.')
    rounds = int(os.environ.get('JMETER_ROUNDS', '20'))
    if rounds < 1:
        raise SystemExit('JMETER_ROUNDS must be positive.')
    require_test_instance()
    api = Client(API, **credentials()[2])
    run = Path(args[0]).resolve()
    run.mkdir(parents=True)
    results = []
    for scenario in requested:
        threads = SCENARIOS[scenario]
        out = run / scenario
        out.mkdir()
        fixture = prepare(api, scenario, threads, rounds, out)
        (out / 'fixture.json').write_text(json.dumps(fixture, indent=2), encoding='utf-8')
        before = database()
        (out / 'database-before.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
        env = os.environ.copy()
        env.pop('_JAVA_OPTIONS', None)
        env.update(JAVA_HOME='/usr/local/openjdk21', HEAP='-Xms64m -Xmx256m',
                   JVM_ARGS='-XX:ActiveProcessorCount=2 -XX:MaxMetaspaceSize=160m')
        cmd = [str(ROOT / 'tools/apache-jmeter-5.6.3/bin/jmeter'), '-n', '-t', 'jmeter/lab2-concurrency.jmx',
               '-Jhost=127.0.0.1', '-Jport=40797', '-JbasePath=/movie-lab/api', '-Jscenario=' + scenario,
               f'-Jthreads={threads}', f'-Jrounds={rounds}', f'-JfixtureFile={out / "fixture.json"}',
               f'-JcredentialsFile={ROOT / ".runtime/lab2-users.json"}', f'-JresultFile={out / "responses.jsonl"}',
               '-l', str(out / 'results.jtl'), '-j', str(out / 'jmeter.log'), '-e', '-o', str(out / 'html')]
        (out / 'command.json').write_text(json.dumps(cmd, indent=2), encoding='utf-8')
        started = time.time()
        with (out / 'stdout.log').open('w', encoding='utf-8') as log:
            code = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        after = database()
        (out / 'database-after.json').write_text(json.dumps(after, indent=2), encoding='utf-8')
        raw = out / 'responses.jsonl'
        records = [json.loads(line) for line in raw.read_text(encoding='utf-8').splitlines()] if raw.exists() else []
        result = verify(api, fixture, records, before, after)
        jtl_file = out / 'results.jtl'
        jtl = []
        if jtl_file.exists():
            with jtl_file.open(encoding='utf-8', newline='') as stream:
                jtl = list(csv.DictReader(stream))
        failed = sum(row['success'] != 'true' for row in jtl)
        result.update(jmeterExit=code, jtlFailures=failed, elapsedSeconds=time.time() - started)
        if code or failed or not jtl:
            result['passed'] = False
            result['errors'].append('JMeter process/JTL setup or sampler failure')
        (out / 'assertions.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        results.append(result)
        (run / 'summary.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)
        if not result['passed'] and os.environ.get('JMETER_KEEP_GOING') != '1':
            return 1
    return 0 if all(result['passed'] for result in results) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
