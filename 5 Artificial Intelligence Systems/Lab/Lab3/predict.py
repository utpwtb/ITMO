"""Predict with a saved model, including train-fitted preprocessing."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from model import transform

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--model', default='M3_Baseline')
    args = parser.parse_args()
    models = json.loads((ROOT / 'results/models.json').read_text(encoding='utf-8'))
    params = json.loads((ROOT / 'results/preprocessing.json').read_text(encoding='utf-8'))
    model = models[args.model]
    data = pd.read_csv(args.input)
    x = transform(data, params)[model['features']].to_numpy()
    beta = np.array(model['beta'])
    output = data.copy()
    output['prediction'] = beta[0] + x @ beta[1:]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)


if __name__ == '__main__':
    main()
