"""Numerical correctness, leakage prevention and saved-output checks."""
import json
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import (FEATURES, TARGET, MODELS, fit, metrics, fit_preprocessor,
                   transform, split_data, optimality_residual)


class ModelTests(unittest.TestCase):
    def test_orthogonal_closed_form_all_penalties(self):
        # Orthogonal standardized features have an exact soft-threshold solution.
        x = np.array([[-1., -1.], [-1., 1.], [1., -1.], [1., 1.]])
        y = 3 + x @ np.array([2., .1])
        for lam, ratio in [(0., 0.), (.5, 1.), (.5, 0.), (.5, .5)]:
            beta, _ = fit(x, y, lam=lam, ratio=ratio, iterations=2000)
            expected = np.maximum(np.array([2., .1]) - lam*ratio, 0) / (1+lam*(1-ratio))
            np.testing.assert_allclose(beta, np.r_[3., expected], atol=1e-11)
            self.assertLess(optimality_residual(x, y, beta, lam, ratio), 1e-11)

    def test_intercept_not_penalized(self):
        x = np.zeros((8, 2))
        y = np.full(8, 7.)
        for ratio in [0., .5, 1.]:
            beta, _ = fit(x, y, lam=10., ratio=ratio, iterations=2000)
            np.testing.assert_allclose(beta, [7, 0, 0], atol=1e-11)

    def test_zero_lambda_equivalence(self):
        rng = np.random.default_rng(5)
        x, y = rng.normal(size=(30, 3)), rng.normal(size=30)
        b0, _ = fit(x, y)
        for ratio in [0, .2, .5, .8, 1]:
            b, _ = fit(x, y, ratio=ratio)
            np.testing.assert_array_equal(b, b0)

    def test_history_matches_direct_unpenalized_metrics(self):
        rng = np.random.default_rng(8)
        x, y = rng.normal(size=(40, 3)), rng.normal(size=40)
        xv, yv = rng.normal(size=(10, 3)), rng.normal(size=10)
        beta, h = fit(x, y, lam=1, ratio=.5, validation=(xv, yv), record=True, iterations=300)
        self.assertEqual(len(h), 301)
        self.assertAlmostEqual(h.iloc[-1].train_mse, metrics(y, beta[0]+x@beta[1:])['mse'], places=11)
        self.assertAlmostEqual(h.iloc[-1].validation_mse, metrics(yv, beta[0]+xv@beta[1:])['mse'], places=11)
        self.assertAlmostEqual(h.iloc[0].train_mse, np.mean(y**2))

    def test_train_only_preprocessing(self):
        train = pd.DataFrame([[1, 50, 'Yes', 7, 1], [3, 70, 'No', 9, 3],
                              [np.nan, 60, None, 8, 2]], columns=FEATURES)
        params = fit_preprocessor(train)
        frozen = json.dumps(params, sort_keys=True)
        val = pd.DataFrame([[10000, 20000, None, 50000, 500]], columns=FEATURES)
        result = transform(val, params)
        self.assertEqual(json.dumps(params, sort_keys=True), frozen)
        self.assertEqual(params['mean']['Hours Studied'], 2.)
        self.assertTrue(np.isfinite(result.to_numpy()).all())
        np.testing.assert_allclose(transform(train, params).mean(), 0, atol=1e-14)

    def test_split_disjoint_and_matches_lab1(self):
        raw = pd.read_csv(ROOT / 'data/Student_Performance.csv')
        train, val, test = split_data(raw)
        self.assertEqual([len(train), len(val), len(test)], [5923, 1975, 1975])
        self.assertFalse(set(train.index) & set(val.index))
        self.assertFalse(set(train.index) & set(test.index))
        self.assertFalse(set(val.index) & set(test.index))
        self.assertEqual(len(set(train.index) | set(val.index) | set(test.index)), len(raw.drop_duplicates()))
        previous = ROOT.parent / 'Lab1/results/split.csv'
        if previous.exists():
            old = pd.read_csv(previous)
            self.assertEqual(set(test.index), set(old.loc[old.split == 'test', 'source_row']))

    def test_saved_selection_and_predictions(self):
        results = ROOT / 'results'
        final = pd.read_csv(results / 'metrics.csv')
        grid = pd.read_csv(results / 'validation_search.csv')
        predictions = pd.read_csv(results / 'test_predictions.csv')
        params = json.loads((results / 'preprocessing.json').read_text())
        models = json.loads((results / 'models.json').read_text())
        data = pd.read_csv(ROOT / 'data/Student_Performance.csv')
        for row in final.itertuples():
            candidates = grid[(grid.model == row.model) & (grid.method == row.method)]
            self.assertAlmostEqual(row.validation_mse, candidates.validation_mse.min(), places=9)
            p = predictions[(predictions.model == row.model) & (predictions.method == row.method)]
            saved = models[f'{row.model}_{row.method}']
            x = transform(data.loc[p.source_row], params)[saved['features']].to_numpy()
            beta = np.array(saved['beta'])
            np.testing.assert_allclose(beta[0]+x@beta[1:], p.prediction, atol=1e-8)
            self.assertAlmostEqual(metrics(p.actual.to_numpy(), p.prediction.to_numpy())['mse'], row.test_mse, places=7)
            self.assertLess(row.kkt_residual, 1e-7)

    def test_invalid_parameters_and_step_rejected(self):
        x, y = np.ones((3, 1)), np.arange(3.)
        for kwargs in [dict(lam=-1), dict(ratio=2), dict(learning_rate=10)]:
            with self.assertRaises(ValueError):
                fit(x, y, **kwargs)


if __name__ == '__main__':
    unittest.main()
