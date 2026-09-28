"""ЛР 3: МНК с собственным решением нормальных уравнений.

NumPy/Pandas используются для данных и арифметики; Matplotlib только для графиков.
Запуск: python experiment.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if (ROOT / '.deps').exists():
    sys.path.insert(0, str(ROOT / '.deps'))
import hashlib
import json
import platform
import numpy as np
import pandas as pd

FEATURES = ['Hours Studied', 'Previous Scores', 'Extracurricular Activities',
            'Sleep Hours', 'Sample Question Papers Practiced']
TARGET = 'Performance Index'
SYNTHETIC = 'Hours x Previous Scores'
MODELS = {'M1': FEATURES[:1], 'M2': FEATURES[:2], 'M3': FEATURES,
          'M4 (bonus)': FEATURES + [SYNTHETIC]}


def gauss_solve(a, b):
    """Метод Гаусса с выбором максимального по модулю ведущего элемента."""
    a, b = np.asarray(a, dtype=float).copy(), np.asarray(b, dtype=float).copy()
    n = len(b)
    if a.shape != (n, n):
        raise ValueError('Expected a square matrix')
    tolerance = 1e-12 * max(1.0, float(np.max(np.abs(a))))
    for k in range(n):
        pivot = k + int(np.argmax(np.abs(a[k:, k])))
        if abs(a[pivot, k]) <= tolerance:
            raise ValueError('Singular or nearly singular normal matrix')
        a[[k, pivot]], b[[k, pivot]] = a[[pivot, k]], b[[pivot, k]]
        for i in range(k + 1, n):
            factor = a[i, k] / a[k, k]
            a[i, k:] -= factor * a[k, k:]
            b[i] -= factor * b[k]
    x = np.zeros(n)
    for k in range(n - 1, -1, -1):
        x[k] = (b[k] - a[k, k + 1:] @ x[k + 1:]) / a[k, k]
    return x


def fit_ols(x, y):
    """Минимизация SSE: X^T X beta = X^T y; без готовых решателей."""
    design = np.column_stack([np.ones(len(x)), x])
    return gauss_solve(design.T @ design, design.T @ y)


def predict(x, beta):
    return beta[0] + x @ beta[1:]


def metrics(y, prediction):
    residual = y - prediction
    sse = float(residual @ residual)
    sst = float(np.sum((y - y.mean()) ** 2))
    return {'r2': 1 - sse / sst if sst > 0 else None,
            'rmse': float(np.sqrt(sse / len(y))),
            'mae': float(np.mean(np.abs(residual))), 'sse': sse}


def encode(frame):
    out = frame[FEATURES].copy()
    category = out['Extracurricular Activities']
    unknown = category.notna() & ~category.isin(['Yes', 'No'])
    if unknown.any():
        raise ValueError('Unknown extracurricular category')
    out['Extracurricular Activities'] = category.map({'Yes': 1.0, 'No': 0.0})
    return out.astype(float)


def prepare(train, test):
    """Параметры заполнения и стандартизации оцениваются только на train."""
    a, b = encode(train), encode(test)
    fills = a.median()
    mode = a['Extracurricular Activities'].mode()
    if len(mode):
        fills['Extracurricular Activities'] = mode.iloc[0]
    if fills.isna().any():
        raise ValueError('A training feature has no observed values')
    a, b = a.fillna(fills), b.fillna(fills)
    for frame in (a, b):
        frame[SYNTHETIC] = frame['Hours Studied'] * frame['Previous Scores']
    mean, scale = a.mean(), a.std(ddof=0)
    scale = scale.mask(scale == 0, 1.0)
    params = {'fill': fills.to_dict(), 'mean': mean.to_dict(), 'scale': scale.to_dict()}
    return (a - mean) / scale, (b - mean) / scale, params


def verification():
    """Проверки известных решений, вырожденности, метрики и предобработки."""
    x = np.array([[0, 0], [1, 0], [0, 1], [2, 3], [-1, 2]], dtype=float)
    y = 3 + 2 * x[:, 0] - 4 * x[:, 1]
    assert np.allclose(fit_ols(x, y), [3, 2, -4], atol=1e-10)
    assert np.allclose(gauss_solve([[0, 1], [2, 3]], [2, 8]), [1, 2])
    try:
        fit_ols(np.ones((5, 2)), np.arange(5))
    except ValueError:
        pass
    else:
        raise AssertionError('Singularity was not detected')
    assert metrics(y, y)['r2'] == 1
    assert abs(metrics(y, np.full(len(y), y.mean()))['r2']) < 1e-12
    a = pd.DataFrame([[1, 50, 'Yes', 7, 1], [3, 70, 'No', 9, 3],
                      [np.nan, 60, None, 8, 2]], columns=FEATURES)
    b = pd.DataFrame([[1000, 90, None, 8, 2]], columns=FEATURES)
    za, zb, params = prepare(a, b)
    assert params['fill']['Hours Studied'] == 2
    assert params['mean']['Hours Studied'] == 2
    assert np.isfinite(za.to_numpy()).all() and np.isfinite(zb.to_numpy()).all()
    families = np.array([[40, 60], [55, 36], [45, 36], [30, 15], [30, 90]])
    savings = np.array([3, 6, 5, 3.5, 1.5])
    assert np.allclose(fit_ols(families, savings), [0.2787, 0.1229, -0.0294], atol=5e-5)
    return ['exact linear recovery', 'pivot row swap', 'singularity detection',
            'perfect and mean-baseline R2', 'missing values and train-only preprocessing',
            'five-family example from Notion theory attachments']


def plots(df, results, predictions, ytest, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    labels = ['Часы учёбы', 'Предыдущие баллы', 'Часы сна',
              'Решённые варианты', 'Индекс успеваемости']
    numeric = df.select_dtypes('number')
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.4), layout='constrained')
    for ax, col, label in zip(axes.flat, numeric.columns, labels):
        v = df[col].dropna()
        ax.hist(v, bins=20, color='#356e91', edgecolor='white')
        q = v.quantile([0.25, .5, .75])
        for value in q:
            ax.axvline(value, color='#cd6535', alpha=.75, linewidth=1)
        ax.set_title(label)
        ax.set_ylabel('Количество')
        ax.text(.03, .97, f'n={len(v)}; mean={v.mean():.2f}\nstd={v.std():.2f}\n'
                f'min={v.min():g}; max={v.max():g}\n'
                f'Q1={q.iloc[0]:g}; Q2={q.iloc[1]:g}; Q3={q.iloc[2]:g}',
                transform=ax.transAxes, va='top', fontsize=8,
                bbox=dict(facecolor='white', alpha=.88, edgecolor='none'))
    df['Extracurricular Activities'].value_counts().plot.bar(ax=axes.flat[5], color='#356e91')
    axes.flat[5].set(title='Внеучебные занятия', xlabel='', ylabel='Количество')
    axes.flat[5].tick_params(axis='x', rotation=0)
    fig.savefig(out / 'distributions.png', dpi=180)
    plt.close(fig)
    corr = encode(df).assign(**{TARGET: df[TARGET]}).corr()
    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
    short = ['Учёба', 'Пред. баллы', 'Занятия', 'Сон', 'Варианты', 'Индекс']
    ax.set_xticks(range(6), short, rotation=25, ha='right')
    ax.set_yticks(range(6), short)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f'{corr.iloc[i,j]:.2f}', ha='center', va='center',
                    color='white' if abs(corr.iloc[i,j]) > .6 else 'black')
    fig.colorbar(im, ax=ax, label='Корреляция Пирсона')
    fig.savefig(out / 'correlation.png', dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout='constrained')
    names = list(results)
    for ax, key, title in zip(axes, ['r2', 'rmse'], ['$R^2$ на тесте', 'RMSE на тесте']):
        values = [results[m]['test'][key] for m in names]
        ax.bar(names, values, color=['#9eabb3', '#6099b3', '#285c80', '#cd6535'])
        ax.set_title(title)
        for i, value in enumerate(values):
            ax.text(i, value, f'{value:.4f}', ha='center', va='bottom', fontsize=9)
        ax.set_ylim(0, max(values) * 1.13)
    fig.savefig(out / 'comparison.png', dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    p = predictions['M3']
    axes[0].scatter(ytest, p, s=7, alpha=.25)
    axes[0].plot([10, 100], [10, 100], color='#cd6535')
    axes[0].set(xlabel='Фактический индекс', ylabel='Прогноз M3')
    axes[1].scatter(p, ytest-p, s=7, alpha=.25)
    axes[1].axhline(0, color='#cd6535')
    axes[1].set(xlabel='Прогноз M3', ylabel='Остаток y - прогноз')
    fig.savefig(out / 'diagnostics.png', dpi=180)
    plt.close(fig)


def main():
    checks = verification()
    source = ROOT / 'data/Student_Performance.csv'
    raw = pd.read_csv(source)
    if list(raw.columns) != FEATURES + [TARGET]:
        raise ValueError('Unexpected dataset schema')
    missing = raw.isna().sum().to_dict()
    # Удаляем полные повторы до разделения, чтобы они не попали в обе части.
    clean = raw.drop_duplicates().dropna(subset=[TARGET]).copy()
    ids = np.random.default_rng(42).permutation(len(clean))
    cut = int(.8 * len(clean))
    train, test = clean.iloc[ids[:cut]], clean.iloc[ids[cut:]]
    a, b, preprocessing = prepare(train, test)
    ytrain, ytest = train[TARGET].to_numpy(), test[TARGET].to_numpy()
    out = ROOT / 'results'
    out.mkdir(exist_ok=True)
    clean.describe().to_csv(out / 'statistics.csv')
    raw.describe().to_csv(out / 'statistics_raw.csv')
    clean['Extracurricular Activities'].value_counts().to_csv(out / 'categories.csv')
    pd.DataFrame({'source_row': clean.index,
                  'split': np.where(clean.index.isin(train.index), 'train', 'test')}).to_csv(
                      out / 'split.csv', index=False)
    results, predictions, coefficient_rows = {}, {}, []
    for name, columns in MODELS.items():
        x, xt = a[columns].to_numpy(), b[columns].to_numpy()
        beta = fit_ols(x, ytrain)
        p = predict(xt, beta)
        predictions[name] = p
        gradient = np.column_stack([np.ones(len(x)), x]).T @ (predict(x, beta)-ytrain)
        assert np.max(np.abs(gradient)) / len(x) < 1e-9
        scale = np.array([preprocessing['scale'][c] for c in columns])
        mean = np.array([preprocessing['mean'][c] for c in columns])
        original = beta[1:] / scale
        intercept = float(beta[0] - mean @ original)
        results[name] = {'features': columns, 'train': metrics(ytrain, predict(x, beta)),
                         'test': metrics(ytest, p), 'beta_standardized': beta.tolist(),
                         'intercept_original': intercept,
                         'beta_original': original.tolist(),
                         'normal_equation_max_residual_per_row': float(np.max(np.abs(gradient))/len(x))}
        for feature, coef in zip(['Intercept'] + columns, [intercept] + original.tolist()):
            coefficient_rows.append({'model': name, 'feature': feature, 'coefficient': coef})
    metadata = {'seed': 42, 'raw_rows': len(raw), 'rows': len(clean),
                'duplicates_removed': int(raw.duplicated().sum()), 'missing': missing,
                'train_rows': len(train), 'test_rows': len(test),
                'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__,
                'checks': checks, 'preprocessing': preprocessing,
                'baseline': metrics(ytest, np.full(len(ytest), ytrain.mean())), 'models': results}
    (out / 'results.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    pd.DataFrame(coefficient_rows).to_csv(out / 'coefficients.csv', index=False)
    pd.DataFrame({'source_row': test.index, 'actual': ytest, **predictions}).to_csv(out / 'predictions.csv', index=False)
    pd.DataFrame([{ 'model': n, **r['test']} for n,r in results.items()]).to_csv(out / 'metrics.csv', index=False)
    plots(clean, results, predictions, ytest, out)
    print(json.dumps({k: v for k,v in metadata.items() if k not in ['preprocessing', 'models']}, indent=2))
    print(pd.read_csv(out / 'metrics.csv').to_string(index=False))


if __name__ == '__main__':
    main()
