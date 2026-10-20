"""Run the complete regularization experiment: python experiment.py."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from model import (FEATURES, TARGET, MODELS, split_data, fit_preprocessor,
                   transform, fit, metrics, optimality_residual)

ROOT = Path(__file__).resolve().parent
LAMBDAS = [.001, .01, .1, 1., 10.]
RATIOS = [.2, .5, .8]
LABELS = {'Baseline': 'Без регуляризации', 'L1': 'L1', 'L2': 'L2', 'ElasticNet': 'ElasticNet'}


def plot_results(history, grid, coefficients, destination):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    styles = [('Baseline', '#202020', '-'), ('L1', '#0072b2', '--'),
              ('L2', '#d55e00', '-.'), ('ElasticNet', '#009e73', ':')]
    destination.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        fig, axes = plt.subplots(2, 2, figsize=(10.4, 7), layout='constrained')
        for ax, key, title in zip(axes.flat,
                ['train_mse', 'validation_mse', 'train_r2', 'validation_r2'],
                ['MSE: обучение', 'MSE: валидация', '$R^2$: обучение', '$R^2$: валидация']):
            for method, color, style in styles:
                subset = history[(history.model == model) & (history.method == method)]
                ax.plot(subset.iteration, subset[key], label=LABELS[method], color=color,
                        linestyle=style, linewidth=1.7)
            ax.set(xlabel='Итерация', ylabel='MSE' if key.endswith('mse') else '$R^2$', title=title)
            ax.set_xscale('symlog', linthresh=10)
            if key.endswith('mse'):
                ax.set_yscale('log')
            ax.grid(alpha=.2)
            ax.legend(fontsize=8)
        fig.savefig(destination / f'{model}_curves.pdf')
        fig.savefig(destination / f'{model}_curves.png', dpi=170)
        plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7), layout='constrained')
    for ax, model in zip(axes.flat, MODELS):
        subset = grid[grid.model == model]
        baseline = subset[subset.method == 'Baseline'].iloc[0].validation_mse
        ax.axhline(baseline, color='#202020', label='Без регуляризации')
        for method in ['L1', 'L2', 'ElasticNet']:
            selected = subset[subset.method == method]
            for ratio, group in selected.groupby('ratio'):
                label = method if method != 'ElasticNet' else f'EN, α={ratio:g}'
                ax.plot(group.lam, group.validation_mse, 'o--', markersize=3, label=label)
        ax.set(xscale='log', yscale='log', xlabel='λ', ylabel='MSE на валидации', title=model)
        ax.grid(alpha=.2)
        ax.legend(fontsize=7)
    fig.savefig(destination / 'parameter_search.pdf')
    fig.savefig(destination / 'parameter_search.png', dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.5), layout='constrained')
    for ax, model in zip(axes, ['M3', 'M4']):
        subset = coefficients[(coefficients.model == model) & (coefficients.feature != 'Intercept')]
        names = list(MODELS[model])
        positions = np.arange(len(names))
        for i, (method, color, _) in enumerate(styles):
            values = subset[subset.method == method].set_index('feature').loc[names].standardized
            ax.bar(positions + (i-1.5)*.19, values, width=.19, label=LABELS[method], color=color)
        ax.set_xticks(positions, ['Учёба', 'Баллы', 'Занятия', 'Сон', 'Варианты', 'Произведение'][:len(names)], rotation=30, ha='right')
        ax.set(title=model, ylabel='Коэффициент стандартизованного признака')
        ax.legend(fontsize=7)
        ax.grid(axis='y', alpha=.2)
    fig.savefig(destination / 'coefficients.pdf')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--learning-rate', type=float, default=.05)
    parser.add_argument('--iterations', type=int, default=15000)
    parser.add_argument('--lambdas', type=float, nargs='+', default=LAMBDAS)
    parser.add_argument('--ratios', type=float, nargs='+', default=RATIOS)
    args = parser.parse_args()
    source = ROOT / 'data/Student_Performance.csv'
    raw = pd.read_csv(source)
    train, validation, test = split_data(raw)
    params = fit_preprocessor(train)
    a, v, t = [transform(frame, params) for frame in [train, validation, test]]
    yt, yv, ye = [frame[TARGET].to_numpy() for frame in [train, validation, test]]
    out = ROOT / 'results'
    out.mkdir(exist_ok=True)
    splits = pd.concat([pd.DataFrame({'source_row': frame.index, 'split': name})
                        for frame, name in [(train, 'train'), (validation, 'validation'), (test, 'test')]])
    splits.sort_values('source_row').to_csv(out / 'split.csv', index=False)
    (out / 'preprocessing.json').write_text(json.dumps(params, indent=2), encoding='utf-8')
    configs = [('Baseline', 0., 0.)]
    configs += [('L1', lam, 1.) for lam in args.lambdas]
    configs += [('L2', lam, 0.) for lam in args.lambdas]
    configs += [('ElasticNet', lam, ratio) for lam in args.lambdas for ratio in args.ratios]
    grid, final, histories, coefs, predictions, saved = [], [], [], [], [], {}
    for name, features in MODELS.items():
        x, xv, xe = [frame[features].to_numpy() for frame in [a, v, t]]
        local = []
        for method, lam, ratio in configs:
            beta, _ = fit(x, yt, lam=lam, ratio=ratio, learning_rate=args.learning_rate,
                          iterations=args.iterations)
            row = {'model': name, 'method': method, 'lam': lam, 'ratio': ratio,
                   'train_mse': metrics(yt, beta[0] + x @ beta[1:])['mse'],
                   'validation_mse': metrics(yv, beta[0] + xv @ beta[1:])['mse'],
                   'l1_norm': float(abs(beta[1:]).sum()), 'l2_norm': float(np.sqrt(beta[1:] @ beta[1:])),
                   'zeros': int(np.sum(beta[1:] == 0)),
                   'near_zeros': int(np.sum(abs(beta[1:]) < .01)),
                   'kkt_residual': optimality_residual(x, yt, beta, lam, ratio)}
            local.append(row)
            grid.append(row)
        for method in LABELS:
            # Select only by validation MSE; deterministic tie breakers.
            choice = min((r for r in local if r['method'] == method),
                         key=lambda r: (r['validation_mse'], r['lam'], r['ratio']))
            lam, ratio = choice['lam'], choice['ratio']
            beta, history = fit(x, yt, lam=lam, ratio=ratio,
                                learning_rate=args.learning_rate, iterations=args.iterations,
                                validation=(xv, yv), record=True)
            history.insert(0, 'method', method)
            history.insert(0, 'model', name)
            histories.append(history)
            row = dict(choice)
            for split, xs, ys in [('train', x, yt), ('validation', xv, yv), ('test', xe, ye)]:
                row.update({f'{split}_{k}': value for k, value in metrics(ys, beta[0]+xs @ beta[1:]).items()})
            final.append(row)
            scale = np.array([params['scale'][f] for f in features])
            mean = np.array([params['mean'][f] for f in features])
            raw_w = beta[1:] / scale
            raw_beta = np.r_[beta[0] - mean @ raw_w, raw_w]
            for feature, bs, br in zip(['Intercept'] + features, beta, raw_beta):
                coefs.append({'model': name, 'method': method, 'feature': feature,
                              'standardized': bs, 'original_scale': br})
            predictions.append(pd.DataFrame({'source_row': test.index, 'model': name,
                                            'method': method, 'actual': ye,
                                            'prediction': beta[0] + xe @ beta[1:]}))
            saved[f'{name}_{method}'] = {'features': features, 'beta': beta.tolist(), 'lam': lam, 'ratio': ratio}
        print(f'{name}: {len(local)} configurations complete', flush=True)
    grid, final, history, coefficients = pd.DataFrame(grid), pd.DataFrame(final), pd.concat(histories), pd.DataFrame(coefs)
    for name, frame in [('validation_search', grid), ('metrics', final), ('learning_curves', history),
                        ('coefficients', coefficients), ('test_predictions', pd.concat(predictions))]:
        frame.to_csv(out / f'{name}.csv', index=False, float_format='%.12g')
    (out / 'models.json').write_text(json.dumps(saved, indent=2), encoding='utf-8')
    summary = {'raw_rows': len(raw), 'duplicates_removed': int(raw.duplicated().sum()),
               'missing': raw.isna().sum().to_dict(), 'train': len(train), 'validation': len(validation), 'test': len(test),
               'learning_rate': args.learning_rate, 'iterations': args.iterations,
               'lambdas': args.lambdas, 'ratios': args.ratios, 'initial_weights': 'zeros',
               'seed_outer': 42, 'seed_inner': 43, 'configurations': len(grid),
               'data_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    plot_results(history, grid, coefficients, ROOT / 'report/figures')
    print(final[['model', 'method', 'lam', 'ratio', 'validation_mse', 'test_mse', 'test_r2', 'zeros']].to_string(index=False))


if __name__ == '__main__':
    main()
