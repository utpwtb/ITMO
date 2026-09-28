"""Использование сохранённой модели без повторного обучения."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from model import FEATURES, Preprocessor, sigmoid

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--row-id', type=int, help='Индекс строки локального набора, от 0 до 767')
group.add_argument('--input', type=Path, help='CSV с заголовками восьми признаков')
args = parser.parse_args()
state = json.loads((ROOT/'results/model.json').read_text())
prep = Preprocessor()
for key, value in state['preprocessing'].items():
    setattr(prep, key, pd.Series(value).reindex(FEATURES))
if args.input:
    frame = pd.read_csv(args.input)
else:
    frame = pd.read_csv(ROOT/'data/pima-indians-diabetes.csv', header=None,
                        names=FEATURES+['Outcome'])
    if not 0 <= args.row_id < len(frame):
        parser.error('--row-id must be between 0 and 767')
    frame = frame.iloc[[args.row_id]].copy()
probabilities = sigmoid(prep.transform(frame) @ np.array(state['weights']))
result = pd.DataFrame({'probability': probabilities,
                       'predicted': (probabilities >= state['threshold']).astype(int)})
if 'Outcome' in frame:
    result['actual'] = frame.Outcome.to_numpy()
print(result.to_csv(index=False), end='')
