"""Regenerate all numeric LaTeX tables from the experiment outputs."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'report/tables'
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(ROOT / 'results/metrics.csv')
grid = pd.read_csv(ROOT / 'results/validation_search.csv')
coef = pd.read_csv(ROOT / 'results/coefficients.csv')
labels = {'Baseline': 'Без рег.', 'L1': 'L1', 'L2': 'L2', 'ElasticNet': 'ElasticNet'}


def write_table(name, columns, header, rows):
    text = '\\begin{tabular}{' + columns + '}\n\\toprule\n'
    text += ' & '.join(header) + r' \\' + '\n\\midrule\n'
    text += '\n'.join(' & '.join(row) + r' \\' for row in rows)
    text += '\n\\bottomrule\n\\end{tabular}\n'
    (OUT / f'{name}.tex').write_text(text, encoding='utf-8')


write_table('selection', 'llrrrr',
            ['Модель', 'Метод', r'$\lambda$', r'$\alpha$', r'MSE$_{train}$', r'MSE$_{val}$'],
            [[r.model, labels[r.method], f'{r.lam:g}', '--' if r.method != 'ElasticNet' else f'{r.ratio:g}',
              f'{r.train_mse:.6f}', f'{r.validation_mse:.6f}'] for r in df.itertuples()])
write_table('test', 'llrrrr', ['Модель', 'Метод', 'MSE', 'RMSE', 'MAE', r'$R^2$'],
            [[r.model, labels[r.method], f'{r.test_mse:.6f}', f'{r.test_rmse:.6f}',
              f'{r.test_mae:.6f}', f'{r.test_r2:.6f}'] for r in df.itertuples()])
names = ['Часы учёбы', 'Предыдущие баллы', 'Внеучебные занятия', 'Часы сна', 'Решённые варианты', 'Произведение']
for model in ['M3', 'M4']:
    subset = coef[(coef.model == model) & (coef.feature != 'Intercept')]
    features = subset.feature.drop_duplicates().tolist()
    rows = []
    for label, feature in zip(names, features):
        values = subset[subset.feature == feature].set_index('method')
        rows.append([label] + [f'{values.loc[m, "standardized"]:.6f}' for m in labels])
    write_table('coefficients_' + model, 'lrrrr', ['Признак', 'Без рег.', 'L1', 'L2', 'ElasticNet'], rows)
subset = grid[(grid.model == 'M3') & (grid.method == 'L1')]
write_table('sparsity', 'rrrrr',
            [r'$\lambda$', r'MSE$_{val}$', r'$\|w\|_1$', r'$\|w\|_2$', 'Нулей'],
            [[f'{r.lam:g}', f'{r.validation_mse:.6f}', f'{r.l1_norm:.6f}', f'{r.l2_norm:.6f}', str(r.zeros)]
             for r in subset.itertuples()])
print('Report tables regenerated from CSV.')
