"""Build LaTeX tables and copy figures directly from saved experiment results."""
from pathlib import Path
import csv
import json
import shutil

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / 'report'
for name in ['tables', 'figures']:
    (REPORT / name).mkdir(exist_ok=True)
r = json.loads((ROOT / 'results/results.json').read_text(encoding='utf-8'))


def table(name, specification, header, rows, caption):
    text = '\\begin{table}[H]\\centering\\small\n'
    text += '\\begin{tabular}{' + specification + '}\\toprule\n'
    text += ' & '.join(header) + '\\\\\\midrule\n'
    text += '\n'.join(' & '.join(row) + '\\\\' for row in rows)
    text += '\n\\bottomrule\\end{tabular}\n\\caption{' + caption + '}\n'
    text += '\\label{tab:' + name + '}\n\\end{table}\n'
    (REPORT / 'tables' / (name + '.tex')).write_text(text, encoding='utf-8')


stats = list(csv.reader((ROOT / 'results/statistics.csv').open(encoding='utf-8')))
names = ['Количество', 'Среднее', 'Станд. откл.', 'Минимум', 'Q1 (25\\%)',
         'Медиана', 'Q3 (75\\%)', 'Максимум']
rows = []
for label, row in zip(names, stats[1:]):
    values = [f'{float(v):.3f}' if row[0] in ['mean', 'std'] else f'{float(v):g}' for v in row[1:]]
    rows.append([label] + values)
table('statistics', 'lrrrrr', ['Показатель', '$H$', '$P$', '$S$', '$Q$', '$y$'], rows,
      'Числовая статистика после удаления полных повторов.')

rows = []
for name, model in r['models'].items():
    rows.append([name.replace('(bonus)', '(бонус)'), str(len(model['features'])),
                 f"{model['train']['r2']:.6f}", f"{model['test']['r2']:.6f}",
                 f"{model['test']['rmse']:.4f}", f"{model['test']['mae']:.4f}"])
table('metrics', 'lrrrrr', ['Модель', '$p$', '$R^2$ train', '$R^2$ test', 'RMSE test', 'MAE test'],
      rows, 'Фактически полученные результаты на едином разбиении; $p$ не включает свободный член.')

raw = list(csv.DictReader((ROOT / 'data/Student_Performance.csv').open(encoding='utf-8')))
pred = list(csv.DictReader((ROOT / 'results/predictions.csv').open(encoding='utf-8')))
rows = []
for item in pred[:5]:
    source = raw[int(item['source_row'])]
    rows.append([item['source_row'], source['Hours Studied'], source['Previous Scores'],
                 '1' if source['Extracurricular Activities'] == 'Yes' else '0',
                 source['Sleep Hours'], source['Sample Question Papers Practiced'],
                 f"{float(item['actual']):g}", f"{float(item['M3']):.3f}",
                 f"{float(item['actual'])-float(item['M3']):.3f}"])
table('examples', 'rrrrrrrrr', ['Индекс', '$H$', '$P$', '$E$', '$S$', '$Q$', '$y$', '$\\widehat y$', '$y-\\widehat y$'],
      rows, 'Примеры M3 на тестовой части (исходные единицы).')
for f in (ROOT / 'results').glob('*.png'):
    shutil.copy2(f, REPORT / 'figures' / f.name)
print('Report assets generated from results/')
