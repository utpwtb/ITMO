"""Проверка согласованности сохранённой модели, таблиц и отчёта."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
from model import FEATURES, Preprocessor, sigmoid, metrics

ROOT = Path(__file__).resolve().parent
results = ROOT/'results'
state = json.loads((results/'model.json').read_text())
summary = json.loads((results/'summary.json').read_text())
data = pd.read_csv(ROOT/'data/pima-indians-diabetes.csv', header=None,
                   names=FEATURES+['Outcome'])
stored = pd.read_csv(results/'test_predictions.csv')
prep = Preprocessor()
for key, value in state['preprocessing'].items():
    setattr(prep, key, pd.Series(value).reindex(FEATURES))
p = sigmoid(prep.transform(data.iloc[stored.row_id]) @ np.array(state['weights']))
np.testing.assert_allclose(p, stored.probability, atol=1e-14)
m = metrics(stored.actual.to_numpy(), (p >= .5).astype(int))
for key, value in m.items():
    assert abs(value - summary['selected_result'][key]) < 1e-12
grid = pd.read_csv(results/'test_metrics.csv')
validation = pd.read_csv(results/'validation_metrics.csv')
assert len(grid) == len(validation) == 21
assert int(validation.val_log_loss.idxmin()) == summary['selected_id']
assert int(grid.selected.sum()) == 1
assert hashlib.sha256((ROOT/'data/pima-indians-diabetes.csv').read_bytes()).hexdigest() == summary['dataset_sha256']
assert (ROOT/'report/main.pdf').read_bytes().startswith(b'%PDF-')
log_path = ROOT/'report/main.log'
log = log_path.read_text(encoding='utf8', errors='replace') if log_path.exists() else None
if log is not None:
    assert 'Overfull' not in log and 'Missing character' not in log
record = dict(grid_configurations=21,
              saved_predictions_reproduced=True, dataset_sha256_verified=True,
              pdf_present=True, tex_log_checked=log is not None,
              selected_metrics=m)
(results/'verification.json').write_text(json.dumps(record, indent=2), encoding='utf8')
print(json.dumps(record, indent=2))
