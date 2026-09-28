"""Create clean delivery archives, excluding dependencies and temporary files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
root_files = ['README.md', 'requirements.txt', 'experiment.py', 'build_report_assets.py',
              'qa_report.py', 'package_delivery.py', '.gitignore',
              '实验三任务与实现讲解.md']
files = [ROOT / name for name in root_files]
for folder in ['data', 'results']:
    files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file())
files.extend(ROOT / 'sources' / name for name in ['README.md', 'linear_regression.pdf', 'linear_regression.docx'])
report = [p for p in (ROOT / 'report').rglob('*') if p.is_file()
          and p.suffix in {'.tex', '.png', '.otf'}]
report.append(ROOT / 'report/fonts/OFL.txt')
files.extend(report + [ROOT / 'report/main.pdf'])
archives = [
    (ROOT.parent / 'Lab3_complete.zip', files, ROOT.parent),
    (ROOT.parent / 'Lab3_report_latex.zip', report, ROOT / 'report'),
]
for destination, members, relative_to in archives:
    with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(set(members)):
            archive.write(path, path.relative_to(relative_to).as_posix())
    with ZipFile(destination) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert not any('.deps/' in name or '/tmp/' in name for name in names)
    print(f'{destination.name}: {len(names)} files; {destination.stat().st_size} bytes; CRC OK')
