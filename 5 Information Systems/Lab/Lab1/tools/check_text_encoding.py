"""Verify authored Russian report/application files using explicit UTF-8 only."""
from pathlib import Path
import json
import re

base = Path(__file__).resolve().parents[1]
roots = [base / 'report', base / 'movie-lab' / 'src', base / 'movie-lab' / 'scripts']
extensions = {'.tex', '.java', '.js', '.cjs', '.html', '.css', '.xml', '.md', '.ps1'}
files = [p for root in roots for p in root.rglob('*') if p.is_file() and p.suffix in extensions]
files += [base / 'movie-lab' / 'README.md', base / 'verification' / 'ACCEPTANCE.md']
errors = []
for path in files:
    try:
        text = path.read_text(encoding='utf-8-sig')
    except UnicodeError as error:
        errors.append({'file': str(path.relative_to(base)), 'error': str(error)})
        continue
    for number, line in enumerate(text.splitlines(), 1):
        # These authored files contain Russian and English, not Chinese.
        # Chinese characters here reveal the specific UTF-8 -> GBK -> UTF-8 bug.
        if re.search(r'[\u4e00-\u9fff\ufffd]', line):
            errors.append({'file': str(path.relative_to(base)), 'line': number,
                           'error': 'Unexpected CJK or replacement character'})
body = (base / 'report' / 'body.tex').read_text(encoding='utf-8-sig')
for expected in ['Постановка задачи', 'Архитектура и модель данных',
                 'Специальные операции', 'Заключение']:
    if expected not in body:
        errors.append({'file': 'report/body.tex', 'error': 'Missing Russian text: ' + expected})
result = {'encoding': 'UTF-8', 'files_checked': len(files), 'errors': errors,
          'passed': not errors}
(base / 'verification' / 'encoding-check.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)
