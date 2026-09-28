"""Воспроизводимый эксперимент; запуск: python run_experiment.py."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import pandas as pd
from model import (FEATURES, ZERO_MISSING, LogisticRegression, Preprocessor,
                   stratified_split, log_loss, metrics)

ROOT = Path(__file__).resolve().parent


def run():
    out = ROOT / 'results'
    out.mkdir(exist_ok=True)
    source = ROOT / 'data/pima-indians-diabetes.csv'
    data = pd.read_csv(source, header=None, names=FEATURES + ['Outcome'])
    assert data.shape == (768, 9) and set(data.Outcome) == {0, 1}
    data.describe().T.to_csv(out / 'statistics_raw.csv')
    clean = Preprocessor.clean(data)
    clean.describe().T.to_csv(out / 'statistics_observed.csv')
    clean.isna().sum().rename('missing').to_csv(out / 'missing_values.csv')
    y = data.Outcome.to_numpy()
    train, test = stratified_split(y, 0.2, 42)
    subtrain, validation = stratified_split(y[train], 0.2, 43)
    fit_indices, val_indices = train[subtrain], train[validation]
    pd.DataFrame({'row_id': np.arange(len(data)), 'split':
                  np.where(np.isin(np.arange(len(data)), test), 'test',
                           np.where(np.isin(np.arange(len(data)), val_indices),
                                    'validation', 'fit'))}).to_csv(out / 'splits.csv', index=False)
    prep_inner = Preprocessor().fit(data.iloc[fit_indices])
    Xi = prep_inner.transform(data.iloc[fit_indices])
    Xv = prep_inner.transform(data.iloc[val_indices])
    configurations = [dict(method=m, learning_rate=a, iterations=n)
                      for m, rates, budgets in
                      [('gd', [0.001, 0.01, 0.1, 1.0], [100, 1000, 5000]),
                       ('newton', [0.1, 0.5, 1.0], [3, 10, 30])]
                      for a in rates for n in budgets]
    validation_rows = []
    for i, config in enumerate(configurations):
        model = LogisticRegression(**config).fit(Xi, y[fit_indices])
        validation_rows.append(dict(config_id=i, **config,
            val_log_loss=log_loss(y[val_indices], Xv @ model.weights),
            **{f'val_{k}': v for k, v in metrics(y[val_indices], model.predict(Xv)).items()}))
    validation_table = pd.DataFrame(validation_rows)
    # Правило зафиксировано до просмотра test: минимум validation log loss.
    best_id = int(validation_table.val_log_loss.idxmin())
    validation_table.to_csv(out / 'validation_metrics.csv', index=False)
    prep = Preprocessor().fit(data.iloc[train])
    Xtr, Xte = prep.transform(data.iloc[train]), prep.transform(data.iloc[test])
    rows, histories, fitted = [], {}, {}
    for i, config in enumerate(configurations):
        model = LogisticRegression(**config).fit(Xtr, y[train])
        fitted[i] = model
        histories[str(i)] = model.loss_history
        rows.append(dict(config_id=i, **config, selected=(i == best_id),
            train_log_loss=model.loss_history[-1],
            test_log_loss=log_loss(y[test], Xte @ model.weights),
            **metrics(y[test], model.predict(Xte))))
    table = pd.DataFrame(rows)
    table.to_csv(out / 'test_metrics.csv', index=False)
    selected = fitted[best_id]
    predictions = pd.DataFrame({'row_id': test, 'actual': y[test],
                               'probability': selected.predict_proba(Xte),
                               'predicted': selected.predict(Xte)})
    predictions.to_csv(out / 'test_predictions.csv', index=False)
    coefficients = pd.DataFrame({'feature': ['Intercept'] + FEATURES,
                                 'weight': selected.weights,
                                 'odds_ratio': np.exp(selected.weights)})
    coefficients.to_csv(out / 'coefficients.csv', index=False)
    (out / 'loss_histories.json').write_text(json.dumps(histories), encoding='utf8')
    model_state = dict(config=configurations[best_id], threshold=0.5,
                       weights=selected.weights.tolist(), preprocessing=prep.to_dict())
    (out / 'model.json').write_text(json.dumps(model_state, indent=2), encoding='utf8')
    summary = dict(rows=len(data), duplicates=int(data.duplicated().sum()),
        raw_nulls=int(data.isna().sum().sum()), class_counts=data.Outcome.value_counts().to_dict(),
        split_sizes=dict(train=len(train), test=len(test), fit=len(fit_indices), validation=len(val_indices)),
        split_classes={name: np.bincount(y[idx], minlength=2).tolist()
                       for name,idx in [('train',train),('test',test),('fit',fit_indices),('validation',val_indices)]},
        missing=clean.isna().sum().to_dict(), selected_id=best_id,
        selected_config=configurations[best_id], selected_result=rows[best_id],
        validation_result=validation_rows[best_id],
        baseline=metrics(y[test], np.zeros(len(test), dtype=int)),
        dataset_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        versions=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__))
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    run()
