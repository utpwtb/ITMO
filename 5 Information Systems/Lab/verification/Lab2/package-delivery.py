"""Package the current Lab 2 sources, Russian report and compact Helios evidence."""

import hashlib
import json
from pathlib import Path
import tarfile
import zipfile

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / 'movie-lab'
RUN = HERE / 'compact-20261110'
REPORT = ROOT / 'report/Lab2'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


source = read_json(APP / 'source-manifest.json')
for name, expected in source.items():
    assert digest(APP / name) == expected, name
source_archive = HERE / 'source-current.tar.gz'
with tarfile.open(source_archive) as tar:
    assert set(tar.getnames()) == set(source) | {'source-manifest.json'}
    for name, expected in source.items():
        assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == expected, name
    assert tar.extractfile('source-manifest.json').read() == (APP / 'source-manifest.json').read_bytes()

config = read_json(RUN / 'configuration.json')
cases = read_json(RUN / 'jmeter/summary.json')
assert [item['scenario'] for item in cases] == config['scenarios'] == ['C01', 'C02', 'C03']
assert config['persistenceUnit'] == 'movies-helios-test' and config['isolation'] == 'READ COMMITTED'
assert config['runnerSha256'] == source['scripts/lab2-jmeter.py']
assert config['jmxSha256'] == source['jmeter/lab2-concurrency.jmx']
for case, requests, conflicts in zip(cases, (40, 200, 40), (20, 180, 20)):
    assert case['passed'] and case['completedRounds'] == case['rounds'] == 20
    assert case['requests'] == requests and case['expectedConflicts'] == conflicts and case['commits'] == 20
    assert case['unexpected'] == case['duplicates'] == case['jtlFailures'] == 0
    assert read_json(RUN / 'jmeter' / case['scenario'] / 'assertions.json') == case
assert cases[2]['lateDuplicateConflicts'] == 20 and cases[2]['failedImportResidue'] == 0
functional = read_json(RUN / 'functional/http-functional.json')
assert functional['passed'] and len(functional['results']) == 17
assert all(check['passed'] for check in functional['results'])
last_row = read_json(RUN / 'functional/invalid-last-field.json')
assert last_row['passed'] and last_row['before'] == last_row['after']
assert last_row['revisionBefore'] == last_row['revisionAfter']

pdf = REPORT / 'report.pdf'
pages = [page.extract_text() for page in PdfReader(pdf).pages]
text = '\n'.join(pages)
assert all(item in text for item in ('C01', 'C02', 'C03', '280', '18 функциональных'))
assert all(item not in text for item in ('Требования к отчёту', 'Вопросы к защите', 'SERIALIZABLE', '1640'))
assert 'Заключение' in pages[-1]
for name, expected in read_json(REPORT / 'uml/source-hashes.json').items():
    assert digest(APP / name) == expected, name

paths = {APP / name for name in source}
paths.update((APP / 'source-manifest.json', APP / 'target/movie-lab.war',
              source_archive, HERE / 'ACCEPTANCE.md', HERE / 'DEPLOYMENT.md', Path(__file__).resolve()))
paths.update(path for path in RUN.rglob('*') if path.is_file())
paths.update(path for path in (ROOT / 'defense/Lab2').glob('*.md') if path.is_file())
report_types = {'.tex', '.pdf', '.png', '.svg', '.dot', '.json', '.md', '.txt', '.otf'}
paths.update(path for path in REPORT.rglob('*') if path.is_file()
             and path.suffix.lower() in report_types and path.name != 'main.pdf')
assert all(path.is_file() and path.resolve().is_relative_to(ROOT.resolve())
           and '.runtime' not in path.relative_to(ROOT).parts for path in paths)

test_users = APP / '.runtime/lab2-users.json'
secrets = [user['password'].encode() for user in read_json(test_users)] if test_users.is_file() else []
text_types = {'.py', '.java', '.js', '.groovy', '.jmx', '.md', '.tex', '.json', '.jsonl',
              '.xml', '.txt', '.log', '.csv', '.jtl', '.sql', '.html', '.properties'}
scanned = 0
for path in paths:
    if path.suffix.lower() in text_types:
        content = path.read_bytes()
        assert not any(secret in content for secret in secrets), str(path.relative_to(ROOT))
        if path.suffix.lower() == '.xml':
            assert b'<property name="MOVIE_DB_PASSWORD"' not in content, str(path.relative_to(ROOT))
        scanned += 1

manifest = {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(paths)}
manifest_path = HERE / 'delivery-manifest.json'
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
bundle = HERE / 'lab2-delivery.zip'
candidate = bundle.with_suffix('.zip.tmp')
with zipfile.ZipFile(candidate, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=4) as archive:
    for name in manifest:
        archive.write(ROOT / name, name)
    archive.write(manifest_path, manifest_path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(candidate) as archive:
    assert set(archive.namelist()) == set(manifest) | {manifest_path.relative_to(ROOT).as_posix()}
    for name, expected in manifest.items():
        assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
candidate.replace(bundle)
result = {
    'passed': True, 'serverRun': RUN.name, 'jmeterScenarios': ['C01', 'C02', 'C03'],
    'jmeterTargetRequests': 280, 'jmeterCommits': 60, 'jmeterExpectedConflicts': 220,
    'jmeterUnexpectedFailures': 0, 'functionalChecks': 18, 'pdfPages': len(pages),
    'serverTestWarSha256': config['warSha256'], 'sourceFiles': len(source),
    'textArtifactsScanned': scanned, 'testCredentialLeaks': 0, 'bundleFiles': len(paths) + 1,
    'bundleSha256': digest(bundle), 'reportSha256': digest(pdf), 'sourceArchiveSha256': digest(source_archive),
}
(HERE / 'delivery-checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
